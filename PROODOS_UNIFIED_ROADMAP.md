# PROODOS EduAI — Ενοποιημένο Roadmap

**Έκδοση:** 4.0 — Απρίλιος 2026
**Σκοπός:** Ενιαίο σχέδιο πορείας. Αντικαθιστά όλα τα προηγούμενα idea/roadmap/patch αρχεία.

---

## Περιεχόμενα

1. Πρόλογος
2. Τι έχει ολοκληρωθεί
3. Φάσεις πορείας (A → I, plus deferred J)
4. Ξεπαρκαρισμένες ιδέες με αιτιολόγηση
5. Παρκαρισμένες ιδέες (future work / v2.0)
6. Σχεδιαστικές αρχές
7. Ευρετήριο αρχείων αναφοράς

---

## 1. Πρόλογος

Η πλατφόρμα PROODOS έχει συσσωρεύσει πολλαπλά roadmap αρχεία τους τελευταίους μήνες. Κάθε αρχείο γράφτηκε σε διαφορετική στιγμή. Πολλές ιδέες υλοποιήθηκαν, άλλες αναδύθηκαν στην πορεία (TAB1 redesign, TAB2 magazine, NotebookLM videos, M5/M8 orchestration). Αυτό το αρχείο είναι η ενιαία αλήθεια από εδώ και πέρα.

Δύο βασικοί κανόνες:

**Κανόνας 1.** Οι τεχνικές specs (RTM Part 3, DTP, Peer Synthesizer, Module Content Guide, EU AI Act Plan, M16 Spec και Patch) παραμένουν ως ξεχωριστά αρχεία. Δεν είναι ιδέες, είναι τεκμηρίωση που πρέπει να συμβουλεύεσαι όταν υλοποιείς. Λίστα στο Section 7.

**Κανόνας 2.** Όλα τα αρχεία ιδεών και πλάνων που αναφέρονται στο Section 7 ως "διαγράφονται" αντικαθίστανται από το παρόν αρχείο.

---

## Τρέχουσα κατάσταση (snapshot — 2026-05-24)

*Latest update (2026-05-24, Phase G closure): **Phase G COMPLETE — with strategic deprecation.** After G.0-G.3 shipped, G.6a-c implemented, and three sequential prompt-engineering correction cycles (§24 → §24.11 → §24.12) on the Aletheia dialogue agent, live re-testing of §24.12 showed example-verbatim recitation — the third failure in the same family. Root-cause analysis (reflection fatigue + RPE framework dilution + technical fragility of Flash + reflective-companion register) concluded that the problem is structural, not prompt-surface. **PI decision (2026-05-24): Aletheia is removed from the PROODOS Epilogue.** The Epilogue narrows to **Stage 0 Personal Evolution Dashboard + Continue button**. Dialogue + Portrait views/templates deactivated in place; PDF infrastructure preserved for Phase H certificate of attendance; Aletheia visual identity + persona prompt-craft preserved for new **Phase J** (deferred Aletheia chatbot re-introduction, scope TBD post-pilot, 4 candidate placements catalogued: onboarding companion, always-on help, AI literacy sandbox, post-pilot deferred). Deprecation doc: `proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md`. Master proposal §25 amended with deprecation pointer + reading guide. Roadmap §3 Phase G marked complete with deprecation note; new §3 Phase J entry added. Remaining code-bearing work: **Phase G.4** (M15 content alignment, pre-pilot) + **Phase H** (closing flow + certificate of attendance, reuses preserved PDF + Article 50(2) pattern).*

*Earlier (2026-05-21, Phase F complete): **Phase F COMPLETE** — the TAB5 redesign is delivered and verified end-to-end. TAB5 is now a five-screen magazine wizard (four parts + a review screen, in the TAB1/TAB2 editorial register) with voice input built in: per-screen microphone clusters on the Web Speech API, one reused SpeechRecognition instance, synchronised language selectors, feature detection, and an Article 50 notice. The post-submit feedback panels (RAG/RTM/DTP/peer) received a magazine visual pass with the Article 50 / XAI / HITL contract preserved; the completed-state DTP ordering was fixed (it had rendered before the other panels). Input modality (text/voice/mixed) is recorded on `reflection_input_modality` for the voice-vs-text research dimension. Six commits: 1705e27 (F.1a field), ba289c0 (stage 1 wizard), 4132455 (stage 2 voice), a35d1ac (stage 3 magazine pass), 37e0aa9 (DTP fix), 02720ef (stage 4 modality). Frontend-only after F.1a; one migration (the modality field). Canonical doc: `proodos_files/F_TAB5_REDESIGN_DESIGN_PROPOSAL_v1_20260520.md`. The voice-input notice wording was approved, and a design-refresh pass (screen-transition motion, review-screen polish, magazine result panels, a sticky post-submit results section-nav) was implemented and verified — commits 527bb48 and b8ee15f. Phase F is closed; no open items — the voice-input rationale was added to the literature note (`Literature_Review_Synthesis_Note(1).md` §14, 2026-05-21, four verified references). Remaining code-bearing work: Phase G, Phase H.*
*Earlier (2026-05-20, Phase F redesign pivot): **Phase F redefined — TAB5 redesign with voice.** Two decisions after the voice-only scoping: (1) F.1b (server-side transcription agent) cancelled — a live Web Speech API test was satisfactory, so no server path, no toggle, no Platform Settings page, no second migration. (2) The per-part four-microphone build hit a Web Speech API multi-session reliability wall, so F.1 (voice) and the parked F.5 (TAB5 redesign) merge: Phase F becomes a single piece of work — rebuild TAB5 as a four-screen wizard in the magazine style (TAB1/TAB2 family) with voice built in, one microphone per screen (which sidesteps the multi-session problem). Backend untouched — no migration, no new endpoint, the submit/RAG/RTM/DTP pipeline unchanged; it is a rewrite of `tab5_reflection.html` plus a ~2-line view change for modality tracking. The `reflection_input_modality` field (F.1a commit 1) stays valid. Canonical doc: `proodos_files/F_TAB5_REDESIGN_DESIGN_PROPOSAL_v1_20260520.md` (draft, awaiting review); supersedes the F.1 voice proposal.*
*Earlier (2026-05-20, Phase F kickoff): **Phase F scoped to voice-only.** F.2 (image input) removed from Phase F. Rationale: the TAB5 reflection is prospective — all four parts ask what the teacher learned and what they will do, before any AI-integrated lesson has been taught — so no classroom artefact exists at reflection time for an image upload to attach to. The F.2 pitch ("show me what you tried, don't just describe it") presupposes retrospective reflection on completed practice, which TAB5 is not; and the Mayer multimedia-learning justification concerned how learning content is presented to learners, not the reflection-input modality. Image-based reflection is re-filed as a candidate for Phase G (Epilogue), where reflection is retrospective and a real artefact exists. Phase F is now F.1 (voice) only; the F.5 redesign trigger updated accordingly.*
*Earlier (2026-05-20, Phase D complete): **Phase D COMPLETE** — D.4 (the cohort dashboard) landed and Phase D is now fully done (D.1+D.2+D.3+D.4). D.4 added two cohort visualisations to the `/analytics/` dashboard — a UNESCO 5×3 completion matrix and a 16×15 RTM coverage heatmap; the dashboard was also made consent-restricted with date/subject filters. Analytics suite 24 tests pass. Canonical doc: `proodos_files/D4_DASHBOARD_DESIGN_PROPOSAL_v1_20260520.md`. A related observation — the teacher dashboard duplicates the Modules menu — is logged as TD-021 for a later UX pass. Remaining code-bearing work: Phase F, F.5, G, H.*
*Earlier (2026-05-20, later): **Phase D.2 COMPLETE** — Engagement Depth. A second section on the `/analytics/` dashboard reports the Engagement Depth Score (EDS) — the share of RTM tensions a teacher actively engaged with (`position_confirmed` telemetry), separating surface from deep engagement, the basis for the "beyond completion rates" dissertation argument. Researcher-facing, read-only, no migration; analytics suite 14 tests pass. Canonical doc: `proodos_files/D2_ENGAGEMENT_DEPTH_DESIGN_PROPOSAL_v1_20260520.md`. Phase D now has only D.4 remaining.*
*Earlier (2026-05-20): **Phase D.1 COMPLETE** — the AI Output Relevance Profile. A new `apps/analytics/` app aggregates the `AIOutputDispute` ratings teachers give on the RAG/RTM/DTP outputs into a researcher-facing, staff-only perceived-relevance profile (cohort + per-teacher). The roadmap's "Trust Calibration Score" name was rejected on construct-validity grounds (no reliability ground-truth axis); peer is excluded as a separate construct (TD-019). Read-only, no migration; 10 tests pass. Canonical doc: `proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md`. Phase D now has D.2 and D.4 remaining.*
*Earlier (2026-05-19): **Phase D.3 COMPLETE** — the DTP sub-track delivered in two parts. **D.3a** redefined the Developmental Trajectory Predictor from a single cross-aspect comparison into a dual-signal model (Vertical Continuity Signal + Temporal Shift Signal), descriptive-only, no thresholds/labels in the pilot. **D.3b** added the `XAIAgent` — the first concrete `ServiceAgent` — producing a faithful, domain-driven natural-language explanation of the DTP composite. Both committed and live-verified on M6. Canonical docs: `proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md` and `proodos_files/DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md`. See §3 Phase D for the full breakdown. Phase D now has D.1 (TCS), D.2 (Position Confirmation Analytics), D.4 (Dashboard) remaining.*
*Earlier (2026-05-14): **Phase E COMPLETE** — 11 commits, monolith deleted, 316 tests green, hierarchy of 4 agents under `apps/agents/` with two public entry points (`generate()` for "AI commits, human disputes" + `extract()` for "AI proposes, human ratifies"). Seven distinct architectural improvements delivered (atomic strengthening at one site + dual entry points + cost tracking 1/4→4/4 + DB-idiom unification + dead-code findings + silent-failure antipattern exposure + pre-deletion audits as complementary safety). See §3 Phase E for the full retrospective + §4.3 for the closed parked-idea entry.*
*Earlier (2026-05-13): Phase F.5 (TAB5 Visual Redesign) added to remaining work as a parked entry awaiting Phase F.1+F.2 functional completion. See §3 Phase F.5 for the full addendum content.*

Bird's-eye view. Αυτό το block ενημερώνεται σε κάθε session-end. Τα detail sections (§2, §3) δίνουν depth· εδώ είναι το at-a-glance index για να ξέρει το επόμενο παράθυρο πού στεκόμαστε.

### Code-bearing work — DONE

| Phase | Status | Reference |
|---|---|---|
| **A.** Module content (M1-M15) + RAG ingest + browser tests | ✅ Complete | §3 Phase A |
| **B.** Validation & Cleanup | ⚠️ Partial — B.2 (video badges) + B.4 (Edit Profile via C.2.1) done· B.1 (Content Validation Matrix) + B.3 (code cleanup) trickling | §3 Phase B |
| **C.** Onboarding + EU AI Act + GDPR | ✅ **100% code-bearing complete** — 15 commits, 214 tests pass. Career Stage Step 2 gap closed by Option A decision 2026-05-13 (deferred to post-pilot research direction — TD-020). | §2.8, §3 Phase C |
| **E.** Multi-agent refactor | ✅ **100% complete (2026-05-14)** — 11 commits, monolith deleted, 316 tests pass. Four named agents under `apps/agents/` (`RAGFeedbackAgent`, `RTMAgent`, `DTPAgent`, `PeerSynthesisAgent`) all inheriting from `BaseAIAgent` with two public entry points (`generate()` + `extract()`) and shared infrastructure (LLM client, cost tracker, audit logger, unified DB helper). Seven distinct architectural improvements delivered. | §3 Phase E |
| **D.3** DTP sub-track (D.3a redefinition + D.3b XAI narrative) | ✅ **Complete (2026-05-19)** — D.3a redefined the DTP into a dual-signal model (Vertical Continuity + Temporal Shift), descriptive-only. D.3b added the `XAIAgent` — first concrete `ServiceAgent` under a new `ServiceAgent` parent — a faithful, domain-driven explanation of the DTP composite. Live-verified on M6; agent suite 123 tests pass. | §3 Phase D |
| **D.1** AI Output Relevance Profile | ✅ **Complete (2026-05-20)** — new `apps/analytics/` app: a researcher-facing, staff-only aggregation of the `AIOutputDispute` ratings into a perceived-relevance profile (cohort + per-teacher, by feature/module/subject). "Trust Calibration Score" rejected on construct-validity grounds; peer excluded as a separate construct (TD-019). Read-only, no migration. | §3 Phase D |
| **D.2** Engagement Depth (Position Confirmation Analytics) | ✅ **Complete (2026-05-20)** — a researcher-facing Engagement Depth Score over the RTM `position_confirmed` telemetry (share of tensions a teacher actively engaged), with supporting signals and module/subject slices. Rendered as a section on the unified `/analytics/` dashboard. Read-only, no migration. | §3 Phase D |
| **D.4** Dashboard: UNESCO Matrix + RTM Heatmap | ✅ **Complete (2026-05-20)** — two cohort visualisations on the `/analytics/` dashboard: a UNESCO 5×3 completion matrix and a 16×15 RTM coverage heatmap. The dashboard was also made consent-restricted with date/subject filters. **Phase D complete** (D.1+D.2+D.3+D.4); analytics suite 24 tests pass. Teacher-dashboard redundancy logged as TD-021. | §3 Phase D |
| **F.** TAB5 redesign (magazine wizard + voice) | ✅ **Complete (2026-05-21)** — TAB5 rebuilt as a five-screen magazine wizard (four parts + review) with Web Speech API voice input (per-screen mic clusters, one reused SpeechRecognition); post-submit panels given a magazine pass with the Article 50/XAI/HITL contract preserved; completed-state DTP ordering fixed; input-modality tracking (text/voice/mixed). End-to-end verified. Six commits. | §3 Phase F |

**Phase C breakdown:**

  - **C.2.0–C.2.5b** — AI Disclosure modal + middleware + onboarding 4-step flow + AILST T0/T1/T2 administration + Epilogue placeholder + Confirm interstitial
  - **C.4** — Privacy Dashboard (per-consent revoke + GDPR Art. 15 JSON export + Art. 17 anonymisation)
  - **C.1** — AI Impact Assessment (EU AI Act Article 50(1) transparency notice)
  - **C.6 (in-phase, not the pre-prod one)** — Sequential prerequisite gates (TD-012 + TD-013)
  - **C.3** — Machine-readable AI markers (EU AI Act Article 50(2)) — `AIArtefactProvenance` model + forward-write hooks + export mirror (`export_version` v1→v2) + HTML data-attrs σε 9 rendering sites + `Generated at` row σε υπάρχοντα XAI panels + νέο peer XAI panel + page-level JSON-LD + reusable `{% ai_provenance %}` + `{% ai_provenance_jsonld %}` template tags
  - **CP-11** wipe script: READY (operational, executed σε §3.C.6 pre-production sequence)

### Code-bearing work — REMAINING

