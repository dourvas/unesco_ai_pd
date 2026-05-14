# Phase E — Multi-agent Refactor — FINAL DESIGN DOCUMENT (v11)

**Date:** 2026-05-13
**Status:** 📘 FINAL — canonical Phase E document; ready for commit 10 (file deletion)
**Supersedes:** all v1 through v10 design proposals
**Document role:** Dual — (a) specification for commit 10, (b) canonical retrospective of Phase E for future reference and dissertation use

---

## Reading guide

This document serves two audiences:

- **Now:** specification for the final commit of Phase E (§8).
- **Future:** canonical record of what Phase E accomplished, why, and how. Suitable as primary source for the dissertation architecture chapter, viva preparation, and onboarding new contributors to the multi-agent system.

Sections §0–§3 are retrospective and canonical. Sections §8–§12 are commit-10 specification. The remainder is reference material.

---

## 0. Phase E — One-paragraph summary

Phase E migrated four AI features (RAG feedback, RTM tension extraction, DTP development trajectory, Peer Synthesis) from a 1112-line monolithic Python file at the repository root into four named agent classes under `apps/agents/`, all inheriting from a common `BaseAIAgent` with shared infrastructure for cost tracking, audit logging, provenance writing, and atomicity enforcement. The work was completed in eleven incremental commits over a single design-then-execute cycle, with each commit reviewed bidirectionally between chat (architectural design and decisions) and Claude Code (code-level execution and counter-proposals). The refactor preserved byte-identical behaviour for the primary user paths and produced **seven distinct architectural improvements** documented in §3 D3b.

---

## 1. What Phase E delivered (final state)

### 1.1 Architecture before Phase E

```
project_root/
├── rag_query_system.py          # 1112-line monolith, imported via sys.path.append
├── apps/
│   ├── modules/
│   │   └── views.py             # called monolith functions procedurally
│   └── compliance/              # provenance service
└── manage.py
```

Three DB-connection idioms coexisted (hardcoded `DB_CONFIG`, `psycopg2` with `settings.DATABASES`, Django ORM). Cost tracking covered only 1 of 4 AI paths. Provenance writing was distributed across the monolith and `views.py` with inconsistent atomicity guarantees.

### 1.2 Architecture after Phase E

```
project_root/
├── (rag_query_system.py deleted)
├── apps/
│   ├── agents/                  # NEW APP
│   │   ├── base.py              # BaseAIAgent (ABCMeta)
│   │   ├── research.py          # ResearchInstrumentAgent
│   │   ├── rag_feedback.py      # RAGFeedbackAgent
│   │   ├── rtm.py               # RTMAgent
│   │   ├── dtp.py               # DTPAgent
│   │   ├── peer.py              # PeerSynthesisAgent + NoPeerReflectionsAvailable
│   │   ├── shared/
│   │   │   ├── llm_client.py    # NEW/OLD Gemini SDK wrapper
│   │   │   ├── embedding.py     # embed_query
│   │   │   ├── json_repair.py   # clean_json_response
│   │   │   ├── cost_tracker.py
│   │   │   ├── audit.py         # structured JSON logger
│   │   │   └── db.py            # dict_cursor() unified DB access
│   │   └── tests/               # 102 agent-suite tests
│   ├── modules/
│   │   └── views.py             # calls agents
│   └── compliance/              # unchanged
└── manage.py                    # UTF-8 stdio guard
```

Single DB-connection idiom (Django connection via `dict_cursor()`). Cost tracking on 4 of 4 paths. Provenance writing centralised in `BaseAIAgent` template-method pattern.

### 1.3 Class hierarchy (final)

```
BaseAIAgent (ABCMeta + @abstractmethod _do_generate)
│   Two public entry points: generate() + extract()
│
└── ResearchInstrumentAgent (pure marker class)
    ├── RAGFeedbackAgent     — generate(), dual provenance rows
    ├── RTMAgent             — extract(), no atomic-time persistence
    ├── DTPAgent             — generate(), multi-call orchestration
    └── PeerSynthesisAgent   — generate(), three-way failure modes
```

