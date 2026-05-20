# F.1 — Voice Input — Design Proposal v1

- **Phase:** F (Multimodal Reflection), sub-track F.1
- **Date:** 2026-05-20
- **Status:** Reviewed — design decisions recorded 2026-05-20
- **Canonical roadmap entry:** `PROODOS_UNIFIED_ROADMAP.md` §3 Phase F

## 1. Scope and decisions already taken

Decisions confirmed with John at the Phase F kickoff (2026-05-20):

1. **Phase F is voice only.** Image input (former F.2) was removed because the
   TAB5 reflection is prospective — all four parts ask what the teacher learned
   and will do, before any AI-integrated lesson has been taught — so no
   classroom artefact exists at reflection time for an image upload to attach
   to. Image-based reflection is re-filed as a Phase G (Epilogue) candidate.
2. **Two transcription paths** will be built behind a toggle: a browser-side
   path (Web Speech API) and a server-side path (a transcription agent calling
   Gemini).
3. **The toggle is an evaluation aid**, not a pilot-time experimental
   manipulation. It is global and staff-only. Both paths are tried during
   development; one is selected for the pilot, so every teacher receives the
   same transcription modality and the voice-vs-text comparison stays free of a
   transcription-quality confound.
4. **Incremental sequencing:** the Web Speech API path is built first. The
   server-side path is deferred but the architecture must leave a clean seam
   for it.
5. **"AI proposes, human ratifies"** governs both paths: a transcript is always
   reviewed and editable by the teacher before it is saved as reflection text.

## 2. What exists today (baseline)

- **TAB5 reflection form** (`templates/modules/tabs/tab5_reflection.html`) has
  four textareas — `part1_insights`, `part2_application`, `part3_concerns`,
  `part4_action` — each a roughly 100-word answer to a module-specific prompt.
- The four parts are **a UI device only**. On submit they are concatenated
  client-side into a single string and POSTed as `reflection_text`. There are
  no per-part fields in the database.
- The reflection is persisted to `UserModuleProgress.reflection_text`
  (`apps/modules/models.py:287`). The RAG, RTM and DTP agents all read this one
  field.
