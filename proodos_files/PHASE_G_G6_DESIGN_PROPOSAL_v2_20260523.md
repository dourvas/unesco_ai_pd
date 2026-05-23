# PROODOS Epilogue G.6 — Magazine Design Upgrade (Design Proposal v2)

**Date:** 2026-05-23 (v1); 2026-05-23 (v2, same evening — incorporates
external-reviewer feedback received the same day).
**Status:** v2 awaiting final PI sign-off before G.6a starts.
**Origin:** Promised in `PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md` §19
(G.6 commit row) and §20 (re-evaluate §8.3 single-render trade-off at G.6
design time). Triggered after the G.3 live sample-review against `mavros`
(2026-05-23), where the PI surfaced two design defects (internal labels
leaking, phase-seams in the dialogue) and introduced the chatbot identity
("Aletheia").
**Roadmap relationship:** Implements `PROODOS_UNIFIED_ROADMAP.md` §3 Phase G
(G.6 row) and closes the design-debt incurred by shipping G.1-G.3 with
plain Bootstrap-style markup. Depends on v2 §23 of the master Phase G
proposal landing first (4-line agent-prompt addition enforcing the
Aletheia persona inside the dialogue).
**Supersedes:** v1 of this document (same date). Builds on, does not
replace, v2 of the Phase G proposal (which holds the data-model, agent,
and HITL contracts unchanged).

---

## v1 → v2 changelog (external review 2026-05-23)

External reviewer (second Claude instance, full project context except
Phase G implementation; briefed via `PHASE_G_BRIEFING_FOR_EXTERNAL_REVIEWER_
20260523.md`) returned a structured critique the same evening. Three
substantive blockers, five improvements, answers to all five §11
open questions. v2 incorporates them, with two specific divergences
documented inline:

| Reviewer item | v2 treatment |
|---|---|
| **B.1** — `TeacherFacingLabelLeakTest` would break Article 50(2) compliance content | §9.4 rewritten: BeautifulSoup `get_text()` after stripping `<script>` / `<style>` / `<meta>` / `<head>`, word-boundary regex for short tokens. |
| **B.2** — Collapsed prior phases need methodological disclosure | New §10 trade-off paragraph + cross-reference to literature note for the dissertation methodology chapter. |
| **B.3** — Anti-anthropomorphisation rule is template-only; the model itself does not know it is "Aletheia" | **Escalated to v2 §23** of the master Phase G proposal (PI decision, 2026-05-23). 4-line prompt addition lands in its own commit before G.6a. G.6 §3.5 corrected to reference §23 rather than claim the existing prompt already enforces. |
| **C.1** — Palette derivation method not documented | §3.1 grows a "derivation" sub-paragraph naming the sampling points and tool. |
| **C.2** — "Aletheia" vs "Gemini" boundary fuzzy in skip-note copy (§4.5) | §3.3 clarified: Aletheia for narrative + system-action copy *inside the Epilogue narrative frame*; Gemini for formal Article 50 disclosure paragraphs. |
| **C.3** — Heidegger reference needs an education-domain bridge | §6.5 marks the bridge citation as placeholder pending PI verification (the reviewer's specific suggestion — Gallagher 2018 *Phenomenology and Educational Research* — could not be verified in time; per the project's no-hallucination citation rule, the verified Gallagher 2012 *Phenomenology* (Palgrave) is named as a candidate but final source needs PI confirmation). |
| **C.4** — Greek translation of "Look Back/In/Forward" deserves care | §4.2 grows a translation-guidance note. **Diverges from reviewer's suggestion** of "Παρελθόν/Παρόν/Μέλλον" (Past/Present/Future) — that reframe loses Korthagen ALACT's action-orientation; recommend gerund-form Greek ("Κοιτάζοντας πίσω / μέσα / μπροστά") instead. |
| **C.5** — PDF template render-budget guard could be a 10-line test, not out-of-scope | §9.7 replaced: actual 10-line regex-substring test specified. |
| **E.2** — Mobile sample-review missing from §9.5 | §9.5 grows a mobile-specific note. |
| **E.5** — Olive branch as completion ornament on Portrait | Adopted. §4.3 + §4.4 add olive-ornament treatment (footer divider in-page, page-end mark in PDF). Ties PROODOS (πρόοδος) to laurel-as-completion symbolism. |
| **Q1-Q5** answered | §11 reorganised: Q1-Q5 marked **resolved** with the reviewer's answers and reasoning; §12 decisions log updated. |
| **E.4** — Reeves & Nass (1996) is 30 years old | **Diverges** — kept as the canonical foundational citation; the social-actor framing it supports is uncontested in 2026 and standard in doctoral work. A modern follow-up would be additive only and is left to PI discretion. |
| **E.1, E.3** — Already addressed inside the proposal as written | No edit needed. |

Two reviewer points required PI escalation (B.3 + the C.3 citation
verification path). Both are surfaced in §11 of v2 as the only two
remaining open items.

---

## v2 → v2-revised changelog (second-pass review, same evening)

The same reviewer ran a second pass on the v2 above and returned
five improvements (no blockers). v2-revised incorporates them inline:

| Item | v2-revised treatment |
|---|---|
| **Bridge citation choice** | §6.5 adopts **van Manen 1990 / 2016, *Researching Lived Experience*** (verified, canonical for phenomenology-in-teacher-education) — supersedes the Gallagher candidate from v2. Closes O-2. |
| **Defense statement: why Heidegger AND Schön** | §6.5 grows a committee-question-anticipated paragraph: Schön grounds *how* reflection happens, Heidegger §44 grounds *what* it is; van Manen sits between them as the established education bridge. |
| **Error-state copy rule** | §3.3 adds a third category beyond narrative + disclosure: **error states use passive voice**, naming neither Aletheia nor Gemini ("The reflection could not be generated" not "Aletheia could not respond"). §4.5 portrait-skip note revised accordingly. Protects against eroding Article 50(1) over time. |
| **Concrete dissertation methodology disclosure** | §10 trade-off paragraph now carries a **pre-written verbatim block** for `Literature_Review_Synthesis_Note(1).md` §16 and the dissertation methodology chapter — saves drafting time later and locks the disclosure to the exact G.6c mechanism. |
| **Three dialogue fixtures for label-leak test** | §9.4 test class extended: instead of one `test_dialogue_page_no_leaks`, the dialogue page is exercised in **three active-stage states** (Stage 1 active, Stage 2 active, Stage 3 active with prior collapsed) plus the portrait page in two states (draft + accepted). Catches leaks that surface mid-dialogue, not only at end-state. |
| **Behavioural-regression test for v2 §23 prompt change** | Master Phase G v2 **§23.6** rewritten as **two-layer verification**: layer 1 = forbidden-substring scan (the four new restrictive rules hold); layer 2 = stance-preservation check (the existing descriptive-not-evaluative, refusal-of-evaluation, one-open-question, warm-register guarantees do not regress). Protects against over-constraining prompt drift. |

The v2-revised changes are non-substantive (no design pivot, no scope
change, no commit-plan change) — they harden citations, tighten copy
rules, and strengthen test coverage. The G.6 surfaces (§4) are
unchanged. Filename stays `PHASE_G_G6_DESIGN_PROPOSAL_v2_20260523.md`
under the master-proposal convention of using inline revision notes
for same-day refinements (cf. v2 §22, §23 of the master proposal).

Only one item remains open after v2-revised: **O-1** (PI confirmation
of the exact wording of the four prompt lines in master proposal
§23.2 — needs to be read and signed off before the §23 commit lands).

---

## 0. Summary

G.1-G.3 shipped the Epilogue's structure and AI machinery: the frozen
Stage 0 snapshot, the three-phase reflective dialogue, the Learning
Portrait with PDF and Article 50(2) markers. They shipped with **plain
markup** — DaisyUI defaults, chat-bubble dialogue, prose-card portrait.
The text the teacher reads is correct; the visual register is wrong.
G.6 brings the three Epilogue surfaces (Stage 0 page, dialogue, Portrait
in-page + PDF) into the **TAB1/TAB2/TAB5 editorial register** the modules
already use (v2 proposal §19), gives the chatbot the **Aletheia**
persona introduced 2026-05-23, fixes the dialogue **phase-seam** bug
surfaced in the same review, and resolves the §22.3 single-render
question with a clear in-page-vs-PDF split grounded in a measured
`xhtml2pdf` render-budget test.