| Item | Effort | Reference |
|---|---|---|
| **Phase G** — Full PROODOS Epilogue (Stage 0..3 + Gemini dialogue + Learning Portrait PDF — TD-011) | Multi-session | §3 Phase G |
| **Phase H** — Closing flow (3-timepoint T0/T1/T2 design + Certificate of Attendance PDF + Dashboard redesign per TD-021 + Optional follow-up consent at onboarding) | Multi-session | §3 Phase H |
| **Phase I** — Dissertation writing | External (John) | §3 Phase I |

### Pre-production tasks (post-all-phases — executed once before pilot launch)

These are **operational tasks, NOT in-phase code-bearing work**. They run after every code-bearing phase is complete (or at minimum the platform is feature-frozen for the pilot) AND immediately before participant recruitment. They are NOT Phase C blockers. The code is ready; what's missing is the timing trigger (IRB approval + final code freeze).

| Step | Trigger | Reference |
|---|---|---|
| **C.5** — IRB-driven copy revision (mint `V2_IRB_REVISED` constants σε `apps/compliance/copy.py`, bump 3 version pins, re-deploy + re-ack staff) | IHU IRB feedback arrives (CP 7 + CP 10) | §3.C.5 |
| **C.6 (pre-prod)** — Pre-pilot operational sequence (backup → `backfill_ai_provenance --commit` → CP-11 wipe → re-ack staff → smoke test → pilot recruitment) | All phases complete + C.5 applied + IRB approved | §3.C.6 |

### Tech debt summary

| State | TDs |
|---|---|
| **Resolved** | TD-008 (consent revoke clear ack), TD-012 (sequential gate), TD-013 (Epilogue M15 gate), TD-017 (machine-readable markers — closed in C.3), TD-005 (cp1253 encoding — closed in Phase E commit 1.5 via `manage.py` UTF-8 stdio guard, 2026-05-13), **TD-019 (peer synthesis dispute UX — redefined as a usefulness signal and resolved, 2026-05-19)** |
| **Active deferred to post-pilot Phase G/H or beyond** | TD-001, TD-002, TD-003, TD-004, TD-009, TD-010, TD-011, TD-014, TD-015, TD-016, **TD-018 (per-artefact dispute deep-links)**, **TD-020 (post-hoc career-stage exploratory analysis — 2026-05-13)**, **TD-021 (teacher dashboard duplicates the Modules menu — 2026-05-20)** |
| **Convenience-when-possible** | TD-006 (.gitignore ephemerals), TD-007 (M1 placeholder squash) |

Full TD register: `proodos_files/TECH_DEBT_LOG.md`.

---

## 2. Τι έχει ολοκληρωθεί

### 2.1 Modules (περιεχόμενο, RAG ingest, browser-tested)

**Πλήρως υλοποιημένα όλα τα 15 modules:** M1 έως M15.

Όλα τα TABs ολοκληρωμένα και των 15 modules με RAG ingest.

### 2.2 TAB2 Subject Boxes

Τα TAB2 σε όλα τα modules έχουν 3 subject boxes (part2, part3, part4). Υπάρχουν ηθελημένες εξαιρέσεις (π.χ. M15 με 2 boxes).

### 2.3 NotebookLM Videos σε όλα τα TAB2

Νέα videos σε κάθε TAB2 παραγμένα από το NotebookLM με source το ίδιο το TAB2 content. Λειτουργούν ως οπτική εισαγωγή για visual learners.

Disclaimer που συνοδεύει κάθε video: *"This video prepares you for the content — it doesn't replace it. The full module content follows below."*

### 2.4 Πλατφόρμα-wide υλοποιήσεις (Απρίλιος 2026)

Λεπτομερές break-down υπάρχει στα session logs. Συνοπτικά:

**Optimisation Patch — όλα τα 15 modules:** subject_box_part3, νέα persona "Dimitris" στο `other`, TAB4 XAI explanations 3 στρωμάτων, generic TAB4 template, letter-based correct answers, subject box normalisation (720 records), RAG re-ingest.

**RTM Redesign:** minimum tensions από 2 σε 1, auto-save με `position_confirmed` flag, διάκριση "δεν ασχολήθηκε" από "συνειδητά επέλεξε ουδέτερο".

**TAB1 Magazine Redesign:** typographic hero, info bar, 5-aspect colour system.

**Subject Intro Hooks (Zhou Idea 2):** 255 records (16 subjects + 1 Universal × 15 modules).

**TAB2 Magazine Upgrade:** sticky Part navigator, aspect-coloured numerals, reading progress bar, Compact toggle.

**M5/M8 Co-orchestration Shift (Zhou Idea 5):** νέο Part 5 σε M5 και M8 με orchestration framing.

**XAI Layer:** RAG XAI panel, EU AI Act "Limited Risk" statement, RTM XAI panel.

**HITL Layer:** RAG και RTM HITL ratings, dispute form, `modules_aioutputdispute` table.

**Data Normalisation:** unesco_aspect rows, proficiency_level case fixes, M8 module_overview unwrapped.

**Αρχεία αναφοράς για όλα τα παραπάνω:**
- `M1_SYSTEM_VERIFIED.md` — master architecture reference
- `MODULE_CONTENT_GUIDE.md` — content development guide
- `SESSION_LOG_OPT_PATCH_APR2026.md` — Optimisation Patch
- `M5_M8_ORCHESTRATION_CHANGELOG_APR2026.md` — co-orchestration shift
- `SESSION_LOG_APR2026_TAB1.md` — TAB1 redesign
- `SESSION_LOG_TAB2_MAGAZINE_APR2026.md` — TAB2 magazine
- `SUBJECT_BOX_NORMALIZATION_LOG_APR2026.md` — normalisation
- `DISSERTATION_TAB5_XAI_HITL.md` — XAI/HITL design

### 2.5 Research Instruments

- Reflective Tension Mapper (RTM) — `RTM_Feature_Specification_Part3.md`
- Cross-Specialty Peer Synthesizer — `Cross_Specialty_Peer_Synthesizer_Documentation.md`
- Developmental Trajectory Predictor (DTP) — `DTP_Documentation_Mar2026.docx`

### 2.6 Επιστημονικές δημοσιεύσεις

- Paper RPE Framework — submitted στο Electronics journal — `Reconceptualizing_Prompt_Engineering_as_Reflective_Professional_Practice_FINAL_VERSION.pdf`

### 2.7 UNESCO Compliance Validation (Phase A Tier 1+2+3+4 — Μάιος 2026)

**Final state:** **163/170 STRONG (~95.9%)** · 4 Cluster D defendable design choices · 3 Cluster C pilot-deferred indicators · **170/170 defensible position** για viva.

**Trajectory:** 127 (baseline) → 138 (Tier 1+2) → 142 (Tier 3) → 145 (Sprint 1) → **163 (Sprint 2 final post-A16)**. +36 net STRONG indicators across 4 tiers; +21.2 percentage points coverage lift. **First crossing of 95% threshold at A16 (6 May 2026).**

**Cluster B 6-of-6 closure ratio:** 4 audit-only sync (A11/A12/A13/A14) + 2 substantive Branch B (A15/A16). 4+2 ratio more defendable in viva than hypothetical 5+1 outlier.

**Methodology corpus:** 5 formalised audit-first pattern variants (A11 sync residue · A12 UNESCO triplet cross-level · A13 composite cross-aspect · A14 multi-source inconsistency-resolution · A15 stress-test course-correction) + 2 auxiliary methodologies (UNESCO Qualifier Reading · A14 low-cardinality sub-variant).

**Cluster D — 4 indicator-level defendable design choices:**
1. **CG1.2.2** local/national regulatory frameworks (M6) — international scope decision
2. **CG2.2.1** AI safety taxonomy ορολογία (M7) — dilemma framing pedagogically stronger
3. **CG2.3.3** multi-stakeholder regulatory simulation (M12) — institutional analogue
4. **CG3.3.1** programming/data/algorithms hands-on (M13) — UNESCO Section 2.5 K-12 scoping

**Cluster C — 3 pilot-deferred indicators:**
1. **LO4.3.4** teacher-facing learning analytics dashboard (M14)
2. **CG5.3.2** institutional tracking AI co-creation workshops (M15)
3. **LO5.3.3** organisation-wide trajectory aggregation (M15)

**Σημείωση ορολογίας:** Στα authoritative source files η φράση "Phase A Tier 4" αναφέρεται στις audit-correction εργασίες της Sprint 1 + Sprint 2 (Μάιος 2026) που έφεραν την κάλυψη από 142/170 σε 163/170. Αυτή η εργασία είναι λειτουργικά μέρος του **Phase B.1 — Content Validation Matrix συμπλήρωση** (Section 3.B), αλλά διατηρεί την "Phase A Tier N" ορολογία για continuity με τα predecessor docs.

**Αρχεία αναφοράς:**
- `proodos_files/UNESCO_VALIDATION_STARTING_POINT.md` — single canonical entry-point για future synthesis sessions (THIS IS THE PRIMARY HANDLE)
- `proodos_files/CONTENT_VALIDATION_MATRIX.md` — per-module content + UNESCO mapping
- `proodos_files/CONTENT_GAPS_LOG.md` — per-gap closure history
- `proodos_files/PHASE_A_REMAINING_GAPS_POST_TIER3.md` — cluster classification (post-audit-resolution)
- `proodos_files/platform_changes_log.md` — chronological patch log
- `proodos_files/audits/UNESCO_INDICATOR_AUDIT_RESOLUTION.md` — 8 May 2026 audit-resolution verdict
- `proodos_files/audits/*.md` — 16 per-indicator independent audit deliverables (Sprint 1 + Sprint 2 A1-A16)

**Synthesis-phase consolidation files (pending):** `METHODOLOGY_CONSOLIDATION.md`, `CLUSTER_D_DEFENCE.md`, `CLUSTER_C_DEFERRAL.md`, `AUDIT_DELIVERABLES_INDEX.md`. Total estimated effort ~6-10h distributed across 3-4 sessions.

### 2.8 Phase C — onboarding, AILST, GDPR, EU AI Act compliance (Μάιος 2026)

**Status:** Code-bearing Phase C work complete στα 15 commits (11 από το προηγούμενο arc + 4 του C.3 σε αυτό το παράθυρο). Δύο gaps στο C.2 sub-scope παραμένουν (Career Stage Differentiation step + AI-TPACK step, βλ. 3.C.2). C.3 ολοκληρώθηκε σε αυτό το παράθυρο — βλ. 3.C.3 για τις 4 commits.

**214 Phase C tests pass** στις πέντε αλλαγμένες apps (compliance 115 · users 23 · ailst 47 · modules 13 · epilogue 16). Aύξηση 31 tests από το C.3 arc (10 storage + 6 write hooks + 8 read paths + 7 template tags/JSON-LD).

**Migrations εφαρμοσμένες σειριακά:**

| Migration | Σκοπός | Pre-apply backup |
|---|---|---|
| `compliance/0001_initial` | M1 — `consent_records` (Django ORM replacement) | `pre_migration_backup_phaseC_M1_20260509.sql` |
| `users/0007_teacherprofile_*` | M2 — 4 Phase C personalisation fields | `pre_migration_backup_phaseC_M2_20260509.sql` |
| `compliance/0002_drop_dead_schema` | Γ.1 — dead-schema cleanup (22 tables + 2 functions dropped) | `pre_migration_backup_phaseC_GAMMA1_20260509.sql` |
| `users/0008_teacherprofilehistory` | M3 — audit history table + signal | `pre_migration_backup_phaseC_M3_20260509.sql` |
| `ailst/0001_initial` + `0002_seed_ailst_en` | M4 — AILST instrument schema + 36-item EN seed | `pre_migration_backup_phaseC_M4_20260510.sql` |
| `ailst/0003_ailstresponse` | M5 — AILST response model + scoring helper | `pre_migration_backup_phaseC_M5_20260510.sql` |
| `compliance/0003_consentrecord` + `0004_migrate_teacherprofile_consents` | M6 — `ConsentRecord` model + legacy boolean backfill | `pre_migration_backup_phaseC_M6_20260510.sql` |
| `users/0009_drop_not_null_subject_grade` | Schema drift hotfix (mid-C.2.3) | (no separate backup — model already declared nullable) |
| `epilogue/0001_initial` | C.2.5 — `epilogue_completions` table | `pre_migration_backup_phaseC_C25_20260511.sql` |
| `users/0010_research_data_opted_out` | C.4 — durable research-opt-out flag | `pre_migration_backup_phaseC_C4_20260512.sql` |

**Implementation arc:**

- **C.2.0** — AI Disclosure modal + `AIDisclosureMiddleware` + `apps.compliance.copy` consent text constants (commit `c115372`).
- **C.2.1** — Profile Edit extension for the 3 new M2 personalisation fields (commit `e86a727`).
- **C.2.2** — Step 3 consent refactor: two independent consents (`research_participation` + `data_sharing`), `record_consent` supersede semantics, M6 sync signal (commit `a117220`).
- **C.2.3** — AILST T0/T1/T2 administration views + flow, parameterised on timepoint, mobile-aware Likert UI (CP 8 closed) (commits `014789e` + `4748302` + 2 hotfixes).
- **C.2.4** — M5 → T1 gating wired into `mark_tab_complete`, JSON `ailst_redirect_url` mechanism + frontend handler updates (commit `f8501ef` + leak hotfix).
- **C.2.5** — PROODOS Epilogue placeholder + M15 → Epilogue → T2 reroute. New `apps.epilogue` app with `EpilogueCompletion` model. Full Epilogue Stage 0..3 + Learning Portrait PDF deferred to TD-011 (commit `bec8951`).
- **C.2.5b** — Confirm interstitial after Step 3 (CTA-dropout UX fix) (commit `bdb6670`).
- **C.4** — Privacy dashboard at `/profile/privacy/`: three per-consent revoke endpoints, Art. 15 JSON data export (`gather_user_export`), Art. 17 anonymisation (`anonymize_user` Python service). Closes TD-008. Three commits (`eb36db1` + `6055616` + `1dee58b`) plus one in-flight correction (`2cd0a04` — `DELETE` instead of `ΔΙΑΓΡΑΦΗ` to match the English UI).
- **C.1** — EU AI Act Article 50 transparency notice. Seven-section AI Impact Assessment at `/about/ai-act-compliance/`, replacing the C.2.0 stub. Versioned as `AI_IMPACT_ASSESSMENT_V1_PRE_IRB` (commit `f64cbda`).
- **Footer + entry-point wiring** — `base.html` + `landing.html` footers + Privacy dashboard now all link to the transparency notice. Also fixed "International University of Greece" → "International Hellenic University" in the `base.html` footer (commit `22d38ad`).
- **C.6 (TD-012 + TD-013)** — pre-pilot sequential progression gates. `ModuleDetailView` blocks out-of-order navigation, `mark_tab_complete` returns 409, `/epilogue/` gated on M15 completion. Staff/superuser bypass. (commit `050aba7`).
- **CP-11** — `scripts/cp11_wipe_test_users.py` — non-staff user wipe script with `--dry-run` default and interactive YES confirmation. Cascades through Django ORM + explicit raw-SQL DELETE on `rag_queries` (commit `950e44a`).

**Closed tech-debt items this phase:** TD-008 (AI Disclosure revocation must clear ack timestamp), TD-012 (sequential module gate), TD-013 (Epilogue gating on M15).

**Active tech-debt items added this phase, all deferred to post-pilot:**

