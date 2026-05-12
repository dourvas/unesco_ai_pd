# C.4 Design Proposal — Privacy Dashboard + Right of Access / Right to Erasure

**Date:** 2026-05-11
**Author:** Claude Code (this session)
**Status:** DRAFT — awaiting confirmation of D1-D14 before implementation
**Companion docs:**
- `PHASE_C_MIGRATION_PLAN_v1_20260509.md` (the §3.10 anonymize_user reference is **stale**; see D1 below)
- `audits/DEAD_SCHEMA_AUDIT_20260509.md` (confirms the DB function was dropped + was broken)
- `apps/compliance/services.py` (contains the canonical `record_consent` / `revoke_consent` helpers we will reuse)
- `proodos_files/TECH_DEBT_LOG.md::TD-008` (the AI Disclosure revocation bug this design closes)

---

## 0. Scope summary

C.4 adds a participant-facing Privacy dashboard at `/profile/privacy/` that exposes the three GDPR self-service rights covered by the pilot:

- **Article 7(3) — right to withdraw consent** for each of the three consent types (`ai_disclosure`, `research_participation`, `data_sharing`).
- **Article 15 — right of access**: download a JSON export of all personal data the platform holds about the user.
- **Article 17 — right to erasure**: trigger a full account anonymization that NULLs all PII while retaining research-relevant data per the consent state at erasure time.

It also closes TD-008 (the AI Disclosure revocation path that previously did not clear `TeacherProfile.ai_disclosure_acknowledged_at`).

**Out of scope for C.4:**
- Selective deletion of single reflections / single AILST responses (deferred to **TD-014**, post-pilot).
- PDF data export (deferred to TD-015, post-pilot — JSON suffices for GDPR Art. 15).
- The pre-pilot module/Epilogue progression gates (TD-012 / TD-013) — orthogonal.
- Full PROODOS Epilogue feature (TD-011).

---

## 1. Reusable inventory

| Component | Use in C.4 |
|---|---|
| `apps.compliance.services.record_consent` | Used to write the explicit "denial" row when the user revokes. Supersede semantics keep audit trail clean. |
| `apps.compliance.services.revoke_consent` | Used to flip `revoked_at` on the active row for each `consent_type`. Per-row save() so the M6 sync signal fires. |
| `apps.compliance.signals.sync_teacher_profile_booleans` | Already keeps `TeacherProfile.research_consent` and `.consent_data_sharing` in sync with canonical state. **Not touched** by this design. |
| `apps.compliance.copy.AI_DISCLOSURE_TEXT_V1_PRE_IRB` etc. | Read for "what version did the user agree to" display in the consent history card. |
| `apps.compliance.templatetags.consent_format` | Reused for any verbatim consent text rendering (history detail expand). |
| `apps.ailst.models.AilstResponse` | Read for data export. **Not deleted** on research_consent revoke (per D9 cascade policy). |
| `apps.modules.models.UserModuleProgress` | Read for data export. Same retention policy as AilstResponse. |
| `apps.epilogue.models.EpilogueCompletion` | Read for data export. |

---

## 2. Design decisions

### D1 — anonymize_user implementation: Python service, not DB function

**Decision:** Implement `apps.compliance.services.anonymize_user(user)` as a Python helper running inside a `transaction.atomic()` block. **Do NOT use the historical PostgreSQL function** (it was dropped in Γ.1 migration `compliance/0002_drop_dead_schema` and was column-broken before that).

The historical function's _semantic_ intent is the reference for what fields to touch, but the column names in its body (`years_experience`, `ai_experience_level`) do not match the current `teacher_profiles` schema. Treat its source code as documentation of intent, not as a template for column mapping.

**What the Python service does (atomic):**

1. **`auth_user` row** (NOT deleted — preserves FK targets for ConsentRecord and research data):
   - `username` → `f'anonymized_{user.id}'` (must remain unique; the integer keeps it so)
   - `email` → `''` (empty string; column is `NOT NULL UNIQUE` historically, empty is safer than NULL; revisit if conflict with other anonymized rows by appending `f'@deleted.local-{user.id}'`)
   - `first_name` → `''`
   - `last_name` → `''`
   - `is_active` → `False` (prevents login)
   - `password` → unusable (`user.set_unusable_password()`)

