# Phase J — Aletheia Chatbot Re-introduction
## Design Proposal v1 — 2026-05-27

**PI:** John Dourvas, IHU Thessaloniki
**Status:** Draft — awaiting PI review
**Timing decision:** Pre-pilot (alongside Phase K + L)
**Placements selected:** J.1 Always-on Help Bot + J.2 AI Literacy Sandbox

---

## §1. Context and rationale

### §1.1 Why now (not post-pilot)

The original Phase J deferral criterion was: "wait for pilot debrief to see where a chatbot adds value." Two things changed that justify advancing the decision:

1. **Known gap surfaced pre-pilot.** The platform has no mechanism for a teacher who is confused mid-module to get help. The forum is peer-based and asynchronous. Without support, confused teachers either abandon or email the PI. For a ~110-teacher Greek pilot this is manageable but suboptimal — and fixable now at low cost.

2. **RPE framework integration opportunity.** The RPE paper (submitted to *Electronics*) argues that prompt engineering is a form of reflective professional practice. The platform demonstrates this *implicitly* (through the reflection→AI→dispute cycle) but not *explicitly*. A dedicated sandbox where teachers practise prompt engineering with coaching directly operationalises the paper's central thesis and is a novel empirical contribution.

### §1.2 Why NOT the other two candidate placements

| Placement | Reason not selected |
|---|---|
| Onboarding companion | Onboarding is already 4-step + AILST T0. Adding conversational AI increases perceived complexity at the most fragile moment. Phase K landing page redesign addresses first-impression clarity without adding cognitive load. |
| Post-pilot deferred | Selected placements justify pre-pilot implementation. Option 4 ("freeze as historical asset") becomes the fallback *only* if both J.1 and J.2 fail their design checkpoints. |

### §1.3 Preserved infrastructure (from Phase G deprecation)

All assets are in place and require adaptation, not reconstruction:

| Asset | Location | Reuse in Phase J |
|---|---|---|
| Aletheia visual identity | `static/images/aletheia/` + `ALETHEIA_COLOURS` template tag | Both J.1 and J.2 surfaces |
| Multi-turn agent harness | `apps/agents/epilogue_dialogue.py` (DEACTIVATED banner) | Fork into `help_agent.py` (J.1) and `sandbox_agent.py` (J.2) |
| Article 50(1) notice pattern | Dialogue template (deactivated) | Both surfaces — model interaction = transparency obligation |
| Anti-anthropomorphisation rule | `EpilogueDialogueAgent._SYSTEM_PROMPT` §23 block | Carry forward to both agents |
| EU AI Act Article 50(2) wiring | `{% ai_provenance %}` template tag | Applies to sandbox outputs if they are persisted |
| Persona prompt-craft | `_SYSTEM_PROMPT` segments | New register per placement (utility vs coaching) |

---

## §2. J.1 — Always-on Help Bot

### §2.1 Scope

Aletheia as a persistent, utility-shaped assistant accessible on every logged-in page. Answers questions about the platform, modules, AI concepts, and what the AI outputs mean. Does NOT ask for reflections or generate personalised research artefacts.

**In scope:**
- "What does the DTP result mean?"
- "How do I complete TAB5?"
- "What is the RTM trying to show me?"
- "I'm stuck on Module 7, what should I do?"
- "What does 'Deepen level' mean in UNESCO terms?"

**Out of scope:**
- Generating new reflections on behalf of the teacher
- Accessing or summarising the teacher's own data (privacy + measurement-reactivity risk)
- Subject-specific content help beyond what TAB2 already provides

### §2.2 UI placement

Floating chat bubble, fixed bottom-right corner, available on all authenticated pages. On click → expands to a chat panel (sidebar or modal, TBD in Phase K visual pass). Collapsed by default; state remembered per session.

**Alternatives considered and rejected:**
- Navbar menu item → increases nav density already under pressure from H.7 dashboard links
- Dedicated `/help/` page → breaks the "always available" premise
- Inline per-page tooltips → different tool, different feature

### §2.3 Knowledge base strategy

Three tiers of knowledge, no external RAG call:

| Tier | Content | Storage |
|---|---|---|
| **Static FAQ** | 40-60 Q&A pairs about platform navigation, research features, AILST, consent | Structured JSON constant in `apps/agents/help_agent.py` |
| **Module glossary** | Module names, descriptions, TAB purpose per tab | Read from DB on agent init (cached) |
| **Concept library** | Key terms: RTM tension, DTP signal, proficiency level, UNESCO aspect, XAI, HITL | Structured constant |