| TD | Topic | Defer to |
|---|---|---|
| TD-010 | Post-pilot AILST score reveal page | Phase G/H |
| TD-011 | Full PROODOS Epilogue (Stage 0..3 + Learning Portrait PDF) | Phase G (covered already at Phase G in this roadmap) |
| TD-014 | Selective deletion of individual reflections / AILST responses | Post-pilot |
| TD-015 | Data export as PDF (in addition to JSON) | Post-pilot |
| TD-016 | 7-year ConsentRecord retention cleanup management command | Phase H |
| TD-017 | Machine-readable AI content markers (Article 50(2)) — C.3 | **Επόμενο παράθυρο** (βλ. 3.C.7) |

**Session logs covering Phase C:**

| Log | Range |
|---|---|
| `proodos_files/SESSION_LOG_PHASE_C_M1_M3_20260509.md` | M1 + M2 + Γ.1 + M3 migrations |
| `proodos_files/SESSION_LOG_PHASE_C_M4_20260510.md` | M4 AILST seed |
| `proodos_files/SESSION_LOG_PHASE_C_M5_M6_20260510.md` | M5 AILST response + M6 ConsentRecord |
| `proodos_files/SESSION_LOG_PHASE_C_C20_C22_20260510.md` | C.2.0 + C.2.1 + C.2.2 |
| `proodos_files/SESSION_LOG_PHASE_C_C23_C25_20260511.md` | C.2.3 + C.2.4 + C.2.5 + C.2.5b + hotfixes |
| `proodos_files/SESSION_LOG_PHASE_C_C4_C1_CP11_20260512.md` | C.4 + C.1 + footer wiring + C.6 + CP-11 |
| `proodos_files/C4_DESIGN_PROPOSAL_PRIVACY_DASHBOARD.md` | Design D1-D14 + 8 CP refinements για το C.4 |
| `proodos_files/C23_DESIGN_PROPOSAL_20260510.md` | Design για C.2.3 |
| `proodos_files/EPILOGUE_C25_IMPLEMENTATION_NOTES_20260511.md` | Epilogue placeholder specifics |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | Master changelog (συμπληρώνεται entry ανά piece) |
| `proodos_files/TECH_DEBT_LOG.md` | Όλο το TD log |

---

## 3. Φάσεις πορείας

Οι φάσεις ακολουθούν αυστηρή σειρά. Phase A έχει ήδη ολοκληρωθεί.

---

### Phase A — Ομοιογένεια M2–M15 (ΟΛΟΚΛΗΡΩΘΗΚΕ)

Όλα τα 15 modules content-complete με RAG ingest, NotebookLM videos, και browser tests.

---

### Phase B — Validation & Cleanup

**Στόχος:** Επιβεβαίωση ότι η πλατφόρμα είναι έτοιμη για τις επόμενες φάσεις. Καμία νέα δουλειά — μόνο επικύρωση και καθαρισμός.

#### B.1 — Content Validation Matrix συμπλήρωση

Πρώτη προτεραιότητα. Ολοκλήρωση του `CONTENT_VALIDATION_MATRIX.md` ώστε κάθε TAB και κάθε module να έχει επιβεβαιωμένη πληρότητα.

**Αρχείο αναφοράς:** `CONTENT_VALIDATION_MATRIX.md`

#### B.2 — Video duration badges (ΟΛΟΚΛΗΡΩΘΗΚΕ)

Όλα τα video badges έχουν πλέον σωστές τιμές duration.

#### B.3 — Code cleanup

- Αφαίρεση debug print statements από `views.py`, `rag_query_system.py`, και templates
- Καθαρισμός `migrations/` → `sql/` directory
- Drop legacy backup tables (αν υπάρχουν)

**Αρχείο αναφοράς:** `SESSION_LOG_OPT_PATCH_APR2026.md` (PENDING table).

#### B.4 — Edit Profile page

Σελίδα όπου ο εκπαιδευτικός μπορεί να ενημερώσει τα στοιχεία του profile του (subject_area, grade_level, teaching_years, κλπ). Το backend υπάρχει ήδη — λείπει το frontend.

**Αρχείο αναφοράς:** `M1_SYSTEM_VERIFIED.md` (TeacherProfile, 27 fields).

---

### Phase C — Onboarding Redesign + EU AI Act Compliance (παράλληλα)

**Στόχος:** Ένα νέο onboarding που εξυπηρετεί ταυτόχρονα 4 σκοπούς:
- EU AI Act Article 50 compliance (AI disclosure)
- Career Stage Differentiation (Zhou Idea 6)
- AILST baseline (T0 για το pilot — Ning et al. 2025)
- AI-TPACK profiling (Eyal 2025) — προαιρετικά

Δουλεύεις στον ίδιο κώδικα μία φορά αντί για τέσσερις.

#### C.1 — AI Impact Assessment

**Status:** ✅ DONE — HTML version live at `/about/ai-act-compliance/`, seven sections covering System / AI components / Risk classification / Mitigation + oversight / Data handling + retention / Participant rights / Contact. Versioned as `AI_IMPACT_ASSESSMENT_V1_PRE_IRB` in `apps/compliance/copy.py`. Replaces the C.2.0 stub. Commit `f64cbda`.

**Note on the "PDF" framing in the original roadmap:** the deliverable is currently HTML rather than a 5-page formal PDF. The HTML page satisfies Article 50(1) transparency obligation (machine- and human-readable, persistently reachable from three footer entry points). A PDF export pass is deferred — same TD entry as the data-export PDF (TD-015) covers it.

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 1). The implementation deviated from the "5σέλιδο PDF" framing per pragmatic decision documented in `proodos_files/SESSION_LOG_PHASE_C_C4_C1_CP11_20260512.md`.

#### C.2 — Onboarding Redesign (ενοποιημένο)

**Status:** ⚠️ ΜΕΡΙΚΩΣ DONE — Step 1 και Step 3 ολοκληρώθηκαν. Step 2 (Career Stage RAG personalisation) και Step 4 (AI-TPACK) **δεν έγιναν** σε αυτή τη φάση. Βλ. ξεχωριστά bullets:

**Step 1 — AI Disclosure Modal (Article 50(1))** — ✅ **DONE** (C.2.0, commit `c115372`)
- `AIDisclosureMiddleware` slot between Authentication και Messages middleware
- Modal at `/onboarding/ai-disclosure/` with "I acknowledge and continue" + "Or log out" links
- `ConsentRecord` write path with `consent_type='ai_disclosure'` via `record_consent` service
- Versioned as `AI_DISCLOSURE_TEXT_V1_PRE_IRB`
- TD-008 (revocation must clear ack timestamp) closed in C.4 commit 1

**Step 2 — Career Stage Capture** — ⏸ **DEFERRED to post-pilot research direction (decision 2026-05-13)**

Το `teaching_years` field υπάρχει ήδη στη DB (από M2) και συλλέγεται στο onboarding Step 1 form. Η δεύτερη μισή του spec (χρήση της τιμής στις RAG queries + feedback emphasis logic per career stage) **δεν θα υλοποιηθεί πριν το pilot** — Option A approved 2026-05-13.

**Rationale (four points):**

1. **Already documented as limitation.** TAB1 dissertation chapter §8.1 explicitly states that PROODOS does not personalise at career-stage level και ότι "the current design accepts this limitation." Adding career-stage differentiation now would invalidate the acknowledged scope.
2. **Pedagogical claim risk.** The proposed mapping (early-career → ethics framing, experienced → workload relief) lacks documented theoretical/empirical backing. Implementing it χωρίς literature support would create an unjustified design claim στο dissertation.
3. **Research design integrity.** Differentiated treatment now requires IRB protocol amendment, statistical plan update, και potential per-stage stratified analysis (underpowered σε ~25 users per stage).
4. **Pilot timing.** Phase C είναι structurally complete και frozen for IRB review. Adding new AI behaviour risks delaying IRB submission.

**Personalisation narrative preserved without career-stage work.** The dissertation already supports:
  - Hybrid personalisation = pre-generated subject content + RAG retrieval + reflection-adaptive AI
  - Subject (16 values) + grade-band = segmentation axes
  - Reflection-adaptive AI (RTM/DTP/RAG/peer) = true per-individual personalisation

**Post-pilot follow-up (optional, exploratory):** TD-020 opened to investigate whether career stage (via existing `teacher_profile.teaching_years`) predicted differential outcomes in AILST T2-T0 deltas, RTM tension patterns, or reflection quality. Becomes a post-hoc research question, NOT a treatment variable.

**Action:** none required pre-pilot. No code changes. No IRB amendment. No dissertation chapter rewrite.

**Step 3 — AILST Baseline (T0)** — ✅ **DONE** (C.2.3, commits `014789e` + `4748302`)
- Πλήρης AILST scale (Ning et al. 2025, 36 items, 4 factors) στο M4 seed
- T0/T1/T2 administration parameterised σε ένα view set
- Mobile Likert UI (CP 8 closed: radio-table desktop / stacked card mobile, full anchors σε κάθε breakpoint)
- Resume-from-partial state machine με cannot-skip-ahead + select_for_update concurrency guard
- Scoring (`apps.ailst.scoring`): CP 5 anchor mapping + CP 4 reverse (K1/A3/E3) + CP 6 mean-of-factor-means, mathematically verified end-to-end on `smith@example.com` smoke test
- T1 triggers from M5 completion (C.2.4); T2 triggers from PROODOS Epilogue completion (C.2.5 reroute — see G.x in Phase G)
- D4 decision: factor scores hidden during pilot for all timepoints; post-pilot reveal as TD-010

**Step 4 — AI-TPACK self-assessment** — ❌ **PARKED**
- Original spec marked as "προαιρετικό" + "μπορεί να μπει σε δεύτερη φάση αν το onboarding γίνει υπερφορτωμένο"
- Decision: parked as future-work entry. Reason: τρία AILST timepoints + Epilogue ήδη συγκροτούν επαρκές measurement scaffold για το dissertation; AI-TPACK additive value δεν δικαιολογεί επιπλέον participant burden στο pilot
- Listed στο Section 5 (παρκαρισμένες ιδέες) below

**Επιπρόσθετα κομμάτια που υλοποιήθηκαν στο C.2 arc αλλά δεν προβλέπονταν στο original roadmap:**

- **C.2.1 — Profile Edit extension** — οι 3 Phase C personalisation fields (current_curriculum_pressure, student_population_special_needs, institutional_ai_policy) εκτίθενται στο profile edit form (commit `e86a727`).
- **C.2.2 — Step 3 consent amendment** — δύο ανεξάρτητες consents (research_participation + data_sharing), supersede pattern στο `record_consent`, IRB-defensible verbatim text storage (commit `a117220`).
- **C.2.4 — M5 → T1 module-completion gating** — JSON `ailst_redirect_url` mechanism wired into `mark_tab_complete`, frontend handlers updated σε δύο template sites (commit `f8501ef`).
- **C.2.5 — PROODOS Epilogue placeholder + M15 → Epilogue → T2 reroute** — separate `apps/epilogue/` app with `EpilogueCompletion` model. T2 πια triggers μετά το Epilogue, όχι κατευθείαν μετά το M15 (commit `bec8951`). Full Epilogue Stage 0..3 + Learning Portrait PDF is Phase G of this roadmap (TD-011).
- **C.2.5b — Confirm interstitial** — short page between Step 3 Summary and AILST T0 to reduce dropout risk (commit `bdb6670`).
- **C.6 — Pre-pilot sequential gates** — TD-012 (module prerequisite gate) and TD-013 (Epilogue gating on M15) closed in commit `050aba7`.

