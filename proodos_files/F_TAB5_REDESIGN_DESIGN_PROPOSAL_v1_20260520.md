# Phase F — TAB5 Redesign (5-screen wizard + magazine + voice) — Design Proposal v1

- **Phase:** F (formerly split as F.1 voice + the parked F.5 TAB5 redesign — now merged)
- **Date:** 2026-05-20
- **Status:** Reviewed — design decisions recorded 2026-05-20
- **Supersedes:** `F1_VOICE_INPUT_DESIGN_PROPOSAL_v1_20260520.md` and the parked
  F.5 entry in `PROODOS_UNIFIED_ROADMAP.md` §3.

## 1. How we got here (decisions already taken)

The Phase F kickoff (2026-05-20) produced a chain of scoping decisions:

1. **F.2 (image input) removed** — the TAB5 reflection is prospective, so no
   classroom artefact exists at reflection time. Re-filed as a Phase G
   candidate.
2. **Voice input via the Web Speech API** — browser-side dictation, no server
   call.
3. **F.1b (server-side transcription agent) cancelled** — a short live test of
   the Web Speech API gave satisfactory results, so the server-side path is
   not needed. This also cancels the toggle, the Platform Settings page, the
   `apps/core` configuration model, and the second migration that F.1b implied.
4. **The per-part-microphone build hit a wall** — four microphones on one page
   triggered a Web Speech API multi-session reliability problem (first
   microphone worked, the rest did not). Rather than fight it, the work merges
   with the TAB5 redesign: one microphone per screen sidesteps the entire
   problem class.

