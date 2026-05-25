# Phase H — Closing Flow + Certificate + Dashboard Redesign — Design Proposal v1.1

*Phase H. Drafted 2026-05-25. Supersedes the Phase H block of
`PROODOS_UNIFIED_ROADMAP.md` lines 851–956 (which still carried
pre-G-closure stale text and a delayed-post-test scope that this
proposal rescinds). Builds on the Phase G closure decision
(`PHASE_G_DIALOGUE_DEPRECATION_20260524.md` — the full deactivation
rationale + preserved-infrastructure inventory + lessons-learned
narrative; required reading for any reviewer asking "why did G.6c
go from in-progress to deactivated?") and the deferred TD-021
dashboard-redundancy ticket.*

## Version history

- **v1.1.1 (2026-05-25, second-pass review):** Three follow-up
  refinements from second external review:
  - §7.4 LAD framing rewritten to more accurately render Verbert
    et al. — the paper identifies purposes a *single* LAD may
    serve (often in combination), not categories of distinct LAD
    types. PROODOS distributes those purposes across two surfaces
    as a platform design choice, which the rewrite now owns
    explicitly rather than implying that Verbert legitimises the
    one-purpose-per-surface mapping.
  - §5.5 bilingual certificate effort estimate decoupled into
    engineering cost (0.5 day for parallel-column PDF layout) vs.
    translation QA cost (3-5 days with external dependencies on
    Kokkonis availability + 2-3 pilot teachers cognitive
    interviewing). §1 total effort estimate revised accordingly
    (8-10 → 11-15 days if translation QA runs serially; ~10 days
    if QA runs in parallel with H.6/H.7/H.8 work).
  - §13 References + proposal header confirm
    `PHASE_G_DIALOGUE_DEPRECATION_20260524.md` exists, is mirrored
    to the Desktop dissertation folder, and is the authoritative
    record for "why G.6c was deactivated" questions.
- **v1.1 (2026-05-25, same day):** Incorporated 10 actionable
  comments from external review:
  - **A.1 resolved →** Greek certificate decision finalised as
    **bilingual from v1** (EN front + EL below in same PDF); see
    §5.5. Was open question Q3 in v1.
  - **A.2 →** Explicit verification statement in §6.5 that
    `RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB` contains zero
    references to dialogue / Learning Portrait / Stages 1-3 /
    Aletheia (re-read 2026-05-25 of `apps/compliance/copy.py:79-121`).
    Phase G v2 §B.4 decision to add dialogue-corpus language was
    never implemented before the G closure; byte-identical V2 for
    this constant remains correct.
  - **A.3 →** §7.4 rewritten from "awareness-type vs
    reflection-type LADs" hard typology to "distinct purposes from
    Verbert's awareness / reflection / sense-making set", plus
    addition of Schwendimann et al. (2017) IEEE TLT systematic
    review as broader LAD-taxonomy support. Both citations now
    verified (Verbert at 09:00, Schwendimann at 09:15 via
    WebSearch). Lit-note §19 updated.
  - **B.1 →** `generate_verification_code()` helper with retry
    loop (5 tries, raise on exhaustion) in §5.2.
  - **B.2 →** Certificate "no AI" footer wording expanded in §5.3
    to acknowledge that the *programme* uses AI tools (RTM, DTP,
    RAG) while the *certification* is deterministic — defends
    against the "didn't AI inference happen somewhere upstream?"
    inspector question.
  - **B.3 →** §6.4 adds visual-distinction requirement between
    required (RESEARCH_PARTICIPATION + DATA_SHARING) and
    optional (FOLLOWUP_RECRUITMENT) Step 3 checkboxes.
  - **B.4 →** §7.2 next-action card grows from 3 to 4 states; the
    new state covers "M15 done but Epilogue not yet visited" (the
    M15→Epilogue→T2 gate that v1 implied but did not enumerate).
  - **B.5 →** §5.4 gating logic uses `completed_at__isnull=False`
    not `submitted_at__isnull=False` (corrects v1 field-name
    error). `AilstResponse.completed_at` is set only when all 36
    responses are filled and scores computed (verified in
    `apps/ailst/models.py:172` + docstring at lines 113-115). No
    partial-T2 issuance risk.
  - **Last note →** §1 table now explicitly marks H.4 and H.5 as
    RESCINDED rows so the missing-numbers question never arises.
- **v1 (2026-05-25):** Initial draft.

---

## 1. Summary

Phase H closes the pilot user-journey loop. The teacher finishes M15,
enters the (Stage-0-only) PROODOS Epilogue, takes the final AILST
administration (T2), and lands on a redesigned `/dashboard/` where a
**Certificate of Attendance** PDF download is now enabled. A small
optional consent collected at onboarding Step 3 keeps the door open
for a possible later follow-up study, without committing the
platform to building any follow-up infrastructure now.

Phase H bundles six sub-tracks. The numbering preserves the prior
roadmap §H block (H.1-H.5); H.4 and H.5 are explicitly RESCINDED
so the gap in numbering is not a documentation error.

| # | Sub-track | Effort | Status pre-H |
|---|---|---|---|
| H.1 | Closing flow doc rewrite + roadmap stale-text fix | ~1 day | partial (roadmap text exists but stale) |
| H.2 | Research justification rewrite (Ning-anchored, 3-timepoint design) | bundled with H.1 | pre-G-closure text in roadmap |
| H.3 | Certificate of Attendance (new `apps/certification/`) | 2–3 days | dormant `_generate_portrait_pdf` preserved as seed |
| ~~H.4~~ | ~~Email cron for delayed T2b~~ | — | **RESCINDED** (see §2.2 — delayed post-test moved to Future Work §I.6) |
| ~~H.5~~ | ~~In-platform interview cohort model~~ | — | **RESCINDED** (same as H.4) |
| H.6 | Optional follow-up consent at onboarding Step 3 + consent V2 bump | 1–2 days | not started |
| H.7 | Dashboard redesign (TD-021 resolution, option a + b hybrid) | 3–4 days | open TD ticket |
| H.8 | 7-year ConsentRecord retention command (TD-016) | 0.5 days | open TD ticket |

**Total effort estimate:** ~8–10 engineering days, **+3-5 days
external-dependency translation QA** for the bilingual certificate
text (Greek-side review by Asst. Prof. Kokkonis + 2-3 pilot-teacher
cognitive interviewing — see §5.5 for the decoupled estimate). If
translation QA runs in parallel with H.6/H.7/H.8 engineering work,
end-to-end Phase H wall time stays near ~10 days; if it runs
serially after H.3 engineering, wall time grows to ~13-15 days.
Path-A vs Path-B decision in §5.5 governs.

**Out of scope (explicit rescission from prior roadmap §H):**
delayed post-test (T2b), email cron infrastructure, T2b reminder
windows, interview cohort model, Greek AILST translation. The
delayed-post-test design is moved to Future Work (see §10);
Greek translation is moved to the planned platform-wide
translation pass.

---

## 2. Motivation

### 2.1 Why now

The pilot needs a clean closing surface. With Phase G closure
(2026-05-24) removing the Aletheia dialogue and the Learning Portrait,
the post-M15 flow shrinks to: Epilogue Stage 0 dashboard → AILST T2 →
"now what?". The "now what?" is the gap Phase H fills. Without it,
the teacher reaches T2 submission and lands back on a `/dashboard/`
that simply repeats the Modules menu — a flat anticlimax for a
15-module commitment, and no concrete acknowledgement of programme
completion.

### 2.2 Why three timepoints, not four

The roadmap §H block (drafted before Phase G closure) proposed adding
a delayed post-test (T2b) 4–6 weeks after T2, plus email reminders
and an interview cohort. After review of the bibliographic basis
(`Literature_Review_Synthesis_Note(1).md` §5 and Roles 2 + 5), the
following points argued against this scope:

- **The AILST paper (Ning et al. 2025) is a cross-sectional CFA
  validation study (n=604).** It does not prescribe delayed
  administration; its proposed practical use is "pre/post". The
  current PROODOS use (T0/T1/T2 = three administrations) is already
  more extensive than anything Ning recommends.
- **The Erhardt et al. (2025) "longitudinal evidence gap" — the only
  citation the roadmap §H.2 advanced as justification for T2b — is
  already answered by PROODOS via DTP cross-module tracking (15
  timepoints per teacher).** This mapping is recorded twice in the
  lit-note (lines 238, 278). Re-using Erhardt to motivate T2b would be
  citing the same paper for two different claims, the second of which
  he does not in fact make.
- **The honest bibliography for delayed post-test design** —
  Kirkpatrick (1959/1994) Level 3/4, Guskey (2002) 5-level PD
  evaluation, Joyce & Showers (2002) transfer-of-training — is not
  currently in the lit-note. Adding T2b would require lit-note
  expansion *before* implementation, not after.

Three timepoints stay defensible because they sit *inside* the Ning
validation envelope (pre/post use) and because the longitudinal
question is answered by a different instrument (DTP, 15 timepoints).
A delayed wave remains valuable as future work, but is most
honestly designed as a separate study with its own IRB protocol —
not as an in-platform extension (§10).

### 2.3 Why the dashboard redesign goes here

TD-021 (raised 2026-05-20, logged in `TECH_DEBT_LOG.md:428`) records
that `/dashboard/` (`templates/home.html`) duplicates the Modules
menu: it builds `modules_with_progress` as a flat list and shows
exactly what the Modules menu already shows. The TD entry names
Phase H as one of the legitimate slots for the resolution.

Phase H also needs a landing point for the Certificate of Attendance
button. Putting the certificate in the Stage-0 Epilogue would
collapse two distinct surfaces (synthesis vs. credential) and is
methodologically wrong. Putting it on the AILST T2 completion screen
is a transient surface the teacher will not revisit. The dashboard
is the natural permanent home — but only if the dashboard itself
stops duplicating the Modules menu and becomes a distinct surface
worth landing on.

This is why H.7 (dashboard redesign) and H.3 (certificate panel) are
bundled rather than sequenced. They are one design problem with two
heads, and one design pass solves both.

---

## 3. The closing flow (H.1)

### 3.1 End-to-end sequence

```
M15 complete
   │
   ▼
/epilogue/                  (Stage 0 Personal Evolution Dashboard, magazine
   │                         register; first-entry freezes snapshot)
   │  user clicks "Continue"
   ▼
POST /epilogue/complete/    (flips completed_at; _post_epilogue_destination
   │                         routes to T2)
   ▼
/ailst/t2/                  (AILST 36 items across 4 pages, Likert)
   │
   │  final page POST
   ▼
ailst_complete_view         (acknowledgement + a single "Go to dashboard"
   │                         button — no scores shown, per C.2.3 D4)
   │
   ▼
/dashboard/                 (redesigned: UNESCO 5×3 progress matrix +
                             certificate panel now ENABLED with
                             "Download Certificate of Attendance" button +
                             next-action card)
```

### 3.2 Roadmap stale-text fixes

`PROODOS_UNIFIED_ROADMAP.md:862` currently reads:

> `PROODOS Epilogue (Stage 0–3 + Learning Portrait PDF)`

Replace with:

> `PROODOS Epilogue (Stage 0 Personal Evolution Dashboard)`

The entire roadmap §H.1 ASCII diagram (lines 859–875) is rewritten
to match §3.1 above. The §H.4 ("Σχεδιασμός delayed follow-up") and
§H.5.cohort-interview blocks are moved to a new "Future Work" section
in the roadmap (§I.6 or §J extension) with a one-line pointer back
to this proposal for rationale.

---

## 4. Research justification rewrite (H.2)

### 4.1 What the rewritten §H.2 will say

The new §H.2 anchors the three-timepoint design on Ning et al.
(2025) directly:

- T0 (post-onboarding): baseline AILST score on the validated
  4-factor structure (Perception, Knowledge & Skills, Applications &
  Innovation, Ethics).
- T1 (post-M5): mid-programme score after the Acquire level.
- T2 (post-M15): end-of-programme score after the full Create level.

Analytical use: paired comparisons T0→T1, T1→T2, T0→T2 per factor,
plus an overall change score. Effect-size reporting (Cohen's d for
paired samples) per Ning's own analytical convention. DTP composite
trajectories provide a within-pilot longitudinal complement to the
three discrete AILST waves.

### 4.2 The three acknowledged limitations

These will be written into the dissertation methods chapter as
*acknowledged limitations*, not as hidden weaknesses:

**L1 — AILST is validated cross-sectionally, not as a
change-sensitive instrument.** Ning et al. (2025) report internal
consistency and factor-structure validity from a single-timepoint
CFA (n=604). Test-retest reliability, sensitivity-to-change, and
practice effects in repeated administration have not been
independently established. The present study administers the scale
at three timepoints in line with the paper's recommended pre/post
practical use, but the inference that observed changes reflect true
construct change (rather than measurement-instrument artefacts)
rests on the validation envelope of the original paper.

**L2 — Greek translation.** The Greek-language version of the
instrument (`ning_2025_v1_el`) will be produced as part of the
forthcoming platform-wide translation pass (separate work-stream).
The pilot administration in Greek therefore depends on translation
quality assurance from that pass. The methodology chapter will
disclose the translation provenance (translator, review process,
any cognitive-interview validation) at the time the translation
ships.

**L3 — Single-site, single-cohort, single-PI pilot (n≈110).**
Generalisation beyond Greek K-12 educators in the IHU-affiliated
network is not warranted from this design. Multi-site replication
is named as future work.

### 4.3 Why the longitudinal question is answered, just not by AILST

DTP cross-module tracking gives 15 timepoints per teacher within the
pilot. This is the longitudinal arc; it is qualitatively richer
than a delayed AILST wave would be, because it tracks development
*through* the programme rather than measuring decay *after* it. The
"delayed post-test" framing the prior roadmap §H carried was a
displacement of that question onto the wrong instrument. The new
§H.2 makes this explicit.

---

## 5. Certificate of Attendance (H.3)

### 5.1 New app: `apps/certification/`

Reasons for a separate app rather than placing the certificate code
inside `apps/epilogue/` or `apps/ailst/`:

- The trigger for certificate eligibility is **T2 submission**, not
  Epilogue completion. The certificate is conceptually decoupled
  from synthesis.
- Future credential changes (e.g., a digital-badge variant, an
  Europass-compatible export) belong in the same app rather than
  accreting onto `apps/ailst/`.
- A separate app keeps the PDF-generation Article 50(2) machinery
  scoped to one clear owner.

### 5.2 Schema

One model:

```python
class CertificateOfAttendance(models.Model):
    user             = models.OneToOneField(User, on_delete=PROTECT)
    issued_at        = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=16, unique=True)
    teacher_display  = models.CharField(max_length=255)  # frozen at issue
    modules_summary  = models.JSONField()                # frozen list of 15
    instrument_version_t2 = models.CharField(max_length=20)
    pdf_metadata_version  = models.CharField(max_length=20, default='v1')
```

- `OneToOneField` enforces one-certificate-per-teacher at the DB
  level (matches `EpilogueCompletion`'s pattern; revisions handled
  by issuing a new `pdf_metadata_version` on re-render rather than a
  new row).
- `verification_code` is a 16-char URL-safe random string, generated
  through a retry helper that survives the (vanishingly unlikely)
  collision on the `unique=True` index:

  ```python
  # apps/certification/models.py
  import secrets

  def generate_verification_code():
      for _ in range(5):
          code = secrets.token_urlsafe(12)[:16]
          if not CertificateOfAttendance.objects.filter(
              verification_code=code
          ).exists():
              return code
      raise RuntimeError(
          "Could not generate unique verification code after 5 attempts; "
          "investigate code-space exhaustion."
      )
  ```

  Mathematical collision probability at n=110 issued certs over a
  96-bit code space is ~6e-26; the retry guards against the
  theoretical IntegrityError without adding meaningful runtime cost
  (each `.exists()` is an indexed-key lookup).

- A small public endpoint `/certification/verify/<code>/` returns the
  teacher name + issue date + module list (no scores, no AILST
  factor breakdown, no PII beyond what is already on the PDF) — see
  §5.6 for the rationale of public name disclosure.
- `teacher_display` and `modules_summary` are **frozen at issue
  time** — if the teacher later updates their profile or M15 is
  edited post-pilot, the certificate keeps its issued-state. This
  matches the same frozen-state pattern that the Epilogue
  `stage0_snapshot` uses (PROODOS Epilogue v2 §5.4).

### 5.3 PDF template and the Article 50(2) machinery

The dormant `_generate_portrait_pdf` helper (`apps/epilogue/views.py:193`)
is moved verbatim to `apps/certification/services.py` as
`_render_certificate_pdf`. Two things change:

1. **New template:** `templates/pdf/certificate_of_attendance.html`
   replaces the removed `templates/pdf/learning_portrait.html`. The
   visual register inherits the Phase G magazine pattern (eyebrow +
   serif numeral + standfirst + body + ornament) but the payload
   shifts to: teacher name, issue date, 15-module list with UNESCO
   aspect/level tags, an ICT-CFT alignment statement, and a
   verification-code footer.
2. **AI-provenance footer becomes a no-AI provenance footer, with
   explicit scope.** The certificate is *not* an AI artefact (no
   LLM call generates any part of it). But a careful inspector will
   ask: didn't AI inference happen *somewhere* upstream in the
   participation that produced this certificate? Yes — the
   programme uses AI tools (RTM, DTP, RAG mentor) during the 15
   modules. The footer makes the scope of "no AI" precise:

   > This certificate is issued deterministically based on
   > completion of the AILST T2 self-assessment instrument. No AI
   > inference is involved in eligibility determination, score
   > calculation, or certificate generation. The platform's
   > pedagogical features include AI tools (described in the AI
   > Impact Assessment available at /compliance/ai-impact/); their
   > use during the programme does not affect certification.

   This wording (a) defends the certification claim, (b) does not
   pretend the programme avoids AI, (c) directs the inspector to
   the AI Impact Assessment for the upstream picture. The
   Article 50(2) PDF metadata block (Title / Author / Subject /
   Creator via `<meta>` tags + the JSON-LD body block) is preserved
   verbatim, since the pattern itself is the reusable contribution
   — the JSON-LD body asserts `aiInvolved: false` for this artefact
   kind with a `programmeUsesAI: true` companion key pointing to the
   `/compliance/ai-impact/` URL.

### 5.4 Gating logic — completeness, not just timestamp

```python
# apps/certification/services.py
def teacher_is_eligible(user) -> bool:
    return AilstResponse.objects.filter(
        user=user,
        timepoint='T2',
        completed_at__isnull=False,
    ).exists()
```

The gate uses `completed_at__isnull=False`, not a generic submission
timestamp. Per the `AilstResponse` model docstring
([apps/ailst/models.py:113-115](apps/ailst/models.py:113)):

- *just-started:* `started_at=NOW, completed_at=NULL, responses={}`
- *in-progress:* `responses` has 1-35 paper_code keys,
  `completed_at=NULL`
- *completed:* `responses` has **all 36 keys**, scores filled,
  `completed_at=NOW`

So `completed_at__isnull=False` already implies (a) all 36 responses
present, (b) derived scores computed. **No partial-T2 issuance
risk** — a teacher who submitted 12/36 items before timeout has
`completed_at=NULL` and is correctly not eligible. No additional
`is_complete` field needed.

Gate is *eligibility*, not *issued state*. First call to the download
view creates the `CertificateOfAttendance` row (idempotent via
`get_or_create`) and renders the PDF; subsequent calls re-render
from the frozen row.

### 5.5 Certificate language — bilingual from v1

The certificate PDF is **bilingual from version 1**: English on the
front face, Greek translation in a parallel block below. Both
languages render in the same PDF, so the teacher carries a single
file usable in both Greek (local educational context, ΕΗΔΕ
ΔΙ.ΠΑ.Ε. inspection) and English (international portfolios, EU
mobility, publication) settings.

**Why bilingual from v1, not English-only-then-Greek-later:**
the pilot is ~110 Greek K-12 educators. The ΕΗΔΕ ΔΙ.ΠΑ.Ε. (Greek
IRB at IHU) will require Greek-language documentation; an
English-only certificate creates an IRB-compliance gap. The
bilingual layout decouples the certificate template from the
forthcoming platform-wide Greek translation pass — even if that
pass slips, the certificate ships unaffected.

**Effort cost — decoupled.** The bilingual decision adds two
distinct costs that the v1 estimate conflated:

| Component | Effort | Dependencies |
|---|---|---|
| **Engineering** — parallel-column PDF layout, xhtml2pdf CSS, font subset for Greek glyphs, test that both blocks render | ~0.5 day | self-contained |
| **Translation QA** — Greek text drafting (PI), expert review by Asst. Prof. Kokkonis, 2-3 pilot-teacher cognitive interviewing, revision pass | ~3-5 days | **external availability** (Kokkonis schedule + pilot-teacher response time) |

These two costs are **separable in time**: the engineering can
ship with placeholder Greek text marked `DRAFT — pending IRB
review`, and the final translation lands in a follow-up commit
once QA completes. This pattern matches the standard pre-IRB
workflow already used for the `_V1_PRE_IRB` consent constants
([copy.py:11-18](apps/compliance/copy.py:11)) — ship the
infrastructure with versioned placeholder content; bump versions
when IRB-revised content lands.

**Decided implementation order for H.3 (PI decision, 2026-05-25):
Path A (ship-then-translate).** H.3 lands with engineering complete
+ DRAFT Greek placeholder; pilot does not launch until the
translated text is reviewed and committed (separate small follow-up
PR). Allows H.3 to clear the technical critical path early.
Matches the standard `_V1_PRE_IRB` consent-versioning workflow
already used elsewhere on the platform. The DRAFT marker is visible
in both the rendered PDF (a `DRAFT — pending IRB review` watermark
band beneath the Greek block) and in the PDF metadata layer
(`certificate_translation_status: draft_pending_review` in the
JSON-LD body), so any inspector reading the artefact during the
review window knows the Greek text is not yet final.

The Greek-side follow-up commit replaces the placeholder text and
flips the metadata to `certificate_translation_status: irb_reviewed`
once Asst. Prof. Kokkonis review + at least one pilot-teacher
cognitive interview have completed.

The Greek translation provenance follows the same pattern named
for the future `ning_2025_v1_el` AILST seed (see lit-note §5 L2
limitation): translator identity, review process, cognitive-
interview outcomes recorded in the methodology chapter at the
time the translation lands.

### 5.6 Public verification view — name disclosure decision

The `/certification/verify/<code>/` endpoint returns the teacher's
name + issue date + 15-module summary on a public surface. Rationale
(against the alternative of disclosing only "code valid + date"):

- Standard academic-credential pattern (Coursera, edX, university
  verification portals all disclose holder name).
- The 16-char verification code is high-entropy (~96 bits) — only
  someone holding the certificate PDF, or the holder themselves, can
  reach the verification URL. The code is not enumerable.
- A "code valid + date" minimal disclosure requires the verifier to
  also possess the certificate PDF to compare names, which defeats
  the verification surface's purpose for third parties (a future
  employer, a postgraduate admissions panel).