2. **`TeacherProfile` row** (NOT deleted):
   - `first_name` → `''`
   - `last_name` → `''`
   - `display_name` → `''`
   - `ai_disclosure_acknowledged_at` → `None` (so middleware re-prompts if somehow re-activated)
   - `profile_completed` → False
   - `research_consent` → False, `consent_data_sharing` → False, `contact_for_research` → False
   - `research_data_opted_out` → True (the new flag from D13)
   - Free-text fields that may contain identifiable content: `subject_area_other`, `ai_tools_used`, `ai_teaching_integration`, `primary_goals`, `current_curriculum_pressure`, `institutional_ai_policy` → cleared per audit-driven list (see D13 implementation note).

3. **`ConsentRecord` rows** (retained per D12):
   - `ip_address` → `None` (redact remaining IPs immediately; the 30-day batch job is moot post-erasure)
   - All other fields unchanged. `granted` / `granted_at` / `revoked_at` / `consent_text` / `version` are part of the IRB audit trail and survive 7 years.

4. **`AilstResponse` rows, `UserModuleProgress` rows, `EpilogueCompletion` row, reflection text, AI dispute submissions**: **retained as-is**. The `user_id` FK now points to an anonymized auth_user row. Research analyses can exclude opt-outs by filtering on `TeacherProfile.research_data_opted_out=True`.

5. **Final actions** (after the atomic block commits):
   - `logout(request)` to drop the current session.
   - `messages.info(request, 'Your account has been anonymized.')`
   - Redirect to `users:landing`.

**Why retain auth_user instead of delete:** all FK relations cascade on User delete. Deleting the user would `CASCADE` and drop AilstResponse, UserModuleProgress, ConsentRecord, EpilogueCompletion — destroying both the research data AND the IRB audit trail. The pseudonymized-username pattern preserves both while making the user un-identifiable.

### D2 — URL location: `/profile/privacy/`

**Decision:** Mount the dashboard at `/profile/privacy/`, with sub-routes under it for actions:

```
/profile/privacy/                       # GET — dashboard (consents + actions)
/profile/privacy/revoke/ai-disclosure/  # POST — revoke AI disclosure
/profile/privacy/revoke/research/       # POST — revoke research participation
/profile/privacy/revoke/data-sharing/   # POST — revoke data sharing
/profile/privacy/export/                # GET — JSON file download
/profile/privacy/erase/                 # GET — confirmation page
/profile/privacy/erase/confirm/         # POST — execute anonymization
```

Lives under the `compliance` URL namespace. Rationale: `/profile/edit/` already exists in `users` namespace, so `/profile/privacy/` is the natural sibling URL, but the implementation belongs to compliance (where the consent + erasure surface lives).

### D3 — Single-page dashboard, three sections

**Decision:** One page, three DaisyUI `card` sections vertically stacked:

1. **Consents** — list of three rows (ai_disclosure, research_participation, data_sharing) with current state (active / revoked / never granted), granted/revoked dates, version, and a "Withdraw" button on each active row.
2. **Your data** — counts + sources (e.g., "1 profile, 3 AILST responses, 4 module completions, 1 Epilogue completion, 27 reflection turns"), with a "Download as JSON" button. Includes the AI-outputs section per D11.
3. **Delete account** — short explanation + "Delete my account" button leading to the confirmation page.

No tabs / no JS state. A user must scroll to see the delete option, which provides a small UX friction against accidental clicks. The page is intentionally non-busy.

### D4 — Data export format: JSON v1

**Decision:** JSON file download, served via `HttpResponse(content_type='application/json')` with `Content-Disposition: attachment; filename="proodos_export_<username>_<date>.json"`. No upload to any external storage. Synchronous (response body size will be small — at most ~50 KB even for completed participants).

**Top-level shape:**