Future agents (Epilogue Q&A in Phase G, Multimodal in Phase F, XAIAgent in Phase D.3) extend this hierarchy without modifying it.

---

## 2. Commit-by-commit summary

| # | Title | Hash | LOC | Tests | Theme |
|---|---|---|---|---|---|
| 1 | BaseAIAgent + RAGFeedbackAgent + shared/ | `f806a18` | +1640 | 214 → 238 | Foundation |
| 1.5 | manage.py UTF-8 stdio guard | `7786a7a` | +12/-12 | 238 | Environment fix |
| 2 | views.py RAG cutover + atomic STRENGTHENING | `0f50b7a` | +97/-93 | 238 → 237 | First cutover; inconsistency window eliminated |
| 3 | RTMAgent + ResearchInstrumentAgent + `extract()` | `935241a` | +925/-21 | 237 → 270 | Dual entry points discovered |
| 4 | views.py RTM cutover (preservation) | `4497a0b` | +22/-10 | 270 | Honest preservation |
| 5 | DTPAgent + commit-6 diagnostic | `1c2c193` | +998 | 270 → 295 | Multi-call orchestration |
| 6 | views.py DTP cutover (preservation + UX tightening) | `6943da7` | +80/-41 | 295 | Silent-failure antipattern eliminated |
| 7 | PeerSynthesisAgent + commit-8 diagnostic + dead block removal | `373449f` | +830/-32 | 295 → 316 | Triple-aspect commit |
| 8 | views.py Peer cutover (preservation, three-way catch) | `2927311` | +103/-61 | 316 | Smoothest cutover |
| 9 | Monolith function deletion + grep audits + Gemini 1.5 cleanup + tests.py migration | `45131c5` | +320/-8114 | 316 | Audit-protected cleanup; 7 distinct findings |
| **10** | **Delete `rag_query_system.py` + drop sys.path hack** | ⏸ **Next** | ~-1115 | 316 | Final tombstone removal |

**Net LOC change for Phase E (commits 1-9):** roughly +5,000 added (agents, shared, tests) − 8,400 deleted (monolith, phantom files, dev scripts) ≈ **−3,400 net deletion**. The codebase shrunk while gaining structure and seven distinct improvements.

> **Post-commit-10 update (2026-05-14):** commit 9 hash shifted to `45969bc` after an in-place amend (heredoc parse error left modifications unstaged; pre-push amend was safe). Commit 10 final hash: `1e2de04`. Content matches the v11 spec; only the SHA changed.

---

## 3. Foundational decisions (CANONICAL)

### Decision 1 — Class hierarchy: TIERED with marker class

`BaseAIAgent` is abstract (`ABCMeta` + `@abstractmethod _do_generate`). `ResearchInstrumentAgent` is a pure marker class that earns its keep through (a) docstring contract, (b) `isinstance` type-tag for cross-cutting code, and (c) future-extensibility into multi-agent subhierarchies. Four concrete agents under `ResearchInstrumentAgent`. `ServiceAgent` reserved for D.3 when XAI becomes a generative concern.

### Decision 2 — XAI: NOT IN PHASE E

XAI today is HTML templates + provenance display, not generated content. Building an `XAIAgent` in Phase E would have abstracted an empty box. Deferred to D.3 (DTP XAI narrative) where the first generative XAI workflow lands.

### Decision 3 — Provenance + HITL: BASE CLASS, THREE SUBSECTIONS

**3a. Multi-row provenance contract.** Default one row per call. Subclass overrides when artefact composition requires it. RAG overrides for dual rows (`rag_query` telemetry + `rag_feedback` artefact). RTM, DTP, Peer use the default single-row.

**3b. Final atomic-scope tally:**