- The teacher's name on a completion certificate is not sensitive
  PII in the same sense as a medical record or a salary; it is the
  point of a certificate.

A `verified` template asserts the disclosure scope clearly:
"This certificate of attendance, identified by code XXXX, was
issued to [name] on [date] for completion of the PROODOS
professional-development programme; 15 modules listed below. No
AILST scores, no factor breakdown."

### 5.7 No retroactive issuance

Existing pre-Phase-H test users who already have `completed_at` on
their T2 row become eligible immediately at H.3 deploy. The
certificate is issued lazily on first download request — no batch
backfill.

---

## 6. Optional follow-up consent at onboarding Step 3 (H.6)

### 6.1 Why onboarding, not T2 completion

Earlier drafts of this proposal placed the optional follow-up consent
checkbox at the T2 completion screen. After review, onboarding Step 3
is the better placement because:

- **Step 3 already hosts two parallel optional/required consents**
  (RESEARCH_PARTICIPATION + DATA_SHARING). The component, the
  versioning workflow, and the `ConsentRecord` storage pattern are
  reusable verbatim.
- **One consent ceremony, one audit point.** All consents collected
  at one timestamp + one IP + one set of consent_text versions.
  IRB-clean.
- **Most informed consent.** The teacher sees the full landscape of
  possible research uses *before* investing 15 modules + 3 AILST
  administrations.