```json
{
  "export_version": "1",
  "exported_at": "2026-05-11T18:23:00Z",
  "user": { "username": "...", "email": "...", "date_joined": "..." },
  "profile": { ... all TeacherProfile fields ... },
  "consents": [ { consent_type, version, granted, granted_at, revoked_at, consent_text }, ... ],
  "ailst_responses": [ { timepoint, started_at, completed_at, responses, all 5 scores }, ... ],
  "module_progress": [ { code, started_at, completed_at, completion_percentage, reflection_text, ... }, ... ],
  "epilogue_completion": { started_at, completed_at } or null,
  "ai_outputs": {
    "rtm_positions": [ ... per-module ... ],
    "dtp_narratives": [ ... per-module ... ],
    "rag_feedback": [ ... per-module reflection ... ]
  }
}
```

If `research_data_opted_out` is True, the export still includes the data — the opt-out affects **future research analyses**, not the user's own right of access (Art. 15 is a personal right, not contingent on research participation).

### D5 — Data export scope

Already detailed in D4 shape. Defaults:
- **Includes** every table the user has linked rows in.
- **Excludes** internal-only fields like `_change_source` audit attributes; includes the human-meaningful change history from `TeacherProfileHistory`.
- **Verbatim consent text** is included (Art. 15 explicitly covers "the information given to the data subject").
- **AI outputs** (RTM, DTP, RAG feedback) — see D11.

### D6 — Erasure confirmation: Greek free-text "ΔΙΑΓΡΑΦΗ"

**Decision:** Two-step. The "Delete my account" button on the dashboard navigates to `/profile/privacy/erase/`, which shows:

- A `alert alert-warning` block listing the consequences:
  - "All identifying information will be permanently removed: your name, email, profile, IP addresses."
  - "Your research contributions stay in the platform, attached to an anonymous account."
  - "You will be logged out immediately. You cannot log in again."
  - "This action is irreversible."
- A `<input type="text">` field labelled "Type ΔΙΑΓΡΑΦΗ in capital Greek letters to confirm" — the submit button is JS-disabled until the exact case-sensitive match.
- The form POSTs to `/profile/privacy/erase/confirm/`, where the view re-validates the exact match server-side as well (never trust JS).

Greek language for the confirmation token matches the participant pool (Greek-speaking K-12 educators). The English token `DELETE` would be cognitively foreign and slightly less impactful.

### D7 — Post-erasure: logout + redirect to landing

**Decision:** After the `transaction.atomic()` block commits, call `django.contrib.auth.logout(request)`, attach a flash message, redirect to `users:landing`. The user lands on the public landing page (not the dashboard, which they can no longer access).

The flash message: "Your account has been anonymized. Thank you for your participation."

### D8 — AI Disclosure revocation: atomic transaction with profile flag clear

**Decision:** The revoke view runs inside `transaction.atomic()`:

```python
with transaction.atomic():
    profile = TeacherProfile.objects.select_for_update().get(user=request.user)
    revoke_consent(user=request.user, consent_type='ai_disclosure')
    profile.ai_disclosure_acknowledged_at = None
    profile.save(update_fields=['ai_disclosure_acknowledged_at'])
logout(request)
messages.info(request, 'AI Disclosure consent withdrawn. You have been logged out.')
return redirect('users:landing')
```

Logout-after-revoke is **deliberate**: the next anonymous request to any platform URL will trigger the middleware → re-show the modal. Forcing the logout here gives the user a clean "I have withdrawn" state rather than a half-logged-in user bouncing between modal and dashboard.

The `select_for_update` on the profile row guards against the (rare) race where the user double-clicks the revoke button and a parallel request leaves the flag set.

This closes **TD-008**.

### D9 — research_consent revocation cascade

**Decision:** Following John's specification:

1. `revoke_consent(user, consent_type='research_participation')` — supersede pattern, ConsentRecord row marked revoked.
2. M6 signal auto-syncs `TeacherProfile.research_consent = False`.
3. **Set `TeacherProfile.research_data_opted_out = True`** (the new flag from D13). This is the durable opt-out that filters the user out of future research analyses and exports.
4. **Already-collected data is preserved** — no auto-delete. The AILST responses and reflection texts stay in the DB.
5. **Future AILST timepoints are blocked** — the C.2.3 entry view already gates on `profile.research_consent` and will redirect the user to the `research_consent_required` page.