G.6 is **design + template + CSS**. No data-model migration, no agent
change, no compliance change. The `dialogue_turns` JSON record (the
research artefact) is byte-identical to G.3.

---

## 1. What changed since v2 — the three triggering inputs

### 1.1 Live sample-review defects (2026-05-23, `mavros` end-to-end)

After the G.3 live review the PI raised two issues that v2 did not
anticipate:

**(a) Internal research labels leak into the teacher-facing UI.**
"Stage 0", "Stage 1", "Stage 2", "Stage 3", "DTP", "RTM", "AILST",
"T0/T1/T2" appear in user-visible copy. These are load-bearing
research constructs (Korthagen ALACT mapping, instrument names,
research timepoints) but the teacher experiences them as bureaucratic.
The same defect recurs platform-wide; saved as a project-wide rule.

**(b) Dialogue phase transitions are visually invisible.** Moving from
Stage 1 to Stage 2 (or 2 to 3) produces two consecutive assistant
messages — the closing turn of phase N + the opening turn of phase
N+1 — in one flat chat scroll. The phase shift is pedagogically
load-bearing (ALACT structure, v2 §6.1 / §15) but visually it reads
as the chatbot talking to itself.

### 1.2 The Aletheia chatbot identity (2026-05-23)

The reflective dialogue agent + the Portrait author are given a single
teacher-facing persona: **Aletheia** (ἀλήθεια — unconcealment / truth
revealing itself). Logo `Aletheia2048Square.png` at the repo root:
faceted blue-teal crystal inside a silvery ring with a classical
olive-laurel branch curling at the lower right, on a deep teal
background. The classical Greek register ties to PROODOS (πρόοδος =
progress) and to the project's Schön / Mezirow / Korthagen reflective-
practice grounding (v2 §15).

Compliance and research instruments keep `gemini-2.5-flash` as the
canonical model name (Article 50(2), `AIArtefactProvenance`,
`dialogue_turns[i].model`, PDF document metadata Creator field). The
teacher experience names the persona. Two layers, two audiences,
no conflict.

### 1.3 `xhtml2pdf` render-budget test (2026-05-23)

To resolve the §22.3 "one render path may need to relax" question
empirically, a small render-budget probe was run against `xhtml2pdf`
(`pisa`). Results, exhaustively measured:

| CSS feature | xhtml2pdf result |
|---|---|
| `font-family: Georgia, ui-serif` | ✅ Renders correctly |
| Editorial serif numerals (Georgia 48pt) | ✅ Renders correctly |
| `border-left: 4pt solid <color>` + padding | ✅ Tab2 part-rule signature works |
| Tinted callout panels (flat `background-color`) | ✅ Works |
| `text-transform: uppercase` + `letter-spacing` | ✅ Eyebrow style works |
| `border-radius` | 🟡 Renders, but subtle |
| `rgba(...)` colors | ✅ Works |
| `column-count: 2` multi-column flow | ❌ Falls back to single column |
| `:first-letter` drop cap | ❌ Pseudo-element not honoured |
| Inline `<svg>` | ❌ Not rendered |
| `linear-gradient(...)` | 🟡 Collapses to first colour (flat) |

(Test artefact: `pisa_render_budget_test.pdf` + rendered `.png`.)

**Resolution.** Adopt a **two-track render policy**:

- **In-page (web)** track may use multi-column, SVG, `:first-letter`
  drop caps, true gradients, JS interactions, and `prefers-reduced-
  motion`-gated animations.
- **PDF** track stays single-column, no SVG (HTML/CSS shapes only),
  drop caps via explicit `<span class="dropcap">A</span>` wrapper,
  flat-colour anchors (no gradient).
- The **shared Stage 0 partial** (`_stage0_panel.html`) already uses
  none of the broken features and stays a single template. The new
  Portrait visual treatments split (`portrait.html` rich, `pdf/
  learning_portrait.html` PDF-safe) — v2 §8.3's "one render path"
  ambition is **explicitly relaxed for the Portrait body**, accepted
  as a trade-off and recorded here.

---

## 2. The TAB1/TAB2/TAB5 editorial register — the visual contract G.6 implements

Extracted by survey of `templates/modules/tabs/tab1_introduction.html`,
`tab2_content.html`, `tab5_reflection.html` (2026-05-23). The register
has eight consistent signatures:

### 2.1 Typography signature

- **Serif numerals & headings** in `ui-serif, Georgia, "Times New
  Roman"` (system fonts; no `@font-face`, no Google Fonts).
- **Hero numeral**: 4rem, weight 600, line-height 1, letter-spacing
  −0.04em. Mobile scales to 3rem.
- **Section title**: serif 1.5-2.25rem, weight 600/700.
- **Eyebrow** (small caps label above title): sans 0.7-0.75rem,
  weight 600, uppercase, letter-spacing 0.06-0.1em.
- **Body**: sans 0.9-0.95rem, line-height 1.55-1.6, applied via
  Tailwind `prose` classes.

The "**serif numeral + sans title + eyebrow**" triplet is the editorial
signature for openings across all three tabs.

### 2.2 Aspect-colour injection

Each tab injects three CSS variables on its wrapper element from the
module's aspect:

```html
<div class="tab1-redesign"
     style="--aspect-main: {{ aspect_colour.main }};
            --aspect-bg:   {{ aspect_colour.bg }};
            --aspect-text: {{ aspect_colour.text }};">
```

All decorative colour downstream references these variables. The
Epilogue has no module — G.6 introduces a dedicated **Aletheia**
aspect (see §3.2) so the Epilogue surfaces inherit the same injection
pattern.

### 2.3 Editorial left-border rules

- **Part rule** (Tab2): `border-left: 4pt solid var(--aspect-main);
  padding-left: 12pt;` for major chapters.
- **Review rule** (Tab5): `border-left: 3pt solid oklch(var(--bc)/
  0.35);` for secondary panels.

### 2.4 Aspect-tinted callout panels

Used for collapsibles, intro stripes, prompt cards. Background =
`var(--aspect-bg)`, text = `var(--aspect-text)`, no left rule, no
heavy border.

### 2.5 Sticky part navigation

Tab2 keeps a sticky horizontal pill strip at the top of the page,
synchronising the active pill with the scrolled-into-view part and
filling a 0.25rem progress bar. Available for re-use in the dialogue.

### 2.6 Wizard pattern (Tab5 Phase F refresh)

Each reflection screen is a discrete "card" with a `rfx-screen-in`
keyframe (0.28s `opacity 0→1` + `translateY 10px→0`), pill-based
inter-screen navigation, progress bar, and `prefers-reduced-motion`
respect. **This is the direct answer to §1.1(b).**

### 2.7 No SVG dividers, no drop caps

The register relies on whitespace, typography, and accent colour
alone — there are no decorative SVG dividers in TAB1/2/5. This is
helpful: the register is naturally PDF-safe (§1.3) without
back-porting.

### 2.8 AI provenance inline at top

`{% ai_provenance_jsonld %}` block ships at the top of `tab5_
reflection.html` (line 9) and rendered prose carries `{% ai_provenance %}`
inline rows. **Already mirrored in `portrait.html` — no change needed.**

---

## 3. The Aletheia persona — visual + linguistic application

### 3.1 Asset

`Aletheia2048Square.png` (2048×2048, square). Faceted blue-teal
triangular crystal inside silvery ring, classical olive-laurel branch
lower-right, deep teal background, small diamond/star accent lower-right.

Derived palette (sampled from the logo for the Epilogue aspect):

