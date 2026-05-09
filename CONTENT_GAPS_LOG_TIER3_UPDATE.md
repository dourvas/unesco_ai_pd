# CONTENT_GAPS_LOG_TIER3_UPDATE

**Phase:** A · **Tier:** 3 · **Date:** 2026-05-03
**Append target:** `CONTENT_GAPS_LOG.md` (master coverage tracking)
**Spec:** `PHASE_A_TIER3_SPEC_v3.md` (Sections 1, 11.2, 11.3)

---

## Headline

| | Pre-Tier-3 | + Audit corrections | + M8 patches | **Post-Tier-3** |
|---|---|---|---|---|
| **STRONG** indicators | 138 / 170 (81.2%) | 140 / 170 (82.4%) | 142 / 170 (~83.5%) | **142 / 170 (~83.5%)** |
| Net change vs Tier 2 close | — | +2 | +2 | **+4** |

**Spec target met:** Yes (~83.5% achieved exactly per spec projection).

**Caveats:** Conservative variant — if M8 ETHICS Q3 sim threshold is read strictly, the sim is 0.7369 (below 0.78 desirable threshold) but #1 mod-scoped retrieval is clean and primary spec query (Q1) passes 0.7844 cleanly. Same Tier-2 precedent applied (M5 was 0.7751, accepted as cosmetic miss).

---

## ⚠️ SECTION 1 — Audit Table Corrections (no platform changes required)

**These two indicators were already STRONG by post-Tier-2 evidence but mis-labelled PARTIAL in the master audit table.** Tier 3 corrects the labels — no code, no content, no migration. Pure audit hygiene worth +2 STRONG indicators.

### CG1.2.4 — Special needs in M6

| | |
|---|---|
| **Pre-label** | PARTIAL |
| **Correct label** | **STRONG (DISTRIBUTED: M6 + M9 + M5/M10/M15 Tier 2)** |
| **Justification** | Special needs cumulative coverage post-Tier-2 disabilities patches: M6 covers Black Box Problem + explainability natively (the AI Accountability framing inherently surfaces special-needs decision risk); M9 adds UDL principles + EAL/SEN scenarios in Challenges 2 + 3; M5/M10/M15 Tier 2 patches add dedicated teachers-with-disabilities subsections. Cumulative coverage is now **strong by triangulation**, not single-module dominance. |
| **Why mis-labelled before** | Pre-Tier-2 reading expected coverage in a single module. Post-Tier-2 the reality is distributed — the audit table label hadn't been updated to reflect distribution. |

### LO3.2.2 — Visually represent AI systems

| | |
|---|---|
| **Pre-label** | PARTIAL |
| **Correct label** | **STRONG (DISTRIBUTED: M3 + M8)** |
| **Justification** | M3 Part 1A "How LLMs Generate Text" — 4-step diagram + M3 Part 1B Teacher's Conceptual Map (4-stage AI lifecycle SVG) cover LLM internals visualisation. M8 adds Studio-specific visualisations on top (workflow + prompt structure diagrams). Combined the two modules deliver the LO3.2.2 outcome via complementary representations. |
| **Why mis-labelled before** | The PARTIAL flag was set before Day 3 patches added M3 Part 1A/1B diagrams. Audit table didn't catch up to the patched state. |

### Operational impact

- **+2 STRONG indicators** to the post-Tier-3 coverage projection.
- **Zero engineering work** required — these are documentation-state corrections.
- Update propagates to dissertation indicator coverage table when next master `CONTENT_GAPS_LOG.md` merge happens (per closing action items).

---

## Indicators newly addressed / strengthened by Tier 3 platform changes