If the user wants the already-collected data deleted, they must use the **separate "Delete my account" action** (the erasure flow). Two rights, two actions. This matches the legal framing: revocation is forward-looking; erasure is retrospective.

The post-revoke flash message clarifies this: "Research participation consent withdrawn. We will not collect new research data from you. Your existing data remains until you ask us to delete it via the 'Delete my account' option below."

### D10 — Middleware bypass for `/profile/privacy/`: NO

**Decision:** No bypass. Verified that the AI Disclosure modal has the "Or log out" link ([templates/onboarding/ai_disclosure.html:74-75](templates/onboarding/ai_disclosure.html)), so a user who has revoked `ai_disclosure` and is intercepted by middleware has a clean exit path. The Privacy dashboard sits behind the same gate as the rest of the authenticated platform.

### D11 — AI-generated outputs display

**Decision:** A dedicated section "AI-generated insights based on your reflections" in the **Your data** card on the dashboard. Layout:

- **Summary line**: counts ("12 RTM positions across 9 modules", "5 DTP narratives generated", "4 RAG feedback responses").
- **"View all" expand button** that reveals collapsible cards per module:
  - **RTM positions card** for each module: shows the tension positions JSON the user confirmed.
  - **DTP narrative card** for each module: shows the rendered narrative HTML/text.
  - **RAG feedback card** for each reflection: shows the feedback HTML.
- **Every AI-generated card carries `data-ai-generated="true"`** (HTML attribute) per the C.3 forward compatibility note (no C.3 yet, but the marker is cheap to add now).

The same AI outputs appear verbatim in the JSON export under `ai_outputs`. The export is the canonical Art. 15 deliverable; the dashboard view is a friendly UI on top.

**Source tables:**
- RTM positions: `apps.modules.models.ReflectionTension`
- DTP narratives: `UserModuleProgress.reflection_dtp` JSON field
- RAG feedback: `UserModuleProgress.reflection_rag_feedback` text field
- Peer synthesis (also AI-generated): `UserModuleProgress.reflection_peer_synthesis` text field — include in the same card stack.

### D12 — ConsentRecord retention post-erasure: 7 years, pointer to anonymized auth_user

**Decision:** Per John's specification:

- ConsentRecord rows are **never deleted** during erasure.
- Their `user_id` FK continues to point to the (now anonymized) auth_user row.
- `ip_address` is cleared at erasure time (no need to wait for the 30-day batch).
- All other fields (granted, granted_at, revoked_at, consent_text, version) remain intact for 7-year IRB / GDPR audit.

This matches the table's existing schema comment about long-term retention and aligns with the EU AI Act recital recommendations for record-keeping. A future TD entry will define the 7-year cleanup job (run nightly, deletes ConsentRecord rows where `granted_at < NOW() - INTERVAL '7 years'` AND the user is anonymized). Out of scope for C.4.

### D13 — New `TeacherProfile.research_data_opted_out` BooleanField

**Decision:** Add a new boolean column to `TeacherProfile`:

```python
research_data_opted_out = models.BooleanField(
    default=False,
    help_text=(
        "Set to True when the user revokes research_participation consent "
        "OR triggers an account erasure. Future research analyses and "
        "exports MUST filter out users with this flag set. The user's "
        "already-collected data remains in the DB (no retroactive delete) "
        "but is excluded from new analyses per the user's withdrawal."
    ),
)
```

New migration `users/0010_teacherprofile_research_data_opted_out.py` (additive: adds the column with default=False, no data backfill needed since existing users default to False).

The flag is the durable "this user is opted out" signal, distinct from `research_consent` which is the active consent state. After erasure both will be False, but `research_data_opted_out=True` is the dominant filter for analytics queries.