| Token | Hex | Role |
|---|---|---|
| `--aletheia-deep` | `#0F4A45` | Background anchor, deep teal |
| `--aletheia-main` | `#1A8A73` | Aspect-main accent (left rules, badges) |
| `--aletheia-bg`   | `#D4E8E2` | Aspect-bg tinted panel (callouts) |
| `--aletheia-text` | `#0D2A25` | Aspect-text on tinted panel |
| `--aletheia-silver` | `#94A3B8` | Decorative rule / secondary border |
| `--aletheia-gem` | `#3FAFE0` | Highlight / gem-blue accent |

(Hex anchors are PDF-safe; in-page may use `oklch()` variants where
DaisyUI's token system applies.)

**Derivation (audit trail).** Anchors were sampled by visual inspection
of `Aletheia2048Square.png` (2026-05-23, color-picker tool against
representative pixels). Sampling points:

- `--aletheia-deep`: upper-left quadrant background, away from the
  vignette gradient (avoids the lighter centre).
- `--aletheia-main`: mid-crystal facet, the dominant blue-teal of the
  central gem.
- `--aletheia-bg`: derived by lightening `--aletheia-main` (HSL L+
  ~60%) to a tint that survives `xhtml2pdf` rendering as a flat
  panel background (verified in the §1.3 budget test).
- `--aletheia-text`: deep-teal, contrast partner to `--aletheia-bg`
  (WCAG AA target on body text).
- `--aletheia-silver`: the metallic ring of the logo, a neutral cool
  grey.
- `--aletheia-gem`: highest-saturation blue facet on the right side
  of the crystal, the brightest highlight in the image.

Locked for the pilot (§10 trade-off). Post-pilot revision is fine; a
mid-pilot change is forbidden so all teachers' PDFs look consistent.

### 3.2 Aspect registration

The Epilogue is registered as a synthetic "aspect" in the design-
system tag layer used by Tab1/Tab2/Tab5. The aspect name is
"Reflective Synthesis" (Greek: "Στοχαστική Σύνθεση"); the icon is
the Aletheia crystal (cropped circle of the logo); colours per §3.1.
Implementation note: the existing `module_design` template tag pack
(`{% module_aspect_colour module as aspect_colour %}`) is the source
of these values; G.6 adds an "epilogue" aspect entry to that pack so
the same `--aspect-*` injection works in the Epilogue templates.

### 3.3 Linguistic rules — when to say "Aletheia"

**Use "Aletheia"** in teacher-facing copy:

- Chat header / avatar label in the dialogue.
- Stage 0 page intro framing ("Aletheia will guide a short reflective
  conversation about your journey…").
- Portrait page intro ("Aletheia has written this Learning Portrait
  from your reflections…").
- Portrait accept screen copy.
- Button hover hints, tooltips, empty states.

**Keep "Gemini" or "gemini-2.5-flash"** in formal compliance copy and
machine-readable surfaces (this is non-negotiable for Article 50(2)):

- The Article 50(1) transparency notice paragraph on each Epilogue
  surface.
- `AIArtefactProvenance.model_name`.
- `dialogue_turns[i].model`.
- PDF document metadata `<meta name="creator">`.
- The AI footer paragraph at the bottom of the PDF.

**Pattern**: friendly framing names the persona ("Aletheia is here to
help you look back"), then the small-print compliance line names the
engine ("This conversation is with an AI system (Google Gemini)…").

**Boundary clarification (C.2, reviewer feedback 2026-05-23).** The two
layers separate by *function*, not by *location*:

- **Aletheia** appears in **narrative copy** and in **system-action
  notifications that sit inside the Epilogue narrative frame**.
  Example narrative: "Aletheia will help you look back". Example
  system action: "Aletheia has saved your Portrait safely" (used in
  the PDF-fallback skip note, §4.5). The teacher is inside the
  Aletheia framing; an action description that names the partner is
  consistent with that frame.
- **Gemini** / **gemini-2.5-flash** appears in **formal Article 50
  disclosure paragraphs** (the always-visible AI Act notice, the
  Portrait PDF's AI footer, the `<meta name="creator">` field) and in
  **machine-readable provenance** (`AIArtefactProvenance.model_name`,
  `dialogue_turns[i].model`, JSON-LD blocks). These are *compliance*
  artefacts, addressed to a different audience (an auditor, a research
  reviewer, a downstream parser) than the teacher inside the
  narrative.

The distinction is *function-based* (narrative vs disclosure) not
*location-based* (in-page vs PDF) — disclosure paragraphs appear in
both the in-page and the PDF surfaces, and they name Gemini in both.

**Error states — passive voice, not named persona (added v2-revised
per second-pass reviewer point 2).** A third category sits between
narrative and disclosure: **system-failure messages**. The natural
phrasing of v1 — "Aletheia could not respond. Please try again." —
is friendly but **persistently teaching the teacher that Aletheia
is an agent that can fail**. Over many sessions this erodes the
Article 50(1) framing (an AI *system* is in use; system failures
are system failures, not the partner's failures) and risks
attributing failure modes to a personified partner.

**Rule.** Error states use the **passive voice**, naming neither
Aletheia nor Gemini:

- ✅ "The reflection could not be generated. Please try again."
- ✅ "The Portrait PDF could not be prepared just now; it will be
  available the next time you request the download."
- ❌ "Aletheia could not respond."
- ❌ "Gemini returned an error."

This treats failure as a property of the *generation event*, not of
the *agent*. It also avoids the contradiction of saying "Aletheia
saved your Portrait safely" (success → named partner, friendly) and
"Aletheia could not respond" (failure → named partner, ominous) in
the same surface.

Applies across all three Epilogue surfaces. The G.3 portrait-skip
notice (§4.5) is revised accordingly: "**The PDF could not be
prepared just now. Your Portrait has been saved safely; the PDF
will be generated when you next request the download.**" (Note:
"has been saved safely" is passive; the prior framing "Aletheia
has saved your Portrait safely" was active-voice attribution to
the persona and is dropped.)

### 3.4 Visual placement of the logo

- **Dialogue avatar** (assistant chat-bubble side): cropped circular
  version of the logo (64×64 on desktop, 48×48 mobile). Replaces the
  current speaker-less chat bubble.
- **Dialogue header card**: small (32×32) avatar + "Aletheia" name
  next to the phase eyebrow + title (§4.2).
- **Stage 0 hero**: a single, large (96px) circular avatar paired
  with the editorial numeral, in the hero block.
- **Portrait page**: small avatar + "By Aletheia" byline above the
  Portrait body.
- **Portrait PDF**: same byline pattern. Logo embedded at ~80×80px in
  the header block (PNG, raster — pisa handles raster fine, no SVG
  issue).

### 3.5 No anthropomorphisation traps

The persona is named and visualised; it is **not** dramatised. The
rules:

- Aletheia does not name itself in the dialogue ("as Aletheia, I…"
  is forbidden — that would surface the persona inside the conversation
  and collapse the §3.3 narrative-vs-disclosure boundary).
- Aletheia does not use first-person emotional voice ("I am moved",
  "I find this powerful", "I am glad to hear").
- Aletheia does not reference being an AI, a model, a system, an
  assistant, or a chatbot within the dialogue — that information
  belongs to the Article 50(1) transparency notice, not to the
  turn-by-turn conversation.
- Aletheia does not have a "personality" beyond the descriptive-non-
  evaluative stance already specified in v2 §6.

**Enforcement** (revised v1→v2 per reviewer feedback, B.3). The G.6
v1 of this document claimed "the prompt already forbids self-
disclosure" — that was **incorrect** when checked against
`apps/agents/epilogue_dialogue.py::_SYSTEM_PROMPT`, which contains
the no-evaluation / no-appraisal rules but **no** rule against
self-naming, first-person emotional voice, or in-dialogue AI self-
reference. Without an explicit prompt rule, the model would happily
write "I am moved by what you said" — the template would say
"Aletheia" while the chat content broke the framing.

The four-line prompt addition that enforces the §3.5 rules is
escalated to **v2 §23 of the master Phase G proposal** (the agent
contracts live there, v2 §7). That commit lands **before G.6a** so
the G.6 design changes inherit a prompt that already enforces the
persona. See v2 §23.2 for the exact prompt text and §23.6 for the
verification approach (live sample-review checks the four guards
hold in generated turns).

The persona is a **frame** the teacher places the conversation
inside; the AI's *behaviour* (descriptive stance, refusal of
evaluation, the four new anti-anthropomorphisation rules) is now
prompt-enforced, not just template-asserted.

---

## 4. Surface-by-surface redesign

### 4.1 Stage 0 — Personal Evolution Dashboard (`stage0.html`)

**Today** (G.1 markup): plain DaisyUI page, H1 "PROODOS Epilogue",
subtitle "**Stage 0** — Your Personal Evolution", a paragraph of intro
text, then `_stage0_panel.html` included verbatim, then action buttons.
The subtitle leaks the Stage 0 label.

**G.6 redesign**:

- **Hero block** (mirrors Tab1 hero, §2.1): aspect-injected wrapper;
  large serif numeral that is **not** "0" (avoids stage numbering) —
  use the Aletheia crystal icon at editorial-numeral scale (~80px)
  instead, paired with an editorial serif title "**Your reflective
  journey**" and the eyebrow "**Look back · Reflective synthesis**".
- **Standfirst** (one paragraph, magazine register): rephrased intro
  text, no "Stage 0", no "M1-M15" — frame as "across your fifteen
  modules" instead.
- **Stage 0 panel** (`_stage0_panel.html`): keep the partial intact;
  give the panel container a `tab1-redesign`-style wrapper so the
  `--aspect-*` variables cascade into the stat-grid, theme blocks,
  timeline, and trajectory cards. The numerical stats keep the
  hero-numeral treatment but with the Aletheia-deep colour.
- **Theme blocks**: three editorial cards with 4pt left-border in
  `--aletheia-main`, eyebrow ("Themes that grew", "Recurring themes",
  "Themes that receded"), badges with rounded outline. Already
  semantically structured; G.6 reskins the CSS.
- **Trajectory timeline**: the current narrative timeline becomes a
  Tab2-style vertical column with serif module-numerals (M2, M3, …)
  on the left, narrative on the right, 4pt left rule per item.
- **RTM trajectory cards**: current badges become aspect-tinted
  panels per tension, with position labels rendered as a left-to-right
  pill strip (visual analog of the 1-5 RTM scale).
- **Action footer**: action buttons re-styled to magazine register
  (no change in copy beyond removing the stage label from the
  "Back to dashboard / Continue without the dialogue / Begin the
  reflective dialogue" trio).

**Label removals**: subtitle line 11; collapse-title in dialogue.html
that references "Stage 0 data".

### 4.2 Dialogue (`dialogue.html`) — phase-as-chapter rewrite

**Today** (G.2 markup): one flat chat-bubble scroll, all turns from
all phases in chronological order, a section-header at top that flips
"Stage 1 — Look Back" → "Stage 2 — Look In" → "Stage 3 — Look Forward"
based on `current_stage`. When phase N+1 is entered, the closing turn
of phase N and the opening turn of phase N+1 appear back-to-back as
two consecutive assistant bubbles — the phase-seam bug (§1.1(b)).

**G.6 redesign** — phases as chapters, not as a label that flips:

- **Page header** (sticky): Aletheia avatar (32×32) + "**Aletheia**"
  byline + a small phase-pill nav (three pills: "Look Back · Look In ·
  Look Forward" — **no** "Stage 1/2/3" labels). The active pill is
  filled with `--aletheia-main`; passed pills are muted; upcoming
  pills are outlined. The pill strip is the only persistent phase
  indicator.
- **Each phase = a chapter card** with its own opening header
  (serif numeral I/II/III, phase title, one-line standfirst describing
  the move). Previous-phase chapters collapse into a closed
  `<details>` with the phase title and the last teacher turn as a
  one-line preview ("Look Back · You said: 'By M10 I felt…'"). The
  teacher can re-open them to read the full prior phase if they want.
- **Within a chapter**: chat-bubble layout for that phase's turns
  only. Assistant bubble carries the Aletheia avatar on the left;
  teacher bubble stays right-aligned (DaisyUI `chat-end`).
- **Phase transition** (advance button): when the teacher clicks
  "Continue to Look In", the current chapter collapses with a 0.28s
  `rfx-screen-out`-style transition; the new chapter card animates
  in with the **`rfx-screen-in`** keyframe (`opacity 0→1` +
  `translateY 10px→0`, the Tab5 Phase F signature, §2.6). The new
  chapter's opening turn is the *first* visible bubble; the prior
  phase's closing turn lives inside the collapsed `<details>` block.
  **The two consecutive assistant bubbles never appear together.**
- **Stage 2 skip-record**: today rendered as `{% if stage2_skip_record %}`
  alert mid-scroll. G.6: a small editorial "skip card" replaces the
  Look-In chapter entirely (greyed-out crystal, italic standfirst
  "Look In was set aside automatically — your reflective record had
  fewer than three distinct tensions and fewer than three shifting
  composites, so there was no juxtaposition to surface. This is a
  reflection of the data, not of your work.") with a button to
  continue to Look Forward.
- **Article 50(1) notice**: relocated to the page footer (still
  always-visible, still names "Google Gemini" for compliance, but no
  longer the first thing the teacher sees — the Aletheia hello is).
- **Stage 0 side panel**: keep the collapsible Stage 0 panel on the
  right side (Q2 / split-attention, v2 §15); rename its label from
  "Your Personal Evolution (Stage 0 data)" to "Your reflective
  evidence" (no stage label leak).

**Label removals**: stage-name header lines 11-19; collapse-title
line 40; stage2 skip notice lines 75-83.

**Identity additions**: Aletheia avatar (assistant bubbles + header);
Aletheia name in the header + chapter standfirsts.

**Greek translation guidance (C.4, added v2).** The phase-pill labels
"Look Back · Look In · Look Forward" need careful Greek translation
when the platform's EL locale is filled in pre-pilot. A literal
"Κοίτα Πίσω / Μέσα / Μπροστά" is awkward; the reviewer's suggestion of
"Παρελθόν / Παρόν / Μέλλον" (Past / Present / Future) reframes the
phases as phenomenological time markers, which **loses Korthagen ALACT's
action-orientation** (the phases are reflective *actions*, not temporal
regions). Recommended Greek: **gerund form** — "Κοιτάζοντας πίσω /
Κοιτάζοντας μέσα / Κοιτάζοντας μπροστά" — preserves the action
register and reads naturally. Final translation decision belongs to
the PI; G.6 only commits to the English pill labels and to the
translation principle (action-preserving, not time-region).

### 4.3 Learning Portrait — in-page (`portrait.html`)

**Today** (G.3 markup): plain prose card with the Portrait text
inside a bordered DaisyUI panel; regenerate / accept buttons below;
collapsible Stage 0 side panel; AI-provenance notice and JSON-LD
block.

**G.6 redesign** — editorial **magazine spread**:

- **Magazine header**: full-width editorial header card (Aletheia
  aspect-injected). Aletheia avatar (48×48) + "**A Learning Portrait,
  by Aletheia**" byline + eyebrow "**For** {{ teacher_display }}" +
  serif title "**Your reflective journey**" + standfirst paragraph
  framing the Portrait as a synthesis the teacher accepts (or
  regenerates).
- **The Portrait body**: serif body text (1.05rem, line-height 1.65),
  optional **drop cap** on the first letter (`:first-letter` pseudo
  — in-page only), left-border accent in `--aletheia-main`, max
  reading-width 38rem (centred). Mirrors a magazine feature opening.
- **Inline AI-provenance row** (already present): kept, restyled
  with eyebrow + small caps treatment.
- **Stage 0 side panel** (collapsible): kept, relabel as in §4.2.
- **Regenerate / accept controls**: aspect-coloured primary CTA
  ("Accept and finish"), ghost regenerate ("Regenerate Aletheia's
  reading"), with a small italic counter ("You may regenerate up to
  N more times").
- **Accepted state**: the buttons collapse, a discreet "**Accepted on
  {{ date }}**" stamp appears in the header, the magazine spread
  loses the "proposed" framing, and the Download PDF + Continue
  buttons (G.3) sit in the footer.
- **Phase-of-the-flow indicator**: the same three-pill strip from
  the dialogue header sits at the top of the page, with **all three
  pills filled** (the teacher has completed all phases) — visual
  closure of the journey.
- **Olive ornament — completion mark** (added v2 per reviewer E.5).
  Beneath the Portrait body and the inline AI-provenance row, a
  small horizontal divider carries the olive-laurel detail extracted
  from the logo's lower-right (rasterised at ~32px, centred). It is
  silent typographic punctuation — the laurel-as-completion symbol
  that ties the Aletheia identity to the project name (PROODOS =
  πρόοδος = progress) and, in the classical register the logo
  already establishes, marks the closing of the reflective journey.
  The crystal stays exclusive to "Aletheia speaks" moments (avatar +
  header byline + PDF cover); the olive marks the teacher's *own*
  completion. Two visual marks, two meanings, one identity.

**Label removals**: any AI-system framing changes to name "Aletheia"
in friendly copy, "Google Gemini" in the compliance line.

### 4.4 Learning Portrait — PDF (`pdf/learning_portrait.html`)

**Today** (G.3 markup): PDF-safe template, header block, portrait
text in a tinted block, full Stage 0 summary in plain HTML, AI
footer + page footer. Plain-corporate aesthetic; readable but bland.

**G.6 redesign** — PDF-safe magazine ("printed magazine cover" register):

- **Cover-style header** (page 1 top): Aletheia logo (raster PNG,
  80×80, embedded via `<img>` — pisa handles raster well), eyebrow
  "**A Learning Portrait, by Aletheia**" in small caps, large serif
  numeral title "**I**", main title "**Your reflective journey**",
  byline "**For** {{ teacher_display }} · {{ accepted_on|date }}".
  Uses the §2.1 typography signature, all PDF-safe (Georgia serif,
  no SVG, no multi-column).
- **The Portrait body**: serif (Georgia 11.5pt), 1.65 line-height,
  4pt left-border in `--aletheia-main`. **Drop cap**: rendered via
  an explicit `<span class="dropcap">` wrapper around the first
  letter of `portrait_text` (server-side string split — pisa cannot
  do `:first-letter`).
- **Stage 0 summary block** (page 2): keep the existing PDF-safe
  layout from G.3, restyled with §2.1/§2.3 typography and left-rule
  signatures. The current `<table class="stat-grid">` becomes a
  serif-numeral row; theme blocks acquire the 4pt aspect-main left
  rule; trajectory cards adopt the 3pt review-rule.
- **AI footer block** (page 2 bottom, above the page-number footer):
  the existing Article 50(1) human-readable paragraph, restyled in
  the editorial register (eyebrow "**AI provenance — EU AI Act
  Article 50**", italic standfirst paragraph).
- **PDF document metadata** (Article 50(2) strict, v2 §22.3):
  unchanged from G.3 — `<meta>` tags continue to write Title /
  Author / Subject / Keywords / Creator into the PDF Info dict.
- **JSON-LD block**: unchanged from G.3 — kept inline at the body
  head, defensive `script { display: none }` rule retained so the
  JSON-LD does not render as visible text.
- **Page footer**: keep the existing "PROODOS · Learning Portrait …
  Page X / Y" footer; restyle with editorial register.
- **Olive ornament — completion mark** (added v2 per reviewer E.5).
  At the end of the Portrait body (above the AI footer block), a
  small horizontal divider with the olive-laurel detail (PNG raster,
  ~28pt, centred — `xhtml2pdf` handles raster PNGs natively; no SVG
  issue, §1.3). Same symbolism as the in-page version (§4.3): the
  laurel marks the closing of the reflective journey, the crystal
  marks Aletheia. The PDF is the keepsake artefact — the olive
  ornament gives the document a graceful end-mark instead of
  trailing off into compliance footnotes.

### 4.5 Portrait skip note (rare path)

If pisa raises during accept (G.3 §10.1 / TD-022 path), the in-page
accepted state shows a small editorial card: "**The PDF could not be
prepared just now. Your Portrait has been saved safely; the PDF
will be generated when you next request the download.**" This is the
existing G.3 fallback, given a polite register. Both sentences use
passive voice per §3.3 (error-state rule, added v2-revised) — failure
is a property of the generation event, not of the named persona.

---

## 5. Label-relabel table (the systematic fix for §1.1(a))

Applied to every teacher-facing string in the three Epilogue surfaces:

| Internal label | Teacher-facing replacement |
|---|---|
| "Stage 0" / "Stage 0 — Your Personal Evolution" | "Your reflective journey" / "Look back · Reflective synthesis" |
| "Stage 1 — Look Back" | "Look Back" (the chapter title) |
| "Stage 2 — Look In" | "Look In" |
| "Stage 3 — Look Forward" | "Look Forward" |
| "Stage 2 (Look In) was skipped" | "Look In was set aside automatically" |
| "RTM tensions" / "Reflective Tension Mapper" | "Professional tensions" |
| "DTP" / "developmental trajectory" | "your trajectory" / "how your reflections moved" |
| "AILST T2" / "the T2 assessment" | "your closing reflection" |
| "M1-M15" | "your fifteen modules" |
| "Stage 0 data" (collapsible label) | "Your reflective evidence" |
| "AI system (Google Gemini)" (everyday) | "Aletheia" (friendly) — Gemini retained in the Article 50(1) line |
| "epilogue_portrait" (artefact kind) | not user-facing; unchanged |

These are **substitutions in template strings only**. The model
field names, JSON keys, log lines, and admin labels stay as-is.

---

## 6. Bibliographic grounding

The G.6 design choices are not aesthetic preferences — each rests on
a defensible principle. Drawn from sources already in the project's
literature note (§15) where possible.

### 6.1 Typography hierarchy and editorial register

**Bringhurst, *The Elements of Typographic Style* (4th ed., 2013).**
The serif-numeral + sans-title + eyebrow pattern is a canonical
magazine opening (Bringhurst §3 on hierarchy of titles), chosen so
the eye reads the section's *position in the whole* before the
section's *title* — a help for reflective re-entry, where the
teacher returns to a Portrait they already accepted.

### 6.2 Phase-as-chapter (§4.2)

**Norman, *The Design of Everyday Things* (2013), chapters 4-5 on
feedback and conceptual models.** A user needs the system to make
**state transitions visible**. The Tab5 wizard pattern (`rfx-screen-
in` keyframe) implements exactly this: the change from one phase to
the next is a visible **event**, not an unannounced label flip. The
v2 §6.1 ALACT mapping is preserved in the data; G.6 makes it
preserved *in the perception*.

**Cognitive Load Theory — Sweller (1988); Chandler & Sweller (1992)**
(already cited in v2 §15 for Q2). Collapsing prior chapters into
`<details>` keeps the relevant phase in working memory while keeping
the prior phases retrievable — split-attention extraneous load is
reduced, not eliminated.

### 6.3 Naming the AI partner

**Reeves & Nass, *The Media Equation* (1996).** Users relate to
computers as social actors; a named partner is talked *to*, an
unnamed system is talked *at*. Naming the chatbot (Aletheia) is
expected to deepen the descriptive-reflective stance the dialogue
agent is already prompted toward — the teacher answers a partner,
not a form field.

**Bryson, "Robots should be slaves" (2010).** A counter-weight: the
named partner must not be dramatised into a peer, an authority, or
a friend, because that misrepresents the relationship and is
manipulative in an educational context. §3.5 codifies the
no-anthropomorphisation rule that follows.

### 6.4 Drop caps and reading openings (§4.3)

**Bringhurst §3.3.** The drop cap is the canonical magazine-feature
opening — it signals "this is a *piece*, not a *page*", which is
exactly what the Learning Portrait is. The PDF-safe `<span class=
"dropcap">` wrapper (§1.3) preserves this signature in both render
paths.

### 6.5 The Aletheia name

**Heidegger, *Sein und Zeit* (1927), §44 on ἀλήθεια as Unverborgenheit
(unconcealment).** The Greek term names truth as a *revealing* —
something the reflective practitioner does, rather than a fact
delivered. The naming is therefore not decorative; it is a
**linguistic claim about what the dialogue is**: an unconcealing,
which only the teacher can perform. The choice is also continuous
with the dissertation's framing of reflection-as-revealing in
Dourvas, Kokkonis & Kontogiannis, *Reconceptualizing Prompt
Engineering as Reflective Professional Practice* (already in the
literature note, v2 §15).

**Bridge source — van Manen (chosen v2-revised after second-pass
reviewer recommendation, 2026-05-23).** A *Sein und Zeit* citation
in a doctoral education thesis is uncommon and would draw committee
questions about the relevance of fundamental ontology to teacher
reflection. A phenomenology-in-education bridge is needed to carry
the argument from Heidegger's unconcealment into the reflective-
practice domain.

**Max van Manen, *Researching Lived Experience: Human Science for an
Action Sensitive Pedagogy* (State University of New York Press, 1990;
2nd ed. Routledge, 2016).** van Manen is the canonical
phenomenologist of teacher education — the standard bridge text
cited in hundreds of doctoral theses on teacher reflection — and
treats lived experience as something the practitioner *does* and
*reveals through writing*, which is exactly the move the Aletheia
naming claims for the Epilogue dialogue. The first-pass reviewer's
suggestion (Gallagher 2018) could not be verified under the
project's no-hallucination citation rule; the second-pass review
proposed van Manen as a more established and easier-to-verify
alternative, and v2-revised adopts it. PI to confirm availability
in the ΔΙ.ΠΑ.Ε. library (almost certain — van Manen 1990 is a
standard holding).

**Bibliographic logic.** **Heidegger §44** anchors the etymology
(why this Greek term, why "unconcealment" rather than "truth");
**van Manen 1990 / 2016** carries the unconcealment claim into
*educational* lived-experience research (why this matters for a
teacher's reflective practice, not only for fundamental ontology);
**Dourvas, Kokkonis & Kontogiannis, RPE paper** then carries it
into the project's own theoretical frame (already cited in v2 §15).

**Defense statement for the committee (anticipating an examiner
question, added per second-pass reviewer point 5).** If asked "why
Heidegger when you already cite Schön for reflection?", the prepared
answer is: **Schön grounds the reflective practice (how reflection
happens, when it happens, what it produces); Heidegger §44 grounds
the choice of name (what reflection is — an unconcealing that only
the practitioner can perform).** The two cite different anchors of
the same argument; van Manen 1990 sits between them and shows the
phenomenology-to-pedagogy bridge has been walked many times in
teacher-education research. Together, the three sources justify
both the structure of the Epilogue (Schön) and its persona naming
(Heidegger via van Manen).

**All G.6 external sources are folded into `Literature_Review_
Synthesis_Note(1).md` §16 in commit G.6e.**

---

## 7. Files

**New:**

- `templates/epilogue/_aletheia_header.html` — shared header partial
  (avatar + name + phase-pill nav). Included by `dialogue.html` and
  `portrait.html`.
- `templates/epilogue/_phase_chapter.html` — partial that renders
  one phase's chapter card (open or collapsed) — used by
  `dialogue.html` (§4.2).
- `templates/pdf/_aletheia_pdf_header.html` — PDF-safe header partial
  with the logo image + editorial typography (§4.4).
- `static/css/epilogue.css` — the G.6 CSS layer, scoped to
  `.epilogue-redesign` wrapper. Contains the §2.1-§2.6 register +
  the Aletheia aspect block + the phase-chapter transitions.
- `apps/modules/templatetags/module_design.py` — small addition:
  the existing template-tag pack grows a synthetic "epilogue" aspect
  entry so the `--aspect-*` injection works in Epilogue templates
  without needing a Module row (§3.2).

**Modified:**

- `templates/epilogue/stage0.html` — applies §4.1 redesign.
- `templates/epilogue/dialogue.html` — applies §4.2 (phase chapters,
  collapsibles, Aletheia header, label removals).
- `templates/epilogue/portrait.html` — applies §4.3.
- `templates/pdf/learning_portrait.html` — applies §4.4.
- `templates/epilogue/_stage0_panel.html` — restyled in §2.1/§2.3
  register but keeps the same data contract.
- `apps/epilogue/views.py` — minimal: drop-cap server-side wrapper
  for the Portrait PDF (§4.4) is added to the PDF context build.

**Assets (no migration):**

- `Aletheia2048Square.png` — copied from repo root into
  `static/images/aletheia/aletheia_logo_2048.png`; `collectstatic`
  picks it up.
- A circular-cropped version (`aletheia_avatar_256.png`) for chat
  avatars, derived once (Python PIL one-liner, committed as a
  built asset; no runtime image processing).

**No database changes. No new migration. No agent change. No view
contract change beyond the §4.4 drop-cap helper. The G.3 test sweep
should pass unmodified except for the label-text assertions.**

---

## 8. Commit plan

| Commit | Content |
|---|---|
| G.6a | The Aletheia aspect (template-tag entry + colour tokens + assets) + `static/css/epilogue.css` with the §2 register CSS only (no template changes yet, no behaviour change). One render-pass smoke test: the existing G.3 templates pull in the CSS file but the markup is unchanged, the test sweep stays green. |
| G.6b | `stage0.html` redesign per §4.1 + `_stage0_panel.html` restyling. Label-removal sweep on this surface only. Updated tests for the new copy. |
| G.6c | `dialogue.html` phase-as-chapter rewrite per §4.2 + new `_aletheia_header.html` + `_phase_chapter.html` partials. The phase-seam bug fix. Live sample-review against `mavros` before the commit closes. |
| G.6d | `portrait.html` magazine spread per §4.3 (in-page) + `pdf/learning_portrait.html` per §4.4 + the drop-cap server helper. Article 50(2) strict regression test re-run (verifies PDF metadata is unchanged). |
| G.6e | Test sweep + literature note §16 (the four new external refs from §6) + roadmap §3 Phase G row marked design-complete + TD-011 closed. |

Each commit lands a single coherent surface; the G.3 functional tests
stay green throughout. The label-relabel sweep (§5) is applied
*within* the surface commit, not as a separate pass — that keeps each
commit self-contained.

---

## 9. Testing

### 9.1 Functional regression

The G.3 test suite (96 epilogue + dialogue + portrait tests) is
expected to **pass unchanged** except for the small set of tests that
assert on user-facing strings ("Stage 2 was skipped automatically"
becomes "Look In was set aside automatically", etc.). These are
counted and updated in each surface commit's CI; the count delta is
recorded in the commit message.

### 9.2 Article 50(2) PDF metadata regression

`PortraitPDFArticle50MetadataTest.test_pdf_carries_document_metadata`
must remain green after §4.4 changes — the PDF Info dict (Title,
Author, Subject, Keywords, Creator) is the **load-bearing compliance
marker** and a magazine-design refactor must not regress it.

### 9.3 Phase-seam fix verification

A new test in `PortraitGenerateAndRenderTest`'s neighbouring class
(or a new `DialoguePhaseChapterTest` class) asserts that the rendered
dialogue HTML never contains two consecutive `<div class="chat
chat-start">` assistant bubbles for *different* `stage` values.
The collapse pattern (`<details>` for prior phases) guarantees this
structurally.

### 9.4 Label-leak guard test (rewritten v2 per reviewer B.1)

A platform-wide regression test
(`apps/epilogue/tests.py::TeacherFacingLabelLeakTest`) renders all
three Epilogue pages and asserts none of the forbidden labels appear
in the **teacher-visible text** of the rendered HTML. The test makes
the §5 rule self-enforcing.

**Critical correction from v1.** The v1 of this proposal specified
the test as "search the rendered HTML for forbidden substrings".
That would have **falsely failed** on legitimate Article 50(2)
compliance content — the C.3 infrastructure ships `epilogue_portrait`,
`gemini-2.5-flash`, and other identifiers inside `<script type=
"application/ld+json">` blocks and `<meta>` tags. The test must scope
itself to teacher-visible text only.

**Correct shape:**

```python
import re
from bs4 import BeautifulSoup
from django.test import TestCase
from django.urls import reverse

class TeacherFacingLabelLeakTest(TestCase):
    """Render every teacher-facing Epilogue page and assert no
    internal research label leaks into the visible text. Compliance
    content (JSON-LD, meta tags, head) is excluded — those are
    machine-readable, not teacher-readable."""

    # Word-boundary patterns — bare "T0/T1/T2" would otherwise
    # match prose like "the T2 closing reflection"; the exact-word
    # form catches the bureaucratic label without false positives.
    FORBIDDEN = [
        r'\bStage\s*[0-3]\b',
        r'\bDTP\b',
        r'\bRTM\b',
        r'\bAILST\b',
        r'\bT[012]\b',
        r'\bTab\s*[125]\b',
    ]

    def _visible_text(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Drop machine-readable content: JSON-LD, scripts, meta,
        # the entire head, and inline style blocks. Article 50(2)
        # markers live in these surfaces and are legitimate.
        for tag in soup(['script', 'style', 'meta', 'head', 'link']):
            tag.decompose()
        return soup.get_text(separator=' ')

    def _assert_no_leaks(self, url_name):
        resp = self.client.get(reverse(url_name))
        self.assertEqual(resp.status_code, 200)
        visible = self._visible_text(resp.content.decode('utf-8'))
        for pattern in self.FORBIDDEN:
            self.assertFalse(
                re.search(pattern, visible),
                f'{url_name} leaks {pattern}: ...{visible[:200]}...',
            )

    def test_stage0_page_no_leaks(self):
        self._stage0_only_fixture()
        self._assert_no_leaks('epilogue:placeholder')

    # Three dialogue fixtures, not one — the label rule must hold
    # at every point in the dialogue, not just at completion
    # (added v2-revised per second-pass reviewer point 4: a leak
    # could surface in the Stage 1 active state and stay invisible
    # to a test that only renders the post-Stage-3 collapsed view).

    def test_dialogue_page_no_leaks_stage1_active(self):
        self._dialogue_fixture(active_stage=1)
        self._assert_no_leaks('epilogue:dialogue')

    def test_dialogue_page_no_leaks_stage2_active(self):
        self._dialogue_fixture(active_stage=2)
        self._assert_no_leaks('epilogue:dialogue')

    def test_dialogue_page_no_leaks_stage3_active_collapsed_prior(self):
        self._dialogue_fixture(active_stage=3, collapse_prior=True)
        self._assert_no_leaks('epilogue:dialogue')

    def test_portrait_page_no_leaks_draft(self):
        self._portrait_fixture(accepted=False)
        self._assert_no_leaks('epilogue:portrait')

    def test_portrait_page_no_leaks_accepted(self):
        self._portrait_fixture(accepted=True)
        self._assert_no_leaks('epilogue:portrait')
```

**Fixture coverage rationale** (added v2-revised per second-pass
reviewer point 4). The dialogue page must be tested in **three
active-stage states**, not just at completion:

- **Stage 1 active.** Only the Look Back chapter is open. A leak
  here would only show in the early dialogue and would be invisible
  to any test that runs after stage transitions.
- **Stage 2 active.** Look Back collapsed; Look In open. The
  juxtaposition opening + stage2-skip path (if triggered) are both
  visible only in this state.
- **Stage 3 active, prior phases collapsed.** The §4.2 collapse
  pattern is exercised. The Stage 2 skip card (if present, §4.2
  end-of-section) is reachable only from this state.

The portrait page also gets two fixtures (draft + accepted) because
the accepted state surfaces the provenance row + olive ornament +
download button — copy that does not appear in the draft state.

Fixture helpers reuse `PortraitViewBase` (G.3b test suite); the new
`_dialogue_fixture(active_stage=N, collapse_prior=bool)` and
`_stage0_only_fixture()` helpers extend it.

**What the test catches vs. what it does not.** Catches: any
teacher-facing string in template copy, button labels, headings,
alerts, modals, tooltips that contain the forbidden words, in any
of the seven user-visible states above. Does **not** catch:
identifiers in `class=` attributes (legitimate CSS hooks like
`class="stage-2-skip-card"`), `data-*` attributes (legitimate JS
hooks), the JSON-LD machine-readable marker (Article 50(2)). This
is the correct scope.

### 9.5 In-page-vs-PDF visual delta

Manual: after G.6d lands, the `mavros` live sample-review walks
end-to-end with the new design (Stage 0 → dialogue → Portrait →
PDF download). Screenshots of each surface land in
`proodos_files/SCREENS_G6_FINAL_20260524.md` (the sample-review
artefact pattern from G.2/G.3).

**Mobile sample-review (added v2 per reviewer E.2).** The
end-to-end review must include a **mobile viewport pass** in
addition to the desktop pass. Specific risk: the §4.2 phase-as-
chapter collapse pattern (`<details>` for prior phases) may not
read well on a narrow viewport — the collapsed phase header could
be lost in vertical scroll, leaving the teacher uncertain whether
prior context is retrievable. Sample-review checks: (a) the
collapsed `<details>` summary is visually distinct enough on a
375px-wide viewport to draw the eye; (b) re-expanding a prior
phase does not break the sticky pill nav; (c) the Aletheia avatar
on each assistant bubble does not crowd the message text at mobile
widths. If any of these fail, G.6c gets a follow-on commit to
adjust before G.6d.

### 9.6 `prefers-reduced-motion` respect

The `rfx-screen-in` keyframe (§4.2) must wrap its transform in
`@media (prefers-reduced-motion: no-preference)` — a teacher with
the OS preference for reduced motion sees an instant transition
(opacity only), not the translate. Tab5 already does this (lines
475-478 of `tab5_reflection.html`); G.6 mirrors the pattern.

### 9.7 PDF render budget guard (revised v2 per reviewer C.5)

The §1.3 render-budget test stays in `proodos_files/` as a one-off
artefact, but the *findings* are encoded as a code-enforced rule —
the test is 10 lines, not out-of-scope as v1 suggested:

```python
from pathlib import Path
from django.conf import settings
from django.test import SimpleTestCase

class PortraitPDFTemplateRenderBudgetTest(SimpleTestCase):
    """Guard against a future commit reintroducing CSS features
    that xhtml2pdf cannot render (measured in G.6 §1.3,
    2026-05-23). The Portrait PDF template must stay PDF-safe."""

    def test_pdf_template_uses_only_pdf_safe_css(self):
        template = Path(settings.BASE_DIR) / 'templates' / 'pdf' / 'learning_portrait.html'
        content = template.read_text(encoding='utf-8')
        forbidden = {
            'column-count':    'multi-column flow (renders single-column)',
            ':first-letter':   'pseudo-element drop cap (not honoured)',
            '<svg':            'inline SVG (not rendered)',
            'linear-gradient': 'gradients (collapse to first colour)',
        }
        for token, why in forbidden.items():
            self.assertNotIn(
                token, content,
                f'PDF template must not use {token!r}: {why} (G.6 §1.3).'
            )
```

Self-enforcement: a future commit adding any of the four broken
CSS features to `learning_portrait.html` fails the test, with the
error message naming the §1.3 finding that justifies the rule. The
in-page Portrait template (`templates/epilogue/portrait.html`) is
**not** scoped — the in-page track may use all four (§1.3 / §4.3).

---

## 10. Trade-offs explicitly accepted

- **`_stage0_panel.html` stays one template, the Portrait splits.**
  The shared partial works in both render paths (it uses none of the
  broken CSS features). The Portrait body, by contrast, uses a drop
  cap and a richer reading-width layout in-page, and a simpler
  serif-on-tinted-block in PDF. The v2 §8.3 single-render ambition
  is preserved where it can be, relaxed where it cannot — and the
  reason is documented (§1.3, §4.3-§4.4).

- **The dialogue prior-phase collapse hides content by default.**
  A teacher who wants to re-read the Look Back chapter while in
  Look Forward must open the `<details>`. This is a defensible
  cognitive-load trade-off (§6.2), but it does mean one extra click.
  The Stage 0 side panel + the prior-stages carry-forward in the
  agent prompt (v2 §6.3) compensate — the relevant evidence stays
  accessible at all times even with the prior phase collapsed.

- **Methodological disclosure for the dissertation dialogue-corpus
  analysis (added v2 per reviewer B.2; refined v2-revised per
  second-pass reviewer point 3).** Until G.6, the dialogue rendered
  as one flat scroll; every teacher saw every prior turn while
  composing a new one. From G.6c onward, prior phases collapse by
  default, so a teacher may compose a Stage 3 (Look Forward) turn
  **without re-reading** their Stage 1 / Stage 2 turns. The
  `dialogue_turns` JSON record (the research artefact) is unchanged
  — every turn from every phase is stored in chronological order —
  but the **conditions of production** differ: pre-G.6c turns were
  produced *seeing* the prior phases, post-G.6c turns may be
  produced *not seeing* them. When the dissertation chapter performs
  qualitative analysis of the dialogue corpus (v2 §13), this
  asymmetry must be disclosed in the methodology: pilot participants
  saw the post-G.6c presentation, so any thematic continuity across
  phases reflects what the teacher *remembered* of prior phases plus
  what the carry-forward summary surfaced — not what was visible
  on-screen during composition.

  **Pre-written disclosure paragraph** (to be lifted verbatim into
  `Literature_Review_Synthesis_Note(1).md` §16 in commit G.6e, and
  reused in the dissertation methodology chapter when written):

  > *From G.6c onward, the dialogue interface collapsed prior phases
  > by default. Qualitative analysis of the dialogue corpus must
  > therefore treat thematic continuity across phases as evidence of
  > teacher memory plus the agent's carry-forward summary, not of
  > co-present text. Coding rules account for this asymmetry: any
  > theme appearing in a later phase that did not appear in the
  > carry-forward must be treated as actively recalled, not visually
  > prompted.*

  This pre-written form saves drafting time later and locks the
  disclosure to the exact mechanism (collapse + carry-forward) the
  G.6 design introduces.

- **Aletheia is named, not voiced.** §3.5 explicitly forbids the
  agent from saying things like "I, Aletheia, think…". The name is
  a frame; the voice is unchanged. A future iteration could explore
  a more developed persona — the G.6 proposal rules it out as
  out-of-scope.

- **The Aletheia palette is locked.** §3.1 fixes six hex anchors.
  Future iterations may revise them, but mid-pilot drift is
  forbidden (the PDFs the teachers download must look consistent
  across the pilot window). A change after the pilot is fine.

---

## 11. Open questions for PI

**Q1-Q5 from v1 are resolved (external reviewer answers accepted
2026-05-23).** Two new items remain open from the v2 review.

### 11.1 Resolved (v1 Q1-Q5)

| Q | Resolution | Reasoning |
|---|---|---|
| **Q1 — Avatar shape** | **Round-cropped** for chat avatars; full square reserved for Stage 0 hero + PDF header where the full composition (crystal + ring + olive + diamond accent) reads. | Chat-bubble UI convention; the crystal + ring read well in a circle, the olive + lower-right diamond are signature elements of the *full* logo. Two crops, two uses, one identity. |
| **Q2 — Phase pill labels** | **"Look Back · Look In · Look Forward"** (imperative). Greek translation: gerund form ("Κοιτάζοντας πίσω / μέσα / μπροστά", see §4.2). | Matches v2 §6.1; shorter; preserves the action-orientation of Korthagen ALACT. Gerund-form Greek preserves the same in EL. |
| **Q3 — PDF cover page** | **Inline header** (no dedicated cover page). | A 300-400 word Portrait does not warrant a full cover page (1/4 of the deliverable would be blank). The Portrait is a keepsake to read, not a magazine issue to flip through. |
| **Q4 — Drop cap colour** | **`--aletheia-main`** (deep teal). | The gem-blue accent (`--aletheia-gem`) is reserved for interactive / highlight elements. The drop cap is a typographic anchor, not interactive. Deep teal also carries higher contrast in print/PDF. |
| **Q5 — Stage 0 hero icon** | **Aletheia crystal** for the hero (visual continuity with the dialogue avatar); olive branch becomes the **completion ornament** on the Portrait (§4.3 + §4.4). | First encounter = full Aletheia treatment; the olive then takes a distinct role as the closing mark of the journey. Two visual marks (crystal = Aletheia; olive = completion), one identity. Ties classical-Greek register tightly to PROODOS (πρόοδος → laurel/olive as completion). |

### 11.2 New, open from v2 review

**O-1 (from B.3 + v2 §23 escalation).** Per the C.3 forward-compat
discipline used elsewhere in the project, the v2 §23 prompt addition
needs PI sign-off as a standalone change (4 lines to
`_SYSTEM_PROMPT`, one new test). It is **not** a G.6 commit — it
lands separately before G.6a. PI to confirm the prompt wording at
v2 §23.2 before that commit runs.

**O-2 (from C.3).** The Heidegger bridge citation is unverified.
PI to confirm the final source — Gallagher 2012 *Phenomenology*
(verified candidate, see §6.5(a)) or Gallagher 2018 *Phenomenology
and Educational Research* (reviewer's suggestion, see §6.5(b),
requires verification against the library catalogue). G.6c cannot
close without the final reference fixed.

---

## 12. Decisions log

**Confirmed (G.6 design session, 2026-05-23):** the three surfaces in
scope (Stage 0, dialogue, Portrait in-page + PDF); full v2-style
proposal depth; Aletheia identity (name + logo); phase-seam fix is a
G.6 deliverable.

**Decided in v1, kept in v2:**

- Two-track render policy (§1.3) — in-page rich, PDF safe.
- Aletheia teal palette anchored at six hex values (§3.1).
- "Aletheia" is the friendly name; "Gemini" stays in compliance copy
  (§3.3, function-based not location-based after C.2 clarification).
- Phase-as-chapter pattern with `rfx-screen-in` transition, prior
  phases collapsed into `<details>` (§4.2).
- Label-relabel table fully specified (§5).
- Commit plan G.6a-e, surface per commit (§8).

**Added in v2 (external reviewer 2026-05-23):**

- Q1-Q5 resolved per §11.1.
- Anti-anthropomorphisation rule enforced **at the agent prompt
  level** via v2 §23 of the master Phase G proposal — closes the
  template-only persona gap (§3.5 + B.3).
- Label-leak guard test scoped to **teacher-visible text only**
  (BeautifulSoup + word-boundary regex) so it does not break on
  legitimate Article 50(2) compliance content (§9.4 + B.1).
- Methodological-disclosure trade-off (§10 + B.2) for the
  dissertation dialogue-corpus analysis chapter.
- Palette derivation method documented for audit trail (§3.1 + C.1).
- Greek translation guidance for the phase-pill labels (§4.2 + C.4).
- Olive ornament as the completion mark on the Portrait, both
  in-page and PDF (§4.3 + §4.4 + E.5) — crystal = Aletheia, olive
  = completion of the journey, classical-register continuity.
- PDF render-budget code-enforced guard test (§9.7 + C.5).
- Mobile sample-review explicitly added to the §9.5 acceptance
  bar (E.2).
- Heidegger reference flagged for bridge-citation verification
  (§6.5 + C.3) — Gallagher 2012 named as the verified candidate
  pending final PI decision.

**Open for PI review:** §11.2 O-1 (the v2 §23 prompt wording) and
O-2 (the Heidegger bridge citation choice).

---

*End of Phase G G.6 design proposal v2.*
