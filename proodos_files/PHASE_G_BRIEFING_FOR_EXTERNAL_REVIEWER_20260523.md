# Phase G — Briefing for External Reviewer

**Date:** 2026-05-23
**Audience:** A Claude conversational instance, already familiar with
the PROODOS platform, doctoral context, and Phases A-F, but **not**
with anything that has happened inside Phase G. Read this first; it
gives you the time anchor, the implementation status, and the precise
questions you are being asked to weigh in on. Then read the two
design documents and the Aletheia logo image.

---

## 1. Reading order

1. **This briefing** (you are here) — sets time, status, and scope.
2. **`PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md`** — the
   "constitution" of Phase G. Read in full. PI-approved 2026-05-21.
   The §22 amendment at the end is part of the approved text (added
   during G.3 implementation, 2026-05-23).
3. **`Aletheia2048Square.png`** (repo root) — visual reference for
   the new chatbot persona; required to weigh in on §3 / §4 of the
   G.6 proposal.
4. **`PHASE_G_G6_DESIGN_PROPOSAL_v2_20260523.md`** — the document
   you are being asked to review. Written 2026-05-23 (v1, morning →
   v2, evening). If you are reviewing for a second iteration: v2's
   changelog (header section) lists every change from v1 with the
   reviewer item that motivated it, so you can confirm your prior
   points landed faithfully and spend your time on the two
   genuinely-new open items (§11.2 O-1 and O-2).

Optional follow-ups if a specific claim needs verification — see
§5 of this briefing for codebase pointers.

---

## 2. Phase G commit-plan status (as of 2026-05-23)

The commit plan was set in v2 §19. Status today:

| Commit | Subject | Status (2026-05-23) |
|---|---|---|
| **G.0** | Schema extension (10 fields on `epilogue_completions`) | ✅ Merged. Single additive migration `0002_*`. PI dry-run + backup approved. |
| **G.1** | Stage 0 Personal Evolution Dashboard | ✅ Merged. Pure aggregation (no LLM), shared `_stage0_panel.html` partial, frozen on first entry. |
| **G.2a** | Stage 1 (Look Back) dialogue + `EpilogueDialogueAgent` | ✅ Merged. Live sample-reviewed against `mavros`. |
| **G.2b** | Stage 2 (Look In) juxtaposition surfacing | ✅ Merged. §6.4 skip-threshold enforced. Live sample-reviewed. |
| **G.2c** | Stage 3 (Look Forward) + dialogue completion + skip path | ✅ Merged. Live sample-reviewed end-to-end. |
| **G.3** | Learning Portrait + PDF + Article 50(2) markers | ✅ Merged in two sub-commits: G.3a (`EpiloguePortraitAgent` + service + agent tests), G.3b (4 views, PDF template, integration tests). Live sample-reviewed against `mavros` 2026-05-23. Two §22 clarifications landed (no migration). |
| **G.4** | M15 content alignment + RAG re-ingest | ⏳ Pending. Not started. |
| **G.5** | Test sweep + roadmap + TD-011 close + literature note | ⏳ Pending. Not started. |
| **G.6** | **Magazine design upgrade — design proposal v1 in your hands** | 🟡 **Design draft awaiting review. No code written.** |

**Test status, 2026-05-23:** 467 / 467 platform tests pass. Phase G
contribution is 96 tests (Stage 0 services, dialogue agent, portrait
agent, integration views, Article 50(2) PDF metadata regression).

**Time anchor.** Today is 2026-05-23. The G.3 live sample-review
happened *this morning*; the two PI feedback inputs (§3 below) came
out of that review; the G.6 design proposal was written the same
afternoon and is being sent to you the same evening.

**What is locked vs. open.** Anything in v2 (G.0-G.3 architecture,
HITL contracts, schema, agent semantics, Article 50 compliance posture,
ALACT/Mezirow/Schön bibliographic grounding) is **locked** —
PI-approved and partially shipped. G.6 is purely **design + template
+ CSS**; it must not modify the data model, agents, view contracts,
or the dialogue_turns JSON record schema. If your review surfaces a
tension that would require changing G.0-G.3 substance, please flag
it explicitly so we can decide whether to escalate to a v3.

---

## 3. The two PI feedback inputs that triggered G.6

These are the verbatim inputs from the 2026-05-23 review session
that informed the G.6 proposal. Reproduced here so you can judge
whether the proposal honours them faithfully.

### 3.1 Internal research labels leak into teacher-facing UI

**PI's phrasing** (Greek): "Όλες οι αναφορές στο stage 0 1 κτλ δεν
πρέπει να τις βλέπει ο χρήστης" — All references to "stage 0 1 etc."
should not be visible to the user.

