# Reactive Moderation Policy

**PROODOS EduAI — Phase A Tier 3, May 2026**
**Scope:** `apps.peer_blog` (Practice Workshop) — `BlogPost` and `BlogComment` records.
**Out of scope:** Forum (`apps.community`) follows its own approval-by-default conventions; this policy applies only to artefact-anchored Workshop posts and their comments.

---

## Philosophy

PROODOS adopts **reactive moderation** for community-shared content (workflows from M13, lesson designs from M9, gamified units from M14, and the comments/thumbs-up that orbit each post). This is a deliberate philosophical choice that contrasts with **proactive curation**.

### Reactive moderation

- Content is **visible immediately** when shared.
- Researcher (or trusted moderators) can **hide** problematic content after the fact.
- The community sees content, dialogues, and self-coordinates.
- Hide actions are documented (`hidden_reason` field on `BlogPost` and `BlogComment`) and **reversible** (`unhide_selected` admin action; the underlying record is preserved for research integrity).

### Why not proactive curation?

- **Proactive curation creates aspirational/reality mismatch.** Repository documentation that promises "master teacher review" sets expectations that approval gates fail to meet at scale.
- **Proactive curation introduces researcher bias into pilot study data.** Whatever passes a researcher's filter is no longer a record of community dynamics — it's a record of researcher preference.
- **Proactive curation contradicts the Wenger Communities of Practice framing** central to PROODOS Aspect 5 (Professional Development). CoPs self-coordinate; they do not depend on a curator's blessing.
- **Proactive curation creates a researcher bottleneck.** A 110-teacher pilot generating 50–150 active threads would require continuous researcher attention to prevent drift.

---

## Hide-trigger criteria (the only reasons to hide)

Content is hidden if and only if it falls in one of these **four categories**. The category is recorded in the `hidden_reason` field for auditability and dissertation analysis:

1. **Platform safety violation** (`safety_violation`)
   Content that promotes harm to students, ignores child safeguarding, recommends illegal AI use cases, or proposes AI-only decisions on consequential outcomes (e.g., final grading, admission, special-needs placement) without human oversight (M6 4 Rights violation).

2. **Off-topic / spam** (`off_topic_spam`)
   Content not related to AI in education, promotional content for unrelated products/services, or duplicate/automated submissions.

3. **Real student PII** (`contains_pii`)
   Content that includes identifying student information (real names, photos, identifying anecdotes) that should be anonymised before sharing.

4. **Copyright violation** (`copyright_violation`)
   Explicit infringement of third-party content (lyrics, full articles, copyrighted curricula, trademarked imagery).

---

## Hide-NEVER criteria

Researcher must **NOT** hide content for any of the following reasons. These reflect community variance, not policy violations:

- Pedagogical disagreement
- Quality concerns ("not good enough")
- Different theoretical orientations
- Beginner-level work
- Subject-area unfamiliarity
- Personal aesthetic preferences
- Disagreement with the author's framing

If a hide action would be triggered by any of the above rather than by the four trigger criteria, **do not hide**. Trust the community to engage critically through comments instead.

---

## Author self-service (distinct from researcher moderation)

Phase A Tier 3 Step 3.5 added **author self-service controls** that are NOT part of researcher moderation:

| Action | Who can do it | DB effect | `hidden_reason` value |
|---|---|---|---|
| Withdraw own post | Post author | `BlogPost.is_hidden=True` | `'author_withdrawn'` |
| Edit own post title | Post author | `BlogPost.title` updated, `updated_at` bumped | — |
| Delete own comment | Comment author | `BlogComment.is_hidden=True`, `BlogPost.comments_count` decremented | `'author_deleted'` |
| Edit own comment | Comment author | `BlogComment.body` updated, `updated_at` bumped | — |

These actions are recorded with their own `hidden_reason` values to keep researcher-driven hides distinct from author-initiated withdrawals/deletions in the moderation log. Author actions are **not** counted in the researcher's weekly review queue.

---

## Researcher monitoring cadence

The researcher reviews the moderation queue **weekly** during the pilot study (n = 110 teachers, ~6-month duration).

### Weekly review activities

1. **Scan** posts and comments created since last review for the 4 hide-trigger criteria.
2. **Document** any hide actions in the moderation log (auto-generated via the Django admin's `LogEntry` table when admin actions are used).
3. **Note patterns** — which categories trigger hides most often — for dissertation analysis.
4. **Reconsider** any prior hide actions if the author has revised content (use `unhide_selected` admin action).

**Where:** Django admin
- Posts: `/admin/peer_blog/blogpost/`
- Comments: `/admin/peer_blog/blogcomment/`
- Filters: by `is_hidden`, `hidden_reason`, `module`, `subject_area`

**Estimated time:** ~30 minutes per week. Manageable load given pilot scale.

---

## Pilot study integrity

The reactive moderation log is itself **research data**:

- Patterns of hidden content reveal **community dynamics**, not researcher curation outcomes.
- Hide rates per category indicate where the community needs better onboarding (e.g., if PII hides spike, the share-flow PII reminder should be strengthened).
- Researcher self-discipline (only hide for the 4 criteria) **protects against bias**.

The categorical separation between researcher-initiated hides (`safety_violation`, `off_topic_spam`, `contains_pii`, `copyright_violation`) and author-initiated soft-deletes (`author_withdrawn`, `author_deleted`) preserves dissertation-grade signal: the former measures community friction, the latter measures author agency.

---

## Defendability for dissertation

The reactive moderation policy:

- **Aligns with platform-wide community-driven philosophy** (Wenger CoP framing, Schön reflective-practice mindset operationalised in the Practice Workshop UI label).
- **Avoids proactive bias in pilot data** — researcher actions are after-the-fact and traceable.
- **Provides a safety net for legal/ethical concerns** without becoming a quality gatekeeper.
- **Documents transparent decision criteria** — the four trigger categories and the seven hide-NEVER cases are public and reproducible.
- **Makes researcher actions auditable** — every hide carries a `hidden_reason`; every `LogEntry` is timestamped and attributed.

---

## Quick reference: when in doubt

| Situation | Action |
|---|---|
| Post includes a real student's full name | Hide — `contains_pii`. Notify author via email if contact_email provided. |
| Post promotes a paid AI product unrelated to teaching | Hide — `off_topic_spam`. |
| Post advocates fully-automated grading without teacher oversight | Hide — `safety_violation`. |
| Post copies a full lyric / article without attribution | Hide — `copyright_violation`. |
| Post is theoretically thin or beginner-level | **DO NOT HIDE.** Let the community comment formatively. |
| Post takes a pedagogical position you personally disagree with | **DO NOT HIDE.** Let the community comment. |
| Author asks researcher to restore a withdrawn post | Use `unhide_selected` admin action. Note the request in research notes. |
| Author asks researcher to permanently delete (vs withdraw) a post | Out of scope of moderation policy — escalate to a separate research-ethics conversation. PROODOS retains records by default for pilot integrity. |

---

*Document scope: M13 / M9 / M14 Practice Workshop content. Forum (apps.community) governed separately.*
*Last updated: 2026-05-03 — Phase A Tier 3 Step 7.*
