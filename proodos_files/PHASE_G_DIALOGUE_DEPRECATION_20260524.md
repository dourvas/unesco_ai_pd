# PROODOS Epilogue — Dialogue + Portrait Deprecation (Phase G Closure)

**Date:** 2026-05-24
**Decision authority:** PI (John Dourvas)
**Status:** ✅ Final decision. Implementation lands in single commit
"Phase G closure: Aletheia removal from Epilogue + Phase J deferred
design".
**Supersedes (in scope):** parts of v2 sections 6, 7, 8 that describe
the Stages 1-3 reflective dialogue and the Learning Portrait HITL
flow. v2 §22 / §23 / §24 / §24.11 / §24.12 amendments retained as
historical record of the prompt-engineering arc that surfaced the
underlying design problem.
**Companion artefacts:** master proposal v2 §25 (pointer); roadmap
§3 Phase G (marked complete with deprecation note); new roadmap
Phase J entry (deferred Aletheia repurposing); literature note §17
(prompt-engineering diminishing-returns methodology evidence).

---

## 1. The decision

**Aletheia is removed from the PROODOS Epilogue.** Final. The four
Phase G surfaces narrow to one teacher-facing surface:

| Surface | v2 plan | Post-deprecation |
|---|---|---|
| Stage 0 — Personal Evolution Dashboard | ✅ ship | ✅ **kept verbatim** (G.1 + G.6b magazine redesign) |
| Stages 1-3 — Aletheia reflective dialogue | ✅ ship | ❌ **removed** |
| Learning Portrait (in-page review + PDF) | ✅ ship | ❌ **removed** (Q1 = Option A in the decision dialogue) |
| Aletheia conversational chatbot | ✅ named persona | ⏸ **deactivated** — repurposed in deferred Phase J |

The Epilogue, post-deprecation, is **a Stage 0 dashboard with a
"Continue" button to T2**. The teacher's flow:

```
M15 complete
   ↓
/epilogue/  →  Stage 0 dashboard (Personal Evolution, magazine register)
                 ↓
                 "Continue" button (POST /epilogue/complete/)
                 ↓
              _post_epilogue_destination → /ailst/t2/  or  /dashboard/
```

Cleanly closes the C.2.5 promise: a post-completion, methodologically
distinct synthesis surface that respects the research-record contract
without adding a sixteenth reflection layer to a platform already
heavy with reflection.

---

## 2. Why

Three converging concerns surfaced 2026-05-24 during the live re-test
cycle that followed the G.6c / §24 / §24.11 / §24.12 prompt-
engineering arc.

### 2.1 Reflection fatigue (pedagogical)

A teacher entering the Epilogue has already produced:

- 15 TAB5 reflections (one per module)
- M5 RTM positioning + M8 DTP composite + M14 Five Roles + Peer
  Synthesis cross-specialty exchanges
- An RPE-grounded reflective stance documented in the dissertation's
  theoretical chapter

Stacking three more reflective phases on top, in a Socratic-dialogue
register, **risks the very thing the dissertation argues against**: a
reflection regime so dense it becomes performative. (See
`Literature_Review_Synthesis_Note(1).md` §15 — the bibliographic
grounding for the original Epilogue dialogue cited Korthagen / Schön /
Mezirow but did not engage the reflection-fatigue literature in
adult professional development.)

### 2.2 RPE framework dilution (methodological)

The Reflective Prompt Engineering framework (Dourvas, Kokkonis &
Kontogiannis, BJET resubmission) is the **distinctive theoretical
contribution** the dissertation rests on. RPE is a *specific* mode of
reflective engagement with AI tools — different in kind from generic
reflection. When the platform offers reflection at every step
(TAB5 × 15 + RTM + DTP + Peer + Epilogue dialogue), the RPE pattern
loses its distinguishing edge: it reads as one slot in a chain of
reflection slots rather than the targeted instrument it is. A
narrower reflection footprint preserves RPE's analytic profile.

### 2.3 Technical fragility (engineering, surfaced during §24)

The §V23 + §24 + §24.11 + §24.12 cycles showed that prompt
engineering for the reflective dialogue had hit **diminishing
returns**:

- §24 reframed "one open question default" → "three closing
  shapes". Live re-test surfaced bare verbatim teacher-parroting.
- §24.11 added an anti-parrot canon + tightened the mirror
  definition. Live re-test surfaced verbatim **example**
  recitation.
- §24.12 added an anti-recitation guard + fictional anchors for
  one specific example. Live re-test surfaced the same recitation
  failure mode in a **different** example.

Each cycle solved the previous failure mode and revealed a new one
in the same family. The diagnosis (recorded in §24.11 of the master
proposal): Gemini 2.5 Flash treats well-matched worked examples as
templates rather than shape demonstrations, and prompt-level rules
are insufficient to override this without programmatic post-
processing.

The technical problem **does not block the Epilogue dialogue from
ever working** — Option A (server-side post-processing guard) or
Option B (upgrade to Gemini 2.5 Pro) would likely close the
recitation hole — but the technical work that would be required to
ship a reliable Aletheia is **disproportionate to the dialogue's
pedagogical contribution**, given §2.1 and §2.2 above.

### 2.4 The decision is not technical — it is pedagogical

The technical fragility was the **trigger** that prompted the
strategic re-evaluation, but the deciding considerations are
pedagogical (reflection fatigue) and methodological (RPE
distinctiveness). Even if the technical problems were solved tomorrow,
the same pedagogical / methodological argument would apply.

---

## 3. What stays, what goes, what defers

### 3.1 What stays — Stage 0 dashboard (the objectively-useful surface)

- Schema (`EpilogueCompletion` model with all 10 fields — see v2 §9
  and §22). The dialogue + portrait fields persist in the DB but
  are no longer populated by removed flows; existing rows (test
  data) are left untouched.
- `apps/epilogue/services_stage0.py::build_stage0_snapshot` and
  related aggregators (DTP theme-evolution, RTM trajectories,
  quantitative summary).
- `apps/epilogue/views.py::epilogue_placeholder_view` (the GET
  endpoint for /epilogue/) — first-entry-only snapshot freeze
  preserved.
- `apps/epilogue/views.py::epilogue_complete_view` — POST endpoint
  flips `completed_at` + routes via
  `_post_epilogue_destination`.
- `templates/epilogue/stage0.html` — G.6b magazine redesign retained,
  simplified to two action buttons: "Back to dashboard" + "Continue".
  The "Begin the conversation with Aletheia" button removed; the
  paragraph that introduced the conversation rewritten.
- `templates/epilogue/_stage0_panel.html` — the partial used inside
  Stage 0, retained.
- `static/css/epilogue.css` — full file retained (the
  `.epilogue-redesign` magazine register is reusable in other
  surfaces; some sections like `.aletheia-header`, `.phase-chapter`,
  `.rfx-screen-in`, `.portrait-spread` become dormant assets
  awaiting Phase J repurposing).
- `static/images/aletheia/` — all four PNG assets retained for
  Phase J repurposing.
- `apps/modules/templatetags/module_design.py` — the
  `epilogue_aspect_colour` template tag + `ALETHEIA_COLOURS` dict
  retained as design-system assets.

### 3.2 What goes — dialogue + portrait teacher-facing surfaces

**Removed from URLs (`apps/epilogue/urls.py`):**

- `/epilogue/dialogue/`
- `/epilogue/dialogue/advance/`
- `/epilogue/portrait/`
- `/epilogue/portrait/regenerate/`
- `/epilogue/portrait/accept/`
- `/epilogue/portrait/pdf/`

**Removed view functions (`apps/epilogue/views.py`):**

- `epilogue_dialogue_view`
- `epilogue_dialogue_advance_view`
- `epilogue_portrait_view`
- `epilogue_portrait_regenerate_view`
- `epilogue_portrait_accept_view`
- `epilogue_portrait_pdf_view`
- Helper functions used only by these:
  `_handle_dialogue_turn`, `_enter_dialogue`, `_advance_dialogue`,
  `_advance_to_stage2`, `_advance_to_stage3`, `_current_stage`,
  `_build_dialogue_phases`, `_dialogue_redirect`,
  `_has_completed_dialogue`, `_build_portrait_context`,
  `_append_portrait_proposal`.