**Generalised by Claude Code on the same day** into a platform-wide
rule (saved as a persistent memory): no leakage of `Stage 0/1/2/3`,
`DTP`, `RTM`, `AILST`, `T0/T1/T2`, `Tab1/2/5`, or other internal
research-instrument labels into any teacher-facing surface. The
labels are fine in code, model `help_text`, audit logs, staff
analytics dashboards, and machine-readable compliance metadata —
they are *not* fine in HTML the teacher sees.

**The G.6 proposal addresses this in §5** with an exhaustive
label-relabel table, and **enforces it** by proposing a new test
(`TeacherFacingLabelLeakTest`, §9.4) that renders all three Epilogue
pages and fails on any forbidden substring.

### 3.2 Dialogue phase transitions are visually invisible

**PI's phrasing** (Greek): "με το chatbot η κάθε φάση δεν ήταν
διακριτή. Φαινόταν άσχημα τα 2 συνεχόμεα μηνυματα του chatbot όταν
αλλαζε φάση." — With the chatbot, each phase was not distinct. It
looked bad that the chatbot had two consecutive messages when the
phase changed.

The G.2 dialogue UI is a flat chronological chat scroll. When the
teacher advances from Stage 1 to Stage 2 (or 2 to 3), the closing
turn of phase N and the opening turn of phase N+1 appear as **two
consecutive assistant chat-bubbles** — visually the chatbot is
talking to itself, and the pedagogical phase shift (load-bearing
in v2 §6.1 / §15 / ALACT mapping) is invisible.

**The G.6 proposal addresses this in §4.2** by reworking the
dialogue into a chapter-per-phase layout: prior phases collapse
into a `<details>` block, the new phase animates in with the Tab5
Phase F `rfx-screen-in` keyframe (0.28s, opacity + translateY).
The underlying `dialogue_turns` JSON record is unchanged (research
integrity preserved); only the visual presentation collapses /
separates the boundary turns.

### 3.3 The Aletheia chatbot identity

**PI's phrasing**: "το chatbot μας καλό είναι να έχει όνομα.
Αποφάσισα το Aletheia. στο ροοτ θα βρεις και λογότυπο." — Our
chatbot should have a name. I decided on Aletheia. You'll find a
logo in the root.

The logo (`Aletheia2048Square.png`, 2048×2048): a faceted blue-teal
crystal inside a silvery metallic ring, with a classical olive-laurel
branch curling at the lower right, on a deep teal background, with a
small diamond accent at lower right. Classical Greek register;
ἀλήθεια = unconcealment / truth revealing itself.

**The G.6 proposal addresses this in §3** with a complete persona
treatment: a derived palette (six hex anchors), an Aletheia "aspect"
registered against the existing `module_design` template-tag pack
(so the Epilogue can use the same `--aspect-main/-bg/-text` injection
that TAB1/2/5 use), placement rules (avatar in dialogue, header
treatments, byline in the Portrait), linguistic rules (when to say
"Aletheia" vs. when to keep "gemini-2.5-flash" for Article 50(2)
compliance), and an explicit no-anthropomorphisation guard (§3.5).

---

## 4. What the G.6 proposal does **not** change

So you don't waste cycles reviewing settled ground:

- **Data model.** No new field, no migration. `dialogue_turns` JSON
  schema is unchanged (G.3 §22.1 portrait events already live there).
- **Agents.** `EpilogueDialogueAgent` and `EpiloguePortraitAgent`
  prompts, parameters, extract-only contracts, and provenance posture
  are unchanged.
- **HITL contracts.** Portrait review/regenerate(×2)/accept flow
  (v2 §8.4), Stage 2 skip threshold (v2 §6.4), one-shot Epilogue
  invariant (v2 §9), all unchanged.
- **Article 50(1) and 50(2) compliance.** The transparency notice
  still names "Google Gemini"; `AIArtefactProvenance.model_name`
  still stores `gemini-2.5-flash`; the PDF Info dict still carries
  Title/Author/Subject/Keywords/Creator (G.3 §22.3 strict variant).
  G.6 wraps friendly framing *around* compliance; it never replaces it.
- **Research record.** The `dialogue_turns` log used in dissertation
  analysis (v2 §13) is byte-identical pre/post G.6.
- **xhtml2pdf as the PDF backend.** No new dependency. §1.3 of G.6
  documents what xhtml2pdf can and cannot render (measured 2026-05-23).

---

## 5. Codebase pointers (for verification of claims)

If you want to verify a claim in v2 or G.6 against the actual code:

