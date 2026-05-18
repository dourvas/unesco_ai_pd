# PROODOS EduAI — Dissertation Section
## TAB5 Transparency Layer: XAI Architecture, Machine-Readable Provenance, and Human-in-the-Loop Mechanism

**For use in:** System Design chapter / Platform Architecture section
**Version:** 2.1 — Phase E supplement added (14 May 2026). Supersedes v2.0 (Phase C complete, 13 May 2026) and the April 2026 draft. The present version preserves the v2.0 content unchanged below and adds (a) a top-of-file pointer to the companion `PROODOS_Architecture_Chapter_DRAFT_v1.md` (the dissertation chapter that describes the Python agent architecture introduced by Phase E on 14 May 2026), (b) one short paragraph at the end of §1 explaining the relationship between this document and the companion chapter, and (c) one entry in §8.4 referencing the companion chapter as the authoritative description of the agent layer. No substantive content in §§2–7 is changed; the v2.0 description of XAI panels, machine-readable provenance, and the HITL dispute mechanism remains accurate after the Phase E refactor because Phase E was scoped not to touch templates or frontend.
**Author:** John Dourvas (Ioannis Dourvas), doctoral researcher, International Hellenic University (IHU), Department of Information and Electronic Systems Engineering, Thessaloniki. Supervisor: Assistant Professor Georgios Kokkonis.
**Companion documents in the same folder:** `PROODOS_Architecture_Chapter_DRAFT_v1.md` (the Multi-Agent Architecture chapter — Python agent layer, complementary level of abstraction to this document; see §1 closing paragraph below for the relationship), `Onboarding_Implementation_Report.md`, `Onboarding_Technical_Documentation.md`, `Onboarding_Testing_Deployment_Guide.md`, `PROODOS_Landing_Auth_Onboarding_Documentation.md`.

---

## 1. Overview