- **The T2 completion screen stays ceremonial.** No legal-copy
  interruption between submitting the final scale and reaching the
  dashboard with the certificate.

### 6.2 The new consent text constant

A third constant joins the existing two in `apps/compliance/copy.py`:

```python
FOLLOWUP_RECRUITMENT_TEXT_V1_PRE_IRB = """\
Optional — Future Research Contact

While completing the PROODOS pilot, you may opt in to allow the
research team to contact you at a later date about a possible
follow-up study. Such a study has not been designed at the time you
grant this consent; if it goes ahead it will typically involve a
short questionnaire and/or an interview, conducted approximately
4-6 weeks after you complete the programme.

What this consent does:
  - Allows the research team to retain your contact email address
    for the sole purpose of inviting you to a possible future
    follow-up.

What this consent does NOT do:
  - Does not automatically enrol you in any future study.
  - Does not alter your primary participation in the PROODOS pilot.
  - Does not affect your access to the programme certificate of
    attendance.

If a follow-up study is launched, you will receive a separate
study-specific information sheet and a separate consent form at the
time of invitation. You will remain free to decline.

Your right to withdraw:
  You may revoke this consent at any time via the Privacy dashboard,
  independently of all other consents. Revocation removes your
  email from the follow-up invitation pool.

Optional consent:
  This consent is OPTIONAL. Declining it does NOT affect your
  participation in the research, your access to the platform, or
  your programme certificate.

Your acknowledgment:
  By checking "I consent to be contacted about possible future
  follow-up research" you confirm that you have read and understood
  the above.
"""
```