| Cutover | Atomic scope | Secondary effects |
|---|---|---|
| Commit 2 (RAG) | **Strengthening** | None |
| Commit 4 (RTM) | Preservation | None |
| Commit 6 (DTP) | Preservation | UX tightening (substantive) |
| Commit 8 (Peer) | Preservation | UX tightening (incidental, catch-all) |

**1 strict strengthening + 3 preservations (2 with UX tightening).** The numerical balance defeats the easy overclaim "the refactor tightened CP-9." It did, but only once. The other contributions are listed below.

**Seven dissertation contributions (FINAL):**

| # | Contribution | Evidence |
|---|---|---|
| 1 | Atomic strengthening at one site | Commit 2 (RAG): two atomic blocks collapsed; inconsistency window eliminated |
| 2 | Dual entry points distinction (`generate()` vs `extract()`) | Commit 3: two architectural stances on HITL — "AI commits, human disputes" vs "AI proposes, human ratifies" |
| 3 | Cost tracking expanded from 1/4 to 4/4 paths | Commits 1–7: every agent emits `agent.cost` events |
| 4 | Elimination of three DB-connection idioms | Commits 1–10: hardcoded credentials, raw psycopg2, Django ORM unified under `dict_cursor()` |
| 5 | Dead-code findings exposed by test-mock review | Commits 2 (C), 4, 5 §11, 7 |
| 6 | Silent-failure antipatterns exposed by architectural enforcement | Commit 6 (DTP substantive), commit 8 (Peer incidental) |
| 7 | Pre-deletion audits as complementary safety | Commit 9: §2 call-site map captured production callers; audits captured test fixtures using monolith as live oracle, phantom monolith copies surviving incremental cutover (one containing a SAFETY HAZARD enable-bomb for deprecated Gemini 1.5), and out-of-tree dev scripts. Two complementary safety layers, not redundant. |

These seven contributions form the architecture chapter of the dissertation.

**3c. Dual entry points.** Verbatim architectural rationale, quotable in dissertation:

> BaseAIAgent exposes two public entry points: `generate()` for persisted artefacts (RAG-style, agent owns the atomic block) and `extract()` for ephemeral AI suggestions where persistence is a separate human action (RTM-style). This distinction is not a special case; it reflects two architectural stances on human-in-the-loop AI: "AI commits, human disputes" (generate) and "AI proposes, human ratifies" (extract). Future features like the Epilogue Q&A dialogue and multimodal voice transcription are expected to use extract() as well.

Extract-only agents MUST override `generate()` with descriptive `ValueError` pointing to the persistence-owning endpoint.

### Decision 4 — Migration strategy: STRANGLER PATTERN

Eleven incremental commits. Each kept tests green. Each had pre-defined scope discipline:

- Agent-add commits (1, 3, 5, 7) — new code, no view changes, may include diagnostic for the next cutover
- Cutover commits (2, 4, 6, 8) — call-site rewiring only; dead code findings deferred to companion agent commit
- Cleanup commits (9, 10) — deletion-dominated, audit-protected

---

## 4. Established patterns (canonical for future phases)

Six patterns proved their value across Phase E and are available for reuse:

**Pattern 1 — Pre-decision pattern.** Each agent-add commit performs a diagnostic during execution to pre-decide the framing of its companion cutover commit. Verdict belongs to: STRENGTHENING / PRESERVATION / HYBRID. Eliminates framing-discovery surprise during cutover.

**Pattern 2 — Triple-aspect agent commits.** When companion cleanup tasks accumulate, an agent commit can combine (a) agent build, (b) diagnostic for next cutover, (c) dead-code or cleanup task. Proven by commit 7.

**Pattern 3 — Stop-and-discuss as quality gate.** Across eleven commits, ten distinct stop-and-discuss interventions prevented or surfaced: architectural mismatches (commit 3), test-mock layer drift (commit 2), Python patching gotchas (commit 3), trailing-whitespace tool gotchas (commit 5), socially-embedded silent-failure antipatterns (commit 6), exception-class semantic precision (commit 7), and audit-revealed phantom debt (commit 9).