**Αρχεία αναφοράς:**
- `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 2) — onboarding modal spec
- `Literature_Review_Synthesis_Note.md` Section 5 — AILST + AI-TPACK measurement plan
- `M1_SYSTEM_VERIFIED.md` — pre-C.2 onboarding architecture (3-step → now 4-step + confirm interstitial)
- `proodos_files/C23_DESIGN_PROPOSAL_20260510.md` — C.2.3 design D1-D13
- `proodos_files/EPILOGUE_C25_IMPLEMENTATION_NOTES_20260511.md` — Epilogue placeholder + spec for full implementation

#### C.3 — Machine-readable AI content markers (Article 50(2))

**Status:** ✅ **DONE — four-commit arc, 2026-05-12.** Commits `6b9ec09` (storage layer + retroactive backfill management command) + `1bc8e55` (forward-write hooks with CP-9 transaction-atomic invariant) + `0d91191` (export mirror + HTML data-attrs + Option C XAI work) + commit 3 (`{% ai_provenance %}` + `{% ai_provenance_jsonld %}` template tags + page-level JSON-LD on tab5 + privacy_dashboard + this roadmap update + session log). TD-017 marked RESOLVED in `proodos_files/TECH_DEBT_LOG.md`. Two open follow-up TDs: TD-018 (per-artefact-instance dispute deep-links, post-pilot), TD-019 (peer-synthesis dispute UX requires `AIOutputDispute.FEATURE_CHOICES` migration, post-pilot). Full Phase C suite at 214 tests.

Design proposal at `proodos_files/C3_DESIGN_PROPOSAL_AI_MARKERS.md` (D1-D12, approved 2026-05-12 with 10 CP-style corrections including D10 revised to Option C — drop standalone attribution line, instead surface per-artefact `Generated at` row inside existing XAI panels + add parity panel for peer synthesis). Pre-flight audit at `proodos_files/audit_rag_queries_provenance_20260512.md` validates the single-constant `gemini-2.5-flash` backfill strategy.

The original NOT DONE status block + the 5 open design questions are kept below for historical context. Each question now has a documented answer in the design proposal D1-D12.

**Status (historical):** ❌ **NOT DONE — carry-over στο επόμενο παράθυρο.** Tracked ως **TD-017** στο `proodos_files/TECH_DEBT_LOG.md` (entry να γραφτεί στο επόμενο session που θα πιάσει το piece — η αναφορά εδώ είναι κανονική roadmap-level).

**Τι έγινε ενώ θα έπρεπε να γίνει το C.3:**
- Partial forward-compatibility marker: `data-ai-generated="true"` HTML attribute σε **4 spots μόνο** στο `templates/compliance/privacy_dashboard.html` (RTM card / DTP card / RAG feedback card / rag_queries card). Στην C.4 commit 2 αναφέρεται ρητά ως "per the C.3 forward-compatibility note" — δηλαδή **προετοιμασία**, όχι το C.3 self.

**Τι ΔΕΝ έγινε (full C.3 scope):**
- HTML data-attributes (`data-ai-generated` + `data-ai-model` + `data-ai-timestamp` + όλα τα provenance metadata) σε **κανέναν άλλο AI output rendering site**: το `tab5_reflection.html` (RAG feedback, RTM positions, DTP narratives, peer synthesis), τα module content templates που εμφανίζουν AI summaries, το AI Disclosure modal, κανένα από αυτά δεν φέρει τα markers.
- Page-level meta tags για AI provenance.
- JSON-LD structured data για AI provenance.
- Template tag `{% ai_provenance %}`.
- Provenance metadata storage layer (model version, generated_at, prompt hash, etc. per artefact).

**Αιτιολόγηση του carry-over:**
- C.3 αγγίζει το αρχιτεκτονικό layer όλων των AI rendering sites, οπότε χρειάζεται προσεκτικό design (HTML attrs vs JSON-LD vs template tag — τρεις διαφορετικές αρχιτεκτονικές επιλογές που πρέπει να αποφασιστούν συντονισμένα)
- Δεν είναι "lost" piece — είναι deferred με σαφές spec
- Το επόμενο session αρχίζει με design proposal pass, ακολουθεί 2 commits (data attrs + provenance metadata · JSON-LD + template tag)
- Estimated effort: ~250-400 LOC + tests

**Open design questions για το επόμενο παράθυρο:**

1. **Provenance storage location** — νέο `apps.compliance.models.AIArtefactProvenance` με FKs σε όλα τα AI-output rows; ή denormalised fields σε κάθε existing model (UserModuleProgress, ReflectionTension, rag_queries); ή hybrid;
2. **Template tag signature** — `{% ai_provenance for=artefact %}` που auto-resolves το type, ή `{% ai_provenance model="gemini-2.5-flash" generated_at=date %}` με explicit args;
3. **JSON-LD schema** — schema.org/CreativeWork με extension; ή schema.org/SoftwareApplication; ή custom EU AI Act schema (αν υπάρχει); ή none και μόνο HTML attrs (lighter footprint);
4. **Coverage scope για το pilot** — όλα τα AI rendering sites, ή μόνο τα 4 main (RAG / RTM / DTP / peer synthesis) και αναβολή ολόκληρου του attribute markup μέχρι v2.0;
5. **Reverse compatibility** — δεν θέλουμε rerender υπάρχουσας research data; νέα markers εφαρμόζονται μόνο σε νέα generated content; ή retroactive backfill via management command;

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 3).

#### C.4 — Privacy Dashboard (GDPR + EU AI Act)

**Status:** ✅ DONE — three commits arc `eb36db1` + `6055616` + `1dee58b` plus correction `2cd0a04`.

**Implemented surface:**
- New page `/profile/privacy/` (linked από `/profile/`, από το `base.html` footer, και από το `landing.html` footer)
- Three per-consent revoke endpoints with explicit per-type session semantics:
  - `revoke_ai_disclosure_view` (POST) — atomic transaction που revokes ConsentRecord **και** clears `TeacherProfile.ai_disclosure_acknowledged_at` (closes TD-008), μετά logout → landing
  - `revoke_research_view` (POST) — supersede + sets `TeacherProfile.research_data_opted_out=True` (new flag from migration `users/0010`), user stays logged in
  - `revoke_data_sharing_view` (POST) — supersede only (narrower scope, does NOT toggle research_data_opted_out), user stays logged in
- Art. 15 data export — `apps.compliance.services.gather_user_export(user)` aggregates TeacherProfile, ConsentRecord, AilstResponse, UserModuleProgress, EpilogueCompletion, AI outputs (RTM, DTP, RAG feedback, peer synthesis) και τα raw-SQL `rag_queries` rows. Served as JSON file download.
- Art. 17 anonymisation — `apps.compliance.services.anonymize_user(user)` Python service (replaces the broken-and-dropped DB function from Γ.1). Atomic transaction: NULLs PII on auth_user + TeacherProfile, retains auth_user row (preserves FKs), clears reflection-content text on UserModuleProgress + ReflectionTension + rag_queries, retains ConsentRecord rows με IP redaction (7-year IRB window), sets `research_data_opted_out=True`. Then logout + landing.
- Confirmation token `DELETE` (server-side validation only, no JS-gated submit — CP-8 accessibility decision)

**Note on "Privacy Policy page" framing in the original roadmap:** there is no separate markdown-rendered privacy policy doc. The AI Impact Assessment at `/about/ai-act-compliance/` covers privacy in Sections 5 + 6, and the footer "Privacy" link points there. Single source of truth.

**Έξοδος Phase C:** Πλήρης συμμόρφωση με EU AI Act Article 50(1) (transparency notice — C.1) και με GDPR Articles 7(3) / 15 / 17 / 21 (Privacy dashboard — C.4) + AILST T0/T1/T2 administration με Epilogue chain (C.2.3 + C.2.4 + C.2.5). **C.3 carry-over** + Career Stage gap (3.C.2 Step 2) + post-IRB updates (3.C.5) + pre-pilot operational tasks (3.C.6).

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 4) + `proodos_files/C4_DESIGN_PROPOSAL_PRIVACY_DASHBOARD.md` (D1-D14 + 8 CP refinements).

---

#### C.5 — Post-IRB updates checklist (PRE-PRODUCTION TASK)

**Status:** ⏸ **Pre-production deployment task — NOT a Phase C blocker.** Executed once, after every code-bearing phase (A-I) is complete (or at minimum the platform is feature-frozen for the pilot) and when IHU IRB feedback (CP 7 + CP 10) has arrived. Until then, the existing v1 copy carries `v1_pre_irb` markers + "Will be revised after IHU IRB review" wording — kept easy-to-grep.

When IRB feedback arrives, apply this checklist in one focused session.

| Change | File / location | Action |
|---|---|---|
| New AI Disclosure text version | `apps/compliance/copy.py` | Add `AI_DISCLOSURE_TEXT_V2_IRB_REVISED` + `AI_DISCLOSURE_HTML_BULLETS_V2_IRB_REVISED`. Do NOT edit v1. |
| New research participation text | `apps/compliance/copy.py` | Add `RESEARCH_PARTICIPATION_TEXT_V2_IRB_REVISED`. Do NOT edit v1. **PROODOS Epilogue v2 §11 binding requirement (Phase G G.5, 2026-05-23):** the V2 text MUST explicitly name "dialogue-form reflection produced in the PROODOS Epilogue, including the teacher's written responses and the AI-generated dialogue turns" as covered personal data. Required regardless of what the IRB feedback otherwise contains — closes B.4 of the Phase G v2 design review. |
| New data sharing text | `apps/compliance/copy.py` | Add `DATA_SHARING_TEXT_V2_IRB_REVISED`. Do NOT edit v1. |
| New AI Impact Assessment list | `apps/compliance/copy.py` | Add `AI_IMPACT_ASSESSMENT_V2_IRB_REVISED` (list of `{'heading','body'}` dicts). Do NOT edit v1. |
| Bump version pins | `config/settings.py` | `AI_DISCLOSURE_CURRENT_VERSION = 'v2_irb_revised'`; `RESEARCH_CONSENT_CURRENT_VERSION = 'v2_irb_revised'`; `AI_IMPACT_ASSESSMENT_CURRENT_VERSION = 'v2_irb_revised'`. |
| Update view import | `apps/compliance/views.py` | `ai_act_compliance_stub_view` imports `AI_IMPACT_ASSESSMENT_V2_IRB_REVISED`. |
| Mark CP 7 + CP 10 resolved | `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` §2 | Move CP 7 + CP 10 από §2.2 (Pending) σε §2.1 (Resolved) με reference στο IRB approval date. |
| Re-verify supersede flow | (operational) | Test ότι existing users with v1 active consents get supersede to v2 on next Step 3 visit. |
| Re-deploy + re-acknowledge staff | `scripts/pre_deploy_c20_acknowledge_staff.py --commit` | Re-run to grant v2 ack to staff. The supersede pattern automatically revokes their v1 row. |

**Σημείωση:** το current copy φέρει σκόπιμα τα `v1_pre_irb` markers + "Will be revised after IHU IRB review" wording για να είναι easy-to-grep όταν φτάσει η ώρα. Σε αυτό το checklist, αυτές οι αναφορές αντικαθίστανται από τις v2 εκδόσεις, ΟΧΙ διαγράφονται.

---

#### C.6 — Pre-pilot operational checklist (PRE-PRODUCTION TASK)

**Status:** ⏸ **Pre-production deployment task — NOT a Phase C blocker.** Scripts and tests are READY. Executed once, after every code-bearing phase (A-I) is complete, C.5 IRB-driven copy revision has been applied, and immediately before participant recruitment.

| Step | Command / Action | Risk |
|---|---|---|
| 1. Fresh DB backup | `pg_dump unesco_ai_teacher_pd > pre_pilot_wipe_<date>.sql` at repo root | None — read-only |
| 2. **C.3 backfill** (provenance for any staff/test artefacts that pre-date the forward-write hooks) | `python manage.py backfill_ai_provenance` (dry-run) then `python manage.py backfill_ai_provenance --commit`, type `YES` | None — idempotent (get_or_create); skips orphan `rag_queries` rows automatically |
| 3. Dry-run wipe | `python scripts/cp11_wipe_test_users.py` | None — read-only; prints user list + cascade footprint |
| 4. Confirm output | Eyeball the list. Staff accounts must NOT appear in the deletion list. | Low |
| 5. Execute wipe | `python scripts/cp11_wipe_test_users.py --commit`, type `YES` when prompted | Destructive — backup at step 1 is the safety net |
| 6. Re-ack staff | `python scripts/pre_deploy_c20_acknowledge_staff.py --commit` | None — idempotent; staff already had ack rows but cascade may have touched the FK targets |
| 7. Verify clean state | Visit `/admin/auth/user/` — only staff + superuser rows should appear | None |
| 8. Smoke test new-user flow | Register a fresh user, walk through Step 1 → 2 → 3 → Confirm → AILST T0 | None |
| 9. Pilot recruitment | Begin inviting participants | — |

**Ordering note:** the C.3 backfill (step 2) MUST run BEFORE the CP-11 wipe (step 5). CP-11 cascade-clears the 19 non-staff `rag_queries` rows; running backfill after the wipe would leave only staff + orphan rows in scope, and would leave the interim window (between deploy and wipe) with inconsistent provenance during staff testing. See `proodos_files/audit_rag_queries_provenance_20260512.md` §5 and `TECH_DEBT_LOG.md` TD-017 (resolved block) for the operational rationale.

The CP-11 wipe script is at `scripts/cp11_wipe_test_users.py`. Core logic exposed as `wipe_non_staff_users()` for direct test invocation. Both `--dry-run` (default) and interactive YES confirmation are built in.

---

#### C.7 — Carry-over (CLOSED): C.3 machine-readable AI markers

**Status:** ✅ CLOSED 2026-05-12 — the C.3 piece this section described was completed in a four-commit arc on 2026-05-12. See **3.C.3** above for the DONE block + commit hashes + cross-references. This section is retained for historical context.

**Historical status:** Identified gap. Spec available, implementation deferred. See **3.C.3** above για το full Status block και τα 5 open design questions.

**One-line summary για το επόμενο handoff:** the platform produces AI-generated content (RAG feedback, RTM positions, DTP narratives, peer synthesis) but only a partial forward-compatibility marker exists (4 HTML attributes on the privacy dashboard). Article 50(2) of the EU AI Act recommends machine-readable marking of synthetic content; C.3 operationalises this with HTML data-attributes + page-level JSON-LD + a reusable `{% ai_provenance %}` template tag. The full work plan is in `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 3) + the five open design questions in 3.C.3.

**Suggested approach for the next session:**

1. Read this section + 3.C.3 above + the EU AI Act plan Συμπλήρωμα 3.
2. Decide the five open design questions με design proposal (`C3_DESIGN_PROPOSAL_AI_PROVENANCE.md`).
3. Implement in 2 commits: (a) provenance metadata storage + HTML data-attrs across all AI rendering sites; (b) JSON-LD + `{% ai_provenance %}` template tag + tests.
4. Update this roadmap: move C.3 from 3.C.7 carry-over to a "DONE" badge inside 3.C.3.
5. Update TECH_DEBT_LOG to mark TD-017 RESOLVED.

---

#### C.x — Other follow-ups raised during Phase C implementation

| Item | Defer to | Reference |
|---|---|---|
| Career Stage RAG personalisation (C.2 Step 2 unfinished half) | **DEFERRED to post-pilot research direction** (decision 2026-05-13) — `teaching_years` retained as exploratory variable for post-hoc analysis only (TD-020). NOT a treatment variable. See 3.C.2 Step 2 above for full rationale. | 3.C.2 Step 2 |
| AI-TPACK self-assessment | Section 5 (παρκαρισμένες ιδέες) | 3.C.2 Step 4 above |
| Full PROODOS Epilogue Stage 0..3 + Learning Portrait PDF | Phase G (this roadmap) | TD-011 |
| Post-pilot AILST score reveal | Phase G/H | TD-010 |
| Selective deletion of single reflections / AILST responses | Post-pilot | TD-014 |
| Data export as PDF (in addition to JSON) | Post-pilot | TD-015 |
| 7-year ConsentRecord retention cleanup management command | Phase H | TD-016 |

---

### Phase D — Pilot Readiness Features

**Στόχος:** Features που πολλαπλασιάζουν την ερευνητική αξία χωρίς νέο περιεχόμενο.

#### D.1 — AI Output Relevance Profile — ✅ COMPLETE (2026-05-20)

The roadmap's original "Trust Calibration Score" framing was rejected on
construct-validity grounds: trust calibration needs a ground-truth reliability
axis the platform lacks (Lee & See, 2004), so what the data supports is
*perceived relevance*, not calibration. D.1 became the **AI Output Relevance
Profile** — a researcher-facing aggregation of the `AIOutputDispute` ratings
teachers already give on the RAG / RTM / DTP outputs.

- New `apps/analytics/` app — the researcher-facing analytics layer, shared
  home for D.1 and (later) D.2. Owns no models; read-only aggregation only.
- `services.py` — cohort and per-teacher perceived-relevance distributions,
  reason breakdown, coverage indicator. Whitelists rag/rtm/dtp; peer is
  excluded as a different construct (TD-019), reported separately.
- A `staff_member_required` view (the `/analytics/` dashboard) — never linked
  from a teacher-facing page (measurement-reactivity guard).

Descriptive, not evaluative; no model, no migration. Canonical doc:
`proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md`.

#### D.2 — Engagement Depth (Position Confirmation Analytics) — ✅ COMPLETE (2026-05-20)

A researcher-facing analytic over the RTM `position_confirmed` telemetry. The
RTM auto-saves every extracted tension at the neutral default; `position_confirmed`
is set true only for a tension whose slider the teacher actually moved. D.2
aggregates that into an **Engagement Depth Score (EDS)** — the share of RTM
tensions a teacher actively engaged with — separating *surface engagement* (the
step completed, nothing touched) from *deep engagement*. It is the empirical
basis for the "beyond completion rates" dissertation argument.

- `apps/analytics/services.py` — cohort and per-teacher EDS, with supporting
  signals (comment-use rate, non-neutral rate, median interaction time) and
  per-module / per-subject slices.
- Rendered as a second section on the unified `/analytics/` dashboard page,
  alongside the D.1 relevance profile.

