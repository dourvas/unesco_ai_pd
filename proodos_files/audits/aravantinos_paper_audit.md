# Aravantinos et al. 2026 — Paper-Level Audit

**Reviewer:** Claude Code (Opus 4.7, 1M context)
**Date:** 4 May 2026
**Scope:** Independent paper-level audit before drafting any reinforcement wording for CG4.2.2 closure.
**Source:** Full PDF read locally at `C:\Users\dourv\Desktop\ΔΙΔΑΚΤΟΡΙΚΗ ΔΙΑΤΡΙΒΗ\ΕΡΓΑΣΙΕΣ\ΤΕΛΙΚΟ ΣΥΣΤΗΜΑ ΕΠΙΜΟΡΦΩΣΗΣ\ΒΙΒΛΙΟΓΡΑΦΙΑ\Artificial_Intelligence_in_K-12_Education_A_System.pdf`. Also cross-checked against Crossref + OpenAlex metadata.

**Lesson from A1 v1 baked in:** I pulled verbatim quotes from the paper (not paraphrases) for all citable claims. Each claim is anchored to a page line in the local extracted text (`/tmp/aravantinos.txt`).

---

## Bibliographic details (verified)

> **Aravantinos, S., Lavidas, K., Komis, V., Karalis, T., & Papadakis, S. (2026). Artificial intelligence in K-12 education: A systematic review of teachers' professional development needs for AI integration. *Computers, 15*(1), 49. https://doi.org/10.3390/computers15010049**

- **5 Greek authors** (4 from University of Patras + 1 from University of Crete; corresponding: Stamatios Papadakis)
- **Journal:** *Computers* (MDPI), Vol. 15, Issue 1, Article 49
- **Submission timeline:** Received 27 December 2025 · Revised 6 January 2026 · Accepted 8 January 2026 · Published 12 January 2026
- **License:** CC-BY (Creative Commons Attribution) — open access ✅
- **Funding:** No external funding (paper notes "MEDICUS" programme acknowledgments)
- **Citation count (March 2026, OpenAlex):** 3 citations

Crossref / OpenAlex / paper title page all agree on the bibliographic record.

> ⚠️ Note on author list: Crossref's record had a discrepancy (one search result mentioned "Voulgari" as a co-author). The actual paper's title page lists exactly **Aravantinos, Lavidas, Komis, Karalis, Papadakis** — 5 authors, no Voulgari. The matrix bibliography in M9 already has the correct author list.

---

## Existence verification

- ✅ DOI resolves to `https://www.mdpi.com/2073-431X/15/1/49`
- ✅ Crossref API returns full metadata
- ✅ OpenAlex API returns full metadata + abstract
- ✅ Open access PDF available at `https://www.mdpi.com/2073-431X/15/1/49/pdf?version=1768216103` (CC-BY)
- ✅ Local copy in dissertation library (read in full)
- ✅ DOAJ-indexed (open access journal)
- 1 academia.edu mirror exists

Paper exists and is genuine. No retraction, no errata.

---

## Paper findings

### Research question / objective

(p2 line 187) "the objective of this study is to systematically review empirical studies to identify the **training needs and practices of primary and secondary education teachers** for efficient AI integration and overall PD."

The paper is **explicitly a teacher-PD-needs review**, not a student-impact study.

### Method