A matching `FOLLOWUP_RECRUITMENT_VERSION = 'v1_pre_irb'` constant is
added. The version-pinned regression test
(`test_stored_consent_text_matches_copy_module_exactly`) extends to
the new constant.

### 6.3 Schema additions

The `ConsentRecord` model in `apps/compliance/models.py` already
supports arbitrary `consent_type` values (the existing
`research_participation` and `data_sharing` types are not enum-bound).
A new logical type `followup_recruitment` is added by:

1. Documenting the type in the model docstring and the
   `compliance/services.py::record_consent` helper.
2. Adding a corresponding revoke endpoint in
   `apps/compliance/urls.py` matching the existing pattern (one revoke
   URL per consent type, per IRB Article 7(3) requirement).
3. Adding a `consent_followup_recruitment` accessor on
   `TeacherProfile` parallel to the existing `consent_data_sharing`
   accessor.

No DB schema migration required — the consent record table already
holds arbitrary types.

### 6.4 Step 3 template changes — with visual distinction

`templates/onboarding/step3.html` adds a third checkbox block below
the existing two. **Required and optional consents must be visually
distinct**, not just textually tagged:

- **Required block** (RESEARCH_PARTICIPATION + DATA_SHARING):
  retained as the top group, primary visual weight (existing
  styling).