- **Agent hierarchy** (`apps/agents/`): `BaseAIAgent` with two public entry
  points — `generate()` ("AI commits, human disputes") and `extract()` ("AI
  proposes, human ratifies"). Two thin marker branches: `ResearchInstrumentAgent`
  (operates on a teacher's reflection, produces primary research data) and
  `ServiceAgent` (operates on another agent's output).

## 3. The two transcription paths

| Concern | Web Speech API (browser) | Server-side agent (Gemini) |
|---|---|---|
| Where it runs | Entirely in the browser | Audio uploaded to the platform, agent calls Gemini |
| Agent involvement | None — bypasses `apps/agents/` entirely | New agent on the `BaseAIAgent` hierarchy via `extract()` |
| Cost | EUR 0 (no platform AI call) | Per-call Gemini cost against the EUR 1/user limit |
| Greek-accuracy control | Fixed — whatever the browser engine provides | Tunable via prompt/model choice |
| Provenance | See §8 | See §8 |
| Offline / browser support | Chrome/Edge only; absent or partial elsewhere | Works on any browser that can record audio |

**The toggle (decided).** A single global, staff-only setting selects the
active path. It lives on a new staff-only **Platform Settings** page, reached
from the navbar avatar dropdown — the same surface that already hosts the
Research Analytics link (the D.4 staff-surface pattern). The setting is
platform-wide, not a per-user preference, and therefore does not belong on the
teacher profile. It is backed by a single-row configuration model in
`apps/core/`, editable inside the platform without a redeploy. The page is
designed to grow (future toggles, F.5). **Build timing:** the toggle has no
function while only one transcription path exists, so the Platform Settings
page and its `apps/core/` configuration model are built in F.1b alongside the
server-side path, not in F.1a. See §7.

## 4. Sequencing and the architectural seam

The Web Speech API path is built first ("F.1a"); the server-side path is
deferred ("F.1b").

**The seam is the transcript string.** Everything downstream of "a transcript
string now exists" — preview, in-place editing, insertion into the textarea,
marking the reflection as voice-sourced — is written modality-agnostic. The two
paths differ only in how the string is produced:

- Web Speech API produces the string in the browser.
- The server agent produces the string from an endpoint response.

Consequence: the **F.1a build touches none of the agent hierarchy**. The agent,
`extract()`, provenance and cost questions all live on the far side of the
seam and are deferred to F.1b without blocking F.1a.

## 5. Web Speech API design (the F.1a build)

- **Browser support.** Chrome and Edge implement the Web Speech API fully (the
  recognition is served by Google's ASR backend). Firefox does not support it
  in a usable form; Safari has a partial WebKit implementation. The UI must
  feature-detect `SpeechRecognition` / `webkitSpeechRecognition` and, when it
  is absent, hide the microphone affordance and leave the textarea as a normal
  text field. Voice is an addition, never a gate.
- **Language (decided).** The recognition `lang` tag is chosen with a single
  form-level selector rendered as a `<select>` dropdown — not a two-state
  toggle, because a dropdown scales to any number of languages with no
  redesign. Default `en-US`; the pilot also offers `el-GR`. The selector
  applies to all four microphones and remembers the teacher's last choice via
  `localStorage`. The supported-language list is a single source-of-truth
  constant; adding a language is one entry, since the recogniser (and the
  future server agent) simply forward whatever BCP-47 tag they are given. When
  the platform later gains full UI translation (Django `LANGUAGES`), this list
  can be derived from it via a small Django-code-to-BCP-47 mapping (`el` to
  `el-GR`, etc.). The voice-recognition language is deliberately independent of
  the UI language — a teacher may use one language for the interface and
  reflect in another.
- **UI.** A microphone button per part (four buttons, matching the four
  textareas), with explicit recording states: idle, recording, finishing.
  Interim results stream into the textarea as the teacher speaks; final results
  are committed to the textarea.
- **The ratify step is intrinsic.** Because recognised text lands directly in
  the editable textarea, the teacher reviews and corrects it in place before
  pressing Submit. No separate confirmation modal is required — the existing
  textarea is the ratification surface. This matters because browser
  recognition of Greek is imperfect.
- **Submit flow unchanged.** The four textareas are still concatenated into
  `reflection_text` and POSTed exactly as today.

## 6. Server-side path (deferred — F.1b sketch)

Recorded here so F.1a leaves room for it; not built yet.

- **New agent.** A transcription agent fits neither existing branch cleanly: it
  does not operate on another agent's output (`ServiceAgent`), and it does not
  read a reflection to produce an artefact *about* learning (`ResearchInstrument
  Agent`) — it produces the reflection input itself, from audio. Two options,
  to be decided at F.1b start: (a) a new thin marker branch (e.g. `InputAgent`),
  consistent with how `ServiceAgent` was added in D.3b when a genuinely new
  kind of agent appeared; or (b) placement directly under `BaseAIAgent`.
  Preliminary lean: (a).
- **Entry point:** `extract()` — the agent proposes a transcript; persistence
  is the separate, user-driven save of the reflection.
- **Audio lifecycle:** captured via `MediaRecorder` (WebM/Opus), uploaded,
  transcribed, then **discarded**. No audio is stored at rest. This keeps the
  GDPR surface minimal.
- **Cost:** to be estimated at F.1b start and checked against the EUR 1/user
  limit.

## 7. Modality tracking (research dimension F.3)

F.3 proposes comparing voice and text reflections, which requires knowing how
each reflection was produced. Because the reflection is stored as one
concatenated `reflection_text` blob with no per-part fields, per-part modality
tracking would store more structure than the reflection itself carries.

**Recommendation:** one field on `UserModuleProgress` —
`reflection_input_modality`, a nullable `CharField` with choices
`text` / `voice` / `mixed` (`null` = reflections created before F.1). This is
the minimal, proportionate instrument for the voice-vs-text comparison.

**Migrations are split across the two F.1 stages.** F.1a carries one migration
— this `reflection_input_modality` field. F.1b carries the second — the
`apps/core/` configuration model behind the toggle (§3). Each is applied one at
a time, with the full project discipline: `pg_dump` backup at repo root,
`sqlmigrate` + `migrate --plan` dry-run, report to John, then wait for explicit
approval before applying.

## 8. Provenance / EU AI Act Article 50 — decided

**Web Speech API path.** Browser dictation places recognised text into an
editable textarea; the teacher reviews and edits it; the saved `reflection_text`
is the teacher's own authored text. The platform makes no server-side AI call
and stores no AI artefact. **Recommendation:** treat browser dictation as an
input method — comparable to a predictive keyboard or operating-system
dictation — and not as AI-generated content that triggers an Article 50
content marker. The reflection remains teacher-authored.

**Decision (2026-05-20).** The Web Speech API position above is approved:
browser dictation is treated as an input method, not Article 50 content.

**User notification.** Chrome's Web Speech API streams captured audio to
Google's speech-recognition servers (verified 2026-05-20 against the Chrome
developer documentation and the Web Speech API specification — recognition is
server-side, not local). Because this is a data flow the teacher should be
aware of, an inline notice appears next to the voice controls on TAB5. Draft
wording:

> Voice input uses your browser's built-in speech recognition. In Chrome and
> Edge, the audio you record is sent to the browser's speech service to
> convert it to text; PROODOS itself does not receive or store the audio. The
> recognised text appears in the box for you to review and edit before
> submitting, and is saved only as part of your written reflection. You can
> type your reflection instead at any time.

This is user-facing, privacy-disclosure-adjacent copy: the final wording
requires John's explicit sign-off and must be aligned with the existing
privacy notice and consent text in the pre-pilot privacy review.

**Server-side path (F.1b).** Gemini transcription is a platform-initiated AI
processing step. Provenance is to be revisited at F.1b — the output is
teacher-ratified, but an audit/provenance trace of the transcription step is
likely warranted.

See §11 for the consolidated decision record.

## 9. Cost

- Web Speech API path: EUR 0 — no platform AI call.
- Server-side path: estimate deferred to F.1b.

## 10. Bibliographic grounding (project rule 8)

The **engineering and methodology decisions** in this proposal — the toggle,
the Web-Speech-first sequencing, the transcript-string seam, the single
`reflection_input_modality` field — introduce no new theoretical construct and
therefore require no new reference. This is stated explicitly so the omission
is not read as an oversight.

The one **construct-bearing claim** is F.1's rationale itself: that voice input
reduces cognitive load and serves inclusive design, answering the literature's
critique that AI-mediated professional development is text-heavy.
`Literature_Review_Synthesis_Note(1).md` currently has no entry for this. Areas
to verify (web search, before any citation): cognitive load and input modality;
speech-to-text/dictation in written composition; Universal Design for Learning
(multiple means of action and expression); accessibility of voice input. No
specific authors are asserted here until verified. A literature-note update is
owed before F.1 is presented as dissertation content.

## 11. Decisions (resolved 2026-05-20)

1. **Toggle home** — a new staff-only Platform Settings page (reached from the
   navbar avatar dropdown), backed by a single-row configuration model in
   `apps/core/` (§3).
2. **Language selection** — a single form-level `<select>` dropdown, default
   `en-US`, single source-of-truth language list, last choice remembered via
   `localStorage` (§5).
3. **Article 50 position** — approved; browser dictation is an input method,
   not Article 50 content. An inline user notice is added to TAB5 (§8).
4. **Modality field** — `reflection_input_modality` (`text` / `voice` /
   `mixed`, nullable) on `UserModuleProgress`, approved (§7).
5. **Microphone granularity** — per-part microphone, four buttons (§5).
6. **Bibliographic verification** — folded into the F.1 build; literature-note
   entries are added as F.1 is built, not blocking the build and not deferred
   to F.3/F.4 (§10).

**One item remains open:** the final wording of the §8 user notice awaits
John's explicit sign-off before it ships.