**Templates removed** (no longer referenced anywhere):

- `templates/epilogue/dialogue.html`
- `templates/epilogue/portrait.html`
- `templates/epilogue/_aletheia_header.html`
- `templates/epilogue/_phase_chapter.html`
- `templates/pdf/learning_portrait.html`

Templates live in git history (commit `3b2b524` and successors) — they
remain recoverable for Phase J repurposing or Phase H certificate
template seed.

### 3.3 What defers — agents + service helpers + PDF infrastructure

**Per Q3 in the deprecation decision: agents stay in code,
deactivated.**

- `apps/agents/epilogue_dialogue.py::EpilogueDialogueAgent` — module
  retained with a DEACTIVATED banner comment at the top.  Tests in
  `apps/agents/tests/test_epilogue_dialogue.py` continue to run
  (agent-level, view-independent).
- `apps/agents/epilogue_portrait.py::EpiloguePortraitAgent` — same
  treatment. Tests retained.
- `apps/epilogue/services_stage0.py` service helpers
  (`summarise_dialogue_for_portrait`, `latest_portrait_proposal`,
  `count_portrait_proposals`, `summarise_prior_stages_for_stage3`,
  `pick_juxtaposition_for_stage2`, `should_skip_stage2`,
  `format_juxtaposition_for_prompt`) — retained as pure functions.
  Tests retained.

**PDF generation infrastructure** (`_generate_portrait_pdf` helper +
the `xhtml2pdf` pattern + Article 50(2) PDF document metadata via
`<meta>` tags + JSON-LD body block) — **retained**. The decision
record explicitly notes this infrastructure will be repurposed in
**Phase H** to generate the teacher's "βεβαίωση παρακολούθησης"
(certificate of attendance) PDF. The Article 50(2) compliance
machinery + the magazine register on the PDF template translate
directly. The Portrait template itself
(`templates/pdf/learning_portrait.html`) is removed, but the patterns
it establishes (eyebrow + serif numeral + standfirst + body + AI
provenance footer + olive ornament) become the seed for the
certificate template when Phase H designs it.

### 3.4 What enters Phase J — deferred chatbot design

A new entry in `PROODOS_UNIFIED_ROADMAP.md` reserves design space for
the question "where, if anywhere, does a chatbot belong in this
platform?". Four candidate placements (from the strategic decision
dialogue):

1. **Onboarding companion** — first-contact platform orientation.
2. **Always-on help** — floating "platform teaching assistant".
3. **AI literacy sandbox** — a safe space where the teacher
   experiments with prompt engineering, directly serving the
   UNESCO AI competency + RPE framework.
4. **Post-pilot deferred** — no chatbot in pilot, future work only.

Phase J is **design-only** (no implementation commitment yet). When
it activates, the inventory of reusable assets from this deprecation
is available verbatim (see Phase J entry §H.5.J of the roadmap).

---

## 4. Tests — what passes, what skips, what stays

### 4.1 Test classes marked `@unittest.skip` with reason

The following test classes in `apps/epilogue/tests.py` exercise
views that no longer exist; they are skipped with `@unittest.skip(
"Deactivated in Phase G closure 2026-05-24 — see PHASE_G_DIALOGUE_
DEPRECATION_20260524.md")`:

- `Stage1DialogueTest`
- `Stage2DialogueTest`
- `Stage3DialogueTest`
- `PortraitViewGatingTest`
- `PortraitGenerateAndRenderTest`
- `PortraitRegenerateTest`
- `PortraitAcceptTest`
- `PortraitPDFDownloadTest`
- `PortraitPDFArticle50MetadataTest`
- `DialoguePhaseSeamTest`

### 4.2 Test classes retained (running)

- `EpiloguePlaceholderViewTest` — Stage 0 view, retained.
- `EpilogueCompleteViewTest` — `/complete/` POST, retained.
- `EpilogueM15GatingTest` — TD-013 gate, retained.
- `Stage0SnapshotTest` — `build_stage0_snapshot` aggregation,
  retained.