The reflection layer of PROODOS EduAI (the fifth tab of each of the platform's fifteen content modules; internally referenced as **TAB5**) generates four distinct AI outputs for each teacher: personalised RAG feedback, pedagogical tension mapping (RTM), cross-disciplinary peer synthesis, and developmental trajectory signalling (DTP). Each output is produced by Google's Gemini 2.5 Flash large language model, but each is conditioned on different input data, follows different generative logic, and serves a different pedagogical intent. The four outputs are not interchangeable; each carries a distinct epistemological status and warrants a distinct transparency posture.

A critical design decision, taken at the original implementation of TAB5 in Phase A and reaffirmed during the Phase C compliance arc in May 2026, was to treat transparency not as a single, uniform feature of the platform but as a **context-sensitive, multi-dimensional property** — one that reflects the specific nature of each AI output. This approach, grounded in the conceptual framework of Vultureanu-Albişi and Bădică (2026) on Explainable and Federated Recommender Systems, operationalises what the authors term *System Transparency* and *Data Provenance* within an andragogical context. The architectural commitment is that adult professional learners require disclosure proportionate to the authority claim of the AI output, and that uniform disclosure either over-burdens low-stakes outputs (such as a longitudinal developmental signal) or under-discloses high-stakes outputs (such as research-grounded RAG feedback that quotes or implies external sources).

Alongside the transparency layer, a **Human-in-the-Loop (HITL) feedback mechanism** was implemented on three of the four AI outputs (RAG, RTM, DTP). The mechanism enables teachers to rate and contextualise each AI output, addressing two simultaneous goals: (i) reducing AI anxiety through teacher agency in an authentic co-evaluator role, and (ii) generating an AI Alignment dataset as a secondary research instrument for the dissertation's empirical work. A documented gap — the peer-synthesis output does not yet have a HITL surface because the underlying `AIOutputDispute.FEATURE_CHOICES` enumeration omits `peer` — is recorded as tech debt TD-019 in `proodos_files/TECH_DEBT_LOG.md` and is documented at Section 5.4 of this document.

The Phase C compliance arc (9–13 May 2026; 15 Git commits; 214 tests across five Django applications) added two layers to the transparency posture: (i) a per-artefact "Generated at" timestamp row inside each of the four XAI panels, rendered by a new `{% ai_provenance %}` template tag in `apps.compliance.templatetags.ai_provenance`; and (ii) a machine-readable provenance layer operationalising Article 50(2) of the EU AI Act, comprising per-element HTML data-attributes on every AI rendering container, page-level JSON-LD blocks declaring each artefact as a schema.org/CreativeWork node, and a polymorphic Django model `AIArtefactProvenance` that mirrors every AI-generated artefact in the platform's data layer. The peer-synthesis XAI panel that the April 2026 draft of this section described as "one of four" was, at the time of that draft, actually absent from the codebase; the Phase C arc's C.3 commit 2b added the missing panel for full parity with the RAG, RTM, and DTP outputs.

The present document is the dissertation-grade narrative for the TAB5 transparency layer and HITL mechanism. It is written for citation in the dissertation's System Design chapter and Platform Architecture section. It maintains the theoretical framing of the April 2026 draft (Knowles 1984 on andragogy; Schön 1983 on reflective practice; Mezirow 1991 on transformative learning; Vultureanu-Albişi and Bădică 2026 on explainable recommender systems; Shneiderman 2022 on human-centered AI; UNESCO 2024 on AI competencies for teachers; the EU AI Act 2024) while expanding the architectural description to the Phase-C-complete state and adding a new section on the machine-readable provenance layer.

**Relationship to the Multi-Agent Architecture chapter (companion document, Phase E, 14 May 2026).** The four AI outputs described above (RAG, RTM, DTP, peer synthesis) are produced, as of 14 May 2026, by four named agent classes — `RAGFeedbackAgent`, `RTMAgent`, `DTPAgent`, `PeerSynthesisAgent` — inheriting from a common `BaseAIAgent` and sharing a common infrastructure layer for cost tracking, audit logging, provenance writing, and atomicity enforcement. The Python architecture of those agents, the dual-entry-point distinction (`generate()` for committed artefacts, `extract()` for ephemeral suggestions) that operationalises two distinct HITL stances at the code level, and the seven distinct architectural improvements that the Phase E refactor produced are documented in the companion `PROODOS_Architecture_Chapter_DRAFT_v1.md`. The two documents are intentionally separated by abstraction level: the companion chapter describes *what the system does to produce an AI artefact and to enforce trustworthy-AI invariants by construction*; the present document describes *what the user sees of that artefact and how the user pushes back against it*. The provenance row written by `BaseAIAgent.generate()` (companion §5.1) is the same row whose `generated_at` field is rendered in this document's "Generated at" row (§3.5) and whose model identifier is emitted as a `data-ai-model` attribute (§4.1) and as a `creator.name` slot in the page-level JSON-LD (§4.2). Reviewers seeking the full trustworthy-AI argument should consult both documents; reviewers focused on the user-facing transparency surface and the dispute dataset will find this document self-contained.

---

## 2. Theoretical Grounding

### 2.1 XAI in Andragogy

Adult learners differ from school-age students in three pedagogically consequential ways: they possess established professional identities, they carry prior pedagogical knowledge that the learning environment must engage rather than overwrite, and they exhibit a heightened sensitivity to being evaluated by an external authority (Knowles, 1984). The research literature on adult learning consistently shows that adults require the *why* behind a recommendation before they will accept it. Applying Vultureanu-Albişi and Bădică's (2026) trustworthiness framework, this means that *Transparency* is not merely a technical property of the AI system — it is a prerequisite for pedagogical adoption.

The PROODOS transparency layer operationalises this insight by making the generative process of each AI output visible to the teacher, on demand, without interrupting the reflective experience. This is what Vultureanu-Albişi and Bădică (2026) term **Just-in-Time disclosure**: information is available when the teacher wants it but is not imposed when they do not. The implementation choice is a collapsible `<details>` element directly below or adjacent to each AI output, closed by default, labelled with a magnifying-glass icon and a concise interrogative phrase ("How this feedback was generated", "How these tensions were identified", "How this signal was generated", "How this synthesis was generated"). The closed-by-default posture respects the experienced teacher who does not need the disclosure for every AI output; the available-on-demand posture respects the early-career or AI-anxious teacher who needs it for every one.

The choice of collapsible disclosure rather than persistent inline disclosure also addresses a tension noted in Erhardt et al. (2025): adult professional learners can be overwhelmed by metacognitive scaffolding that is appropriate for novice learners but excessive for the established practitioner. The transparency disclosures in TAB5 are deliberately accessible (one click to expand) but unintrusive (zero visual weight when collapsed).

### 2.2 Human-in-the-Loop as Teacher Agency

The EU AI Act (Regulation 2024/1689) requires that Limited Risk AI systems — the category under which PROODOS is positioned, as documented in the platform's AI Impact Assessment at `/about/ai-act-compliance/` — provide users with meaningful human oversight mechanisms. The HITL dispute system on the three primary AI outputs (RAG, RTM, DTP) directly operationalises this requirement: every AI output is accompanied by a three-option rating (Yes / Partially / Not quite) plus an optional categorised reason and free-text comment, all surfaced inline beneath the AI output and beneath the XAI disclosure panel.

Beyond regulatory compliance, the HITL mechanism reflects a deliberate pedagogical stance. The teacher is positioned as **co-evaluator** of the AI system, not merely its recipient. This positioning is consistent with Critical AI Literacy as articulated by Shneiderman (2022) in *Human-Centered AI*: the capacity to interrogate, contextualise, and challenge AI outputs is itself a competency to be developed, not a property the user either has or does not have. By building a dispute mechanism into the reflection layer, PROODOS trains this capacity implicitly through use, rather than through explicit instruction.

The acknowledgment text rendered to the teacher after a dispute submission — *"Thank you — your feedback has been recorded and will help improve PROODOS. You are a co-designer of this system."* — is not cosmetic. It communicates a genuine epistemological position: the platform is a research artefact in development; the teacher's professional judgment is a legitimate input into its improvement; the platform does not assert epistemic authority over the teacher's reflection on their own practice. This positioning aligns with the participatory design tradition and with the UNESCO AI Competency Framework's (2024) emphasis on teacher agency in AI-integrated environments.

### 2.3 Algorithmic Literacy as a Design Outcome

An unintended but significant consequence of the transparency panels is **Algorithmic Literacy**: teachers come to understand, through repeated engagement with the XAI disclosures, how Retrieval-Augmented Generation works, what semantic similarity means in the context of a curated knowledge base, why a developmental signal is descriptive rather than predictive, and how cross-disciplinary aggregation can surface patterns without identifying any individual peer. This implicit learning is consistent with Aravantinos et al. (2026), who identify metacognitive awareness of AI tools as a critical but underserved component of teacher professional development.

The pedagogical mechanism here is not novel; it parallels the well-established phenomenon in which students of statistics learn the assumptions behind a test by being repeatedly reminded of them in computational contexts. The novelty in PROODOS is that the platform applies this mechanism not to a single AI concept in isolation but to four distinct AI architectures (RAG, attribute extraction in RTM, longitudinal thematic mapping in DTP, cross-disciplinary aggregation in peer synthesis), each disclosed in terms appropriate to its specific generative logic. The teacher who completes the full fifteen-module programme has, by the end, engaged with each transparency panel between fifteen and forty-five times (depending on which AI outputs they revisited in completed-state replays), accumulating a working vocabulary for the four architectures.

### 2.4 Machine-Readable Provenance as a Second Transparency Layer

The April 2026 draft of this section addressed transparency at the **human-readable** layer: collapsible disclosures, contextualised framings, regulatory references rendered in natural language. The Phase C compliance arc in May 2026 added a **machine-readable** layer that complements (and does not replace) the human-readable one.

The theoretical justification for the second layer is found in Article 50(2) of the EU AI Act, which recommends that providers of AI systems mark generated content in a machine-readable format. The recommendation is operational rather than prescriptive — the article specifies neither the format nor the granularity — but the regulatory intent is clear: downstream consumers of AI-generated content (including crawlers, archives, future audit tools, and the data subject's own analytical tools) should be able to identify the AI-generated portions programmatically.

PROODOS operationalises the recommendation in three sub-layers, each described in Section 4 below: per-element HTML data-attributes that mark every AI output container in the rendered page; page-level JSON-LD blocks that declare every AI artefact on a page as a `schema.org/CreativeWork` node; and a polymorphic Django model `AIArtefactProvenance` that stores per-artefact metadata (model identifier, generation timestamp, optional prompt hash) and is mirrored in the GDPR Article 15 data export. The polymorphic model accommodates the heterogeneous primary-key types of the source tables (UUID for the RTM tension rows, BigAutoField for the others, raw integer for the legacy `rag_queries` table outside the Django ORM); a CharField primary-key column stores the source-row identifier as a normalised string, and a unique constraint on `(artefact_kind, artefact_pk)` enables idempotent `get_or_create` semantics.

The machine-readable layer is in service of the same andragogical commitment that motivates the human-readable layer. A teacher who downloads their data export, opens it in a JSON viewer, and sees that every AI output entry carries a `provenance` sub-dict with the model identifier and the generation timestamp has been provided with the same audit-grade information that the privacy regulator might request, in the same format. The teacher's epistemic position — that they are entitled to know what was AI-generated, by which model, at which time — is supported at both layers.

---

## 3. Architecture: Context-Sensitive XAI

The platform implements **four transparency panels**, one per AI output, each disclosing information appropriate to the nature of that output. All four panels are collapsible (DaisyUI `<details>`/`<summary>` elements), closed by default, with a consistent visual signature: a small magnifying-glass icon, a concise interrogative heading at `text-xs` scale, an `auto`-plus-`1fr` two-column grid for the label-value disclosures, a horizontal separator, and a regulatory framing line in muted opacity.

Three of the four panels (RAG, RTM, DTP) existed before the Phase C compliance arc; the fourth (peer synthesis) was added in C.3 commit 2b after a pre-implementation discovery that the peer-synthesis output had no XAI panel in the rendered HTML despite carrying the same regulatory and pedagogical weight as the other three. All four panels were extended in C.3 commit 3 with a per-artefact "Generated at" row rendered by a reusable template tag (Section 3.5).

### 3.1 RAG Feedback Panel

**Nature of output:** Knowledge-grounded personalised feedback, generated by matching the teacher's reflection text against a curated corpus of AI-in-education research and producing a Gemini-mediated response that integrates the retrieved evidence with the teacher's stated context.

**Transparency disclosure (verbatim from `templates/modules/tabs/tab5_reflection.html`):**

  - **Model.** Gemini 2.5 Flash.
  - **Input.** Your reflection text + PROODOS knowledge base (curated research on AI in education).
  - **Logic.** Retrieval-Augmented Generation — your text was matched against the knowledge base to generate relevant, module-specific feedback.
  - **Intent.** Provide feedback grounded in the module's learning objectives, personalised to what you wrote.
  - **Generated at.** Per-artefact timestamp (Phase C C.3 commit 3 addition).
  - **Warning line.** "This feedback responds to your specific reflection — it is not a generic template."
  - **Regulatory line.** "EU AI Act — Limited Risk: No automated decisions are made about you or your teaching."

The RAG panel is rendered in two states by separate fragments of `tab5_reflection.html`. The **live state** (around line 290) is the panel visible while the teacher is composing their reflection and receives an initial RAG response. The **completed state** (around line 743) is the panel visible after the module's reflection tab has been marked complete and the teacher returns to view their own work. Both states carry the same disclosure content; the two render sites exist for layout reasons (the parent containers differ) but the canonical XAI content is identical.

**Design rationale:** The RAG output carries the highest pretension of authority among the four AI outputs because it appears to quote or imply external research and speaks directly to the teacher's professional practice. The teacher reading "the research suggests..." in a RAG response may, in the absence of explicit disclosure, take the framing as authoritative consensus. The transparency disclosure preempts this by making explicit that (i) the source is a finite curated corpus, not the totality of AI-in-education research, and (ii) the generative logic is *matching*, not *synthesis* of the literature in the strong sense that a human reviewer would perform. The disclosure makes explicit that the RAG output is a *starting point for reflection*, not a verdict on the practice the teacher described.

### 3.2 RTM Panel (Reflective Tension Mapper)

**Nature of output:** Identification of implicit pedagogical tensions within the teacher's reflection — contradictions between two valid professional perspectives — surfaced as bipolar scales on which the teacher then positions themselves. Three to five tensions are typically extracted per reflection.

**Transparency disclosure (verbatim from `templates/modules/tabs/tab5_reflection.html` around lines 378–399):**

  - **Model.** Gemini 2.5 Flash.
  - **Input.** Your reflection text only — no external data.
  - **Logic.** The model scanned your text for implicit contradictions between two valid pedagogical perspectives — not errors, but genuine professional complexity.
  - **Intent.** Surface the productive tensions that drive professional growth.
  - **Generated at.** Per-artefact timestamp.
  - **Warning line.** "This is a mirror, not a judgment. Tensions reflect professional complexity — not weakness. **You are always the final judge of their relevance.**"
  - **Regulatory line.** "EU AI Act — Limited Risk: Tension mapping is descriptive, not evaluative."

A second variant of the panel appears in the saved-tensions display section of the page; the regulatory framing is repeated there ("Tension mapping is descriptive, not evaluative. No conclusions are drawn about your professional competence") to ensure that a teacher who returns to a completed module's saved tensions still encounters the non-evaluative framing.

**Design rationale:** The RTM output is the most psychologically sensitive of the four. A teacher who sees their own thinking described as "in tension" may experience the framing as criticism or as professional exposure. The transparency panel reframes this: professional complexity is not a weakness, and the system does not evaluate whether the teacher's position is correct. This framing is consistent with Schön's (1983) reflective practitioner theory, in which tensions between competing professional commitments are the very engine of reflective practice; surfacing them is the goal, not condemning them. The grounding-quote field on each `ReflectionTension` row provides an audit trail: the verbatim excerpt from the teacher's own reflection that the AI used to identify the tension is stored alongside the tension itself, and surfaced in the privacy dashboard's data export. This protects against the failure mode in which the AI invents a tension and the teacher accepts the invention as their own.

### 3.3 DTP Panel (Developmental Trajectory Predictor)

**Nature of output:** A longitudinal, dual-signal output. Redefined in Phase D.3a (see `proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md`), the DTP compares the teacher's current reflection against up to two earlier reflections: the reflection at the same UNESCO competency aspect one proficiency level lower (the Vertical Continuity Signal) and the reflection at the immediately preceding module (the Temporal Shift Signal). For each available signal the panel shows the modules compared and a thematic breakdown (increased, decreased, and stable themes); a single narrative synthesises both. The pilot DTP shows no continuity label — the earlier three-category label (high / moderate / significant) is deferred to a post-pilot calibration, and each signal's raw similarity is stored but not displayed.

**Transparency disclosure (verbatim from `templates/modules/tabs/tab5_reflection.html`):**

  - **Model.** Gemini 2.5 Flash.
  - **Input.** Your current reflection, compared with up to two earlier reflections — one within the same UNESCO competency area, one from your previous module.
  - **Logic.** Two separate comparisons. Each maps which concepts, concerns and language increased, decreased or stayed stable; the model then describes continuity and shift across them.
  - **Intent.** Help you observe how your thinking about AI is evolving across modules.
  - **Generated at.** Per-artefact timestamp.
  - **Warning line.** "This signal describes what changed — it does not evaluate whether the change is positive or negative. Growth is not always linear."
  - **Regulatory line.** "EU AI Act — Limited Risk: Developmental signals are descriptive, not predictive. No conclusions are drawn about your future performance."

**Design rationale:** The redefinition addressed a construct-validity problem in the earlier DTP, which compared the current reflection against the most recent reflection from any other module and so routinely compared reflections on different UNESCO competency aspects — reporting topic difference as developmental change. The Vertical Continuity Signal holds the competency aspect constant; the Temporal Shift Signal is named for what it measures rather than presented as a developmental claim. The decision to show no continuity label during the pilot is itself a transparency commitment: a cosine-similarity threshold has no theoretically universal value, so presenting a graded label before the thresholds are calibrated against data would assert a precision the instrument does not yet have. The explicit non-evaluative framing — retained from the earlier panel and reinforced here — is grounded in Mezirow's (1991) transformative learning theory, in which change in meaning structures is the substantive learning outcome and no particular *direction* of change can be presumed normatively superior: a teacher whose AI-adoption enthusiasm decreases after a module on ethical risks is not regressing, they are reasoning more carefully. The signals describe conceptual continuity and shift, never the quality of the teacher's development.

### 3.4 Peer Synthesis Panel (added in Phase C C.3 commit 2b)

**Nature of output:** Cross-disciplinary synthesis surfacing patterns from how peers in other subject areas addressed similar challenges. The output is aggregated across the cohort and presented in the teacher's own module context, with no individual peer identified.

**Transparency disclosure (added in C.3 commit 2b at `templates/modules/tabs/tab5_reflection.html` around lines 870–890):**

  - **Model.** Gemini 2.5 Flash.
  - **Input.** Your reflection text + anonymised reflections from peer educators in other subject areas.
  - **Logic.** Cross-disciplinary aggregation — the model surfaced patterns from how peers in different contexts addressed similar challenges.
  - **Intent.** Help you see your reflection in dialogue with the wider PROODOS cohort.
  - **Generated at.** Per-artefact timestamp.
  - **Warning line.** "Peer synthesis surfaces patterns across the cohort — it does not single out any individual peer."
  - **Regulatory line.** "EU AI Act — Limited Risk: No evaluation of you or your peers is implied; peer reflections are anonymised before aggregation."

**Design rationale.** The pre-Phase-C state of the codebase rendered peer synthesis output to the teacher (a styled card with cross-disciplinary insights, gradient background, "Cross-Disciplinary" badge) but did not provide an XAI panel. The April 2026 draft of this dissertation section described "four transparency panels, one per AI output" — an aspirational claim at the time of writing, since the peer panel did not yet exist. The Phase C compliance arc identified the gap during pre-implementation verification of `tab5_reflection.html` and added the panel in commit `0d91191` (C.3 commit 2b). The new panel matches the architectural pattern of the RAG, RTM, and DTP panels: same `<details>`/`<summary>` element type, same `text-xs text-base-content/50 hover:text-base-content/70` styling on the summary, same `bg-base-100 border border-base-300 rounded-lg p-4` styling on the body, same `grid grid-cols-[auto_1fr] gap-x-3 gap-y-1.5` for the label-value rows, same horizontal separator, same `text-base-content/60` and `text-base-content/50` opacity classes for the warning and regulatory lines respectively.

The disclosure content is calibrated to the specific epistemological status of peer synthesis. Two distinct concerns are addressed in the framing: (i) **anonymisation** — the explicit note that peer reflections are anonymised before aggregation responds to the legitimate concern of teachers who might otherwise wonder whether their reflections are being shown to identifiable others; (ii) **non-evaluation** — the explicit note that no evaluation of the teacher or their peers is implied responds to the legitimate concern that cross-disciplinary comparison invites implicit ranking. The two framings together position the peer-synthesis output as a window onto the cohort, not as a comparison instrument.

### 3.5 The "Generated at" Row (added in Phase C C.3 commit 3)

Each of the four panels above renders, after Phase C C.3 commit 3, a per-artefact "Generated at" row inside the `grid` of label-value disclosures. The row is rendered by a reusable template tag `{% ai_provenance for=record %}` declared in `apps/compliance/templatetags/ai_provenance.py` and implemented as a Django inclusion tag that includes the partial `templates/compliance/_ai_provenance_row.html`:


```django
{% load i18n %}
{% if provenance %}
<span class="font-semibold text-base-content/60">{% trans "Generated at" %}</span>
<span>{{ provenance.generated_at|date:'d M Y H:i' }}</span>
{% endif %}
```



The tag accepts a `for=<AIArtefactProvenance instance>` keyword (rendered through Django's `**kwargs` to bypass the `for` keyword's lexer conflict with the `{% for %}` block tag). When the provenance is falsy (no AIArtefactProvenance row exists for the artefact), the tag renders nothing — the panel grid simply omits the row. When the provenance is present, the row appears as the fifth label-value pair inside the four-row Model / Input / Logic / Intent grid, before the horizontal separator and the warning and regulatory lines below.

**Design rationale.** The row was added during the Phase C compliance arc to close a gap in the disclosure: the four pre-Phase-C panels disclosed the generative architecture in generic terms (the same Model / Input / Logic / Intent strings render for every artefact of a given kind, regardless of who generated it or when) but did not provide per-artefact metadata. A teacher who asked "when was this specific output generated" had no answer from the rendered HTML. The Phase C C.3 commit 3 addition provides that answer in a single row, with a locale-formatted timestamp.

The implementation discipline is significant. The label is wrapped in `{% trans "Generated at" %}` — a single-word translation unit, not a concatenated phrase — so that a Greek translation catalogue (when added) can render the label appropriately without requiring template surgery. The timestamp value is locale-formatted via Django's `|date:'d M Y H:i'` filter, which respects the active timezone (`settings.TIME_ZONE`). The tag's failure mode is graceful: if a view layer forgets to prefetch the `AIArtefactProvenance` row and the `provenance` attribute is `None`, the tag renders no row and the panel continues to function normally with the four pre-existing rows.

The row is rendered by the same template tag across all four panels and across both states of the RAG panel (live and completed). The C.3 commit 3 refactor that introduced the tag also replaced four inline copies of the "Generated at" rendering (added in C.3 commit 2b) with calls to the tag, eliminating the duplication. The refactor is functionally identical but reduces the markup-maintenance surface from four sites to one.

---

## 4. Machine-Readable Provenance Layer (Phase C C.3)

The transparency disclosures described in Section 3 are oriented toward the human reader: the teacher who clicks the disclosure summary, reads the four-row grid, and forms an interpretive judgment about the AI output. The Phase C C.3 compliance arc added a parallel **machine-readable** layer oriented toward automated consumers: web crawlers indexing the page, archival tools preserving the historical record, third-party AI-content detectors looking for declared provenance, and the data subject's own analytical tools processing their downloaded data export.

The machine-readable layer comprises four sub-components, each described below: per-element HTML data-attributes (Section 4.1), page-level JSON-LD blocks (Section 4.2), the polymorphic provenance storage model (Section 4.3), and the export mirror (Section 4.4).

### 4.1 HTML Data Attributes

Every AI rendering container in `tab5_reflection.html` and `privacy_dashboard.html` carries a set of five `data-ai-*` attributes after C.3 commit 2b. The attribute set is consistent across the seven primary rendering sites on `tab5_reflection.html` (RAG live, RAG completed-state, DTP, peer synthesis card, per-tension RTM card, plus the corresponding container variants) and the four summary cards on `privacy_dashboard.html`. The attribute names and value formats follow a project-internal convention:

| Attribute | Value format | Example | Notes |
|---|---|---|---|
| `data-ai-generated` | Boolean string | `"true"` | Backward-compatible with the partial markers shipped in C.4 commit 2 (boolean-only `data-ai-generated="true"` markers preserved as a subset of the full attribute set). |
| `data-ai-model` | Free-form model identifier | `"gemini-2.5-flash"` | Per-artefact; pulled from `AIArtefactProvenance.model_name`. |
| `data-ai-generated-at` | ISO 8601 with timezone | `"2026-05-12T14:23:00+00:00"` | Machine-parseable. The user-facing locale-formatted variant lives inside the XAI panel grid. |
| `data-ai-artefact-kind` | Enumeration value | `"rag_feedback"`, `"rtm_position"`, ... | One of six choices defined in `AIArtefactProvenance.ARTEFACT_KIND_CHOICES`. |
| `data-ai-artefact-id` | Source-row primary key as string | `"42"` or `"550e8400-e29b-41d4-a716-446655440000"` | Heterogeneous source-table primary-key types accommodated via string serialisation. |

The four summary cards on `privacy_dashboard.html` (RTM positions, DTP narratives, RAG feedback, raw rag_queries log) carry a reduced attribute set: `data-ai-generated`, `data-ai-model`, `data-ai-artefact-kind`, and `data-ai-latest-generated-at`. The `data-ai-artefact-id` is intentionally omitted because the summary cards represent counts across multiple artefacts of the same kind, not single artefacts; surfacing a per-artefact identifier would mislead the consumer about the granularity of the disclosure. Per-artefact identifiers remain available in the data export (Section 4.4).

### 4.2 Page-Level JSON-LD

In addition to the per-element data-attributes, each page that renders AI output emits a single `<script type="application/ld+json">` block declaring every AI artefact on the page as a `schema.org/CreativeWork` node with a `SoftwareApplication` creator. The block is rendered by the `{% ai_provenance_jsonld provenances %}` template tag declared in `apps/compliance/templatetags/ai_provenance.py` (introduced in C.3 commit 3).

The structure of the block (for a page with three AI artefacts):


```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "CreativeWork",
      "identifier": "rag_feedback#42",
      "dateCreated": "2026-05-12T14:23:00+00:00",
      "creator": {
        "@type": "SoftwareApplication",
        "name": "gemini-2.5-flash"
      },
      "isAccessibleForFree": true,
      "about": "AI-generated rag feedback (PROODOS)"
    },
    {
      "@type": "CreativeWork",
      "identifier": "dtp_narrative#42",
      "dateCreated": "2026-05-12T14:23:30+00:00",
      "creator": {
        "@type": "SoftwareApplication",
        "name": "gemini-2.5-flash"
      },
      "isAccessibleForFree": true,
      "about": "AI-generated dtp narrative (PROODOS)"
    },
    {
      "@type": "CreativeWork",
      "identifier": "rtm_position#550e8400-e29b-41d4-a716-446655440000",
      "dateCreated": "2026-05-12T14:24:15+00:00",
      "creator": {
        "@type": "SoftwareApplication",
        "name": "gemini-2.5-flash"
      },
      "isAccessibleForFree": true,
      "about": "AI-generated rtm position (PROODOS)"
    }
  ]
}
</script>
```



The choice of schema.org as the structured-data vocabulary follows the established convention in web publishing: `schema.org/CreativeWork` is the canonical type for any work created by an identifiable agent, and the `creator` slot accepts a nested `SoftwareApplication` for machine-authored content. The `identifier` slot carries a project-internal compound identifier (`<kind>#<pk>`) that allows cross-reference to the source row in the platform's database; the slot's semantic in schema.org is "an identifier for the item that is unique within the scope of the assigning party", which the compound identifier satisfies by construction.

The page-level granularity (one script block per page, listing every AI artefact rendered on that page) is a deliberate choice. The alternative — one script block per artefact, nested inside the artefact's container — would have multiplied the markup and would have made it harder for automated consumers to enumerate the AI artefacts on the page in a single pass. The page-level block is enumerable by a standard `document.querySelector('script[type="application/ld+json"]')` call in the consumer's JavaScript.

The tag's failure mode is consistent with the inclusion tag's: if no provenance rows are passed to the tag (the iterable is empty or null), the tag emits no script block at all. Pages with no AI artefacts therefore do not declare a JSON-LD block in their `<head>` or `<body>` — the absence of the block is itself the (correct) signal.

### 4.3 Provenance Storage Model: `AIArtefactProvenance`

The per-element attributes (Section 4.1) and the page-level JSON-LD (Section 4.2) both read from a single source of truth: the Django-managed `AIArtefactProvenance` model declared in `apps/compliance/models.py` and operationalised in the database by migration `compliance/0005_aiartefactprovenance`. The model is **polymorphic**: it stores per-artefact metadata for five heterogeneous artefact kinds, none of which share a primary-key type or a parent model.

The polymorphism is implemented through three design choices:

  1. **A `(kind, pk)` reference rather than a Django ForeignKey.** The model declares `artefact_kind = CharField(choices=...)` and `artefact_pk = CharField(max_length=64)` rather than a foreign key to a parent table. The choice of `CharField` for the primary-key column is forced by the heterogeneity of the source-table primary-key types: `ReflectionTension` uses `UUIDField` (a 128-bit identifier rendered as `8-4-4-4-12` hex), `UserModuleProgress` and the raw `rag_queries` table use `BigAutoField` (a 64-bit integer). A single-typed integer column could not accommodate both; a generic `CharField` of sufficient length serves both by storing the primary key in its string-serialised form.

  2. **A unique constraint on `(artefact_kind, artefact_pk)`.** The constraint enables idempotent `get_or_create` semantics in the `record_ai_provenance` service helper: calling the helper twice with the same kind and primary key is a silent no-op (it returns the existing row without modification). The idempotency is operationally important because the helper is called both from forward-write hooks at save time (C.3 commit 2a) and from the retroactive backfill management command (C.3 commit 1); the two paths must not collide.

  3. **A nullable `module` foreign key with `on_delete=SET_NULL`.** Most artefacts are scoped to a single module, but raw `rag_queries` rows can carry a NULL `module_id` (the table is raw-SQL infrastructure outside the Django ORM and its FK semantics are not enforced at the schema level). The nullable field accepts both cases without forcing one to fail validation.

The full schema is documented in the companion `Onboarding_Technical_Documentation.md` Section 4.5. The model's six artefact-kind enumeration values are `rtm_position`, `dtp_narrative`, `rag_feedback`, `peer_synthesis`, `rag_query`, and a forward-compatible `epilogue_portrait` reserved for the post-pilot full Epilogue implementation (tech debt TD-011).

### 4.4 Audit Trail and Export Mirror

The provenance storage layer is mirrored in the GDPR Article 15 data export. The export schema (version `'2'` after C.3 commit 2b) attaches a `provenance` sub-dict to every entry of every AI-output kind in the `ai_outputs` top-level key:


```json
{
  "ai_outputs": {
    "rag_feedback": [
      {
        "module_code": "M3",
        "text": "...",
        "provenance": {
          "model_name": "gemini-2.5-flash",
          "generated_at": "2026-05-12T14:23:00+00:00",
          "prompt_hash": null,
          "artefact_kind": "rag_feedback",
          "artefact_id": "42"
        }
      }
    ],
    "dtp_narratives": [ ... ],
    "peer_synthesis": [ ... ],
    "rtm_positions": [ ... ],
    "rag_queries": [ ... ]
  }
}
```



The mirror serves three audiences. **The teacher** can verify, in their own download, that every AI output they received was produced by a documented model at a documented time. **The IRB or regulatory auditor** can reconstruct, from the export, the AI-mediation history of any participant who consents to the audit. **The dissertation researcher** has, in the same export, the per-artefact metadata required for any analysis that controls for model, timestamp, or artefact identity.

The export version bump from `'1'` to `'2'` is the load-bearing signal for downstream parsers. The C.4 commit 2 shipped export version `'1'`, which did not include the `provenance` sub-dict on AI-output entries. Any parser written against version `'1'` will encounter the additional `provenance` key in version `'2'` exports; the parser should treat unknown keys as opaque (the standard JSON-parsing posture) and continue. A pre-existing C.4 regression test `test_json_top_level_keys_match_spec` was updated in C.3 commit 2b to assert the version bump; the update was caught during the full-suite run after commit 2b and corrected within the same commit message's scope (the regression test was a load-bearing reminder of the schema contract).

The audit trail is robust to the GDPR Article 17 erasure flow. When a participant anonymises their account through the privacy dashboard, `AIArtefactProvenance` rows for that participant cascade-delete (the `user` foreign key declares `on_delete=CASCADE`). The cascade is correct: provenance for an erased participant is no longer relevant to anyone — the participant cannot access it, the IRB audit is satisfied by the surviving `ConsentRecord` rows, and the regulatory record of which AI model produced the now-deleted content is no longer required.

---

## 5. Human-in-the-Loop Mechanism

### 5.1 Design

The HITL mechanism appears below each XAI disclosure panel as a three-option rating prompt:

> Was this [feedback / tension mapping / signal] relevant to your context?
>
> 👍 Yes &nbsp;&nbsp; 🤔 Partially &nbsp;&nbsp; 👎 Not quite

A **Yes** rating is saved immediately on click via a fetch-based AJAX call to `apps.modules.views.save_ai_dispute`. The UI feedback is immediate: the rating row is replaced with the acknowledgment text "Thank you — your feedback has been recorded and will help improve PROODOS. You are a co-designer of this system." No additional input is requested.

A **Partially** or **Not quite** rating opens an optional inline form below the rating row. The form contains:

  - A **categorised reason** dropdown with five options: Content Mismatch, Misinterpretation, Too Generic, Pedagogical Disagreement, Other.
  - A **free-text comment** field (max 300 characters), optional.
  - A submit button and a cancel button.

The categorised reasons were chosen during the original implementation in Phase A to balance research utility (categorisation enables quantitative aggregation) against teacher burden (a free-text-only field would impose excessive composition burden for routine ratings). The five categories cover the most pedagogically meaningful disagreement modes and were validated against early-phase pilot testing.

The acknowledgment text after submission is identical to the Yes-rating acknowledgment, with one substantive addition for the Partially and Not-quite cases: the language "your feedback has been recorded and will help improve PROODOS" communicates the platform's commitment to act on the input. This is not a false promise; the dispute corpus is, as documented in Section 5.3, a research instrument for the dissertation and an input to post-pilot iteration of the platform.

### 5.2 Database Model

Disputes are stored in the `modules_aioutputdispute` table, declared in `apps/modules/models.py::AIOutputDispute`. The model's schema:


```
id              → BigAutoField primary key
user_id         → ForeignKey(auth_user, on_delete=CASCADE)
module_id       → ForeignKey(Module, on_delete=CASCADE)
feature_type    → CharField(choices=[('rag', 'RAG Feedback'),
                                     ('rtm', 'Reflective Tension Mapper'),
                                     ('dtp', 'Developmental Trajectory Predictor')])
rating          → CharField(choices=[('yes', 'Yes'),
                                     ('no', 'Not quite'),
                                     ('partial', 'Partially')])
reason          → CharField(max_length=64, nullable)
comment         → CharField(max_length=300, nullable)
created_at      → DateTimeField(auto_now_add=True)
updated_at      → DateTimeField(auto_now=True)
```



A `unique_together` constraint on `(user, module, feature_type)` enforces that each teacher has exactly one dispute row per module per feature type. The constraint is implemented via Django's `update_or_create` semantics in `apps.modules.views.save_ai_dispute`: a teacher who revisits a completed module and revises their assessment overwrites the previous row, with `updated_at` recording the revision time.

### 5.3 The Dispute Dataset as Research Instrument

The dispute dataset constitutes a secondary research instrument for the pilot study. It yields the following measurable outcomes:

| Metric | Operationalisation | Research value |
|---|---|---|
| **AI Alignment Score (overall)** | Percentage of "Yes" ratings across all dispute rows, computed per feature type. | A single aggregate measure of how often the platform's AI outputs land in the teacher's context. Trends across the pilot duration are computable from the per-row `created_at` timestamps. |
| **Module-level alignment** | Percentage of "Yes" ratings within each `(module, feature_type)` pair. | Identifies modules where AI outputs are systematically less accurate. Module M3 with a low RAG alignment score would prompt review of the M3 knowledge-base segments. |
| **Subject-level alignment** | Cross-tabulation of dispute outcomes against `TeacherProfile.subject_area`. | Reveals subject-specific RAG gaps. A subject area where RAG feedback is consistently rated "Partially" or "Not quite" indicates the knowledge base needs subject-specific augmentation. |
| **Reason distribution** | Frequency of the five categorised reasons across the dispute corpus, sliced by feature type and module. | Guides content improvement priorities. A high "Content Mismatch" frequency for a specific module signals corpus coverage issues; a high "Pedagogical Disagreement" frequency signals framing issues. |
| **Qualitative corpus** | Free-text comments, subject to thematic analysis. | Identifies dispute modes not captured by the five categories. Contributes to the dissertation's qualitative chapter. |
| **Alignment–understanding correlation** | Cross-tabulation of dispute outcomes against the TAB4 assessment score. | Tests whether deeper module understanding (TAB4) corresponds to higher AI alignment (the teacher who understands the module's concepts may evaluate AI outputs as more aligned, or may evaluate them more critically — the directionality is an empirical question). |

This dataset addresses a gap identified in multiple sources of the dissertation's literature review (Erhardt et al., 2025; Ba et al., 2025): the absence of longitudinal, teacher-generated evaluation data on AI feedback quality in professional development contexts. Most existing AI-in-education evaluation literature relies on researcher-coded or external-evaluator-coded assessments of AI output quality. The PROODOS dispute dataset is teacher-coded, longitudinal across the fifteen-module programme, and structured (five categorised reasons plus free text). The dissertation's empirical chapter draws on this dataset as a primary source for the research question on AI alignment with teacher context.

### 5.4 Documented Gap: Peer-Synthesis Dispute UX (Tech Debt TD-019)

The `AIOutputDispute.FEATURE_CHOICES` enumeration currently lists three feature types: `rag`, `rtm`, `dtp`. The fourth AI output — peer synthesis — does not have a HITL dispute surface in the rendered HTML, even though the new peer XAI panel (Section 3.4) was added in C.3 commit 2b. The gap is documented in `proodos_files/TECH_DEBT_LOG.md` as TD-019.

The gap is structural rather than incidental. Closing it requires three changes that together exceed the scope of the C.3 compliance arc:

  1. **Schema migration.** Adding `('peer', 'Peer Synthesis')` to `FEATURE_CHOICES` requires a Django `AlterField` migration plus a corresponding update to the database-level CHECK constraint that enforces the enumeration.
  2. **UI extension.** A new `submitDispute('peer', rating)` button row plus the inline reason-and-comment form must be added to the peer synthesis section of `tab5_reflection.html`, mirroring the RAG, RTM, and DTP UX.
  3. **Test coverage.** New test cases in `apps.compliance.tests` and `apps.modules.tests` covering the new feature type's dispute save path and its participation in the `gather_user_export` aggregation.

The estimated effort is approximately 80–100 lines of code plus the migration. The work is deferred to post-pilot Phase G or H because the immediate research-design hazard (the absence of provenance and disclosure for peer synthesis) is closed by the new XAI panel, and the absence of dispute UX is a UX completion gap rather than a regulatory or methodological one. The dissertation's empirical analysis of peer synthesis quality will rely on inferential signals (re-engagement patterns, the qualitative comments on RAG and DTP disputes that incidentally reference peer synthesis) rather than direct dispute ratings during the pilot.

---

## 6. Implementation Verification

The transparency layer and HITL mechanism are verified at three levels: automated tests, manual procedures, and the load-bearing regression suite.

### 6.1 Automated Tests

The full Phase C test suite at the end of the implementation arc contains 214 tests across five Django applications, of which approximately 70 are directly relevant to the transparency layer and HITL mechanism. The most directly relevant test classes:

  - `apps.compliance.tests.AIArtefactProvenanceModelTest` (3 tests) — verifies the storage model's `__str__`, unique constraint, and user-cascade behaviour.
  - `apps.compliance.tests.RecordAIProvenanceHelperTest` (2 tests) — verifies the `get_or_create` idempotency under attempted-overwrite, and acceptance of `module=None` for the `rag_query` kind.
  - `apps.compliance.tests.BackfillAIProvenanceCommandTest` (4 tests) — verifies dry-run no-op, commit creates rows, idempotent rerun, and the fresh-test-DB rag_queries-missing case.
  - `apps.compliance.tests.ExportMirrorProvenanceTest` (3 tests) — verifies `EXPORT_VERSION` bump, CP-5 fresh-user invariant, and provenance sub-dict attachment for all four ORM kinds.
  - `apps.compliance.tests.Tab5ProvenanceHtmlTest` (3 tests) — verifies data-attrs render for all four kinds, the "Generated at" row appears in at least three panels, and the new peer XAI panel renders with correct disclosure copy.
  - `apps.compliance.tests.PrivacyDashboardProvenanceMarkersTest` (2 tests) — verifies kind and model attrs on summary cards, and the D2b-4 invariant that per-artefact id is absent on summary cards.
  - `apps.compliance.tests.AIProvenanceTemplateTagsTest` (7 tests) — verifies `{% ai_provenance %}` renders the Generated-at row, renders nothing when `for=None`, the JSON-LD block parses as valid JSON-LD, the block is empty when no provenances, the block appears once per page on tab5 and on the privacy dashboard, and the label uses `{% trans %}`.
  - `apps.modules.tests.AIProvenanceWriteHookTest` (6 tests) — verifies the five forward-write hooks plus the CP-9 transaction-atomic rollback invariant.

Full suite invocation:


```
PYTHONIOENCODING=utf-8 venv/Scripts/python manage.py test \
  apps.compliance apps.users apps.ailst apps.modules apps.epilogue --noinput
```


Expected result: `Ran 214 tests in XXXs. OK`. Any failure blocks the next commit.

### 6.2 Manual Verification

The companion `Onboarding_Testing_Deployment_Guide.md` Section 6 contains twelve manual test procedures covering the full Phase C surface; Sections 6.4, 6.5, and 6.12 of that guide cover the TAB5 transparency layer specifically. The procedures verify that:

  - Each of the four AI rendering containers on `tab5_reflection.html` carries the full attribute set after the participant has at least one AI output of the relevant kind.
  - Each of the four XAI panels expands on click, surfaces the Model / Input / Logic / Intent rows plus the per-artefact "Generated at" row, and renders the warning and regulatory lines below the horizontal separator.
  - The JSON-LD block at the top of the reflection-tab body parses as valid JSON, has `@context: "https://schema.org"`, contains a `@graph` array of `CreativeWork` nodes, and lists one node per AI artefact on the page.
  - The HITL dispute UX submits via AJAX, the row is replaced by the acknowledgment text, and a `modules_aioutputdispute` row is created or updated in the database.

### 6.3 The Load-Bearing CP-9 Invariant Test

A single test in `apps.modules.tests.AIProvenanceWriteHookTest.test_cp9_rollback_when_provenance_raises_during_rtm_save` carries an architectural-level invariant: every AI-artefact save site MUST wrap the source-row save and the matching `record_ai_provenance` call in a single `transaction.atomic` block, so that a provenance write failure rolls back the source-row save. The test monkey-patches `record_ai_provenance` to raise `RuntimeError` during a `save_tensions` POST and asserts that no `ReflectionTension` row was committed and no `AIArtefactProvenance` row was created.

The invariant prevents a specific failure mode: an AI artefact being committed to the database without a matching provenance row. If the invariant were not enforced, a transient provenance-write failure (network blip, DB lock, etc.) would produce an AI artefact whose model and timestamp are not recorded — a regulatory gap that the Article 50(2) machine-readable layer would then mis-represent. The test is verified on every full-suite run and is identified in the testing guide as one of three load-bearing tests for the platform's IRB and regulatory defensibility.

---

## 7. Dissertation Positioning

### 7.1 Contribution to Research Questions

The transparency layer and HITL mechanism contribute directly to the dissertation's primary research question:

> *"Can AI-powered systems enable scalable, personalised teacher professional development that was previously impossible to implement manually?"*

The answer is strengthened by demonstrating that the system is not merely *functional* but *trustworthy* — transparent about its processes at both the human-readable and the machine-readable layers, respectful of teacher agency through the co-evaluator stance of the HITL mechanism, and designed to improve through teacher feedback collected as an auditable research dataset. This positions PROODOS beyond a proof-of-concept and toward a **responsible AI system** in the sense articulated by UNESCO (2024) and the EU AI Act (Regulation 2024/1689). The Phase C compliance arc's addition of the machine-readable provenance layer extends the responsibility claim from the human-facing interface to the technical-record layer: any future audit of the platform's AI-mediation history can reconstruct, from the database and the structured-data markup, which artefact was produced by which model at which time.

### 7.2 Comparative Positioning

The dissertation's literature review identifies a small number of AI-in-education platforms that have made comparable transparency commitments, but none, to the author's knowledge, that operationalise the dual-layer (human-readable XAI panels plus machine-readable schema.org JSON-LD) approach taken in PROODOS. The closest precedents in the platform-level AI-explainability literature are domain-specific tools for content recommendation (Vultureanu-Albişi and Bădică, 2026) and clinical decision-support systems (operating under regulatory frameworks that mandate per-output disclosure but rarely extend to structured-data markup). The contribution PROODOS makes to the AI-in-education-platform literature is the demonstration that a research-grade compliance posture across both layers is achievable in a fifteen-module curriculum without compromising the participant-facing learning experience.

The Phase C compliance arc's commitment to deferred decision-making — every architectural decision (D1 through D12 in the C.3 design proposal) was recorded with rationale, every Challenge Point (CP-1 through CP-10) was applied as a pre-implementation correction with documentation, and every tech debt item was explicitly opened in the TD register rather than left as an undocumented implementation gap — also serves as a methodological contribution. The dissertation's chapter on platform development can cite the project's session logs and design proposals as a model of transparent technical decision-making in research-instrument development.

### 7.3 Proposed Dissertation Text (System Design Chapter)

The following passage is suggested for direct incorporation into the System Design chapter of the dissertation, with footnote references to the regulatory texts and the literature.

> The platform implements a two-layer transparency architecture across its reflection layer. The first, human-readable layer comprises context-sensitive disclosure panels for each of the four AI outputs — RAG feedback, Reflective Tension Mapper, Developmental Trajectory Predictor, and peer synthesis — rendered as collapsible accordion elements with consistent label-value disclosures for model, input, logic, intent, and generation timestamp. Each panel surfaces a regulatory framing line (the EU AI Act's Limited Risk classification with output-specific qualifiers) and a pedagogical warning line that prevents evaluative misreading. Rather than applying a uniform transparency template, the system provides disclosure proportionate to the epistemological status of each output: source attribution and corpus grounding for the knowledge-grounded RAG feedback; methodological framing and non-evaluative positioning for the psychologically sensitive tension mapping; epistemological clarification of descriptive-versus-predictive for the longitudinal developmental signal; and cohort-anonymisation framing for the cross-disciplinary peer synthesis. This approach operationalises what Vultureanu-Albişi and Bădică (2026) term System Transparency and Data Provenance within an andragogical context, where adult learners require the *why* behind a recommendation before they will accept it (Knowles, 1984).
>
> The second, machine-readable layer (introduced in the platform's May 2026 compliance arc) operationalises Article 50(2) of the EU AI Act through per-element HTML data-attributes on every AI rendering container, page-level JSON-LD blocks declaring each artefact as a schema.org/CreativeWork node with a SoftwareApplication creator, and a polymorphic Django model that stores per-artefact provenance metadata and is mirrored in the participant's GDPR Article 15 data export. The dual-layer architecture ensures that the platform's AI-mediation history is reconstructable both by the participant in the moment of interaction and by any automated consumer at any later time.
>
> Complementing the transparency layer, a Human-in-the-Loop dispute mechanism enables teachers to rate and contextualise each AI output, with a three-option rating, an optional categorised reason, and an optional free-text comment, stored as research data in a dedicated relational table. This operationalises the EU AI Act's meaningful human oversight requirement for Limited Risk AI systems (Regulation 2024/1689) while simultaneously generating an AI Alignment dataset as a secondary research instrument for the dissertation's empirical work. The corpus of dispute submissions is analysed across feature types, modules, subject areas, and reason categories, addressing a gap identified in the literature review (Erhardt et al., 2025; Ba et al., 2025) regarding the absence of longitudinal, teacher-coded evaluation data on AI feedback quality in professional development contexts. Critically, the mechanism positions the teacher as a co-designer of the system — a stance consistent with participatory design principles and with the UNESCO AI Competency Framework's (2024) emphasis on teacher agency in AI-integrated environments. The acknowledgment text rendered after each dispute submission ("Thank you — your feedback has been recorded and will help improve PROODOS. You are a co-designer of this system.") is not cosmetic but communicates an epistemological position: the platform does not assert authority over the teacher's reflection on their own practice.

### 7.4 Sequel Research Directions

The transparency-and-HITL architecture surfaces several research directions for post-pilot work:

  - **Trust calibration over time.** The longitudinal dispute dataset enables analysis of whether teachers' AI alignment ratings change systematically across the fifteen-module programme. A trajectory toward higher "Partially" or "Not quite" ratings would indicate that teachers' critical AI literacy is increasing; a trajectory toward higher "Yes" ratings could indicate either improved AI quality or habituation. The two are distinguishable by the free-text comments and the reason distribution.
  - **Module-specific AI alignment.** A module-by-module breakdown of dispute outcomes identifies content gaps. The dissertation chapter on the curriculum can use this analysis to inform post-pilot iteration of the knowledge base.
  - **The peer-synthesis dispute UX (TD-019).** Closing the documented HITL gap for peer synthesis (Section 5.4) would extend the alignment dataset to a fourth AI surface, enabling a fuller cross-feature analysis.
  - **The "Generated at" timestamp as a research variable.** The per-artefact timestamp introduced in C.3 commit 3 enables analysis of whether AI output quality varies with the time of day, the day of the week, or the participant's session position within the programme. The post-hoc framing required by the Career Stage decision (TD-020) is also operative here: timestamps are descriptive variables in a post-hoc analysis, not treatment factors in the platform.

---

## 8. References

### 8.1 Literature

  - Aravantinos, S., Lavidas, K., Komis, V., Karalis, T., & Papadakis, S. (2026). Artificial intelligence in K-12 education: A systematic review of teachers' professional development needs for AI integration. *Computers, 15*(1), 49.
  - Ba, S., et al. (2025). *Unraveling the mechanisms and effectiveness of AI-assisted feedback in education: A systematic literature review.*
  - Erhardt, N., Richter, E., Huang, Y., Scheiter, K., & Richter, D. (2025). *Artificial intelligence in teacher professional development: A systematic review* [Preprint]. University of Potsdam.
  - Knowles, M. S. (1984). *Andragogy in action: Applying modern principles of adult education.* Jossey-Bass.
  - Mezirow, J. (1991). *Transformative dimensions of adult learning.* Jossey-Bass.
  - Ning, Y., Wang, H., Zhao, B., & Yang, Q. (2025). *Artificial Intelligence Literacy Scale for Teachers (AILST).* The instrument seeded verbatim in the platform's M4 migration.
  - Schön, D. A. (1983). *The reflective practitioner: How professionals think in action.* Basic Books.
  - Shneiderman, B. (2022). *Human-centered AI.* Oxford University Press.
  - Vultureanu-Albişi, A., & Bădică, C. (2026). Explainable and federated recommender systems. *Electronics, 15*(6), 1292. https://doi.org/10.3390/electronics15061292

### 8.2 Regulatory References

  - Regulation (EU) 2024/1689 of the European Parliament and of the Council (the European Union Artificial Intelligence Act), in particular Article 5 (Prohibited practices), Article 50 paragraphs 1 and 2 (Transparency obligations for AI systems interacting with natural persons and for AI-generated synthetic content), and Annex III (High-Risk categories).
  - Regulation (EU) 2016/679 (the General Data Protection Regulation, GDPR), in particular Articles 6(1)(a), 7(3), 9(2)(j), 15, 17, 21, and 89(1).
  - Greek Law 4624/2019 — the national implementation of GDPR provisions in Greek law.

### 8.3 Framework References

  - UNESCO. (2024). *AI competency framework for teachers.* UNESCO. The pedagogical reference framework for the fifteen-module curriculum.
  - schema.org. *CreativeWork* and *SoftwareApplication* types. https://schema.org/CreativeWork. The structured-data vocabulary used for the JSON-LD layer.

### 8.4 Project Documentation (Phase C arc)

  - `PROODOS_Architecture_Chapter_DRAFT_v1.md` — **(Phase E, 14 May 2026)** the companion dissertation chapter describing the Python multi-agent architecture that produces the four AI outputs disclosed in this document. The two documents are co-citable in the dissertation's System Design chapter: the present document covers the user-facing transparency surface and the dispute dataset; the companion chapter covers the agent layer that enforces trustworthy-AI invariants by construction. See the relationship paragraph at the end of §1 of the present document. The companion chapter's source code references include the four agent classes (`apps/agents/rag_feedback.py`, `apps/agents/rtm.py`, `apps/agents/dtp.py`, `apps/agents/peer.py`) that produce the artefacts whose `AIArtefactProvenance` rows this document describes.
  - `PROODOS_UNIFIED_ROADMAP.md` — the programme-level reference with a bird's-eye snapshot at the top, updated at each session end. Section 3.C.3 documents the C.3 compliance arc; Section 3.E documents the Phase E refactor retrospective; the snapshot block documents the Phase C and Phase E 100% completion states.
  - `proodos_files/C3_DESIGN_PROPOSAL_AI_MARKERS.md` — the C.3 design proposal with twelve design decisions (D1 through D12) and ten Challenge Point corrections (CP-1 through CP-10), including the mid-arc Option C revision that closed the peer-synthesis XAI panel gap.
  - `proodos_files/PHASE_E_DESIGN_PROPOSAL_v11.md` — **(Phase E, 14 May 2026)** the canonical FINAL document for the Phase E multi-agent refactor (engineering record, eleven design-iteration rounds, eleven commits, seven distinct architectural improvements). Read together with `PROODOS_Architecture_Chapter_DRAFT_v1.md`: the latter is the dissertation chapter narrative, the former is the engineering record.
  - `proodos_files/audit_rag_queries_provenance_20260512.md` — the empirical pre-flight audit that validated the single-constant `gemini-2.5-flash` backfill strategy for the C.3 arc.
  - `proodos_files/SESSION_LOG_PHASE_C_C3_20260512.md` — the session log for the four-commit C.3 arc (storage layer, forward-write hooks, export mirror plus HTML markers, template tags plus JSON-LD plus close-out).
  - `proodos_files/TECH_DEBT_LOG.md` — the tech debt register, including TD-017 (closed in the C.3 arc), TD-018 (per-artefact dispute deep-links, deferred post-pilot), TD-019 (peer dispute UX, the gap documented in Section 5.4 of this document), and TD-020 (post-hoc career-stage exploratory analysis, the post-pilot research direction).
  - `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` — the original April 2026 compliance plan that scoped the Phase C arc.

### 8.5 Source Code References

  - `apps/compliance/models.py::AIArtefactProvenance` — the polymorphic provenance storage model.
  - `apps/compliance/services.py::record_ai_provenance` — the write helper with CP-9 transaction-atomic contract.
  - `apps/compliance/services.py::gather_user_export` — the GDPR Article 15 export aggregator that mirrors the provenance layer.
  - `apps/compliance/templatetags/ai_provenance.py` — the two template tags (`{% ai_provenance %}` and `{% ai_provenance_jsonld %}`) introduced in C.3 commit 3.
  - `apps/compliance/management/commands/backfill_ai_provenance.py` — the retroactive backfill command for pre-Phase-C artefacts.
  - `apps/agents/base.py::BaseAIAgent` — **(Phase E, 14 May 2026)** the abstract base class whose `generate()` method is the producer-side counterpart to the present document's consumer-side surface. Calls `record_ai_provenance` inside its transaction-atomic flow.
  - `apps/agents/rag_feedback.py`, `apps/agents/rtm.py`, `apps/agents/dtp.py`, `apps/agents/peer.py` — **(Phase E)** the four concrete agents producing the four AI outputs whose XAI panels are described in §3 of the present document.
  - `apps/modules/models.py::AIOutputDispute` — the HITL dispute storage model.
  - `apps/modules/views.py::save_ai_dispute` — the HITL dispute save endpoint.
  - `templates/modules/tabs/tab5_reflection.html` — the reflection tab template with all four XAI panels and the HITL UX.
  - `templates/compliance/_ai_provenance_row.html` — the partial template included by the `{% ai_provenance %}` inclusion tag.
  - `templates/compliance/privacy_dashboard.html` — the privacy dashboard with the four upgraded summary cards and the page-level JSON-LD block.

### 8.6 Related Earlier Documentation

The April 2026 draft of this section (the predecessor to the present document) referenced `OPTIMIZATION_PATCH_APR2026.md` Αλλαγή 6 and `XFRS_Technical_Improvement_Ideas.md` as upstream documents. Those references remain valid as historical context; the canonical specification of the current architecture is in the four companion documents in this folder plus the Phase C project documentation enumerated above.

---

## 9. Document Maintenance

This document is the authoritative dissertation-grade specification of the TAB5 transparency layer, machine-readable provenance layer, and Human-in-the-Loop mechanism as of 14 May 2026. Version 2.0 (13 May 2026) recorded the Phase C compliance arc; version 2.1 (14 May 2026) added the cross-reference to the Phase E multi-agent architecture documentation without changing the substantive description of the transparency and HITL surfaces (Phase E was scoped to leave templates and frontend untouched). The document supersedes the April 2026 draft, which described the platform's transparency posture before the Phase C compliance arc and which framed the peer-synthesis XAI panel as one of four panels in advance of its actual implementation.

The document is intended for direct citation in the dissertation's System Design chapter and Platform Architecture section. The proposed dissertation text in Section 7.3 may be incorporated verbatim, with footnote references resolved against the formal reference list in Section 8. The companion `PROODOS_Architecture_Chapter_DRAFT_v1.md` should be cited alongside the present document when the dissertation's argument concerns trustworthy-AI invariants at the architectural level rather than the transparency-surface level.

Future amendments should follow the project convention of appending dated sections rather than overwriting prior content. Material changes to the platform's transparency posture should propagate first to `PROODOS_UNIFIED_ROADMAP.md` (the bird's-eye snapshot at the top of that file) and then to this document.

The companion documents in this folder are co-versioned with this file. The five companion documents are: `PROODOS_Architecture_Chapter_DRAFT_v1.md` (the Multi-Agent Architecture chapter — Phase E); `Onboarding_Implementation_Report.md` (what was built, when, with which commits and tests); `Onboarding_Technical_Documentation.md` (architecture, schema, services, middleware, template tags, commands; developer-facing); `Onboarding_Testing_Deployment_Guide.md` (automated tests, manual procedures, pre-production sequence, backup and recovery); and `PROODOS_Landing_Auth_Onboarding_Documentation.md` (the comprehensive dissertation-grade narrative covering landing, authentication, onboarding, AILST integration, Epilogue, EU AI Act compliance, and GDPR compliance).

The single point of programme-level reference remains the snapshot block in the unified roadmap. The present document is the dissertation-citable narrative for the TAB5 layer specifically; the roadmap is the working-state index for the full platform.

---

*Document created: 13 May 2026 (Phase C complete).*
*Phase E supplement: 14 May 2026 (cross-references to `PROODOS_Architecture_Chapter_DRAFT_v1.md` added at top, end of §1, §8.4, §8.5, §9; no substantive content changed in §§2–7).*
*Predecessor: April 2026 draft — preserved in Git history; superseded by the present version.*
*Status: Ready for integration into the System Design chapter of the doctoral dissertation.*