- **Type:** Qualitative thematic synthesis (NOT meta-analysis or effectiveness study). Authors explicitly: "This review adopts a qualitative thematic synthesis rather than an effectiveness-focused meta-analysis."
- **Reporting standard:** PRISMA
- **Databases:** Scopus + Web of Science
- **Search date:** February 2025
- **Inclusion timeframe:** literature up to end of December 2024 (a few Jan 2025 articles included if already online December 2024)
- **PRISMA flow:** 240 papers → 74 duplicates removed → 26 excluded by title → 22 by abstract → 10 reviews removed → 108 papers screened → 2 unavailable + 4 not retrieved + 1 retracted → 101 eligible → 11 wrong educational level + 27 different focus + 19 wrong participants + 1 incomplete → **43 final included articles**
- **Analysis:** Reflexive thematic analysis with 2 researchers, inter-rater reliability 85% (Cohen's κ ≈ 0.8), divergences resolved by 3rd researcher.

### Sample distribution of the 43 included studies

- **Publication years:** 2025 (n=6), 2024 (n=31), 2023 (n=3), 2022 (n=2), 2021 (n=1) — heavily 2024-skewed
- **Geographic distribution:**
  - China (n=9), USA (n=6), Turkey (n=5), South Korea (n=3), Indonesia/Philippines/Vietnam/Saudi Arabia (n=2 each)
  - Single studies: Brazil, Cyprus, Estonia, Hong Kong, Iran, Israel, Japan, Kazakhstan, Kenya, Nepal, Nigeria, Norway, Russia, Sweden, Taiwan, Ukraine
  - **By continent:** Asia 32, Europe 7, North America 7, Africa 2, Oceania 1, South America 1
- **School levels:** primary + secondary K-12 (mixed-participant studies included only when results categorised separately)
- **Greek-context studies:** **0** (no Greek studies in the 43-study corpus, despite the authors being Greek)

### Headline findings — verbatim claims

**Claim 1 (Abstract):**
> "The findings show that **technical training alone is not sufficient**, and that successful integration of AI requires a combination of pedagogical knowledge, positive attitudes, organizational support, and continuous training."

**Claim 2 (Discussion, p18 line 933):**
> "the findings suggest a **paradigm shift towards human–AI collaboration** in school settings, where AI enhances rather than replaces teachers' agency, creativity, and critical thinking for the benefit of their students"

**Claim 3 (Discussion, p18 line 948):**
> "ethical and developmentally effective AI use requires **teacher engagement as a mediating factor**, hence reaffirming the importance of teacher PD and emphasizing pedagogy and ethics over automation"

**Claim 4 (Level 3 of PD framework, p20 line 1075):**
> teachers should "[apply prompts] to their actual teaching needs, **promoting 21st century skills and enhancing creativity, critical thinking, learner engagement, and motivation to participate**"

**Claim 5 (Introduction, p1 line 38):**
> "the **pivotal role of teachers as mediators and facilitators of interactions between students and AI tools** has not been sufficiently explored"

### Four-level PD framework (Section 5.1)

1. **Conditions for AI Professional Learning** — preconditions (basic AI knowledge, beliefs, self-efficacy), teacher attitudes/perceptions, multi-level support (technical, organizational, leadership), networking
2. **Pedagogical Design of AI-Focused PD** — Professional learning communities (PLCs), reflection + hands-on practice, case-based scenarios, peer learning, micro-teaching, experiential learning, embedded ethics
3. **Pedagogical AI Integration in K-12 Classrooms** — actual classroom integration; "AI is integrated **not as a substitute for the teacher but as a collaborative tool**"; GenAI focus; prompt engineering skills; lesson planning + curriculum + assessment + feedback + differentiation; promoting 21st century skills, creativity, critical thinking, engagement, motivation
4. **Ethical and Sustainable Embedding of AI** — long-term consolidation; ethics as cross-cutting principle (data, privacy, bias, integrity); pre-service vs in-service distinctions; long-term holistic approach over scattered tools

### Author-flagged caveats and limitations (Section 5.2)

- "The diversity of study designs prevented the possibility of referring to a single standardized tool for assessing risk of bias"
- Most studies from Asia → potential geographic bias
- Some framework categories have conceptual overlaps
- Future research recommended for: differentiation by educational level (primary/secondary/higher), subject areas, teacher roles, specific contexts
- Ethics was the **least cited theme** in the corpus — authors explicitly flag this as a gap: "issues of AI ethics do not seem to have been fully developed within an educational framework that would guide the integration of AI technology into learning"

### Action research presence

The paper itself does NOT conduct action research — it's a synthesis. But Level 1 of the framework explicitly recommends "the need to conduct action research to adapt the training framework" (p18 line 1023). So action research is endorsed as a future research method, not directly conducted in the paper.

### Greek context

- ✅ 5 Greek authors (University of Patras + University of Crete)
- ❌ NO Greek K-12 studies in the 43-study corpus
- ✅ Methodologically aligned with the dissertation's Greek pilot context (Greek systematic review of PD needs frames the upstream rationale for the dissertation pilot)
- The Greek-author identity is **methodological alignment**, not empirical Greek-data alignment

---

## CG4.2.2 dimension mapping

UNESCO CG4.2.2 names 5 explicit "impact of AI on" dimensions. How does Aravantinos et al. 2026 map?

| CG4.2.2 dimension | Mapping | Strength |
|---|---|---|
| (a) **Students' agency** | Paper mentions "**teachers'** agency" (Claim 2) but not students' agency directly. The framework's Level 3 mentions "21st century skills" (Claim 4) which can be read to include agency, but indirectly. | ⚠️ **WEAK** — paper is teacher-side; student agency not directly addressed |
| (b) **Thinking and learning processes** | Critical thinking explicitly addressed (Claim 4 "enhancing creativity, critical thinking, learner engagement"). Discussion notes AI in pedagogical design + prompt engineering for student tasks (p20). | 🟡 **MODERATE** — partial coverage via Level 3 framework |
| (c) **Interactions with teachers** | **Strongly addressed.** Claim 5 directly: "the pivotal role of teachers as mediators and facilitators of interactions between students and AI tools has not been sufficiently explored". Claim 3: "teacher engagement as a mediating factor". The whole paper's framing is teacher-as-mediator of student–AI interactions — exactly this dimension. | ✅ **STRONG** — direct fit |
| (d) **Academic outcomes** | Brief mention (p7 line 446): "could have a positive impact on teaching practices and **students' learning outcomes**". Plus indirect via Level 3 framework references to "improved skills" and "21st century skills". | ⚠️ **WEAK-MODERATE** — sketched but not quantified |
| (e) **Social-emotional learning** | Not explicitly addressed. One mention in SWOT table (p25) that ChatGPT "increasing student engagement and information retention, but **not emotional support**" — but this is a feature limitation note in a SWOT analysis, not a finding about AI's impact on SEL. | ❌ **NOT ADDRESSED** |

**Net mapping:**
- 1 dimension covered strongly (c — interactions with teachers)
- 1 dimension covered moderately (b — thinking and learning processes)
- 2 dimensions covered weakly (a — agency; d — academic outcomes)
- 1 dimension not covered (e — social-emotional learning)

The paper's strongest CG4.2.2 contribution is to dimension (c). Dimension (c) is precisely the M9 framing — "teacher as mediator of AI–student interactions in lesson design." The fit is non-trivial.

---

## Suitability verdict

**Verdict: ✅ SUITABLE — with framing focused on dimension (c) "interactions with teachers".**

The paper IS suitable for CG4.2.2 reinforcement at M9, provided the citation is framed correctly. Specifically:

- ✅ AI-empirical research (43 empirical studies, peer-reviewed)
- ✅ Systematic review under PRISMA + thematic analysis with high inter-rater reliability
- ✅ K-12 specific (primary + secondary)
- ✅ Already in M9 matrix bibliography (not a new addition — bringing it inline)
- ✅ Open access CC-BY (full text accessible to readers; DOI links work)
- ✅ Recent (published 12 Jan 2026, < 4 months old)
- ✅ Greek-authored (methodological alignment with dissertation pilot context)
- ✅ Strong fit for CG4.2.2 dimension (c) "interactions with teachers" — paper's whole framing is teacher-as-mediator of student–AI interactions
- ✅ Moderate fit for dimension (b) "thinking and learning processes" via Level 3 of the proposed framework
- ⚠️ Weak fit for dimensions (a) student agency and (d) academic outcomes
- ❌ No coverage of dimension (e) social-emotional learning

**The paper closes the (c) dimension genuinely; it does NOT close all 5 dimensions.** This is the same situation Tier 1 had with foundational pedagogical theory citations — partial closure under strict UNESCO reading.

### Why this is still better than no reinforcement

T1.4 + T1.5 closed the foundational-theory layer. Aravantinos et al. (2026) adds an AI-empirical layer that addresses dimension (c) directly with verbatim language about "teacher as mediator of student–AI interactions" — which is precisely M9's framing. Combined with T1.4 + T1.5, the post-A2 closure is:

| Layer | Citation | Dimension(s) addressed |
|---|---|---|
| Backward Design (T1.4) | Wiggins & McTighe (2005) | Pedagogical-theory grounding |
| UDL (T1.5) | Meyer/Rose/Gordon (2014) | Pedagogical-theory grounding |
| Productive friction (T1.5) | Hattie & Donoghue (2016) | (b) learning processes — meta-analytic backbone, not AI-specific but applied to AI |
| **AI-empirical PD synthesis (A2 v1)** | **Aravantinos et al. (2026)** | **(c) interactions with teachers — direct + (b) thinking/learning processes — moderate** |

Three of the five dimensions get coverage (b, c, and the "benefits and risks" sub-clause). Dimensions (a) student agency and (e) social-emotional learning remain less directly served — but those are the soft dimensions even Tier 4 A1 v2 (Létourneau et al.) didn't cover for M4.

### Comparison with alternative references

| Candidate | AI-empirical? | Direct CG4.2.2 dim coverage | Greek context | Already in dissertation library? |
|---|---|---|---|---|
| **Aravantinos et al. 2026** (recommended) | ✅ 43-study review | (c) strong, (b) moderate | ✅ Greek authors | ✅ this PDF |
| Létourneau et al. 2025 | ✅ 28-study ITS review | (d) academic outcomes — strongest fit | ❌ Canadian | ❌ not in lib (was used in M4 A1 v2) |
| Steiss et al. 2024 | ✅ AI feedback RCT | (d) academic outcomes (writing quality) | ❌ US | ❌ in M4 bibliography only |
| "Fostering Human Agency in Age of AI" (in dissertation lib `ΕΡΓΑΣΙΕΣ` folder) | likely yes | (a) student agency — direct title fit | unclear | ✅ in lib |

**Recommendation:** Aravantinos et al. (2026) is the strongest single-citation choice for M9 CG4.2.2 reinforcement because:
1. Already in M9's matrix bibliography (smallest documentation lift — bringing it inline rather than introducing a new reference)
2. Greek authorship aligns with the dissertation's pilot context
3. Paper's framing of "teacher as mediator of student–AI interactions" matches M9's lesson-design framing exactly
4. Open access — readers can verify

If John wants to close additional dimensions (a) or (e), a SECOND inline citation could be added. The "Fostering Human Agency" paper in the local library is the obvious candidate for dimension (a) student agency — but that's a separate audit beyond Step 2A scope.

---

## Safe-to-cite verbatim claims

For Step 2B wording, these 3 claims are all verbatim from the paper and safe to cite without overgeneralisation:

### Citable claim 1 — paradigm shift framing (p18, Discussion)
> "the findings suggest a paradigm shift towards human–AI collaboration in school settings, where AI enhances rather than replaces teachers' agency, creativity, and critical thinking for the benefit of their students"

This claim is **the strongest one for M9** because it directly frames teachers as the mediating layer between AI and students — precisely M9's pedagogical position.

### Citable claim 2 — teacher as mediator (p1, Introduction)
> "the pivotal role of teachers as mediators and facilitators of interactions between students and AI tools has not been sufficiently explored"

Direct verbatim hit on CG4.2.2 dimension (c) "interactions with teachers".

### Citable claim 3 — pedagogical orientation requirement (Abstract)
> "technical training alone is not sufficient" — successful integration "requires a combination of pedagogical knowledge, positive attitudes, organizational support, and continuous training"

Reinforces M9's whole position that AI integration is pedagogical-design work, not tool-handling work.

### Background facts safe to cite
- "43 empirical studies (2021–2025) reviewed under PRISMA"
- "research from 32 Asian, 7 European, 7 North American, 2 African, 1 Oceanian, 1 South American studies"
- "thematic synthesis identified key themes including training practices, teachers' perceptions and attitudes, ongoing PD programs, multi-level support, AI literacy, and ethical and responsible use"

### Caveats to acknowledge if reusing claim 4 (Level 3 framework)
The framework explicitly states that "AI is integrated **not as a substitute for the teacher but as a collaborative tool**" and AI use should "promote 21st century skills and enhance creativity, critical thinking, learner engagement, and motivation to participate" — but this is a **proposed framework based on synthesis**, not an empirical effect-size finding. Cite carefully as a **synthesis recommendation**, not as a measured impact.

### Claims to AVOID
- ❌ Do not claim the paper measures AI's effect size on student outcomes — it doesn't (it's a thematic synthesis of teacher PD literature, not an effect-size meta-analysis)
- ❌ Do not generalise the framework's Level 3 recommendations as proven impacts — they're recommendations from synthesis, not measured outcomes
- ❌ Do not cite the paper for student social-emotional learning — it doesn't address this dimension

---

## Brief verdict for John

**SUITABLE.** Aravantinos et al. (2026) is a peer-reviewed, K-12 specific, AI-empirical PRISMA systematic review of 43 studies, by Greek authors, already in M9's matrix bibliography, and open access. Its strongest contribution to CG4.2.2 is dimension (c) "interactions with teachers" — paper's whole framing is teacher-as-mediator of student-AI interactions, which is exactly M9's lesson-design framing.

The paper does NOT cover all 5 CG4.2.2 dimensions. Dimensions (a) student agency and (e) social-emotional learning remain less directly served. But the (c) closure is genuine and verbatim ("teachers as mediators and facilitators of interactions between students and AI tools"). This is materially stronger than the foundational pedagogical theory of T1.4+T1.5 alone, and is consistent with the Tier 4 A1 v2 precedent (Létourneau et al. 2025 closed CG4.1.2 via single AI-empirical citation).

**Recommended verbatim claims for Step 2B wording:**
- "AI enhances rather than replaces teachers' agency, creativity, and critical thinking for the benefit of their students" (paradigm shift framing)
- "the pivotal role of teachers as mediators and facilitators of interactions between students and AI tools" (direct CG4.2.2 dim c hit)
- "technical training alone is not sufficient" + pedagogical-knowledge requirement (M9 mission alignment)

**Caveats to bake into wording:** the paper is a thematic synthesis, NOT an effect-size meta-analysis. Cite findings as synthesis-derived themes / recommendations, not as measured AI-impact effects.

---

## Hard guardrails respected

- ❌ No DB writes
- ❌ No RAG document changes
- ❌ No Gemini call
- ❌ No patch wording proposed (Step 2B work)
- ❌ No generalisation from single findings to corpus-wide claims
- ✅ Read paper in full (1,858 lines extracted via pdftotext)
- ✅ Verbatim quotes anchored to specific page/line locations
- ✅ Cross-checked Crossref + OpenAlex + paper title page for bibliographic consistency
- ✅ Saved to file; reported back

---

*End of paper-level audit.*