| Topic | Files |
|---|---|
| Schema (v2 §9) | `apps/epilogue/models.py`; migration `apps/epilogue/migrations/0002_*` |
| Stage 0 aggregation | `apps/epilogue/services_stage0.py::build_stage0_snapshot` |
| Stage 0 partial (shared HTML render path, v2 §8.3) | `templates/epilogue/_stage0_panel.html` |
| Dialogue agent (v2 §7) | `apps/agents/epilogue_dialogue.py` |
| Dialogue views + routing (v2 §6 / §10) | `apps/epilogue/views.py::epilogue_dialogue_view` etc. |
| Portrait agent (v2 §7 + G.3) | `apps/agents/epilogue_portrait.py` |
| Portrait views + atomic accept (v2 §8.4) | `apps/epilogue/views.py::epilogue_portrait_*_view` |
| Portrait in-page template (G.3) | `templates/epilogue/portrait.html` |
| Portrait PDF template (G.3 + §22.3 strict) | `templates/pdf/learning_portrait.html` |
| Article 50(2) machine-readable infrastructure | `apps/compliance/templatetags/ai_provenance.py`; `apps/compliance/services.py::record_ai_provenance` |
| Editorial register reference (TAB1/2/5) | `templates/modules/tabs/tab1_introduction.html`, `tab2_content.html`, `tab5_reflection.html` |
| Aspect-colour injection template tag | `apps/modules/templatetags/module_design.py` |
| xhtml2pdf render-budget test artefact | `pisa_render_budget_test.pdf` + `.png` (repo root) |
| Test suite for Epilogue | `apps/epilogue/tests.py` (~1200 lines, ~50 epilogue + dialogue + portrait integration tests) |
| Test suite for agents | `apps/agents/tests/test_epilogue_dialogue.py`, `test_epilogue_portrait.py` |

---

## 6. The 5 open questions you are being asked to weigh in on

From G.6 §11. Listed verbatim so you can answer them directly. Brief
opinions with reasoning are most useful; "no strong view, defer to PI"
is also a valid answer.

**Q1 — Aletheia avatar shape.** Round-cropped square version of the
logo (chat-bubble convention), or the full square (with the deep-teal
background) embedded? The round avatar is the chat convention; the
square is the designer's intended composition. G.6 §4 assumes
round-cropped — flag for confirmation.

**Q2 — Phase pill labels.** "Look Back · Look In · Look Forward"
(matches existing copy) vs. "Looking Back · Looking In · Looking
Forward" (gerund — continuous action). The literal form is shorter
and matches v2 §6.1.

**Q3 — PDF cover page.** G.6 §4.4 puts the cover-style header on
page 1 inline with the Portrait body. Alternative: dedicate page 1
to a full cover (logo + title + byline only); the Portrait starts
on page 2. The dedicated cover is more "magazine"; the inline header
is more compact.

**Q4 — Drop cap colour.** :first-letter drop cap defaults to
`--aletheia-main` (deep teal). Alternative: use the gem-blue accent
`--aletheia-gem` for a stronger visual hit. Minor decision.

**Q5 — Stage 0 hero icon.** G.6 §4.1 uses the Aletheia crystal as
the hero icon. Alternative: a dedicated synthesis-glyph (e.g. a
stylised olive branch, taken from the same logo) to keep the crystal
exclusive to "Aletheia speaks" moments — so the teacher's *own*
journey gets its own visual mark and the crystal stays associated
with the partner.

---

## 7. What else would be useful from you, beyond Q1-Q5

(Optional — only if you have view.)

- **Anthropomorphisation guard (§3.5).** The proposal forbids
  Aletheia from saying things like "I, Aletheia, think…". Is the
  guard strong enough? Should it be encoded into the dialogue agent
  prompt as an explicit no-self-reference rule, beyond the current
  no-self-disclosure rule?
- **§4.2 collapse pattern.** Prior phases collapse into `<details>`
  by default. Acceptable cognitive-load trade-off, or do you think
  the teacher should see all phases unfolded? (See G.6 §10 for the
  current accepted trade-off.)
- **The Aletheia palette (§3.1).** Six hex anchors derived by
  sampling from the logo. Locked for the pilot to avoid mid-pilot
  visual drift. Plausible, or would you adjust any of the six values
  before they lock?
- **Bibliographic grounding (§6).** Bringhurst, Norman, Reeves & Nass,
  Bryson (counter-weight), Heidegger for the Aletheia name, Dourvas
  RPE paper for continuity with v2 §15. Is the grounding adequate or
  is there a missing source that would strengthen it?
- **Anything you would refuse to ship.** If the proposal contains
  any decision you would push back on if you were the PI, please
  say so directly — that is the most useful kind of feedback.

---

## 8. Out of scope for this review

- Whether the PROODOS Epilogue should exist (settled in v2 §1).
- The choice of `gemini-2.5-flash` as the model (settled in v2 §14
  cost envelope).
- The Article 50(1)/50(2) compliance posture (settled in v2 §8.5 +
  §22.3).
- The decision to use `xhtml2pdf` as the PDF backend (settled in
  v2 §8.2, "No new dependency"; reaffirmed by the G.6 §1.3
  render-budget test which shows the register can be honoured within
  xhtml2pdf's limits).
- The G.4 (M15 content alignment) and G.5 (sweep) commits — they are
  pending but they are not design decisions; they are mechanical
  cleanup. The G.6 review can proceed independent of them.

---

*End of briefing. Time to read v2, then the logo, then G.6.*