PII fields that get cleared on erasure (referenced from D1 step 2):
- `first_name`, `last_name`, `display_name`
- `subject_area_other` (free text — may contain identifiers)
- `ai_tools_used` (free text list — may contain identifiable tool names)
- `ai_teaching_integration` (free text)
- `primary_goals` (JSON list of choice values; less likely identifiable but contains preferences — clear to be safe)
- `current_curriculum_pressure` (free text from M2)
- `institutional_ai_policy` (choice + optional free text from M2)

Numeric / categorical research variables are **preserved** (subject_area, grade_level, teaching_years, school_location, average_class_size, ai_experience, preferred_communication_style) — these are the variables of scientific interest, are non-identifying at population scale, and align with the "anonymized data sharing" consent text in `apps/compliance/copy.py:124-155`.

### D14 — Selective deletion (single reflection / single AILST response): deferred to TD-014

**Decision:** Out of scope for C.4. Full account erasure (anonymization) is the only deletion path in C.4 and is sufficient for GDPR Article 17 compliance (the right to erasure is for "the data", not for "a specific subset of the data").

Selective deletion is a fine-grained UX feature that requires:
- A new "Delete this item" button per reflection / per AILST response,
- Confirmation flow per type,
- Cascade rules per type (e.g., deleting an AILST response also clears the corresponding factor scores; deleting a reflection clears the related RAG feedback and DTP narrative),
- Re-export logic to keep the JSON export consistent post-selective-delete.

That belongs in **TD-014**, post-pilot. The TD entry will reference this design proposal as the canonical decision point.

---

## 3. Schema change

One additive migration `users/0010_teacherprofile_research_data_opted_out.py`:

```python
operations = [
    migrations.AddField(
        model_name='teacherprofile',
        name='research_data_opted_out',
        field=models.BooleanField(
            default=False,
            help_text='...'
        ),
    ),
]
```

Standard `pg_dump` backup before apply: `pre_migration_backup_phaseC_C4_20260512.sql`.

No other schema changes. The PII clearing in `anonymize_user` operates entirely on existing columns.

---

## 4. Files to create / modify

### New
| File | LOC est. |
|---|---|
| `apps/users/migrations/0010_teacherprofile_research_data_opted_out.py` | 25 |
| `apps/compliance/templates/compliance/privacy_dashboard.html` | 250 |
| `apps/compliance/templates/compliance/erasure_confirm.html` | 100 |
| `templates/emails/account_anonymized.txt` (optional courtesy email — see Q below) | 30 |

### Modified
| File | Action | LOC est. |
|---|---|---|
| `apps/compliance/services.py` | Add `anonymize_user(user)` function | ~120 |
| `apps/compliance/services.py` | Add `gather_user_export(user) -> dict` | ~80 |
| `apps/compliance/services.py` | Add `clear_pii_on_profile(profile)` private helper | ~40 |
| `apps/compliance/views.py` | Add 7 views (dashboard, 3 revoke, export, erase_confirm, erase_execute) | ~250 |
| `apps/compliance/urls.py` | Add 7 routes under namespace 'compliance' | ~20 |
| `apps/users/models.py` | Add `research_data_opted_out` field | 12 |
| `apps/users/views.py::profile_view` or template | Add "Privacy & data" card with link to dashboard | ~10 |
| `apps/compliance/tests.py` | Add 25-35 tests across the surface (see §6) | ~600 |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | Changelog entry C.4 | +3 |
| `proodos_files/TECH_DEBT_LOG.md` | TD-008 status update; TD-014 selective deletion; TD-015 PDF export; TD-016 7-year cleanup job | +60 |

**Total estimated diff:** ~1500 LOC across 13 files (the test suite dominates).

---

## 5. anonymize_user service signature (skeleton)