The agent uses these as context in the system prompt (no embedding/vector lookup). This approach:
- Eliminates a separate RAG ingest for help content
- Keeps cost predictable (one Gemini call per turn, short context)
- Avoids exposing teacher data to the LLM

### §2.4 Conversation model

Session-scoped only. Conversation turns stored in `request.session['help_turns']` (list of `{role, content}` dicts). No DB persistence. Session clears on logout.

**Rationale for no DB persistence:**
- Help conversations are not research data (TD-019 precedent: peer synthesis dispute is a usefulness signal, help conversation is operational support)
- Avoids migration + IRB scope implications
- Consistent with "utility-shaped, not research instrument" classification

**Turn limit:** 20 turns per session. After turn 20, a gentle message: "For more detailed support, please contact [email]." Prevents runaway cost and sets expectations.

### §2.5 Article 50 compliance

Floating chat header includes a persistent one-line disclosure:
> *"This chat is powered by Gemini 2.5 Flash (Google DeepMind). Aletheia is an AI assistant, not a human advisor."*

This satisfies Article 50(1) for the interaction surface. No Article 50(2) machine-readable markers needed (session-only, no persisted AI artefact).

### §2.6 Agent architecture

New file `apps/agents/help_agent.py` — **does not** extend `ResearchInstrumentAgent`. Extends `BaseAIAgent` directly via `generate()` entry point (agent commits each response to session; no HITL needed for utility help).

```python
class HelpAgent(BaseAIAgent):
    _SYSTEM_PROMPT = """
    You are Aletheia, a friendly AI assistant for PROODOS EduAI, a teacher
    professional development platform aligned with the UNESCO AI Competency
    Framework for Teachers.

    Your role: answer questions about the platform, its modules, its AI features,
    and general AI-in-education concepts. Be concise and practical.

    You are NOT a reflective companion — do not ask the teacher to reflect on
    their practice. Do not access or comment on the teacher's personal learning
    data. If asked about a specific teacher's results, redirect to their dashboard.

    [anti-anthropomorphisation block from §23 — carried forward unchanged]

    Knowledge base: [static FAQ + module glossary injected here]
    """
```

### §2.7 Cost estimate

- Average help turn: ~500 input tokens (system prompt + history + question) + ~200 output tokens
- At €0.00015/1K tokens (Flash), ~€0.0001/turn
- 20 turns max × 110 teachers × 2 sessions avg = 4,400 turns → ~€0.44 total
- Well within the €1/user project budget (adds ~€0.004/user)

### §2.8 Commit plan J.1

| Commit | Content |
|---|---|
| **J.1a** | `HelpAgent` class + static knowledge base + session management + cost tracking |
| **J.1b** | `_aletheia_help.html` partial + `help_view` endpoint + `base.html` include + Article 50 notice |
| **J.1c** | Tests (agent unit + view integration) + roadmap update |

---

## §3. J.2 — AI Literacy Sandbox

### §3.1 Conceptual framing

The RPE paper argues that prompt engineering is a form of reflective professional practice with six dimensions: role clarity, context specificity, output specification, iterative refinement, ethical consideration, and transfer. The platform demonstrates this *implicitly* through TAB5 reflection → AI pipeline → HITL dispute. The sandbox makes it *explicit*: teachers engage in structured prompt engineering challenges and receive coaching on how their prompts align with the RPE dimensions.

This is NOT a general "chat with AI" feature. It is a scaffolded skill-building activity where:
1. Teacher is given a teaching scenario
2. Teacher writes a prompt to achieve a specific educational AI use case (e.g. generating a lesson plan, adapting content for a specific student need)
3. Aletheia (a) executes the prompt AND (b) evaluates its RPE quality in a structured coaching panel
4. Teacher iterates — sees how refinements improve the output and the quality score
5. Session ends with a brief self-reflection prompt (one question, not a full TAB5)

### §3.2 Placement in the platform

**Standalone section at `/sandbox/`**, unlocked after completing Module 5 (Acquire level complete). Accessible from the dashboard via a new "AI Literacy Sandbox" card.

**Why after M5:**
- M5 content covers AI co-orchestration and teacher-AI collaboration framing
- By M5, the teacher has already seen RTM/DTP/RAG AI outputs and interacted with HITL
- The sandbox builds on that foundation — it is not an introduction to AI