EDS as a headline number is admissible (a literal confirmation rate, no
construct over-claim, unlike D.1's rejected "Trust Calibration Score").
Read-only, no migration. Canonical doc:
`proodos_files/D2_ENGAGEMENT_DEPTH_DESIGN_PROPOSAL_v1_20260520.md`.

#### D.3 — DTP redefinition + XAI narrative — ✅ COMPLETE (2026-05-19)

Delivered in two parts. The original D.3 sketch — "extend the DTP prompt with
an attribution + counterfactual hint" — was superseded: live use exposed a
construct-validity flaw in the DTP's single cross-aspect comparison, so D.3
became a redefinition first, then the explanation layer on top.

**D.3a — DTP redefinition (dual-signal).** The DTP was redefined from one
cross-aspect comparison into two signals:
- **Vertical Continuity Signal (VCS)** — same UNESCO aspect, one proficiency
  level down (e.g. a Deepen module vs the matching Acquire module).
- **Temporal Shift Signal (TSS)** — vs the immediately preceding module.

Non-uniform by design: Acquire modules (M1–M5) carry the TSS only; M1 carries
neither. Descriptive-only — no thresholds, labels, or scores in the pilot.
Stored as a `dtp_dual_v1` composite. Canonical doc:
`proodos_files/DTP_REDEFINITION_DESIGN_PROPOSAL_v1_20260518.md`.

**D.3b — DTP XAI narrative.** A new `ServiceAgent` parent under `BaseAIAgent`
and the first concrete `XAIAgent`, which explains the stored DTP composite in
faithful, domain-driven natural language (UNESCO-competency / pedagogical
terms, never cosine numbers). `generate()` persists to
`UserModuleProgress.reflection_dtp_xai` with its own `xai_narrative` provenance
row. The DTP themes panel was reframed to neutral attention-shift language; the
prompt register is fixed by an embedded worked example, with Gemini thinking
disabled to prevent truncation. Canonical doc:
`proodos_files/DTP_XAI_NARRATIVE_DESIGN_PROPOSAL_v1_20260519.md`.

Both parts committed and live-verified on M6; agent suite 123 tests pass. The
`ServiceAgent` parent slot the Phase E hierarchy reserved is now filled.

*(The earlier reference `DTP_Documentation_Mar2026.docx` is superseded by the
two design proposals above.)*

#### D.4 — Dashboard: UNESCO Matrix 5×3 + RTM Heatmap — ✅ COMPLETE (2026-05-20)

Two cohort-level visualisations added as sections 3 and 4 of the `/analytics/`
dashboard:
- **UNESCO Competency Matrix** — the 5 aspects × 3 levels grid; each of the 15
  cells is a module shaded by cohort completion rate (consenting teachers who
  completed it / all consenting teachers). Cumulative — not narrowed by the
  date filter.
- **RTM Coverage Heatmap** — 16 subjects × 15 modules; each cell counts the
  distinct consenting teachers with RTM data. A coverage map at pilot scale.

Both researcher-facing, consent-restricted, and obey the date/subject filters.
Read-only, no migration; analytics suite 24 tests pass. Canonical doc:
`proodos_files/D4_DASHBOARD_DESIGN_PROPOSAL_v1_20260520.md`.

**Phase D is now complete** (D.1 + D.2 + D.3 + D.4). A related follow-up — the
teacher dashboard duplicating the Modules menu — is logged as **TD-021** for a
later UX pass.

---

### Phase E — Multi-agent Refactor — ✅ COMPLETE (2026-05-14)

**Status:** Closed. Eleven commits over a single design-then-execute cycle (chat-Claude designing, Claude Code executing, eleven rounds of bidirectional v1→v11 design docs). 316/316 tests green at every step. Net LOC change ~−4,500 (deletion-dominated). Canonical document: `proodos_files/PHASE_E_DESIGN_PROPOSAL_v11.md` — primary dissertation chapter source material.

#### E.0 — One-paragraph summary

Phase E migrated four AI features (RAG feedback, RTM tension extraction, DTP development trajectory, Peer Synthesis) from a 1112-line monolithic `rag_query_system.py` at the repository root into four named agent classes under `apps/agents/`, all inheriting from a common `BaseAIAgent` with shared infrastructure for cost tracking, audit logging, provenance writing, and atomicity enforcement. The refactor preserved byte-identical behaviour for the primary user paths and produced **seven distinct architectural improvements** (§3 D3b of v11), not the single "atomic strengthening" overclaim that an inattentive framing would have produced.

#### E.1 — Final architecture

```
apps/agents/
├── base.py              BaseAIAgent (ABCMeta + @abstractmethod _do_generate)
│                          Two public entry points: generate() + extract()
├── research.py          ResearchInstrumentAgent (marker class)
├── rag_feedback.py      RAGFeedbackAgent      (generate, dual provenance rows)
├── rtm.py               RTMAgent              (extract, no atomic-time persistence)
├── dtp.py               DTPAgent              (generate, multi-call orchestration)
├── peer.py              PeerSynthesisAgent    (generate, three-way failure modes)
│                          + NoPeerReflectionsAvailable exception
├── shared/
│   ├── llm_client.py    NEW/OLD Gemini SDK wrapper (was duplicated x5)
│   ├── embedding.py     embed_query standalone
│   ├── json_repair.py   clean_json_response (shared by RTM + DTP)
│   ├── cost_tracker.py  per-call cost logging — RAG was 1/4 paths; now 4/4
│   ├── audit.py         structured JSON logger (replaces scattered print())
│   └── db.py            dict_cursor() — unified DB access (was 3 idioms)
└── tests/               102 agent-suite tests + 5 frozen prompt fixtures
```

Future agents (Epilogue Q&A in Phase G, Multimodal voice/image in Phase F) extend this hierarchy without modifying it. The `XAIAgent`, under a new `ServiceAgent` parent, was added this way in Phase D.3b (2026-05-19) — the first agent on the service-agent branch, alongside the existing research-instrument branch.

#### E.2 — Commit-by-commit summary

| # | Title | Hash | Theme |
|---|---|---|---|
| 1 | BaseAIAgent + RAGFeedbackAgent + shared/ | `f806a18` | Foundation; tests 214→238 |
| 1.5 | manage.py UTF-8 stdio guard (closes TD-005) | `7786a7a` | Environment fix |
| 2 | views.py RAG cutover + atomic **STRENGTHENING** | `0f50b7a` | First cutover; inconsistency window eliminated |
| 3 | RTMAgent + ResearchInstrumentAgent + `extract()` | `935241a` | Dual entry points discovered |
| 4 | views.py RTM cutover (preservation) | `4497a0b` | Honest preservation, not strengthening |
| 5 | DTPAgent + commit-6 diagnostic | `1c2c193` | Multi-call orchestration |
| 6 | views.py DTP cutover (preservation + UX tightening) | `6943da7` | Silent-failure antipattern eliminated |
| 7 | PeerSynthesisAgent + commit-8 diagnostic + dead-block removal | `373449f` | Triple-aspect commit |
| 8 | views.py Peer cutover (preservation, three-way catch) | `2927311` | Smoothest cutover; fewer surprises |
| 9 | Monolith deletion + grep audits + Gemini 1.5 cleanup | `45969bc` | Audit-protected cleanup; 7 distinct findings |
| 10 | Delete `rag_query_system.py` tombstone | `1e2de04` | Final removal — Phase E complete |

#### E.3 — Seven distinct architectural improvements (dissertation evidence)

| # | Contribution | Evidence |
|---|---|---|
| 1 | Atomic strengthening at one site | Commit 2 (RAG): two atomic blocks collapsed; inconsistency window eliminated by construction |
| 2 | Dual entry points distinction (`generate()` vs `extract()`) | Commit 3: two architectural stances on HITL — "AI commits, human disputes" vs "AI proposes, human ratifies" |
| 3 | Cost tracking expanded from 1/4 to 4/4 paths | Commits 1–7: every agent emits `agent.cost` events |
| 4 | Elimination of three DB-connection idioms | Commits 1–10: hardcoded credentials, raw psycopg2, Django ORM unified under `dict_cursor()` |
| 5 | Dead-code findings exposed by test-mock review | Commit 2 (C) (dead peer inline block), commit 4 (unused import), commit 5 §11 (4 monolith quirks), commit 7 (dead peer-inline-save block removed) |
| 6 | Silent-failure antipatterns exposed by architectural enforcement | Commit 6 DTP substantive (tolerant try/except showed phantom result on save failure); commit 8 Peer incidental (catch-all message) |
| 7 | Pre-deletion audits as complementary safety | Commit 9: call-site map captured production callers; audits surfaced live-oracle test fixtures (4 prompt-parity tests), phantom monolith copies (`rag_query_systemOLD.py` + `phase2d_testing_package/rag_query_system.py`, both containing a SAFETY HAZARD enable-bomb for deprecated Gemini 1.5), and out-of-tree dev scripts |

These seven form the architecture chapter of the dissertation. The numerical balance (1 strict strengthening of 4 cutovers) defeats the easy overclaim — the existing architecture was mostly CP-9 compliant; the refactor's value is broader than tightening one invariant.

#### E.4 — Six reusable patterns (formalised for future phases)

1. **Pre-decision pattern** — agent-add commits diagnose framing of the next cutover.
2. **Triple-aspect agent commits** — build + diagnostic + cleanup (commit 7).
3. **Stop-and-discuss as quality gate** — prevented ≥10 distinct issues across 11 commits.
4. **Two-layer test invariant** — prompt-identical + behaviour-identical (robust to LLM non-determinism).
5. **Pre-deletion audit protocol** — call-site grep + hazard-pattern grep (commit 9).
6. **Strangler with byte-identical preservation** — no big-bang risk.

#### E.5 — Verbatim architectural rationale (dissertation-quotable)

> BaseAIAgent exposes two public entry points: `generate()` for persisted artefacts (RAG-style, agent owns the atomic block) and `extract()` for ephemeral AI suggestions where persistence is a separate human action (RTM-style). This distinction is not a special case; it reflects two architectural stances on human-in-the-loop AI: "AI commits, human disputes" (generate) and "AI proposes, human ratifies" (extract). Future features like the Epilogue Q&A dialogue and multimodal voice transcription are expected to use extract() as well.

> [Commit 2's atomic strengthening:] The CP-9 atomicity guarantee is strictly STRENGTHENED, not preserved. Before this commit the `rag_queries` INSERT (with its `'rag_query'` provenance) and the `progress.save()` (with its `'rag_feedback'` provenance) lived in TWO separate `transaction.atomic` blocks. Between them existed a window where a failure left the system inconsistent: `rag_queries` row logged but no feedback on progress. The agent collapses both writes into one atomic block, making that window impossible by construction.

#### E.6 — Downstream impact

- **Phase D** builds on the agent architecture. D.3 introduces `ServiceAgent` parent + `XAIAgent` first concrete (the hierarchy reserved this slot).
- **Phase F** Multimodal agents extend via `extract()` (voice transcription user-ratifies before save).
- **Phase G** Epilogue Q&A dialogue extends via `extract()` (user reviews each turn).
- **Phase H** Closing flow benefits indirectly from the audit logger producing structured cost/event records.

**Αρχεία αναφοράς:**
- `proodos_files/PHASE_E_DESIGN_PROPOSAL_v11.md` — canonical FINAL Phase E document (specification + retrospective + dissertation chapter source material; saved to disk 2026-05-14)
- `apps/agents/` — the implementation
- `apps/agents/tests/` — 102 tests + 5 frozen prompt-parity fixtures in `prompt_fixtures/`
- Git history `f806a18..1e2de04` — 11 commits, eleven design-iteration rounds

---

### Phase F — TAB5 Redesign (5-screen wizard + magazine + voice)

**Status: COMPLETE (2026-05-21)** — delivered and verified end-to-end, including a design-refresh pass and a post-submit results section-nav. Eight commits (1705e27, ba289c0, 4132455, a35d1ac, 37e0aa9, 02720ef, 527bb48, b8ee15f). Canonical doc: `proodos_files/F_TAB5_REDESIGN_DESIGN_PROPOSAL_v1_20260520.md`. Voice-input notice wording approved 2026-05-21. No open items — the voice-input rationale was added to the literature note (§14, 2026-05-21).

**Στόχος:** Επανασχεδιασμός του TAB5 ως five-screen wizard στο magazine style (οικογένεια TAB1/TAB2), με voice input ενσωματωμένο.

**Redefinition note (2026-05-20).** Το Phase F ξεκίνησε ως «multimodal reflection» (voice + image). Κατέληξε, μέσα από διαδοχικές αποφάσεις του kickoff, σε ένα ενιαίο κομμάτι: τον επανασχεδιασμό του TAB5. Σύνοψη: **F.2 (image)** αφαιρέθηκε — το TAB5 reflection είναι προοπτικό, δεν υπάρχει artefact να συνδεθεί (re-filed ως Phase G candidate). **F.1b (server-side transcription agent)** ακυρώθηκε — το Web Speech API ήταν ικανοποιητικό σε live test, οπότε δεν χρειάζεται server path / toggle / Platform Settings / δεύτερη migration. **F.1 (voice) και F.5 (TAB5 redesign) συγχωνεύονται** — η υλοποίηση τεσσάρων μικροφώνων σε μία σελίδα χτύπησε σε multi-session αναξιοπιστία του Web Speech API· ένα μικρόφωνο ανά οθόνη (wizard) το παρακάμπτει. **Canonical doc:** `proodos_files/F_TAB5_REDESIGN_DESIGN_PROPOSAL_v1_20260520.md` — υπερισχύει του παρακάτω F.1–F.4 breakdown, που διατηρείται για ιστορικό.

#### F.1 — Voice input
- Web Speech API integration στο reflection form
- Greek + English support
- Speech-to-text → standard reflection text → ίδιο RAG/RTM/DTP pipeline
- Cognitive load reduction για εκπαιδευτικούς που σκέφτονται καλύτερα προφορικά
- "AI proposes, human ratifies": η μεταγραφή εμφανίζεται για διόρθωση/επιβεβαίωση πριν αποθηκευτεί ως reflection text (αξιοποιεί το `extract()` entry point του `BaseAIAgent`)

#### F.2 — Image input — REMOVED from Phase F (2026-05-20)
Αρχική περιγραφή (παραμένει για ιστορικό): upload classroom artefacts (lesson plans, student work, classroom photos), Gemini multimodal ανάλυση, νέα διάσταση reflection "show me what you tried, don't just describe it". Αφαιρέθηκε — βλ. scope note παραπάνω. Re-filed ως Phase G candidate (§3 Phase G).

#### F.3 — Παιδαγωγικό όφελος
- Inclusive design (η φωνή ταιριάζει σε εκπαιδευτικούς που σκέφτονται/εκφράζονται καλύτερα προφορικά)
- Νέα ερευνητική διάσταση: comparison between voice και text reflections

#### F.4 — Δικαίωση για τη διατριβή
Άμεση απάντηση σε critique της literature ότι το AI-mediated PD είναι text-heavy. (Σημείωση: η αρχική επίκληση των αρχών πολυμεσικής μάθησης του Mayer τεκμηρίωνε το image input — οι αρχές αυτές περιγράφουν πώς παρουσιάζεται το μαθησιακό υλικό στον μαθητή, όχι το modality υποβολής αναστοχασμού, οπότε δεν στήριζαν στην πραγματικότητα το F.2. Η δικαίωση του F.1 στηρίζεται σε cognitive load reduction / inclusive design.)

**Canonical doc:** `proodos_files/F_TAB5_REDESIGN_DESIGN_PROPOSAL_v1_20260520.md` — the TAB5 redesign proposal (four-screen wizard + magazine + voice), draft awaiting review. It supersedes `F1_VOICE_INPUT_DESIGN_PROPOSAL_v1_20260520.md` (the earlier voice-only proposal, kept for history; its F.1b / toggle / server-path content is cancelled).

**Αρχεία αναφοράς:**
- `tab5_reflection.html` — current text-only form
- `Literature_Review_Synthesis_Note.md` — critique του text-heavy AI-mediated PD

---

#### F.5 — TAB5 Visual Redesign — MERGED INTO PHASE F (2026-05-20)

**Status:** Merged. F.5 is no longer a separate parked entry — it became Phase F itself. The per-part voice build hit a Web Speech API multi-session wall, which made the redesign and voice inseparable: a four-screen wizard (one microphone per screen) is both the redesign and the fix. See the canonical doc above and the Redefinition note at the top of §3 Phase F. The problem statement and design anchors below are retained as input to that redesign.
**Date added:** 2026-05-13. **Merged:** 2026-05-20.

**Problem statement.** The current TAB5 reflection page is functional but visually old-fashioned. The pain point is overall visual era, not specific structural issues (panels, density, flow). DaisyUI cards with hard-edged borders (`border-2 border-blue-200`), pastel background fills (`bg-blue-50`, `bg-yellow-50`, `bg-green-50`), emoji-prefixed titles (💡 Part 1, 📝 Reflection), DaisyUI `badge` counters for word targets, and a stacked `<form>` layout with no spatial differentiation between reflection-input and AI-output zones together produce a 2020-era admin-UI register. The page reads as "fill out a form", not "reflect and converse with an intelligent system".

**Why not now — three reasons to defer to F.5:**

  1. **Phase E is Python-only.** Touching templates breaks the multi-agent refactor's test invariant ("new + old produce identical output"). Doing the redesign during E would forfeit that safety net.
  2. **Phase F adds new input modalities.** Voice (F.1) and image upload (F.2) introduce new UI affordances that must be designed into the redesign from the start. Redesigning before F = redesigning twice.
  3. **Phase D.4 establishes data-viz language.** The Dashboard (D.4) sets a colour system, typography scale, and visual rhythm for data-dense content. The TAB5 redesign should be consistent with that language. Sequencing matters.

**Proposed scope (when F.5 starts).** A unified "reflection space" rather than cosmetic refresh.

| Concern | Current state | F.5 target |
|---|---|---|
| Visual era | 2020 pastel-card form | Modern editorial / magazine reflective surface |
| Input affordances | Text only (4 textareas) | Text + voice + image (post-F) |
| AI output zones | Mixed into the form flow | Visually distinct from reflection-input zones |
| Reading rhythm | Vertical stack, no hierarchy | Section pacing, generous whitespace, deliberate type scale |
| Color system | Aspect-coloured pastels | Aspect colour system consistent with TAB2 magazine + D.4 Dashboard |
| Trust signals | XAI panels inline | Trust signals (AI provenance, XAI, HITL) as first-class peers to the reflection itself |
| Mobile experience | Functional, not optimised | Equal-priority mobile design |

**Design language anchors (to confirm at F.5 start).** The platform already has visual reference points. F.5 should pull from them, not start fresh:

  - **TAB1 Magazine Redesign** (§2.4) — typographic hero, info bar, 5-aspect colour system. Editorial register.
  - **TAB2 Magazine Upgrade** — sticky Part navigator, aspect-coloured numerals, reading progress bar. Magazine register.
  - **D.4 Dashboard** (Phase D) — data-viz colour system + RTM Heatmap rhythm. To be defined.

TAB5 should sit naturally in this family — same editorial register as TAB1/TAB2, same data-viz language as the Dashboard.

**Open questions to surface at F.5 start (NOT to answer now):**

  1. Should reflection-input and AI-output live in distinct visual columns (split-pane), or alternating bands (vertical magazine flow)?
  2. How prominently should voice input appear once F.1 lands? Equal weight to text, or secondary affordance?
  3. Image upload: thumbnail strip, or single hero artefact per reflection?
  4. Should the four parts of the reflection still be visually separated, or merged into a single flowing space with subtle dividers?
  5. Trust signals (provenance, XAI, HITL): persistent sidebar, or expand-on-demand under each AI output? Note that the C.3 commit 2b + 3 work established the current expand-on-demand pattern (collapsible `<details>` panels with the "Generated at" row plus the data-attrs/JSON-LD machine-readable layer); F.5 must preserve the regulatory contract (Article 50(1) human-readable + 50(2) machine-readable) under any visual change.
  6. Modal AI outputs (RTM, DTP, Peer Synthesis on-demand buttons) — keep as modal, or in-page panel that animates in?

**What this is NOT:**

  - NOT a commitment to a specific visual direction.
  - NOT a substitute for the Phase F roadmap entries (F.1, F.2, F.3, F.4 stay as-is).
  - NOT a dissertation-priority item. The redesign serves UX and pilot adoption, not the research contribution. The Phase C transparency posture (XAI panels, machine-readable provenance, HITL) is the regulatory-defensible substance and is preserved across the redesign.

**Αρχεία αναφοράς:** the addendum source document (drafted 2026-05-13) was merged into this section; the design language anchors above point at §2.4 (TAB1 + TAB2 magazine redesigns) and the future §3 Phase D.4 (Dashboard).

---

### Phase G — PROODOS Epilogue — ✅ COMPLETE (with deprecation, 2026-05-24)

**Στόχος:** Post-completion synthesis feature — methodologically distinct από τα 15 modules, ανάμεσα στο M15 και το AILST T2.

**Final shape (post-deprecation 2026-05-24):** Stage 0 Personal
Evolution Dashboard (magazine register) + "Continue" button to
T2. The Aletheia reflective dialogue (Stages 1-3) and Learning
Portrait (in-page + PDF) are **deactivated** — see deprecation
doc and master proposal §25. Reusable infrastructure preserved
for **Phase H** (PDF + Article 50(2) for the certificate of
attendance) and **deferred Phase J** (Aletheia chatbot
repurposing, scope TBD).

**Status (2026-05-24, late):** G.0-G.3 ✅ shipped. G.4 ✅ shipped — M15 content aligned with the D.3a dual-signal DTP redefinition; same edit pass swept the now-stale Phase-G-closure Epilogue dialogue references that were sitting in the same content rows; M15 RAG corpus re-ingested (43 fresh chunks across Main Content + Subject Examples). G.5 ✅ closed. G.6a-b ✅ shipped (Aletheia aspect + Stage 0 magazine redesign). G.6c ✅ implemented through three live-test correction cycles (§24 / §24.11 / §24.12) before strategic deprecation. G.6d-e ❌ cancelled by deprecation. **All of Phase G now complete.**

**Authoritative deprecation document:**
- `proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md` — full decision rationale (reflection fatigue + RPE framework dilution + technical fragility), scope (stays/goes/defers), test handling, lessons learned.
- `proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md` §25 — deprecation pointer + reading guide for the historical sections (§6-7, §23-24.12) retained as methodological evidence.

**Master design proposals (αρχεία αναφοράς):**
- `proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md` — το «σύνταγμα» του Phase G (PI-approved 2026-05-21). 4-stage architecture, schema, agent contracts, HITL, compliance, bibliographic grounding, commit plan §19. **§22 amendment** (2026-05-23, during G.3): regen-counter via `dialogue_turns` (όχι νέο schema field), skip-dialogue bypass του Portrait, Article 50(2) strict PDF variant (JSON-LD + PDF Info dict). **§23 amendment** (2026-05-23, before G.6a): 5-line anti-anthropomorphisation rule στο `EpilogueDialogueAgent._SYSTEM_PROMPT` για την Aletheia persona.
- `proodos_files/PHASE_G_G6_DESIGN_PROPOSAL_v2_20260523.md` — το G.6 magazine design upgrade proposal (PI-approved 2026-05-23, δύο reviewer passes). TAB1/2/5 editorial register, xhtml2pdf render-budget (μετρημένο εμπειρικά), Aletheia palette + persona application, surface-by-surface redesign, label-relabel table, phase-as-chapter fix για το seam bug, olive-as-completion ornament.
- `proodos_files/PHASE_G_BRIEFING_FOR_EXTERNAL_REVIEWER_20260523.md` — self-contained briefing για external Claude review.
- `M16_CAPSTONE_REFLECTION_SPEC.md` + `PROODOS_EPILOGUE_PATCH_APR2026.md` — προ-v1 historical specs (superseded από το v2 proposal).

**Commit plan (από v2 §19):**

| Commit | Subject | Status |
|---|---|---|
| **G.0** | Schema extension on `epilogue_completions` (10 fields, single additive migration) | ✅ 2026-05-21 `002650b` |
| **G.1** | Stage 0 — Personal Evolution Dashboard (DTP theme-evolution, RTM trajectories, quantitative summary· `_stage0_panel.html` shared partial· first-entry freeze) | ✅ 2026-05-22 `fa42b08` |
| **G.2a** | Stage 1 (Look Back) — `EpilogueDialogueAgent` + dialogue endpoint, extract-only, Article 50(1) notice | ✅ 2026-05-23 `f83210f` |
| **G.2b** | Stage 2 (Look In) — juxtaposition surfacing, §6.4 skip threshold, neutral-stance prompt | ✅ 2026-05-23 `a8efd30` |
| **G.2c** | Stage 3 (Look Forward) — dialogue completion + skip path + prior-stages carry-forward | ✅ 2026-05-23 `39322a7` |
| **G.3** | Learning Portrait + PDF + Article 50(2) strict variant + UX polish (accept→portrait + Continue) | ✅ 2026-05-23 `815c5fb` |
| **G.4** | M15 content alignment (D.3a dual-signal DTP) + Phase-G-closure Epilogue sweep + M15 RAG re-ingest | ✅ 2026-05-24 — 10 DML edits on 2 `modules_modulecontent` rows (id=925 main_content, id=958 assessment), 43 fresh RAG chunks |
| **G.5** | Sweep — roadmap (this update) + TD-011 close + TD-022/023 open + literature note §16 + Desktop mirror | ✅ 2026-05-23 |
| **G.6 design** | Magazine design upgrade proposal v2-revised (separate proposal, PI-approved before any G.6 code) | ✅ 2026-05-23 (this roadmap entry) |
| **§23 prompt** | 5-line anti-anthropomorphisation rule on `EpilogueDialogueAgent._SYSTEM_PROMPT` + `test_persona_guards_present` (standalone, before G.6a) | ✅ 2026-05-23 `0e52044` |
| **G.6a** | Aletheia aspect + `static/css/epilogue.css` register CSS, no markup change | ✅ 2026-05-23 |
| **G.6b** | `stage0.html` redesign + `_stage0_panel.html` restyle + label-removal sweep on Stage 0 surface | ✅ 2026-05-23 |
| **G.6c** | `dialogue.html` phase-as-chapter rewrite (fixes seam bug) + `_aletheia_header.html` + `_phase_chapter.html` partials + live sample-review + §23 two-layer verification | ✅ 2026-05-23 (later deactivated in deprecation 2026-05-24) |
| **§24 / §24.11 / §24.12** | Three sequential prompt-engineering correction cycles after live testing; each fixed prior failure but surfaced a new one in the same family — root cause structural, not prompt-surface | ✅ implemented + tested |
| **G.6d** | `portrait.html` magazine spread + `pdf/learning_portrait.html` magazine register + olive ornament + Article 50(2) metadata regression re-run | ❌ Cancelled by deprecation |
| **G.6e** | Test sweep + literature note §16 cross-check + roadmap design-complete badge | ❌ Cancelled by deprecation (replaced by closure commit) |
| **G.deprecation** | Phase G closure: Aletheia removal from Epilogue (dialogue + portrait views + URLs + templates deactivated; PDF infrastructure preserved for Phase H; Aletheia identity preserved for Phase J) + deferred design Phase J | ⏳ 2026-05-24 (this entry) |

**Tech-debt entries that Phase G opens / closes:**
- **TD-011** (Full PROODOS Epilogue implementation) — ✅ CLOSED 2026-05-23 via G.0-G.3.
- **TD-022** (Epilogue replay post-pilot) — Active, deferred to post-pilot; one-shot `OneToOneField` invariant preserved during the pilot for research integrity.
- **TD-023** (M15 RAG corpus versioning) — Acknowledged, no fix planned under the pilot feature-freeze; logged so the assumption is explicit if mid-pilot M15 edits ever become necessary.

**Research-variable additions (v2 §13, crosswalked into Phase §H.5):** `dialogue_entered` (Q5 measured variable), per-stage completion timestamps, dialogue turn counts per stage, stage-2 skip + metrics, the dialogue corpus (qualitative — extends §H.5), Stage 2 interpretive responses (qualitative), the Learning Portrait text (qualitative — already named in §H.5).

**Image-based retrospective reflection (G-D6 from v2 §4.1).** Parked — candidate for Phase H / v2.0, not Phase G. The post-completion Epilogue is retrospective (the artefacts already exist), so the multimodal idea has its natural home here, but the v2 proposal explicitly rules it out of scope for the current Phase G.

---

### Phase H — Closing Flow + Certificate + Dashboard Redesign

**Στόχος:** Καθαρή ροή τέλους που: (α) σέβεται το Ning validation envelope με 3 timepoints, (β) δίνει στον εκπαιδευτικό μια permanent landing surface (redesigned dashboard) με το certificate αναγνωρισμένο εκεί, (γ) κρατάει ανοιχτή την πόρτα για ξεχωριστή follow-up μελέτη χωρίς να δεσμεύεται σε in-platform infrastructure τώρα.

**Canonical design proposal:** `proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md` (σχεδιάστηκε 2026-05-25, supersedes την προηγούμενη pre-G-closure version του παρόντος §H block).

**Rescissions από prior roadmap §H** (2026-05-25): η delayed-post-test scope (T2b, email cron, classroom-integration questionnaires, in-platform interview cohort) αφαιρέθηκε από το Phase H. Justification στο proposal §2.2: το AILST paper (Ning et al. 2025) είναι cross-sectional CFA — δεν προβλέπει delayed administration· ο longitudinal gap του Erhardt et al. (2025) απαντιέται από το DTP cross-module tracking (15 timepoints), όχι από delayed AILST· η honest βιβλιογραφία για delayed post-test (Kirkpatrick / Guskey / Joyce-Showers) δεν είναι στο lit-note. Delayed wave επιστρέφει ως **Future Work** (βλ. §I.6) αν τα DTP pilot data αναδείξουν ερώτημα που μόνο αυτή μπορεί να απαντήσει — τότε σχεδιάζεται ως **ξεχωριστή μελέτη με δικό της IRB protocol**, όχι ως extension της πλατφόρμας.

#### H.1 — Πλήρης ροή τέλους

```
M15 ολοκλήρωση
    ↓
/epilogue/                  (Stage 0 Personal Evolution Dashboard,
                             magazine register)
    ↓ "Continue"
POST /epilogue/complete/    (_post_epilogue_destination → T2)
    ↓
/ailst/t2/                  (AILST 36 items, 4 pages)
    ↓ final page POST
ailst_complete_view         (acknowledgement, no scores per C.2.3 D4)
    ↓ "Go to dashboard"
/dashboard/                 (REDESIGNED — TD-021 resolution:
                             - UNESCO 5×3 progress matrix
                             - Next-action card
                             - Certificate panel ENABLED:
                               "Download Certificate of Attendance")
```

#### H.2 — Research justification (Ning-anchored)

- T0 (post-onboarding) / T1 (post-M5) / T2 (post-M15) — paired comparisons T0→T1, T1→T2, T0→T2 ανά παράγοντα + Cohen's d for paired samples (Ning's convention)
- DTP composite trajectories = within-pilot longitudinal συμπλήρωμα (15 timepoints)
- **Three acknowledged limitations** στο methods chapter: (L1) cross-sectional validation envelope του Ning paper, (L2) Greek translation provenance, (L3) single-site / single-cohort / single-PI pilot (n≈110)
- Πλήρες reasoning στο proposal §4 + `Literature_Review_Synthesis_Note(1).md` §5 (rewritten 2026-05-25)

#### H.3 — Certificate of Attendance

- Νέο app `apps/certification/` με `CertificateOfAttendance` model (OneToOneField, frozen `teacher_display` + `modules_summary` at issue time, 16-char URL-safe verification code)
- Gate = T2 submission (εξαλείφεται "completion certificate without completing T2" προϋπόθεση του current consent text)
- PDF generation επαναχρησιμοποιεί το dormant `_generate_portrait_pdf` του `apps/epilogue/views.py:193` + Article 50(2) machinery (JSON-LD + PDF Info dict)
- **"No AI involved" provenance footer** — το certificate δεν είναι AI artefact (deterministic generation από submitted data)
- Public verification endpoint `/certification/verify/<code>/` — scope ανοιχτό (βλ. proposal §10 Q2)

#### H.6 — Optional follow-up consent στο onboarding Step 3

- Νέο `FOLLOWUP_RECRUITMENT_TEXT_V1_PRE_IRB` constant στο `apps/compliance/copy.py`
- Τρίτο checkbox δίπλα στα δύο υπάρχοντα (RESEARCH_PARTICIPATION + DATA_SHARING) — ίδιο component pattern, ίδιο versioning workflow
- `ConsentRecord` με `consent_type='followup_recruitment'` (no DB migration — table accepts arbitrary types)
- Revoke endpoint στο Privacy dashboard
- **Consent V2 bump** μαζί — cleanup του stale dialogue/portrait reference στο `AI_IMPACT_ASSESSMENT_V1_PRE_IRB` §2 (Phase G closure follow-up)
- **Δεν υπόσχεται μελλοντική μελέτη** — μόνο pool για πιθανή πρόσκληση· in-context re-consent στη στιγμή της πρόσκλησης αν τελικά γίνει

#### H.7 — Dashboard redesign (TD-021 resolution)

- **Option (a) + slim (b) hybrid:** per-teacher UNESCO 5×3 progress matrix + next-action card + certificate panel
- Lift του D.4 cohort 5×3 component σε shared partial (`templates/partials/_unesco_matrix.html`); cohort + personal callers, μία visual asset
- **Hard constraint preserved:** dashboard = completion-structure, **όχι** developmental-evolution (Epilogue Stage 0 owns evolution)
- Cleanup: `modules_with_progress` flat list αφαιρείται από `templates/home.html` + view context· inline emojis αφαιρούνται (workflow rule)

#### H.8 — Housekeeping

- TD-016 resolution: `apps/compliance/management/commands/prune_old_consent_records.py` — dry-run default, `--apply` flag, mirror of `redact_old_consent_ips` pattern
- Run by external scheduler (cron / Windows Task Scheduler) — πλατφόρμα δεν schedule

#### H.5 — Τι κερδίζει η διατριβή

| Διάσταση | Πριν την Phase H | Μετά την Phase H |
|---|---|---|
| Measurement | Pre/Post (T0, T1, T2) — αλλά χωρίς clean closing surface | Pre/Post (T0, T1, T2) με Ning-anchored design + ρητές acknowledged limitations + clean closing flow |
| Certificate | Promise στο consent χωρίς υλοποίηση | Auto-generated PDF με verification code + Article 50(2) machinery |
| Dashboard | Duplicate του Modules menu (TD-021) | Distinct surface: UNESCO 5×3 personal progress + certificate landing |
| Compliance | Stale dialogue/portrait references στο AI Impact Assessment + 7-year retention TD open | Consent V2 cleanup + retention command shipped |
| Future research | Καμία door για delayed wave | Optional pool consent στο onboarding — pool υπάρχει αν αποφασιστεί ξεχωριστή μελέτη |

**Phase G crosswalk (καταγεγραμμένο 2026-05-23, μερικώς υπερβλέπεται μετά G closure 2026-05-24):** οι Phase G qualitative-corpus rows (`dialogue_turns`, `learning_portrait_text`) **δεν υφίστανται** πια ως teacher-facing surfaces μετά την Aletheia deprecation — τα fields διατηρούνται σχηματικά αλλά δεν συμπληρώνονται. Οι quantitative engagement rows (`dialogue_entered`, per-stage timestamps, turn counts, `stage2_skipped`) επίσης παύουν να είναι zero/null για όλους τους post-deprecation χρήστες. Το `EpilogueCompletion.completed_at` παραμένει ο μόνος ενεργός Phase G research variable. Πλήρες record: `PHASE_G_DIALOGUE_DEPRECATION_20260524.md`.

#### H.9 — Κόστος και tradeoffs

- **Total effort:** ~8–10 working days (H.1+H.2 = 1d, H.3 = 2-3d, H.6 = 1-2d, H.7 = 3-4d, H.8 = 0.5d)
- **Zero AI cost** — καμία LLM call σε όλη την Phase H
- **Open questions** (proposal §10): Verbert et al. 2014 verification, public verification view scope, Greek certificate timing, future delayed post-test placement
- **Migrations:** ένα (H.3 `certification` app skeleton + CertificateOfAttendance model) — pg_dump backup + sqlmigrate dry-run πριν apply

**Αρχεία αναφοράς:**
- `proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md` (canonical design)
- `Literature_Review_Synthesis_Note(1).md` Section 5 (rewritten 2026-05-25 — Ning-anchored 3-timepoint design + L1/L2/L3 limitations)
- `proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md` (Phase G closure decision record + preserved infrastructure inventory)
- `TAB1_DISSERTATION_CHAPTER_FULL_v2.md` Section 7.4 — limitations να ξαναγραφούν να αντικατοπτρίζουν L1/L2/L3 (όχι T2b removal)
- `TECH_DEBT_LOG.md` TD-016 + TD-021 (scheduled to resolve in this phase)

---

### Phase I — Dissertation Writing

**Στόχος:** Πλήρες dissertation manuscript. Έρχεται τελευταίο, αφού όλη η πλατφόρμα και τα features είναι στη θέση τους.

#### I.1 — TAB1 chapter revision phases
Το TAB1 chapter γράφτηκε στο SESSION_LOG_APR2026_TAB1. Έλαβε Gemini review που εντόπισε 9 items σε 3 priority tiers:
- **R1 (~6 ώρες, critical):** 3 citation additions — triangulation πέρα από Zhou 2026, TPB/TAM connection, intention-action gap subsection
- **R2 (~4-5 ώρες, important):** 5 items μετά την επίλυση του #5
- **R3 (~30 λεπτά, polish):** 1 item

**Αρχεία αναφοράς:**
- `TAB1_DISSERTATION_CHAPTER_FULL_v2.md` — current draft
- `TAB1_DISSERTATION_CHAPTER_GEMINI_REVIEW_NOTES_v2.md` — review items (αν υπάρχει στο project)
- `SESSION_LOG_APR2026_TAB1.md` — context της revision

#### I.2 — TAB chapters (νέα)
- TAB2 chapter (TAB2 magazine + subject boxes + NotebookLM videos)
- TAB3 chapter (3 challenges architecture)
- TAB4 chapter (XAI explanations + assessment design)
- TAB5 chapter (RAG + RTM + DTP + Peer Synthesis — μέρος υπάρχει στο `DISSERTATION_TAB5_XAI_HITL.md`)

#### I.3 — Research instrument chapters
- RTM (theoretical grounding + implementation + analysis)
- DTP
- Peer Synthesizer
- TCS (νέο, από Phase D)

#### I.4 — Cross-cutting chapters
- System Design (πλήρης αρχιτεκτονική, multi-agent)
- Trustworthy AI Positioning (XAI + HITL + EU AI Act)
- Onboarding & AILST 3-timepoint measurement framework (Ning-anchored, L1/L2/L3 limitations)
- Closing Flow & Certificate Design (Phase H — `PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md`)
- Multimodal Reflection (Phase F)
- Discussion + limitations + future work (including delayed post-test as separate future study — see proposal §10 Q4)

#### I.5 — Παράλληλα: δημοσιεύσεις
- "Implementing EU AI Act Limited Risk Compliance in Teacher PD Platforms" (AIED 2027 / EC-TEL)
- "Multi-agent architecture for Reflective Teacher PD"
- "Multimodal Reflection in AI-Mediated Teacher Development"
- (Conditional) "Immediate vs Delayed Post-test Effects in AI-Mediated Teacher PD" — depends on §I.6 below being activated

#### I.6 — Future Work: Delayed post-test study (conditional, post-pilot)

**Status:** Conditional — not committed. Activates only if a specific condition is met (see Trigger below).

**Στόχος:** Εξωτερική μελέτη που μετράει AILST 4-6 εβδομάδες μετά την ολοκλήρωση του pilot (T2b), συν 5-7 classroom-integration questions + ημι-δομημένες συνεντεύξεις σε υποσύνολο των ανταποκριθέντων. **Όχι in-platform extension** — ξεχωριστή μελέτη με δικό της IRB protocol, δικό της consent form (στη στιγμή της πρόσκλησης), δικό της data infrastructure (πχ Google Forms / Qualtrics + Zoom interviews).

**Trigger για activation:** Τα DTP pilot data αναδείκνυουν ερώτημα που μόνο μια delayed AILST wave μπορεί να απαντήσει — πχ μη-μονοτονικά trajectories που υπαινίσσονται delayed integration patterns, ή divergence μεταξύ DTP composite signal και T2 AILST score που χρειάζεται post-pilot disambiguation.

**Recruitment pool:** Οι συμμετέχοντες που έδωσαν optional follow-up consent στο onboarding Step 3 (Phase H.6 — `FOLLOWUP_RECRUITMENT_TEXT_V1_PRE_IRB`). Η συναίνεση στο pool **ΔΕΝ είναι συναίνεση στη μελέτη** — εφόσον η μελέτη ξεκινήσει, στέλνεται νέο study-specific information sheet + νέο consent form. Καμία αυτόματη εγγραφή.

**Βιβλιογραφική θεμελίωση (προαπαιτούμενο πριν activation):** Το lit-note σήμερα δεν έχει references για delayed post-test design. Πριν activation, πρέπει να γίνει expansion με Kirkpatrick (1959/1994) Level 3/4, Guskey (2002) 5-level PD evaluation framework, Joyce & Showers (2002) transfer-of-training literature — μετά verify-before-cite rule. Χωρίς αυτή τη βάση, η μελέτη δεν είναι defensible.

**Dependencies:** (1) optional follow-up consent pool υπάρχει (delivered από H.6), (2) DTP pilot analysis ολοκληρωμένη (delivered από Phase I), (3) lit-note expansion πραγματοποιήθηκε, (4) ξεχωριστή IRB submission εγκριμένη.

**Αν activate:** η §I.5 conditional paper γίνεται feasible.

**Reasoning record:** `PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md` §2.2 + §10 Q4 για το rationale αφαίρεσης από την Phase H + τις συνθήκες re-opening.

---

### Phase J — Aletheia chatbot re-introduction (DEFERRED, design only)

**Στόχος:** Επανατοποθέτηση του Aletheia chatbot στην πλατφόρμα σε
ένα πλαίσιο όπου τα τρία δομικά προβλήματα που οδήγησαν στην
απομάκρυνσή του από το Epilogue *δεν* ισχύουν. Διατηρεί την
επένδυση σε infrastructure (UI identity, persona prompt-craft,
multi-turn agent harness, Article 50 transparency wiring) χωρίς να
αναζωπυρώνει το reflection-fatigue και RPE-dilution πρόβλημα.

**Status:** ⏸ Deferred — *no implementation before pilot ends*.
Επανάληψη της απόφασης μετά το pilot debrief, όταν θα υπάρχουν
empirical data για το πραγματικό cognitive load των 15 modules και
το τι έλειψε από την εμπειρία του εκπαιδευτικού.

**Trigger για re-evaluation:** Pilot debrief (post-Phase H / start of
Phase I writing). Αν το post-pilot interview material δείξει
ξεκάθαρα ένα σημείο όπου ένας conversational companion προσθέτει
αξία *χωρίς* να επαναλαμβάνει αυτό που ήδη κάνει ένα από τα 15
modules ή το AILST framework, τότε ανοίγει το Phase J implementation
ticket.

**Reusable infrastructure (preserved 2026-05-24):**

| Asset | Location | Reuse target |
|---|---|---|
| Aletheia visual identity (logo + 4 size assets + olive variant) | `static/images/aletheia/` + `Aletheia2048Square*.png` | All four candidate placements below |
| Aletheia colour palette + classical-Greek register | `apps/modules/templatetags/module_design.py` `ALETHEIA_COLOURS` + `epilogue_aspect_colour` template tag | UI consistency wherever Aletheia surfaces |
| Multi-turn agent harness | `apps/agents/epilogue_dialogue.py` (deactivated, in-place) | Any future conversational agent — rip out reflection-specific logic, keep turn-management + Gemini wiring + Article 50 |
| Anti-parrot / anti-recitation / three-shape canon | Same file + master proposal §24.11 / §24.12 | Future companion prompt engineering — engineering lessons even if the specific rules don't transfer |
| EU AI Act Article 50(1) banner pattern | Dialogue template (deactivated) | Any future model interaction surface |
| EU AI Act Article 50(2) PDF metadata pattern (JSON-LD + PDF Info dict) | `_generate_portrait_pdf` helper in `apps/epilogue/views.py` (will be relocated in Phase H) | Phase H certificate of attendance (primary) + any future generated artefact |
| Persona prompt craft (Aletheia identity, register, honour-uncertainty rule) | `EpilogueDialogueAgent._SYSTEM_PROMPT` segments §23 | Future companion persona — starting point, not finished product |

**Four candidate placement options for the next design cycle**
(όχι πρόταση — *checklist* από όπου θα ξεκινήσει το design
proposal):

1. **Onboarding companion (T0-side).** Aletheia ως guide στο
   onboarding wizard για να εξηγεί τι θα συμβεί, να απαντά σε
   "What does X mean?" ερωτήσεις, να συνοδεύει το consent step.
   Δεν αναμετριέται με το reflection problem γιατί δεν ζητάει
   reflection — απαντά σε γνωσιακές ερωτήσεις.

2. **Always-on help (πανταχού παρόν, στο μενού).** Aletheia ως
   help-bot με knowledge base για τα modules, RAG over the
   teacher's own dashboard data ("τι έδειξα στο DTP του M5;"),
   troubleshooting. Conversational αλλά utility-shaped, όχι
   reflective.

3. **AI literacy sandbox (νέο module / νέα ενότητα).** Aletheia
   ως partner για ένα δομημένο "συνομίλησε με ένα AI για να
   καταλάβεις πώς λειτουργεί" experience — εκπαιδευτικό
   περιεχόμενο για το πώς να *χρησιμοποιείς* AI ως εκπαιδευτικός.
   Αναβαθμίζει το RPE framework γιατί ο εκπαιδευτικός εξασκείται
   στο prompt engineering με coaching.

4. **Post-pilot deferred (κράτηση χωρίς απόφαση).** Αν τα pilot
   data δείξουν ότι κανένα από τα τρία παραπάνω δεν προσθέτει
   ξεκάθαρη αξία, παγώνει το infrastructure ως historical asset
   και η dissertation χρησιμοποιεί τη συνολική εμπειρία (design →
   build → live test → strategic removal) ως single methodological
   case study στο evidence-driven AI-mediated tooling.

**Design proposal ticket:** TBD — δεν δημιουργείται entry στο
TD log τώρα γιατί τυπικά είναι "future work", όχι "tech debt". Θα
ανοίξει ως νέο proposal file `proodos_files/PHASE_J_*.md` όταν
ξεκινήσει το re-evaluation.

**Αρχεία αναφοράς:**
- `proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md` — αιτιολογία απομάκρυνσης + scope of preserved infrastructure
- `proodos_files/PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2_20260521.md` §6-7 + §23-24.12 — preserved historical design + prompt-engineering arc
- `proodos_files/ALETHEIA_PROMPT_REVIEW_BRIEFING_20260524.md` — dual-reviewer methodology evidence
- `proodos_files/V23_PROMPT_VERIFICATION_20260524.md` — live verification methodology pattern
- `proodos_files/POST_V23_DIALOGUE_TURNS_mavros_20260524.json` + `PRE_V23_*.json` — empirical evidence για τι λειτούργησε και τι όχι

---

## 4. Ξεπαρκαρισμένες ιδέες με αιτιολόγηση

Από τις παλιές παρκαρισμένες ιδέες, οι παρακάτω αναβαθμίζονται σε ενεργές φάσεις γιατί προσφέρουν ουσιαστικό όφελος στο σύστημα και τη διατριβή.

### 4.1 Career Stage Differentiation (Zhou Idea 6) → Phase C.2

**Γιατί.** Το `teaching_years` field ήδη υπάρχει στη DB. Δεν χρειάζεται καν schema change. Με μια απλή προσθήκη παραμέτρου στο RAG, αποκτάμε νέα διάσταση εξατομίκευσης που:
- Απαντάει σε γνωστή δυσκολία (νέοι vs έμπειροι έχουν διαφορετικά belief profiles)
- Παράγει νέα ερευνητική μεταβλητή για ανάλυση
- Συνδυάζεται φυσικά με το onboarding που ξαναγράφεται για το EU AI Act

### 4.2 AILST Baseline (Ning et al. 2025) → Phase C.2

**Γιατί.** Ήταν ήδη planned ως measurement tool στο `Literature_Review_Synthesis_Note.md` Section 5, αλλά δεν είχε εκτελεστική φάση στο roadmap. Αν το βάλουμε στο νέο onboarding (που έτσι κι αλλιώς ξαναγράφεται):
- T0 baseline για το pilot
- Σύγκριση με T1 (post-M5) και T2 (post-M15)
- Primary research variable για τη διατριβή
- Καλύπτει το κενό measurement που η Ning et al. αναγνωρίζει ως πιο παραμελημένο (Ethics dimension)

### 4.3 Multi-agent Refactor → Phase E — ✅ DELIVERED (2026-05-14)

**Γιατί.** Δεν ήταν απλώς code cleanup. Ήταν αρχιτεκτονική επιλογή που:
- Δίνει υλικό για ένα ολόκληρο dissertation chapter ✅ (7 distinct contributions, §3 Phase E.3)
- Καθιστά τα νέα features (Multimodal, Epilogue) πιο εύκολα να υλοποιηθούν ✅ (hierarchy ready for extension via `generate()`/`extract()`)
- Επιτρέπει cleaner integration με το EU AI Act compliance work ✅ (CP-9 enforced by construction at the base class level; provenance writing centralised)
- Ευθυγραμμίζεται με την κατεύθυνση της βιβλιογραφίας (multi-agent systems σε education) ✅ ("AI commits, human disputes" vs "AI proposes, human ratifies" framing applicable to broader HITL literature)

**Outcome (2026-05-14).** 11 commits, 316 tests, monolith deleted, four agents under `apps/agents/`. See §3 Phase E for the full retrospective.

### 4.4 Multimodal Reflection (voice) → Phase F

**Γιατί.** Άμεση απάντηση σε critique της literature ότι το AI-mediated PD είναι text-heavy. Δίνει:
- Inclusive design contribution (φωνή για εκπαιδευτικούς που σκέφτονται καλύτερα προφορικά)
- Νέα ερευνητική διάσταση (text vs voice reflection patterns)

*Image input αφαιρέθηκε από το Phase F στις 2026-05-20 — το TAB5 reflection είναι προοπτικό, δεν υπάρχει artefact να συνδεθεί. Re-filed ως Phase G candidate.*

### 4.5 RTM Heatmap Visualization → Phase D.4 (μαζί με UNESCO Dashboard)

**Γιατί.** Ξεκίνησε ως post-pilot future work, αλλά αν υλοποιηθεί τώρα ως μέρος του Dashboard:
- Έτοιμο εργαλείο για ανάλυση όταν έρθουν τα δεδομένα
- Visual για conference presentations από τη μέρα 1
- Δείχνει empty cells που γεμίζουν δυναμικά

---

## 5. Παρκαρισμένες ιδέες (future work / v2.0)

Αυτές οι ιδέες παραμένουν παρκαρισμένες. Είτε δεν προσφέρουν αρκετή αξία αυτή τη στιγμή, είτε απαιτούν ριζική αλλαγή που υπερβαίνει το dissertation scope.

| Ιδέα | Πηγή | Γιατί παρκαρισμένη |
|---|---|---|
| HITL Feedback Loop για RAG prompt optimization | Παλιό roadmap πρόταση Α | Χρειάζεται post-pilot data. Φυσικό next step μετά τη διατριβή. |
| Bayesian Knowledge Tracing | Παλιό roadmap πρόταση 4 | Πολύ μεγάλο feature, δεν προσθέτει ξεκάθαρη αξία πέρα από όσα κάνουν RTM/DTP/TCS. |
| Real-time adaptive content | Παλιό roadmap πρόταση 5 | Απαιτεί ριζική αλλαγή του content pipeline. v2.0 της πλατφόρμας. |
| PWA / offline capability | Παλιό roadmap πρόταση 7 | Service worker + cache. Καθαρά UX, μηδέν research value. |
| Community forum intelligence | Παλιό roadmap πρόταση 6 | Semantic search σε forum posts. Καλό για adoption, όχι για διατριβή. |
| Anonymous Forum (Zhou Idea 4) | Zhou paper | UX βελτίωση, αλλά αλλάζει τη φύση του forum. Post-pilot v1.1. |
| Action Research M15 (Zhou Idea 3) | Zhou paper | Novel contribution που απαιτεί classroom impact study — πέρα από feasibility scope. |
| Federated Learning architecture | XFRS Idea 4 | Απαιτεί ριζική αρχιτεκτονική αλλαγή. Future work chapter στη διατριβή. |
| Belief Profiling με 5 sub-dimensions (Zhou Idea 1) | Zhou paper | Καλύπτεται μερικώς από AILST (Phase C.2). Πλήρης υλοποίηση = future work. |

---

## 6. Σχεδιαστικές αρχές

Αρχές που διαπερνούν όλη τη δουλειά. Ισχύουν αναλλοίωτες σε κάθε φάση.

**6.1 Cost discipline.** €1/χρήστη hard constraint. Πραγματικό κόστος verified πολύ κάτω από το όριο.

**6.2 Anti-hallucination.** RTM extractions πάντα grounded με quotes από το original reflection.

**6.3 Pattern detection όχι prediction.** Το DTP περιγράφει τι άλλαξε, δεν προβλέπει τι έρχεται.

**6.4 TAB3 design.** Structured evaluation forms (radio, checkboxes) > free text. Hard character limits.

**6.5 TAB4 balance.** Ερωτήσεις αντικατοπτρίζουν τις πραγματικές αναλογίες του TAB2 + activity.

**6.6 Reflection system.** On-demand buttons > auto-loading. Δίνουν επιπλέον engagement data.

**6.7 Content placement (αμετάβλητο).**
- Five Roles Framework (Potkalitsky) → primary home M14, forward reference M9
- School AI policy → M12 (όχι M11)
- Ethics topics → M2/M7/M12 only

**6.8 RAG corpus strategy.** Universal docs (UNESCO, RPE) + module-specific subject examples.

**6.9 Research framing.** Design science / feasibility study. Novel instruments (RTM, DTP, Peer, TCS, HITL, Career Stage, AILST) ως primary contribution. EU AI Act Limited Risk positioning.

**6.10 Workflow.**
- Chat window για design / decisions / scripts
- Claude Code για DB execution
- Dry-run + report πριν apply
- Backup table πριν την πρώτη εφαρμογή
- Content before code: structure approval πριν τη συγγραφή
- "You are always the final judge" σε όλα τα Toolbox PART4 entries

**6.11 NotebookLM Videos.** Συνοδεύουν αλλά δεν αντικαθιστούν το TAB2 content. Disclaimer πάντα ορατό.

---

## 7. Ευρετήριο αρχείων αναφοράς

### 7.1 Αρχεία που διαγράφονται (idea/roadmap docs ενσωματωμένα στο παρόν)

| Αρχείο | Περιεχόμενο που ενσωματώθηκε |
|---|---|
| `PROODOS_Updated_Roadmap_Apr2026.md` | Φάσεις + παρκαρισμένα |
| `PROODOS_Next_Steps_Mar2026.md` | Εκκρεμότητες + content placement |
| `Zhou_2026_Improvement_Ideas.md` | Subject Intro & M5/M8 (ολοκληρωμένα), Career Stage (Phase C.2), Action Research (parked) |
| `XFRS_Technical_Improvement_Ideas.md` | DTP XAI narrative (Phase D.3), FL (parked) |
| `OPTIMIZATION_PATCH_APR2026_backup.md` | Όλα ολοκληρωμένα στο Section 2.4 |
| `RTM_REDESIGN_PATCH_APR2026.md` | RTM Redesign block στο Section 2.4 |
| `SUBJECT_INTRO_HOOKS_PATCH_APR2026.md` | Section 2.4 |
| `MODULE_CONTENT_GUIDE_PATCH_M5_PART3_APR2026.md` | Phase A (ολοκληρωμένη) |

### 7.2 Session logs (κρίνεις εσύ — ιστορικό για τη διατριβή)

| Αρχείο | Σημείωση |
|---|---|
| `SESSION_LOG_OPT_PATCH_APR2026.md` | Έχει χρήσιμο IDs table + PENDING tasks |
| `SESSION_LOG_APR2026_TAB1.md` | TAB1 redesign + Gemini review context |
| `SESSION_LOG_TAB2_MAGAZINE_APR2026.md` | TAB2 magazine implementation |
| `SUBJECT_BOX_NORMALIZATION_LOG_APR2026.md` | Subject box normalisation |
| `M5_M8_ORCHESTRATION_CHANGELOG_APR2026.md` | Co-orchestration shift detail (πιθανώς αξίζει για dissertation) |

### 7.3 Active references — μην τα αγγίξεις

**Active specs (Phases C → G):**

| Αρχείο | Χρήση |
|---|---|
| `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` | Phase C — όλες οι λεπτομέρειες των 4 συμπληρωμάτων |
| `M16_CAPSTONE_REFLECTION_SPEC.md` | Phase G — αρχικό spec Epilogue |
| `PROODOS_EPILOGUE_PATCH_APR2026.md` | Phase G — naming + 4-stage architecture update |

**Authoritative tech docs (research instruments):**

| Αρχείο | Χρήση |
|---|---|
| `RTM_Feature_Specification_Part3.md` | RTM technical reference |
| `DTP_Documentation_Mar2026.docx` | DTP technical reference |
| `Cross_Specialty_Peer_Synthesizer_Documentation.md` | Peer Synthesizer reference |

**Developer guides:**

| Αρχείο | Χρήση |
|---|---|
| `MODULE_CONTENT_GUIDE.md` | Content development reference |
| `M1_SYSTEM_VERIFIED.md` | Master architecture reference |
| `Doctoral_System_Design_Summary.md` | High-level overview |
| `CONTENT_VALIDATION_MATRIX.md` | Validation reference (συμπληρώνεται στο Phase B.1) |
| `TAB2_SQL_PRODUCTION_GUIDE.md` | TAB2 SQL patterns |
| `TAB3_NEW_MODULE_GUIDE.md` | TAB3 development |
| `TAB4_TAB5_NEW_MODULE_GUIDE.md` | TAB4/5 development |
| `TAB4_Developer_Guide.md` | TAB4 specific |
| `FORUM_THREAD_INFO_GUIDE.md` | Forum |
| `COMMUNITY_FORUM_DOCUMENTATION.md` | Forum feature documentation |

**Dissertation drafts:**

| Αρχείο | Χρήση |
|---|---|
| `TAB1_DISSERTATION_CHAPTER_FULL.md` | Παλιά έκδοση (v1) |
| `TAB1_DISSERTATION_CHAPTER_FULL_v2.md` | Τρέχουσα έκδοση — Phase H.1 revision base |
| `DISSERTATION_TAB5_XAI_HITL.md` | TAB5 XAI/HITL chapter base |

**Literature & frameworks:**

| Αρχείο | Χρήση |
|---|---|
| `Literature_Review_Synthesis_Note.md` | Literature reference + measurement plan |
| `unesco_ai_competency_framework_for_teachers.pdf` | UNESCO framework primary source |
| `Reconceptualizing_Prompt_Engineering_as_Reflective_Professional_Practice_FINAL_VERSION.pdf` | RPE Framework paper |
| `Analysis_and_Implementation_of_the_UNESCO_AI_Competency_Framework.pdf` | UNESCO implementation paper |
| `EduPrompt_Studio__Technical_Documentation_v2_1.pdf` | EduPrompt Studio (M8 TAB3) |

---

## Closing remark

Με την υλοποίηση των φάσεων B–I, η πλατφόρμα PROODOS θα είναι:

- **Πρώτη** teacher PD platform με RAG + RTM + DTP + Peer Synthesis + TCS + Career Stage + AILST baseline
- **Πρώτη** με 3-level XAI architecture
- **Πρώτη** με HITL dispute mechanism σε κάθε AI output
- **Πρώτη** πλήρως συμβατή με EU AI Act (Limited Risk)
- **Πρώτη** που διακρίνει surface από deep epistemic engagement
- **Πρώτη** multi-agent platform για teacher PD
- **Πρώτη** με multimodal reflection (text + voice + image) για AI-mediated PD
- **Πρώτη** με τρι-φασικό post-test design (immediate + delayed) που απαντάει στο longitudinal evidence gap

Αυτά δεν είναι incremental. Είναι σύνολο first-of-kind features που μαζί συγκροτούν τη διατριβική συμβολή.

---

*Συντάχθηκε: Απρίλιος 2026 (έκδοση 4.0)*
*Επόμενη αναθεώρηση: μετά την ολοκλήρωση Phase C*