```python
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone


@transaction.atomic
def anonymize_user(user: User) -> None:
    """GDPR Art. 17 right-to-erasure implementation.

    Atomic by the decorator. Caller is responsible for the user-facing
    redirect/logout dance — this function only touches the DB.

    Steps (single transaction):
      1. NULL/clear PII on TeacherProfile.
      2. NULL/clear PII on auth_user; mark inactive; unusable password.
      3. Redact remaining IP addresses on ConsentRecord rows.
      4. Set TeacherProfile.research_data_opted_out = True.
      5. Set TeacherProfile.ai_disclosure_acknowledged_at = None.

    Does NOT delete:
      - auth_user (FK target preservation)
      - ConsentRecord rows (7-year retention)
      - AilstResponse rows (research data; filter on opted_out for analytics)
      - UserModuleProgress rows (same)
      - EpilogueCompletion row (same)

    Returns None. Raises Exception on any failure (rolls back the entire
    transaction; caller treats as 500). Idempotent: calling twice on an
    already-anonymized user is a no-op write.
    """
    # 1. TeacherProfile PII clearing
    profile = TeacherProfile.objects.select_for_update().get(user=user)
    _clear_pii_on_profile(profile)
    profile.research_data_opted_out = True
    profile.ai_disclosure_acknowledged_at = None
    profile.profile_completed = False
    profile.research_consent = False
    profile.consent_data_sharing = False
    profile.contact_for_research = False
    profile.save()

    # 2. auth_user PII clearing
    user.username = f'anonymized_{user.id}'
    user.email = ''
    user.first_name = ''
    user.last_name = ''
    user.is_active = False
    user.set_unusable_password()
    user.save()

    # 3. ConsentRecord IP redaction
    ConsentRecord.objects.filter(
        user=user, ip_address__isnull=False,
    ).update(ip_address=None)
    # bulk update OK here — no signal needs to fire, no per-row logic.
```

---

## 6. Test plan — target 30 tests

### `PrivacyDashboardViewTest` (4)
1. GET renders for authenticated user with active consents.
2. GET shows "never granted" state correctly for never-given consent.
3. GET shows "revoked on <date>" for revoked consent.
4. GET requires login (302 to /login/ for anon).

### `RevokeAiDisclosureTest` (5)
5. POST revokes the active ConsentRecord row (`revoked_at` set).
6. POST clears `profile.ai_disclosure_acknowledged_at`.
7. POST logs the user out.
8. After revoke, the next request from the same browser session is intercepted by middleware → 302 to disclosure modal.
9. Atomic failure: simulated DB error during step 2 rolls back step 1 (the consent stays active).

### `RevokeResearchConsentTest` (5)
10. POST revokes the row + sets `research_consent=False` (signal cascade).
11. POST sets `research_data_opted_out=True`.
12. POST does NOT delete existing AilstResponse rows.
13. After revoke, GET on `/ailst/t1/` redirects to `research_consent_required` (gating from C.2.3 still applies).
14. Flash message mentions the separate erasure path.

### `RevokeDataSharingTest` (3)
15. POST revokes the row + sets `consent_data_sharing=False`.
16. Does NOT touch `research_data_opted_out` (that flag tracks the broader research opt-out).
17. Idempotency: second POST is a no-op.

### `DataExportTest` (6)
18. GET returns JSON content-type + Content-Disposition attachment.
19. JSON top-level keys match the spec (export_version, exported_at, user, profile, consents, ailst_responses, module_progress, epilogue_completion, ai_outputs).
20. Verbatim consent_text is included.
21. AI outputs include RTM, DTP, RAG feedback.
22. Export is unaffected by `research_data_opted_out` (Art. 15 is a personal right, not contingent on research participation).
23. Anon user → 302 to login.

### `ErasureConfirmPageTest` (2)
24. GET renders the warning + the Greek confirmation form.
25. Submit without the exact "ΔΙΑΓΡΑΦΗ" string → form re-renders with error, no DB write.

### `ErasureExecuteTest` (5)
26. POST with correct token: PII fields NULL/empty on TeacherProfile + auth_user.
27. POST: `research_data_opted_out` set to True.
28. POST: ConsentRecord rows preserved with `ip_address=None`, all other fields intact.
29. POST: AilstResponse rows preserved unchanged.
30. POST: user is logged out, redirected to landing, flash message present.

### `AtomicityAndEdgeCaseTest` (4)
31. Race: two concurrent revoke POSTs for the same consent — second one is a no-op (M6 supersede + select_for_update on profile).
32. Race: revoke + erasure POST in parallel — erasure wins, consent row is correctly marked revoked AND IP cleared.
33. Post-erasure middleware behaviour: subsequent request to the now-anonymized user is treated as anonymous (since `is_active=False`), redirected to /login/.
34. Idempotency: calling `anonymize_user(already_anonymized_user)` is a no-op write (no exceptions, no state change).