**Pattern 4 — Two-layer test invariant.** Layer-1 prompt-identical (mock LLM, assert prompt match). Layer-2 behaviour-identical (mock returns canned output, assert downstream state matches). Both required; both robust to LLM non-determinism.

**Pattern 5 — Pre-deletion audit protocol.** Before deleting any function from a legacy module, run two grep audits: (A) call-site verification against expected list, (B) hazard-pattern scan (e.g. deprecated API references). Audits surface debt that incremental cutover cannot see.

**Pattern 6 — Strangler with byte-identical preservation.** New code coexists with old; tests verify byte-identical behaviour during overlap; old code removed only after every caller migrates. No "big bang" risk.

---

## 5. Shared infrastructure (canonical)

All six `apps/agents/shared/` modules are dissertation evidence:

| Module | Purpose | Replaces |
|---|---|---|
| `llm_client.py` | NEW/OLD Gemini SDK wrapper | 5 inline duplications in the monolith |
| `embedding.py` | `embed_query` standalone | Monolith function called from 5 sites |
| `json_repair.py` | `clean_json_response` | Monolith helper used by RTM + DTP |
| `cost_tracker.py` | Per-call cost logging | Inline rough estimate (RAG only, pre-Phase-E) |
| `audit.py` | Structured JSON logger | Scattered `print()` statements |
| `db.py` | `dict_cursor()` unified raw-SQL helper | Three DB-connection idioms |

---

## 6. Test invariant + Layer-0 guards (canonical)

**Layer 0 — Static / boilerplate regression class.** Exact-string assertions for prompt boilerplate (sign-offs, system instructions, JSON schema markers, intentional trailing whitespace). Catches escape / newline / whitespace regressions for free.

**Layer 0 tool-choice discipline:** when an agent prompt has intentional trailing whitespace preserved byte-identically from the monolith, do NOT use the Edit tool (which silently strips trailing whitespace). Use direct Python `open()/write()` instead.

**Layer 0 patching-at-import-site rule:** when an agent imports a shared helper via `from apps.agents.shared.X import helper`, tests must patch at `apps.agents.<agent_module>.helper`, not at the source module. The agent's namespace binds the name at import time.

**Layer 1 — Prompt-identical.** Mock the LLM client; assert `mock.call_args.kwargs['contents']` matches the expected prompt string. After commit 9, the expected prompts live as `EXPECTED_*_PROMPT` constants — frozen snapshots from cutover day, not live monolith oracles.

**Layer 2 — Behaviour-identical given fixed LLM output.** Mock returns canned response; assert agent produces the same parsed/validated/saved artefact as the monolith did.

**Per-step gate:** all tests green after every commit. Final baseline: **316 tests.** No commit may drop below.

---

## 7. Final commit status

| Commit | Title | Status |
|---|---|---|
| 1 | BaseAIAgent + RAGFeedbackAgent + shared/ | ✅ |
| 1.5 | manage.py UTF-8 stdio guard | ✅ |
| 2 | views.py RAG cutover + atomic strengthening | ✅ |
| 3 | RTMAgent + ResearchInstrumentAgent + `extract()` | ✅ |
| 4 | views.py RTM cutover (preservation) | ✅ |
| 5 | DTPAgent + commit-6 diagnostic | ✅ |
| 6 | views.py DTP cutover (preservation + UX tightening) | ✅ |
| 7 | PeerSynthesisAgent + commit-8 diagnostic + dead block removal | ✅ |
| 8 | views.py Peer cutover (preservation, three-way catch) | ✅ |
| 9 | Monolith function deletion + grep audits + Gemini 1.5 cleanup | ✅ (final hash `45969bc` after amend) |
| 10 | Delete `rag_query_system.py` + drop sys.path hack | ✅ (`1e2de04`) |