**Why not a TAB6:**
- Adding a sixth tab to 15 modules breaks the TAB1-TAB5 structure that the dissertation describes as the module architecture
- A standalone section has its own URL, its own gate, its own research variable
- Cleaner for IRB scope management

### §3.3 Challenge structure

Each sandbox session has one scenario drawn from a structured scenario bank. Scenarios are categorised by subject area (the teacher's registered subject). This is the first surface in the platform where the subject personalisation extends beyond RAG retrieval.

**Scenario example (Mathematics teacher):**
> *"You are preparing a differentiated activity for a mixed-ability Year 9 class working on quadratic equations. Use the sandbox to prompt Aletheia to generate the activity."*

**Four challenge types** (one per session, rotating):

| Type | RPE Dimension emphasised | Output target |
|---|---|---|
| **Role clarity** | Specify AI's role explicitly | A teaching resource (lesson plan fragment) |
| **Context specificity** | Give detailed classroom context | An adapted explanation |
| **Output specification** | Define format, length, constraints | A structured assessment rubric |
| **Ethical consideration** | Add fairness/inclusion constraint | An inclusive activity design |

### §3.4 Aletheia's dual response

Each prompt submission returns two panels:

**Panel A — Output panel:**
The actual result of the teacher's prompt (e.g. the generated lesson plan fragment). Standard Article 50 provenance footer.

**Panel B — Coaching panel:**
A structured RPE quality assessment:
```
Your prompt: [quoted]

RPE Quality Assessment:
  Role clarity         ██████░░░░  Moderate
  Context specificity  ████░░░░░░  Low — try adding grade level and prior knowledge
  Output specification ████████░░  Good
  Ethical framing      ██░░░░░░░░  Missing — consider adding an accessibility constraint

One suggestion: [specific rewrite hint, max 2 sentences]
```

The coaching panel uses a deterministic scoring rubric (template-matching logic, not LLM-generated scores) to keep cost low and avoid scoring hallucination. The LLM is called for the Output panel and the "one suggestion" sentence only.

### §3.5 Research dimension

The sandbox adds one new research variable:

**`SandboxSession` model:**
```python
class SandboxSession(models.Model):
    teacher = ForeignKey(TeacherProfile)
    scenario_id = CharField()  # e.g. "math_role_clarity_01"
    turns = JSONField()         # [{prompt, output, rpe_scores, coaching}, ...]
    completed_at = DateTimeField(null=True)
    prompt_quality_progression = JSONField(null=True)  # delta across turns
```

**Research value:**
- Does RPE dimension coverage improve across turns? (within-session learning)
- Does sandbox usage correlate with AILST scores? (construct validity check)
- Which RPE dimension is weakest for Greek K-12 teachers? (finding for the paper)
- Does TAB5 reflection quality correlate with sandbox prompt quality? (triangulation)

**IRB implication (CP-1):** The sandbox introduces a new AI interaction type and a new data collection point. The consent form (`RESEARCH_PARTICIPATION_TEXT`) must explicitly name "sandbox sessions" as covered data before pilot launch. This should be part of the C.5 IRB-driven V2 copy revision.

### §3.6 Article 50 compliance

Both panels carry Article 50 compliance:
- Output panel: standard `{% ai_provenance %}` template tag (same as TAB5)
- Coaching panel: the RPE scores are *deterministic template-matching* (not AI-generated). Only the "one suggestion" sentence is LLM output. The template tag marks only that sentence.
- `AIArtefactProvenance` row written for the output panel content (persisted artefact)

### §3.7 Agent architecture

New file `apps/agents/sandbox_agent.py`:

```python
class SandboxAgent(ServiceAgent):
    """
    Two-call architecture:
    Call 1 (generate): Execute the teacher's prompt → Output panel content
    Call 2 (extract): Generate the "one suggestion" coaching sentence
    RPE scoring: deterministic, no LLM call
    """
```

The deterministic RPE scorer is a standalone utility:
`apps/agents/shared/rpe_scorer.py` — keyword/pattern matching against a rubric dictionary. Returns `{dimension: score_0_to_5}` for each of the 6 dimensions.

### §3.8 Cost estimate

- Scenario output call: ~800 input tokens + ~400 output tokens → ~€0.00018/call
- Coaching suggestion call: ~600 input tokens + ~100 output tokens → ~€0.00011/call
- Per sandbox session (4 turns avg): ~€0.0012
- 110 teachers × 3 sessions avg = 330 sessions → ~€0.40
- Total Phase J AI cost: €0.44 (J.1) + €0.40 (J.2) = **~€0.84**
- Budget headroom: €1.00/user limit — cumulative platform total will need re-verification but is expected to remain within budget given existing actuals are well below €1

### §3.9 Commit plan J.2

| Commit | Content |
|---|---|
| **J.2a** | `SandboxSession` model + migration + scenario bank (JSON, 20 scenarios across 4 types × 5 subjects) |
| **J.2b** | `SandboxAgent` + `rpe_scorer.py` + deterministic scoring rubric |
| **J.2c** | `sandbox.html` template (dual-panel layout) + `/sandbox/` view + M5 unlock gate |
| **J.2d** | Dashboard card + Article 50 compliance + `AIArtefactProvenance` write |
| **J.2e** | Tests (scorer unit + agent unit + view integration) + literature note update + roadmap update |

---

## §4. Sequencing and dependencies

```
Phase K (Landing page redesign)
    ↓  (parallel — no code dependency)
Phase L Tier 1 (AILST + consent translation)
    ↓  (parallel)
Phase J.1 (Help bot)
    ↓  (J.1 must be stable before J.2 to avoid template conflicts)
Phase J.2 (Sandbox)
    ↓
C.5 IRB copy revision (add "sandbox sessions" to consent text)
    ↓
C.6 Pre-pilot operational checklist
    ↓
Pilot recruitment
```

**J.1 before J.2** because:
- J.1 modifies `base.html` (adds the floating chat partial) — all subsequent template work builds on the updated base
- J.1 tests the Aletheia identity at low complexity before J.2 deploys it at high complexity
- J.1 is independently useful even if J.2 is delayed

---

## §5. Check Points (decisions needed before implementation)

| CP | Question | Default if not discussed |
|---|---|---|
| **CP-1** | Sandbox sessions added to `RESEARCH_PARTICIPATION_TEXT` V2? (IRB scope) | YES — must be explicit |
| **CP-2** | `SandboxSession` data included in Art. 15 JSON export (`gather_user_export`)? | YES — it is personal data |
| **CP-3** | Sandbox unlock gate: after M5 completion only, or after M5 + TAB5 reflection submitted? | After M5 TAB5 (teacher has seen AI output before using sandbox) |
| **CP-4** | Help bot available to unauthenticated users (landing page)? | NO — login-only. Landing page has contact email as fallback. |
| **CP-5** | Scenario bank: 20 scenarios sufficient for pilot, or needs more breadth? | 20 across 4 types × 5 subject clusters (Math, Sciences, Humanities, Languages, Other) |
| **CP-6** | Sandbox sessions: one-time per scenario, or repeatable? | Repeatable — learning requires iteration |
| **CP-7** | RPE quality scores shown to researcher (in `/analytics/` dashboard)? | YES — new D.5 section (small, read-only) |

---

## §6. Research value summary

| Contribution | Where it appears in the dissertation |
|---|---|
| Help bot fills operational support gap | Methods §limitations — acknowledges participant support mechanism |
| Sandbox operationalises the RPE paper's six dimensions | Novel empirical instrument — Chapter: "From Implicit to Explicit RPE: The AI Literacy Sandbox" |
| Sandbox × AILST correlation analysis | Results chapter — construct validity triangulation |
| Sandbox × TAB5 quality correlation | Results chapter — "does prompt quality predict reflection depth?" |
| Subject-personalised scenarios | Methods — extends personalisation beyond RAG to skill-building |

---

## §7. Open questions

1. **RPE scoring rubric design.** The deterministic scorer needs a validated rubric. The RPE paper has six dimensions — do their descriptions translate directly to keyword/pattern matching, or do we need a small pilot of manual scoring first?

2. **Scenario bank authorship.** Should scenarios be written by the PI (John) or generated/reviewed collaboratively? They are research content, not AI-generated content — the same "content before code" principle applies.

3. **Coaching panel language.** Greek or English? Given the platform's current English-first stance and the Phase L decision pending, the coaching feedback is probably English for the pilot with Greek as Phase L Tier 2.

4. **D.5 analytics section for sandbox.** Should this be a new section in the `/analytics/` dashboard (researcher-facing), or is the raw `SandboxSession` data sufficient for post-pilot analysis?

---

*Design proposal v1 — 2026-05-27 — awaiting PI review before implementation*