**Total: 34 tests.** Comfortably in the 25-35 target.

---

## 7. Commit organisation — 3 commits

Per John's directive:

**Commit 1: Consent revocation endpoints + TD-008 fix**
- New `apps/compliance/services.py::clear_pii_on_profile` helper (used later in erasure).
- New views: `privacy_dashboard_view`, `revoke_ai_disclosure_view`, `revoke_research_view`, `revoke_data_sharing_view`.
- New URL patterns for those four.
- New migration `users/0010_teacherprofile_research_data_opted_out`.
- Templates: `privacy_dashboard.html` (initial version with consents card only).
- Tests classes 1-3 + 4 (17 tests).
- TD-008 closed in TECH_DEBT_LOG.

**Commit 2: Data export (Art. 15)**
- New `apps/compliance/services.py::gather_user_export(user)`.
- New view `export_data_view`.
- New URL pattern.
- Extension of `privacy_dashboard.html` with the Your-data card + AI-outputs section.
- Tests class 5 (6 tests).

**Commit 3: Account erasure (Art. 17)**
- New `apps/compliance/services.py::anonymize_user(user)`.
- New views `erasure_confirm_view` (GET form) + `erasure_execute_view` (POST execute).
- New URL patterns for both.
- New template `erasure_confirm.html`.
- Extension of `privacy_dashboard.html` with the Delete-account card.
- Tests classes 6-8 (11 tests).
- TD-014, TD-015, TD-016 added to TECH_DEBT_LOG.
- Plan changelog entry C.4.

This split is bisectable: a regression in the erasure flow can be reverted without touching the export or the revocations.

---

## 8. Open questions / 🛑 markers

🛑 **Q1 — Courtesy email after anonymization?** Should we send a one-line notification to the user's email (captured before clearing) saying "Your account has been anonymized on <date>; no further action is required"? Pros: nice UX, fulfils best-practice for irreversible actions. Cons: requires email backend config (currently the project does not seem to send email; would need SMTP setup or console backend in dev). **Default: skip for C.4, add as TD if John wants it.**

🛑 **Q2 — Should the dashboard be reachable for an already-anonymized user?** Edge case: if the anonymization happens but somehow the session was not flushed (browser kept a stale cookie that re-authenticates via remember-me?), the user might land on `/profile/privacy/`. With `is_active=False`, Django's auth middleware rejects them at request time. So this should not be reachable in practice. **Default: no special handling; standard `@login_required` redirects to /login/.**

🛑 **Q3 — `auth_user.email = ''` collision risk?** Multiple anonymized users would all have empty email. Django's `User.email` field is NOT unique by default (no `unique=True` in the auth app), so empty strings should not collide. **Verified: no special handling needed.**

🛑 **Q4 — JSON export when there are NO AILST/module/Epilogue rows yet?** A user who just registered and triggered erasure has empty research data. The shape of the JSON should still include those keys with empty arrays / null values, not omit them. **Default: always include all keys; tests will assert this.**

If none of Q1-Q4 are blockers, the design is ready for implementation.

---

## 9. Effort + timeline

| Subpiece | LOC | Notes |
|---|---|---|
| Migration | 25 | Trivial AddField |
| Services (anonymize, export, helpers) | 240 | The bulk of new logic |
| Views | 250 | 7 views, mostly thin wrappers around services |
| URLs | 20 | Straightforward |
| Templates | 350 | Dashboard + erasure confirm |
| Tests | 600 | 34 tests with setUp |
| Wiring + doc updates | 50 | profile link, plan changelog, TD entries |
| **Total** | **~1500** | |

**Session time estimate:** 4-6 hours of focused implementation, including the 3 commits and the migration apply.

---

*End of C.4 design proposal. Awaiting confirmation of D1-D14 and clarification on 🛑 Q1-Q4 (or default acceptance) before implementation begins.*