The net effect: **Phase F collapses into one coherent piece of work** — redesign
TAB5 as a five-screen wizard (four parts plus a review screen) in the magazine
style, with voice input built in from the start. This is what the roadmap
anticipated when it parked F.5 ("voice affordances must be designed into the
redesign from the start").

## 2. What exists today

- `templates/modules/tabs/tab5_reflection.html` (~1880 lines). One long page.
- The reflection form has four parts — `part1_insights`, `part2_application`,
  `part3_concerns`, `part4_action` — each a ~100-word answer to a
  module-specific prompt. Part 3 additionally has a "smart concerns" generator
  (checkboxes to AI-generated text).
- The four parts are a UI device only. On submit they are concatenated
  client-side into one string and POSTed as `reflection_text` to
  `/modules/modules/{code}/complete/reflection/`. There are no per-part
  database fields.
- After submission the page shows the RAG feedback, then the on-demand RTM,
  DTP and peer-synthesis panels.
- Visual register: DaisyUI pastel cards, hard borders, emoji-prefixed titles —
  the "2020 admin-UI" look the parked F.5 entry identified.
- `UserModuleProgress.reflection_input_modality` (`text` / `voice` / `mixed`,
  nullable) was added and migrated on 2026-05-20 (F.1a commit 1). It is valid
  and used by this redesign.

## 3. The magazine pattern to adopt (from TAB1 / TAB2)

TAB1 and TAB2 already establish an in-house magazine pattern. The TAB5 redesign
reuses it rather than inventing one:

- `{% load module_design %}` template tags — `module_aspect_colour`,
  `module_aspect_name`, `module_number_padded`, `module_icon_svg`.
- A scoped root wrapper (`.tab5-redesign`) carrying the aspect colour as inline
  CSS custom properties: `--aspect-main`, `--aspect-bg`, `--aspect-text`.
- An embedded `<style>` block with every selector prefixed by `.tab5-redesign`,
  built on the DaisyUI theme variables (`oklch(var(--b1))`, `--b2`, `--b3`,
  `--bc`).
- Editorial typography: serif titles (`ui-serif, Georgia, serif`), uppercase
  letter-spaced "eyebrow" labels, large numerals.
- A magazine header (eyebrow + serif title + blurb).
- TAB2's **sticky navigator with pills and a progress bar** — directly reusable
  as the wizard's step indicator.
- Mobile `@media` queries; a scoped `<script>` IIFE at the end of the file.

## 4. The redesign — a five-screen wizard

The reflection input becomes a five-step wizard — one part per screen, then a
review screen:

| Screen | Content | Notes |
|---|---|---|
| 1 | Part 1 — Key Insights | |
| 2 | Part 2 — Application in Your Classroom | |
| 3 | Part 3 — Concerns & Challenges | keeps the existing "smart concerns" generator |
| 4 | Part 4 — Action Plan | |
| 5 | Review | all four parts in one read-only overview + total word count; the **Submit** button lives here |

- **One screen visible at a time.** All four part-inputs remain in the DOM; the
  wizard JavaScript shows one screen and hides the others. This is a
  client-side presentation layer — see §6 for why that matters.
- **Free navigation.** Step pills and Next/Back let the teacher move between
  screens freely — no per-part gate. The only validation is the existing
  total-word check (350–500 words), applied on the review screen at Submit.
- **Step indicator** — the TAB2 navigator pattern: five pills
  (`1 · Insights`, `2 · Application`, `3 · Concerns`, `4 · Action Plan`,
  `5 · Review`) plus a progress bar.
- **Next / Back** buttons. On screen 5, Next becomes **Submit Reflection**.
- **Review screen** — screens 1–4 collected into one read-only overview so the
  teacher sees the whole reflection before submitting; each part is editable by
  jumping back to its screen via the pills or Back.
- **Magazine header** above the wizard: eyebrow (`Module {{code}} · {{aspect}}
  · {{level}}`), serif title ("Reflection & Action Plan"), short blurb.
- **Per-screen word count**; the total is shown on the review screen.
- **Draft autosave** — the four parts autosave to `localStorage`, so a refresh
  mid-wizard does not lose work; the draft is cleared on successful submit.
- **Magazine styling throughout** — the pastel cards, hard borders and
  emoji-prefixed titles are replaced with the scoped magazine register from §3.

## 5. Voice input

Each screen has exactly **one** textarea and **one** microphone button.

- **One reused `SpeechRecognition` instance** for the page, created once.
  Because only one microphone is ever on screen, voice usage is sequential
  (record → stop → navigate → record) — the basic, well-supported Web Speech
  pattern, not the multi-microphone switching that failed.
- Interim results stream into the visible textarea; the teacher reviews and
  edits in place before moving on ("AI proposes, human ratifies", intrinsic to
  the editable textarea).
- A form-level language `<select>` — default `en-US`, `el-GR` offered, last
  choice remembered via `localStorage`. A single source-of-truth language list.
- Feature detection: without the Web Speech API the microphone and language
  controls stay hidden and the wizard works as a plain text form.
- An inline Article 50 notice near the voice controls (wording in §8).

## 6. What stays unchanged — the low-risk argument

The redesign is deliberately confined to the **input presentation layer**:

- **The submit endpoint is unchanged.** The four textareas are still
  concatenated into `reflection_text` and POSTed once, exactly as today.
- **The RAG / RTM / DTP / peer-synthesis pipeline is untouched** — the
  research-critical machinery does not move.
- **The reflection questions and content are unchanged** — measurement
  fidelity is preserved.
- **No new migration.** `reflection_input_modality` already exists.
- **No new model, no new URL, no new view.** The only backend change is small:
  the existing reflection submit view reads one extra POST field
  (`input_modality`) and stores it on `UserModuleProgress` (§7).
- The post-submit feedback / RTM / DTP / peer panels receive a **magazine
  visual pass** (decision §10.3) so the post-submit view is consistent with the
  redesigned input. This is a visual change only: their behaviour, their
  JavaScript (RTM sliders, DTP rendering, dispute controls) and — critically —
  the Article 50 regulatory contract (50(1) human-readable XAI panels + 50(2)
  machine-readable provenance) and the HITL controls are preserved unchanged.

In practice the redesign is a rewrite of one template file
(`tab5_reflection.html` — which holds both the input wizard and the post-submit
panels) plus a roughly two-line view change.

## 7. Modality tracking

The wizard JavaScript records, per part, whether voice was used. On Submit it
computes the reflection-level modality — `text`, `voice`, or `mixed` — and
includes `input_modality` in the existing POST body. The submit view reads it
and sets `UserModuleProgress.reflection_input_modality`. This feeds the
voice-vs-text research dimension. No migration — the field already exists.

## 8. Provenance / EU AI Act Article 50

The position from the F.1 proposal stands: browser dictation is an input
method, not Article 50 content. An inline notice appears near the voice
controls. Draft wording (verified 2026-05-20: Chrome's Web Speech API performs
recognition server-side, streaming audio to Google):

> Voice input uses your browser's built-in speech recognition. In Chrome and
> Edge, the audio you record is sent to the browser's speech service to convert
> it to text; PROODOS itself does not receive or store the audio. The
> recognised text appears in the box for you to review and edit before
> submitting, and is saved only as part of your written reflection. You can
> type your reflection instead at any time.

This is user-facing, privacy-disclosure-adjacent copy: the final wording
requires John's explicit sign-off and alignment with the existing privacy
notice and consent text in the pre-pilot privacy review.

## 9. The earlier voice bug — honest note

The per-part build failed in two stages: a fresh `SpeechRecognition` per
recording (only the first captured audio), then a single-instance rewrite that
stopped working entirely for reasons not diagnosed (the browser console was not
available). The redesign reduces the risk surface sharply — one microphone per
screen, sequential use, the simplest supported pattern — but the recognition
lifecycle (start / stop / re-record on one instance) must still be implemented
carefully. During the build this will be verified against the browser console
rather than guessed at blind; one short console check from John may be
requested at the right moment.

## 10. Decisions (resolved 2026-05-20)

1. **Next-button gating** — free navigation between all screens; the only
   validation is the existing total-word check at Submit (§4).
2. **Draft autosave** — the four parts autosave to `localStorage`; a mid-wizard
   refresh does not lose work (§4).
3. **Post-submit panels** — they receive a magazine visual pass so the
   post-submit view matches the redesigned input. Behaviour and the Article 50
   / XAI / HITL regulatory contract are preserved unchanged (§6).
4. **Review screen** — a fifth screen: screens 1–4 are the four parts,
   screen 5 is a read-only review of all four with the total word count, and
   Submit lives there (§4).

**One item remains open:** the final wording of the §8 voice-input user notice
awaits John's explicit sign-off.

## 11. Bibliographic grounding (project rule 8)

This proposal is an interaction-design and UX-redesign change. It introduces
**no new theoretical construct** and therefore requires no new reference — the
wizard, the magazine styling and the modality plumbing are engineering. Stated
explicitly so the omission is not read as an oversight.

The one construct-bearing claim remains the voice-input rationale (cognitive
load, inclusive design, Universal Design for Learning) carried over from the
F.1 proposal. `Literature_Review_Synthesis_Note(1).md` still has no entry for
it; verified references are owed before Phase F is presented as dissertation
content.

## 12. Implementation outline (for review, not yet approval to build)

Staged so each commit is reviewable and browser-testable:

1. **Magazine shell + wizard structure** — rewrite the reflection input in
   `tab5_reflection.html` with the scoped magazine layout, the five-screen
   wizard (four parts + review), step navigator, Next/Back, free navigation,
   per-screen word counts and `localStorage` draft autosave. Plain text inputs,
   no voice yet.
2. **Voice input** — the single-instance Web Speech integration, language
   selector, feature detection, Article 50 notice.
3. **Post-submit magazine pass** — restyle the RAG feedback / RTM / DTP / peer
   panels to the magazine register, preserving behaviour and the Article 50 /
   XAI / HITL regulatory contract.
4. **Modality tracking** — the per-part voice signal and the submit-view field
   write.

Each stage is browser-tested by John before the next begins.