---

## 8. Commit 10 specification (focused — minimal)

**Scope:** Final tombstone removal. Three operations.

### 8.1 Pre-deletion sanity check

Before any file removal, confirm:

1. `rag_query_system.py` is in fact the 33-line tombstone from commit 9 (not accidentally regrown). One-line check: `wc -l rag_query_system.py` should return ~33.
2. Test suite passes before any change: `python manage.py test` returns 316/316.
3. The `sys.path.append` at `views.py:39` is the only reference left to the monolith path. `git grep "sys.path.append.*rag_query"` returns one hit.

If any check fails, surface and stop.

### 8.2 The three operations

1. **`git rm rag_query_system.py`** — deletes the tombstone file.
2. **Remove `sys.path.append`** at `views.py:39` (or whichever line it now sits on after commit 9).
3. **Verify** test suite returns 316/316 green.

### 8.3 Commit message (template)

Working draft:

> Phase E commit 10: Final deletion of monolith file and sys.path hack
>
> This commit completes Phase E by deleting the rag_query_system.py
> tombstone file (left as documentation in commit 9) and removing the
> sys.path.append hack at views.py that allowed root-level import of
> the original monolith.
>
> After this commit:
> - rag_query_system.py no longer exists in the repository
> - views.py no longer manipulates sys.path
> - All four AI features (RAG, RTM, DTP, Peer) live under apps/agents/
> - 316 tests pass
>
> Phase E is complete. Seven dissertation contributions documented in
> PHASE_E_DESIGN_PROPOSAL_v11.md §3 D3b.

### 8.4 Stop-and-discuss triggers (commit-10-specific)

1. Pre-deletion check 1 fails (file is not the 33-line tombstone) — surface, do not delete blindly.
2. Pre-deletion check 2 fails (tests not green pre-change) — surface; do not "fix forward" by deleting.
3. Pre-deletion check 3 fails (more than one sys.path reference) — surface; the second reference may belong to something else.
4. Post-deletion test failure — investigate root cause; do not silently revert. Phase E ends with a green suite or it does not end.

### 8.5 LOC budget

Expected: −1115 LOC (the 33-line tombstone + ~3 lines in `views.py`). One of the smallest Phase E commits.