- **Optional block** (FOLLOWUP_RECRUITMENT): rendered **below** the
  required block, separated by a horizontal rule and a heading
  ("Optional — for future consideration"); rendered in muted
  typography (e.g., `text-base-content/70` rather than full
  contrast), default unchecked, with the "Optional" tag prominent
  in the heading rather than buried in body text.

This addresses two consent-fatigue failure modes:

1. **The teacher checks the optional box thinking it is required**
   → IRB issue (consent not freely given). The visual demotion +
   prominent "Optional" heading makes this less likely.
2. **The teacher does not read the optional block and leaves it
   unchecked** → smaller follow-up pool. The separated layout makes
   the optional block more, not less, salient — readable as a
   distinct item rather than a third paragraph in a wall of legal
   text.

The Step 3 form (`apps/users/forms.py::Step3Form`) gains one boolean
field `consent_followup_recruitment` (default False). Test:
`Step3FormRendersOptionalDistinctlyTest` asserts the optional
block's parent container carries the `optional-consent` CSS class
and is positioned after the required-block container in DOM order.

### 6.5 Consent V2 bump

Phase H is also the right moment for a long-overdue V2 bump of the
existing consent texts, primarily to clean up stale references.

**Verification statement (2026-05-25 re-read of
`apps/compliance/copy.py:79-121`):** `RESEARCH_PARTICIPATION_TEXT_
V1_PRE_IRB` contains **zero references** to "dialogue", "Learning
Portrait", "Stages 1-3", "Aletheia", or "Gemini dialogue". The text
describes platform interactions as: (a) module activities and
reflection prompts, (b) AILST 3 administrations, (c) AI dispute
submissions, (d) module progress and completion data, (e)
personalization fields. None of these references touch the
deactivated G surfaces. The Phase G v2 §B.4 decision (2026-05) to
add explicit dialogue-corpus language to this constant **was never
implemented before the Phase G closure (2026-05-24) deactivated the
underlying surfaces**, so the V1 text is by accident-of-timing
already consistent with the post-closure platform. V2 keeps
`RESEARCH_PARTICIPATION_TEXT` byte-identical.