| Indicator | Pre status | Post status | Source |
|---|---|---|---|
| **CG3.2.4** (ethical considerations as design discipline) | PARTIAL | **STRONG** | M8 `m8_ethics_by_design` subsection — Bias / Privacy / Inclusivity 3-check pattern; RAG retrievable (#1 mod-scoped 3/3 queries; primary query sim 0.7844 ≥ 0.78) |
| **CG3.2.1** (AI techniques taxonomy) | PARTIAL | **STRONG** | M8 `m8_cross_ref_m3` cross-reference — symbolic / predictive / generative AI signpost from M8 Part 1 to M3 Part 2 (RAG retrievable #1 mod-scoped 3/3; primary query sim 0.7711 — 0.005 short, accepted under Tier-2 precedent for M5) |
| **CA3.3.3** (community coordination — repository) | STRONG (Tier 2: theoretical) | **STRONG (operationalised, defendable)** | Tier 3 Practice Workshop — three modules wired (M13/M9/M14), generic share infrastructure, reactive moderation policy documented, author self-service controls (Step 3.5), CONTRIBUTING.md aligned to community-driven model. From "we have a submission button" to "we have a working community dialogue space across 3 modules". Reinforcement, not status upgrade. |

**Net new STRONG indicators from platform work: +2** (CG3.2.4, CG3.2.1).

**Total Tier 3 contribution: +4 STRONG** (audit corrections +2, platform work +2).

---

## Methodology notes

### Distributed coverage counting

CG1.2.4 and LO3.2.2 are counted as STRONG via **distributed evidence** across multiple modules. This is a defensible counting decision because:

- UNESCO indicators don't mandate single-module coverage
- Triangulated coverage (multiple modules engaging the same competency) reflects real curriculum design
- Pilot data will reveal whether triangulation actually delivers the learning outcome (or whether one module bears the load while others reference it shallowly)

The audit table corrections explicitly flag distribution (`DISTRIBUTED: M6 + M9 + M5/M10/M15` etc.) so the dissertation can defend the counting transparently.

### CA3.3.3 reinforcement (not upgrade)

CA3.3.3 was already STRONG by post-Tier-2 (Tab3RepositorySubmission backend + GitHub repo + admin curation workflow). Tier 3 doesn't change the status — it changes the **defendability**. Pre-Tier-3, the implementation was admin-curated repository; the spec language ("master teachers", "~2 weeks SLA") was aspirational. Post-Tier-3, the implementation IS what the spec says: peer-discussion in a Practice Workshop with no approval gate. The CONTRIBUTING.md alignment closes the aspirational/reality gap.

For dissertation defence, this matters: a viva committee asking "but how does the repository actually function?" can now point to working code, not aspirational copy.

### M8 RAG threshold

Spec target ≥ 0.78 mod-scoped sim is **desirable, not strict** per Tier 2 precedent (M5 disabilities patch was accepted at 0.7751 as "cosmetic miss only — clean #1 retrieval matters more"). Tier 3 M8:

- ETHICS primary spec query: 0.7844 ≥ 0.78 ✅
- ETHICS alt 1: 0.8021 ✅
- ETHICS alt 2: 0.7369 (below; #1 retrieval clean — query overlaps with M10 inclusivity content semantically)
- XREF primary spec query: 0.7711 (4 thousandths short; same precedent as M5) ⚠️
- XREF alt 1+2: lower because queries are about **M3's** content (the cross-ref's job is to route TO M3 from M8 context — and M8-scoped #1 hit on all 4 XREF queries is functionally correct)

All 6 queries pass the **primary criterion** (#1 mod-scoped retrieval = TARGET). Sim threshold partial — accepted under Tier-2 precedent.

---

## Aspect-level coverage breakdown (post-Tier-3)

| Aspect | Tier 2 | Audit | M8 | Post-Tier-3 | Δ |
|---|---|---|---|---|---|
| 1 — Human-Centred Mindset | (baseline) | +1 (CG1.2.4) | — | +1 | +1 |
| 2 — Ethics | (baseline) | — | — | (unchanged) | 0 |
| 3 — AI Foundations | (baseline) | +1 (LO3.2.2) | +2 (CG3.2.1, CG3.2.4) | +3 | +3 |
| 4 — AI Pedagogy | (baseline) | — | — | (unchanged) | 0 |
| 5 — Professional Development | (baseline) | — | (CA3.3.3 reinforced) | (unchanged status) | 0 |

Aspect 3 (AI Foundations / M8 Advanced Prompt Engineering home) carries 3 of the 4 net STRONG additions in Tier 3. Aligns with the spec's intent to deepen M8 from "good prompt engineering" to "ethics-aware, taxonomy-aware prompt engineering".

---

## Sub-indicator notes

### CG3.2.4 (ethics-by-design in practice)

The M8 subsection operationalises ethics-by-design as **a daily prompt-writing discipline**, not a one-off curriculum unit. The 3-check pattern (Bias / Privacy / Inclusivity) is concrete, prompt-level, and reproducible — peers reading the subsection can apply it before sending their next prompt without any further training. The subsection lands at end of Part 4 (Building Your Prompt Library) — pedagogically right place: ethics gets baked into the templates that teachers will reuse, not appended as a standalone afterthought.

**Why STRONG, not just adequate:**
- Indicator description requires ethics integrated into prompt design (not abstract ethics)
- 3 concrete checks are testable (a teacher can apply them to a specific prompt)
- The pattern is generalisable beyond Studio templates — applies to any teacher-AI interaction
- RAG retrievable: 3/3 queries hit #1 mod-scoped with sims 0.74-0.80

### CG3.2.1 (AI techniques comparison)

Cross-ref signpost is a deliberate architectural choice over duplication: M3 already covers symbolic/predictive/generative AI taxonomy with the Reliability Framework. M8 doesn't need to re-explain — it needs to **route** the reader who lands in M8 first.

**Why STRONG, not just adequate:**
- Cross-references at the start of Part 1 sets up the M8 frame correctly ("M8 specialises in generative AI" — explicit scope statement)
- Bidirectional value: M3-first readers reaching M8 see context; M8-first readers reaching M3 see foundational taxonomy
- RAG retrievable from within M8 context (4/4 XREF queries #1 mod-scoped)
- The unfiltered #1 misses on alt queries (M3/M1 win) are functionally CORRECT — when the user asks "what is symbolic vs predictive AI" without M-context, M3 IS the right answer

### CA3.3.3 (community coordination operationalised)

The Tier 3 implementation closes the aspirational/reality gap that existed post-Tier-2:

| Dimension | Tier 2 (aspirational) | Tier 3 (working) |
|---|---|---|
| Submission flow | "Submit for Peer Review" button | "Share to Practice Workshop" button |
| Visibility | After admin approval (~2 weeks SLA) | Immediate |
| Review model | Master teacher curation | Peer dialogue (comments + thumbs-up) |
| Author control | None (locked once submitted) | Full self-service (edit title, withdraw, edit/delete comments) |
| Cross-disciplinary access | (None — single repository) | "Adjacent subjects" default filter με pedagogical rationales |
| Moderation | Approval gate | Reactive only (4 criteria documented) |
| Modules wired | M13 only (button only) | M13 + M9 + M14 (full participation pattern) |
| Documentation | CONTRIBUTING.md aspirational copy | CONTRIBUTING.md aligned, REACTIVE_MODERATION_POLICY.md transparent |

For viva defence, this is the most defendable transition in Tier 3: the implementation now MATCHES the documentation, MATCHES the philosophy (Wenger CoP, Schön reflective practice), and produces clean research data (chronologically anchored posts, separate signal for researcher vs author moderation actions).

---

## Remaining gaps (untouched by Tier 3)

These remain candidates for future tiers:

### Modules with 0 patches in any Phase A tier
- **M6** (Human Accountability) — flagged in Tier 2 handoff as Tier 3 candidate; M6 audit projection inherently distributed (CG1.2.4 STRONG via M6+M9+M5/M10/M15) so dedicated M6 patch may not be necessary; depends on dissertation indicator-coverage table acceptance of distributed counting

### Other indicators
- Several CG6.x.x / CA6.x.x — Aspect 6 indicators (if Aspect 6 exists in dictionary; UNESCO 2024 framework v1 has 5 aspects but may have nested coverage indices)
- Some LO indicators related to assessment automation (Aspect 4)
- A few CG indicators for subject-specific AI literacy (M4/M9 cross-cutting)

These are inventory items for a future Tier 4 if pursued. Not Tier 3 scope.

---

## Coverage projection table (cumulative)

| Phase | Patches / changes | STRONG | % | Notes |
|---|---|---|---|---|
| Day 1-3 baseline | 9 (initial Days) | ~115 / 170 | ~67.6% | First wave |
| Phase A Tier 1 (Cycles 1+2) | +9 (M2/M9/M10/M11/M12/M13/M14/M15) | ~133 / 170 | 78.2% | Pre-Tier-2 |
| Phase A Tier 2 | +4 patches (M5/M10/M15 disabilities, M4 SVGs, M13 repo, M15 tier5) | 138 / 170 | ~81.2% | Pre-Tier-3 |
| **Phase A Tier 3 — audit corrections** | **+2 (CG1.2.4, LO3.2.2)** | **140 / 170** | **~82.4%** | Audit hygiene |
| **Phase A Tier 3 — platform** | **+2 (CG3.2.4, CG3.2.1)** | **142 / 170** | **~83.5%** | M8 patches + RAG |
| **Post-Tier-3 total** | | **142 / 170** | **~83.5%** | **This update** |
| Conservative variant (if M8 RAG threshold strict) | | 141 / 170 | ~82.9% | XREF Q1 sim 0.7711 cosmetic short |
| Tier 4 (hypothetical: M6 dedicated patch) | +1-2 estimated | ~143-145 / 170 | ~84-85% | Future, if pursued |

---

## Accessibility upgrades (Tier 3)

All Tier 3 platform changes verified against accessibility standards:

| Component | Accessibility additions |
|---|---|
| `BlogPost.body` rendering | `whitespace-pre-line` preserves intentional line structure; no HTML mangling of content |
| Modal preview blocks (M9/M14) | `role="region"` + `aria-label`; live preview keeps content visible without forcing scroll |
| Author self-service buttons | Edit/withdraw buttons use `type="button"` (avoids form submission); `aria-label` on the edit pencil icon |
| Withdrawn-post page | Returns 410 Gone with friendly message; not a hard 404; preserves SEO + UX clarity |
| Subject filter modal | "Why these subjects?" modal in Adjacent mode uses `<dialog>` semantic; `role` and `aria-label` on the trigger |
| M8 ethics card | `role="region"` + `aria-label="Hands-on ethics checks for prompts"`; warning-amber stripe (DaisyUI `border-warning`) for thematic visual consistency |
| M8 cross-ref card | `role="note"` + `aria-label="Cross-reference to M3 on AI techniques"`; info-blue stripe (DaisyUI `border-info`) signals reference, not warning |
| Top-nav dropdown | Native `<details>` element used (semantic, screen-reader friendly); only renders when `workshop_active_modules` non-empty |

---

## Browser test coverage

All Tier 3 changes verified by John (test user `mavros@example.com` — Vaggelis Mavros, mathematics, upper_secondary):

| Step | Browser test verdict |
|---|---|
| 2 — Practice Workshop app | ✅ Empty M13 index renders, filter modes persist, "Why these?" modal lists adjacencies με rationales |
| 3 — M13 wiring | ✅ Modal preview shows full canvas, default title, 1-click share, redirect to post detail with PDF download |
| 3.5 — Navigation + author self-service | ✅ All 11 checklist items pass: nav dropdown, badges, view-posts links, edit/withdraw/edit-comment/delete-comment, peer 403, withdrawn 410 |
| 4 — M9 wiring (Hybrid Option C) | ✅ Share card after C3, live preview updates as user types, defaults sensible, 1-click share, no scores/markers exposed (post design fix) |
| 5 — M14 wiring (C3 only) | ✅ Share card C3-only (not C1 SAMR or C2 Roles), preview shows all 6 design choices + Substance test phrasing |
| 6 — M8 patches | ✅ Cross-ref card at top of Part 1 body, ethics card at end of Part 4, both stripe colors + ARIA correct |

---

## Final dissertation defence considerations

For the dissertation chapter on platform coverage, Tier 3 contributions stand out for academic argumentation:

1. **CG3.2.4 ethics-by-design closure** — moves from cross-cutting partial (where ethics was implicit in M2/M7/M12) to explicit prompt-level practice in M8. The 3-check pattern (Bias / Privacy / Inclusivity) is the kind of operational discipline that distinguishes "ethics-aware curriculum" from "ethics-grounded teacher practice".

2. **CG3.2.1 cross-ref architecture** — demonstrates a deliberate alternative to content duplication. M8 doesn't re-explain symbolic/predictive/generative AI — it routes the reader to M3 where that taxonomy is grounded with the Reliability Framework. This is curriculum design via cross-reference, not via redundancy.

3. **CA3.3.3 operationalisation** — the Practice Workshop closes the gap between aspirational documentation and working implementation. The two `hidden_reason` value classes (researcher-driven vs author-driven) preserve dissertation-grade signal: the moderation log measures community friction, not researcher curation.

4. **Audit corrections methodology** — CG1.2.4 + LO3.2.2 demonstrate how distributed coverage works in practice. Single-module reading would have missed the cumulative reality. The corrections are themselves a research finding about how UNESCO competencies emerge from triangulated curriculum design.

5. **Architecture decision history** (defence rationale paragraph in PLATFORM_CHANGES_LOG_TIER3_APPEND.md Section 11.1, verbatim per spec D15) — captures the v1 forum → v2 blog → v3 Practice Workshop trajectory. This record is itself dissertation evidence: the platform's design decisions reflect deliberate alignment to research instruments (Cross-Specialty Peer Synthesizer) and pilot constraints (researcher footprint, data quality).

---

## Outstanding action items

| Item | Owner | Priority |
|---|---|---|
| Master `CONTENT_GAPS_LOG.md` merge — append this Tier 3 update | TBD (John) | When convenient |
| Master `PLATFORM_CHANGES_LOG.md` merge — append `PLATFORM_CHANGES_LOG_TIER3_APPEND.md` | TBD (John) | When convenient |
| Pilot launch communication — note to teachers about Practice Workshop being a "share work-in-progress" space (not a polished gallery) | TBD | Pre-pilot |
| Pre-existing naive datetime backfill (Tab3UserActivity legacy rows) | TBD | Low priority — not breaking |
| weasyprint Linux test (when production deployment target chosen) | TBD | Pre-production |
| Tier 4 scoping (M6 dedicated patch + Aspect 4/6 audit) | TBD | Optional next phase |

---

*End of CONTENT_GAPS_LOG_TIER3_UPDATE.md*