> **Post-execution note (2026-05-14):** Operation 2 (sys.path.append removal) collapsed to a no-op because commit 9 Aspect 5 had already removed it. Pre-deletion check 3 returned 0 hits (deviation from spec's expected 1), but the spec text "or whichever line it now sits on after commit 9" anticipated exactly this. Final LOC: −36 (only the tombstone deletion).

---

## 9. After commit 10 — Phase E retrospective tasks

These do NOT block Phase E completion. Listed as the natural next-step queue:

1. **Optional view-layer integration tests** for DTP and Peer failure envelopes (deferred from commit 9 Aspect 6). Low priority belt-and-suspenders.
2. **Phase D commencement.** TCS, Position Confirmation Analytics, DTP XAI narrative, Dashboard 5×3 + RTM Heatmap. All four sub-features build on the clean agent architecture.
3. **Phase F.5 — TAB5 Visual Redesign.** Parked from earlier; reactivates after Phase F's multimodal features land.
4. **Phase G — Full Epilogue.** Uses `extract()` entry point for Stage 1-3 dialogue. Uses D.4 Dashboard for Stage 0.
5. **Postgres-down environment guard.** Tooling polish from commit 4 observation.

---

## 10. Open follow-ups (long-tail)

Items surfaced during Phase E that are NOT Phase E scope but worth tracking:

- **D.3 (DTP XAI narrative)** introduces `ServiceAgent` parent and `XAIAgent` first concrete. The hierarchy is ready.
- **Phase G Epilogue Q&A** likely uses `extract()` — confirmed pattern via RTM precedent.
- **Phase F Multimodal voice transcription** likely uses `extract()` — user reviews before save.
- **Future agent prompt versioning.** When prompts evolve, the frozen `EXPECTED_*_PROMPT` constants in `apps/agents/tests/` will show clear diffs. No dedicated tooling needed; Python equality is the diff.

---

## 11. Dissertation chapter outline (suggested)

Suggested structure for "Multi-agent architecture for trustworthy AI in teacher PD":

### 11.1 Motivation

The pre-refactor architecture: monolithic procedural code, distributed atomicity, partial cost coverage, three DB idioms. Why this matters for the dissertation's CP-9 invariant and trustworthy AI claims.

### 11.2 Design decisions

Section 3 of this document, organised as four decisions with verbatim quotes from commit messages and tests.

### 11.3 The seven contributions

Section 3 D3b, one subsection per contribution, each with concrete commit evidence.

### 11.4 The pattern library

Section 4, six patterns. Reusable across future phases.

### 11.5 The audit story

Section 4 Pattern 5 + the commit 9 retrospective. The complementary-safety argument: incremental cutover maps prevent production breakage; deletion audits prevent archived-copy hazard survival.

### 11.6 Honest framing

The strengthening tally (1 of 4 cutovers). The "agent = class with a contract" honesty clause. The acknowledgement that the existing architecture was mostly CP-9 compliant. The refactor's value is broader than tightening one invariant.

---

## 12. References

Internal:

- All v1 through v10 design proposals (in chat history)
- All commit messages for commits 1, 1.5, 2-10 (in git history)
- `apps/agents/` source tree (the implementation)
- `apps/agents/tests/` test suite (the verification) + `prompt_fixtures/` (five frozen Layer-1 snapshots)
- `proodos_files/audit_rag_queries_provenance_20260512.md` (referenced in §3 D3b)

Project memory:

- `MODULE_CONTENT_GUIDE.md` for module-content patterns
- `PROODOS_UNIFIED_ROADMAP.md` for project-wide context (§3 Phase E for the retrospective)
- `userMemories` (project profile) for bug-preservation contracts

---

## Changelog: v10 → v11

| Change | Source |
|---|---|
| Document role redefined as canonical FINAL retrospective + commit-10 spec | Per agreement |
| §0 added — one-paragraph Phase E summary | New |
| §1 added — before/after architecture | New, canonical |
| §2 added — complete commit-by-commit table | New, canonical |
| §3 contributions expanded from 6 to 7 (audit complementarity) | Commit 9 finding |
| §4 patterns section formalised — six reusable patterns | Distilled from v1–v10 |
| §5 shared infrastructure canonicalised | Stable since v3 |
| §6 test invariant canonicalised with Layer-0 sub-rules | Accumulated through v3, v5, v7 |
| §8 commit-10 spec minimal — three operations | Per commit 9 closeout |
| §11 suggested dissertation chapter outline added | Per the document's dual purpose |
| §12 references list added | New |

---

## Post-execution addendum (2026-05-14)

Commits 9 and 10 landed as specified. Two small deviations worth recording for honest history:

- **Commit 9 hash drift.** A heredoc parse error in the first commit attempt left the modifications/new files unstaged; only the previously-`git rm`-staged deletions made it into the initial commit. Caught via `git status` post-commit; resolved via `git commit --amend --no-edit` after staging the missing files. Local branch (not pushed), so amend was safe. Final hash: `45969bc` (was `45131c5` pre-amend). Content identical to what this document describes.
- **Commit 10 operation 2 was a no-op.** Commit 9 Aspect 5 had already removed the `sys.path.append` hack, so the commit-10 §8.1 check 3 returned 0 hits instead of the spec's expected 1. The spec text "or whichever line it now sits on after commit 9" anticipated this; proceeded without surface. Final LOC for commit 10: −36 (only the tombstone deletion).

Phase E ended with a green suite. **316 tests.** The bar held.

---

*End of v11 — FINAL canonical Phase E document.*