The constants that **do** need V2 cleanup:

- `AI_IMPACT_ASSESSMENT_V1_PRE_IRB` section §2
  (`apps/compliance/copy.py:184-187`) currently reads:
  > "After the pilot, the PROODOS Epilogue will add a Personal
  > Evolution Dashboard, a three-stage Gemini dialogue, and a
  > Learning Portrait PDF. These are currently scaffolded but not
  > yet implemented for participants."
  Phase G closure (2026-05-24) deactivated the dialogue and the
  Learning Portrait. The V2 text reads: "After the pilot, the
  PROODOS Epilogue presents a Personal Evolution Dashboard
  synthesising the teacher's developmental trajectory across the 15
  modules."

Per the versioning workflow documented at
`apps/compliance/copy.py:11-18`, the V1 constants are kept
verbatim; new `_V2_<TAG>` constants are added below them; the
`settings.AI_DISCLOSURE_CURRENT_VERSION` and
`settings.AI_IMPACT_ASSESSMENT_CURRENT_VERSION` pointers flip to V2.
Existing `ConsentRecord` rows continue to reference the V1 text
they were granted against (regression-tested by the existing
`test_stored_consent_text_matches_copy_module_exactly`).

---

## 7. Dashboard redesign (H.7, resolves TD-021)

### 7.1 Option chosen

**Option (a) of TD-021 with a slim option-(b) supplement: per-teacher
UNESCO 5×3 progress matrix + a small next-action card + the
certificate panel.** Option (c) (remove the dashboard entirely) is
rejected because the certificate needs a permanent landing point and
the dashboard is the right place; option (b) alone (slim landing only,
no matrix) wastes the existing D.4 visual component and gives the
dashboard nothing to *show*.

### 7.2 New `/dashboard/` layout

```
┌────────────────────────────────────────────────────────────────┐
│  Welcome, <teacher name>                                       │
│                                                                │
│  [ Profile completion summary — unchanged, kept slim ]         │
├────────────────────────────────────────────────────────────────┤
│  Your progress through the UNESCO competency framework         │
│                                                                │
│  [ 5×3 grid — rows: 5 aspects, cols: 3 levels, cells:          │
│    locked / in-progress / complete — colour-coded ]            │
│                                                                │
│  Reads as: where you are in the framework, at a glance.        │
├────────────────────────────────────────────────────────────────┤
│  Next                                                          │
│                                                                │
│  [ One contextual card, four states:                           │
│    - "Continue to M<n>" while modules remain                   │
│    - "Visit the Personal Evolution dashboard" after M15        │
│      before /epilogue/complete/ POST (Epilogue gate)           │
│    - "Complete the closing AILST" after Epilogue, before T2    │
│    - "Programme complete — download your certificate" after T2 │
│  ]                                                             │
├────────────────────────────────────────────────────────────────┤
│  Certificate of Attendance                                     │
│                                                                │
│  Pre-T2:  [ Locked card with "Available after the closing      │
│             AILST measurement" text ]                          │
│                                                                │
│  Post-T2: [ "Download Certificate" button + issue date +       │
│             verification code summary ]                        │
└────────────────────────────────────────────────────────────────┘
```

### 7.3 Reuse of the D.4 5×3 component

D.4 (`apps/analytics/services.py` + template partial) built a 5×3
matrix at cohort grain — completion rate per cell across all
consenting teachers. The H.7 dashboard needs the same grid at
individual grain — locked / in-progress / complete state for the
viewing teacher.

The refactor:
- Lift the rendering partial (`templates/analytics/_unesco_matrix.html`
  or equivalent) into a shared `templates/partials/_unesco_matrix.html`
  that takes a `cells` context variable of shape
  `[{aspect, level, state, label, url}, ...]`.
- `apps/analytics/services.py` keeps its cohort builder; a new
  `apps/users/services.py::build_personal_unesco_matrix(user)` builds
  the per-teacher version.
- The home template renders the shared partial with the personal
  data; the analytics dashboard continues to render it with cohort
  data. One visual component, two callers — the standard "design
  system asset" pattern.

### 7.4 The pedagogical-evolution boundary, preserved

Per TD-021's hard constraint (line 435), the dashboard remains
**completion-structure**, not **developmental-evolution**. No DTP
curves, no RTM trajectories, no factor scores. The matrix shows
*where the teacher is in the framework* (a static state); the
Epilogue Stage 0 owns *how the teacher developed through the
framework* (the longitudinal arc). Two surfaces, two distinct
questions, no duplication.

This boundary is also defensible against the learning-analytics-
dashboard (LAD) literature, with one important caveat about how
Verbert et al. is rendered.