- `Stage2PickerTest` — `pick_juxtaposition_for_stage2` service
  function (pure logic), retained.
- `TeacherFacingLabelLeakTest` — modified: removes dialogue and
  portrait fixture methods, keeps Stage 0 fixtures only.
- `apps/agents/tests/test_epilogue_dialogue.py` — all 21 tests
  retained (agent-level, view-independent).
- `apps/agents/tests/test_epilogue_portrait.py` — all 16 tests
  retained (same reasoning).

Plus the various service-function tests for `services_stage0.py`
(`summarise_dialogue_for_portrait`, `summarise_prior_stages_for_
stage3`, `pick_juxtaposition_for_stage2`, etc.) — retained as
pure-function tests.

### 4.3 Expected platform test count after deprecation

Pre-deprecation: 479 tests.
Estimated skipped: ~30 tests (10 dialogue + portrait classes,
~3 tests each on average).
Estimated active post-deprecation: ~449 tests passing + ~30 skipped.

The skipped tests show up in test output as "skipped — deactivated
in Phase G closure", making the deprecation visible at test-run
time without breaking CI.

---

## 5. Lessons learned (for the dissertation methodology chapter)

The G.2 / G.3 / G.6c / §23 / §24 / §24.11 / §24.12 arc — followed by
this deprecation — is a methodologically significant case in the
dissertation's chapter on AI-mediated reflective tooling. Three
findings worth recording:

### 5.1 The three-cycle diminishing-returns finding

Successive dual-reviewer correction cycles can close specific failure
modes while leaving the underlying behavioural tendency intact:

- Cycle 1 (§24) corrected over-questioning, introduced bare
  teacher-parroting.
- Cycle 2 (§24.11) corrected bare teacher-parroting, introduced
  uncertainty-example recitation.
- Cycle 3 (§24.12) corrected uncertainty-example recitation,
  surfaced the same recitation in a different example.

This is documented in the master proposal §24.11 and §24.12 +
verified live in `V23_PROMPT_VERIFICATION_20260524.md`. The
empirical signal: at some point, prompt engineering hits structural
limits in the chosen model + scenario combination.

### 5.2 Worked examples are the dominant behavioural signal

Across all three cycles, worked examples carried more weight than
prose rules. The model copied examples verbatim when they matched
real inputs closely (recitation), and copied example shapes when
they did not (good imitation). This is consistent with few-shot
prompting literature but worth recording as a concrete observation
within a teacher-facing reflective-dialogue context where the
prompt designer specifically anchors examples in the same domain
the teacher's input will occupy.

### 5.3 Pedagogical reframing as the right intervention

The trigger for the deprecation was technical fragility, but the
deciding considerations were pedagogical (reflection fatigue +
RPE dilution). When technical iteration approaches diminishing
returns AND a parallel pedagogical reframing question opens, the
pedagogical reframing tends to be the right intervention. The
technical work is not wasted — it surfaced the limits of the
technical-only approach and motivated the pedagogical
re-examination.

This pattern — "technical fragility prompting pedagogical
reconsideration" — is itself an interesting case study for the
dissertation chapter on platform design under research-platform
constraints.

---

## 6. Sequencing — what happens next

1. **This commit** lands the Aletheia removal + Phase J reservation.
2. **G.4** (M15 content alignment + RAG re-ingest) — still useful;
   not affected by this deprecation. Stays as scheduled.
3. **G.5** (sweep) — already complete; lit-note + roadmap get the
   §25 / Phase J updates as part of this commit.
4. **G.6d / G.6e** (Portrait magazine + final sweep) — **cancelled**
   per the deprecation. The G.6c Stage 0 magazine redesign
   (committed `3b2b524`) is the final G.6 visual deliverable.
5. **Phase H** — when designed, the certificate of attendance PDF
   reuses the `_generate_portrait_pdf` infrastructure + the magazine
   register established in G.6.
6. **Phase J** — design-only entry. When activated, the design
   discussion includes the 4 candidate placements + this
   deprecation record + the inventory of reusable Aletheia
   infrastructure.

---

*End of Phase G dialogue deprecation proposal.*