Verbert et al. (2014, *Personal and Ubiquitous Computing*,
18(6):1499–1514, DOI 10.1007/s00779-013-0751-2) identify
**awareness, reflection, and sense-making** as three distinct
purposes that LADs may serve, *often in combination within a
single dashboard*. The paper does not partition LADs into
"awareness LADs" vs "reflection LADs" categories — it presents
the three as purposes any LAD may carry, with many real LADs
serving two or all three at once.

The PROODOS platform implements these purposes **across two
distinct surfaces**: the redesigned `/dashboard/` emphasises the
awareness purpose (where am I in the framework, right now), while
the Epilogue Stage 0 emphasises the reflection purpose (what does
my developmental trajectory mean). This distribution across
surfaces is a **PROODOS platform design choice**, not a Verbert
typology — but each surface remains within the purpose set Verbert
legitimises, and the choice is defensible because it serves the
TD-021 hard constraint that the dashboard must not duplicate the
Epilogue's evolution view.

Schwendimann et al. (2017, *IEEE Transactions on Learning
Technologies*, 10(1):30–41,
[ERIC EJ1141028](https://eric.ed.gov/?id=EJ1141028)) extend this
picture with a systematic review of 55 LAD studies, mapping the
field across multiple dimensions (context × user × indicator ×
representation); their broader landscape supports the general
claim that multiple purpose-bearing surfaces can coexist as
distinct dashboards within one platform without functional
overlap. They do not, however, themselves prescribe the specific
distribution PROODOS adopts.

Both citations were verified via WebSearch on 2026-05-25. The
Verbert paper introduces the awareness / reflection / sense-making
purposes; the cleaner "awareness-type LAD vs reflection-type LAD"
typology that some literature uses comes from later sources (e.g.,
Bodily & Verbert 2017) that are not yet in the lit-note. This
proposal sticks to the Verbert wording — "distinct purposes" — to
stay within the verified bibliographic envelope. Architecture
chapter §6 will follow the same framing.

### 7.5 Stale `home.html` cleanup

The current `templates/home.html` (lines 51–85) builds a `for item in
modules_with_progress` flat-list grid with per-module cards. This
block is removed in its entirety and replaced by the matrix +
next-action + certificate panel. The `dashboard` view
(`apps/users/views.py`) drops `modules_with_progress` from its
context dict and gains the three new context entries. The Modules
menu in the navbar remains the canonical entry point for module
navigation.

Inline emojis in `home.html` (lines 18, 28, 53, `🚀 📊 📚 ✓`) are
removed per the workflow no-emojis-in-code rule.

---

## 8. Housekeeping: 7-year retention command (H.8, resolves TD-016)

A small management command:
`apps/compliance/management/commands/prune_old_consent_records.py`.

- Default behaviour: list (dry-run) all `ConsentRecord` rows where
  `granted_at < NOW() - INTERVAL '7 years'` AND the owning user has
  been anonymised. Report counts per `consent_type`.
- `--apply` flag deletes the listed rows.
- A regression test seeds rows at 7y - 1 day and 7y + 1 day, asserts
  the older one is selected and the newer one is not.
- The command is intended to be run by an external scheduler (cron,
  Windows Task Scheduler, or similar) annually. The platform itself
  does not schedule it; the management-command form keeps it
  composable.

This closes a TD that has been open since C.4. It is bundled into
Phase H because all the other compliance-app work (consent V2 bump,
new `followup_recruitment` consent type, revoke endpoint) is also
happening in this phase — one compliance-app touch, several wins.

---

## 9. Implementation order and dependencies

```
H.1 (doc + roadmap text) ──┐
H.2 (justification text)  ─┤  [no code; safe to land first]
H.8 (retention command)   ─┤  [self-contained]
                           │
H.6 (consent V2 + onboarding wiring) ──┐  [no DB migration; new copy + form field]
                                       │
H.3 (certification app + PDF) ─────────┤  [new app + migration]
                                       │
H.7 (dashboard redesign) ──────────────┘  [depends on H.3 for cert panel context;
                                            depends on D.4 visual component lift]
```

Suggested commit sequence (one commit per row; pg_dump backup
before each migration apply per the workflow rule):

1. H.1 + H.2 documentation edits (roadmap rewrite + lit-note §5
   update). No code.
2. H.8 retention command + tests. No migration.
3. H.6 consent V2 constants + new `followup_recruitment` consent
   type wiring + Step 3 form + revoke endpoint + Privacy-dashboard
   surface. No DB migration (consent records table already accepts
   arbitrary types).
4. H.3 new `apps/certification/` app skeleton + `CertificateOfAttendance`
   model + migration 0001 + admin registration. **pg_dump backup +
   sqlmigrate dry-run before apply.**
5. H.3 PDF service + template + Article 50(2) machinery + download
   view + verification view + tests.
6. H.7 D.4 partial lift to shared template + per-teacher matrix
   service.
7. H.7 dashboard template rewrite + view context update + remove
   `modules_with_progress` + tests.

Each step independently revertable; tests added with the step they
exercise.

---

## 10. Open questions and pending decisions — all RESOLVED in v1.1

**Q1 — Verbert et al. (2014) LAD citation.** **RESOLVED 2026-05-25.**
Verified via WebSearch: Verbert, K., Govaerts, S., Duval, E.,
Santos, J. L., Van Assche, F., Parra, G., & Klerkx, J. (2014).
Learning dashboards: an overview and future research opportunities.
*Personal and Ubiquitous Computing*, 18(6), 1499–1514. DOI
10.1007/s00779-013-0751-2. The abstract verbatim identifies
"awareness, reflection, and sense-making" as the three purposes
LADs promote — exactly the distinction §7.4 invokes. Lit-note §19
added; §7.4 rewritten to "distinct purposes" framing to stay within
the verified envelope (the hard "awareness-type vs reflection-type
LADs" typology comes from later sources). Schwendimann et al. (2017)
IEEE TLT 10(1):30–41 added as systematic-review companion source.

**Q2 — Verification view scope.** **RESOLVED 2026-05-25.** Decision:
**name + issue date + modules** (standard academic-credential
pattern; Coursera/edX/university portals all disclose holder name).
Rationale recorded in §5.6: the 16-char verification code is
high-entropy and not enumerable, so the verification URL is only
reachable by someone holding the certificate PDF or the holder
themselves; minimal "code valid + date" disclosure would defeat the
verification purpose for third parties (employers, postgraduate
admissions).

**Q3 — Greek certificate.** **RESOLVED 2026-05-25.** Decision:
**bilingual from v1** (EN front + EL below in the same PDF).
Rationale recorded in §5.5: pilot is ~110 Greek K-12 educators;
ΕΗΔΕ ΔΙ.ΠΑ.Ε. (Greek IRB at IHU) will require Greek documentation;
an English-only certificate creates an IRB-compliance gap. The
bilingual layout decouples the certificate from the broader Greek
translation pass — even if that pass slips, the certificate ships
unaffected. Effort cost: +0.5 day for parallel-column PDF layout.

**Q4 — Future delayed post-test.** **RESOLVED 2026-05-25.**
Decision: new §I.6 entry in the roadmap. Conditions for activation
named (DTP pilot analysis surfaces a question only a delayed AILST
wave can answer); commitment to design as a **separate study with
its own IRB protocol**, not as in-platform extension; pool of opted-
in participants reserved through Phase H.6 followup_recruitment
consent. Lit-note §5 future-work block points back to §I.6.

---

## 11. Test coverage plan

| Sub-track | Test additions |
|---|---|
| H.3 | (a) eligibility gate respects T2-only completion; (b) idempotent issuance; (c) verification code uniqueness + format; (d) PDF renders without pisa errors; (e) frozen `teacher_display` survives a profile rename post-issue; (f) Article 50(2) PDF metadata round-trip; (g) "no AI involved" JSON-LD body presence. |
| H.6 | (a) Step 3 form accepts the new field; (b) `ConsentRecord` row created with correct `consent_type`; (c) revoke endpoint flips the consent state; (d) `test_stored_consent_text_matches_copy_module_exactly` extends to the new constant. |
| H.7 | (a) personal matrix correctly classifies locked / in-progress / complete per cell; (b) D.4 cohort matrix continues to render (shared partial regression); (c) `modules_with_progress` removed from dashboard context (no template `for` loop left behind); (d) next-action card returns the correct contextual message in each of the three states. |
| H.8 | (a) dry-run lists only rows older than the threshold; (b) `--apply` deletes only the listed set; (c) non-anonymised users are skipped. |

Existing 449-test platform baseline (post-G-closure) extends by
~25–30 tests. No existing test class needs to be skipped or modified
beyond the consent regression-test extension and the dashboard
context assertion.

---

## 12. Dissertation mirror obligations

Per the workflow rule on dissertation documentation mirroring, the
following files are also copied to John's Desktop folder
`Documantation Novel features\` upon landing:

- This proposal: `PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md`
- Updated `PROODOS_UNIFIED_ROADMAP.md` (after §H rewrite)
- Updated `Literature_Review_Synthesis_Note(1).md` (after the §5
  rewrite to reflect Ning-anchored three-timepoint design + the
  Verbert et al. addition once verified)
- Updated `TECH_DEBT_LOG.md` (after TD-016 and TD-021 are marked
  resolved)
- Updated `PROODOS_Architecture_Chapter_DRAFT_v1.md` (new §5.8 or
  §6 entry: certification app, closing flow, dashboard redesign,
  follow-up consent)

---

## 13. References

Cited in this proposal; verified status noted explicitly per the
no-hallucinated-citations rule.

- **Ning, Y., et al. (2025).** Development and validation of the
  Artificial Intelligence Literacy Scale for Teachers (AILST).
  *Education and Information Technologies, 30*. — Already in
  `Literature_Review_Synthesis_Note(1).md` §1 Role 5. **Verified.**
- **Erhardt, N., Richter, E., Huang, Y., Scheiter, K., & Richter, D.
  (2025).** *Artificial intelligence in teacher professional
  development: A systematic review* [Preprint]. University of
  Potsdam. — Already in lit-note §1 Role 2 + §8 References.
  **Verified.**
- **Verbert, K., Govaerts, S., Duval, E., Santos, J. L., Van Assche,
  F., Parra, G., & Klerkx, J. (2014).** Learning dashboards: an
  overview and future research opportunities. *Personal and
  Ubiquitous Computing*, 18(6), 1499–1514. DOI
  10.1007/s00779-013-0751-2. **Verified 2026-05-25 via WebSearch.**
  Now in lit-note §19 with honest caveat on "purposes" vs
  "typology" framing.
- **Schwendimann, B. A., Rodríguez-Triana, M. J., Vozniuk, A.,
  Prieto, L. P., Boroujeni, M. S., Holzer, A., Gillet, D., &
  Dillenbourg, P. (2017).** Perceiving Learning at a Glance: A
  Systematic Literature Review of Learning Dashboard Research.
  *IEEE Transactions on Learning Technologies*, 10(1), 30–41.
  [ERIC EJ1141028](https://eric.ed.gov/?id=EJ1141028). **Verified
  2026-05-25 via WebSearch.** Used in §7.4 as systematic-review
  companion to Verbert.

---

*End of Phase H Closing Flow + Certificate + Dashboard Redesign
Design Proposal v1.*
