# PROODOS EduAI — Ενοποιημένο Roadmap

**Έκδοση:** 4.0 — Απρίλιος 2026
**Σκοπός:** Ενιαίο σχέδιο πορείας. Αντικαθιστά όλα τα προηγούμενα idea/roadmap/patch αρχεία.

---

## Περιεχόμενα

1. Πρόλογος
2. Τι έχει ολοκληρωθεί
3. Φάσεις πορείας (A → I)
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

#### C.1 — AI Impact Assessment PDF

5σέλιδο επίσημο έγγραφο που τεκμηριώνει το PROODOS ως Limited Risk:
- System description
- Risk classification rationale (γιατί Limited όχι High)
- Obligation coverage matrix
- Voluntary high-risk obligations
- Risk mitigation measures

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 1).

#### C.2 — Onboarding Redesign (ενοποιημένο)

Νέο multi-step onboarding που περιλαμβάνει:

**Step 1 — AI Disclosure Modal (Article 50(1))**
- Νέο `consent_records` με `consent_type='ai_disclosure'`
- Modal δεν κλείνει χωρίς acknowledgment
- Κείμενο: "AI-Assisted PD", "Όλες οι προτάσεις είναι συμβουλευτικές", "Εσύ είσαι ο τελικός κριτής"

**Step 2 — Career Stage Capture**
Το `teaching_years` field ήδη υπάρχει στη DB (`'0-5'`, `'6-15'`, `'16-25'`, `'25+'`). Δεν χρειάζεται schema change. Ζητάμε ρητά την τιμή και την χρησιμοποιούμε σε:
- RAG queries με career_stage parameter
- Feedback emphasis (νέοι: critical trust + ethics, έμπειροι: workload relief + identity reframing)

**Step 3 — AILST Baseline (T0)**
Ολόκληρη η AILST scale (Ning et al. 2025, 36 ερωτήματα, 4 παράγοντες):
- AI Perception
- Knowledge & Skills
- Applications & Innovation
- Ethics

Αποθηκεύεται ως T0 baseline. Σύγκριση με T1 (μετά M5) και T2 (μετά M15) → primary research variable για τη διατριβή.

**Step 4 (προαιρετικό) — AI-TPACK self-assessment**
Σύντομο 14-item self-assessment από το Eyal (2025) framework. Δεν είναι αυστηρή προαπαίτηση — μπορεί να μπει σε δεύτερη φάση αν το onboarding γίνει υπερφορτωμένο.

**Αρχεία αναφοράς:**
- `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 2) — onboarding modal spec
- `Literature_Review_Synthesis_Note.md` Section 5 — AILST + AI-TPACK measurement plan
- `M1_SYSTEM_VERIFIED.md` — current 3-step onboarding (Teaching Context → AI Experience → Goals)

#### C.3 — Machine-readable AI content markers (Article 50(2))

- HTML data attributes σε όλα τα AI cards (`data-ai-generated`, `data-ai-model`, `data-ai-timestamp`)
- Page-level meta tags
- JSON-LD structured data
- Template tag `{% ai_provenance %}`

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 3).

#### C.4 — Data Retention & Deletion Policy (GDPR + EU AI Act)

- Profile page section "Privacy & Data"
- View / Download / Delete buttons (καλούν την υπάρχουσα `anonymize_user()`)
- Privacy Policy page (markdown rendered)
- Automated cleanup jobs τεκμηριωμένα

**Αρχείο αναφοράς:** `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 4).

**Έξοδος Phase C:** Πλήρης συμμόρφωση με EU AI Act + νέα ερευνητική μεταβλητή (career stage) + AILST T0 baseline + verification checklist 100%.

---

### Phase D — Pilot Readiness Features

**Στόχος:** Features που πολλαπλασιάζουν την ερευνητική αξία χωρίς νέο περιεχόμενο.

#### D.1 — Trust Calibration Score (TCS)
- Σύνθετο score από RAG/RTM/DTP/Peer ratings
- Aggregation logic στο `rag_query_system.py`
- Dashboard view ανά εκπαιδευτικό
- Νέα ερευνητική μεταβλητή

#### D.2 — Position Confirmation Analytics
- SQL queries για Engagement Depth Score (EDS) με βάση το RTM `position_confirmed` flag
- "Surface engagement" vs "deep engagement" διάκριση
- Βάση για το dissertation section "Beyond completion rates"

**Αρχείο αναφοράς:** `RTM_REDESIGN_PATCH_APR2026.md` (περιγραφή του flag) — *θα διαγραφεί αλλά το περιεχόμενο είναι στο 2.4 του παρόντος*.

#### D.3 — DTP XAI narrative
- Επέκταση του DTP prompt με attribution + counterfactual hint
- "Η πορεία σου δείχνει αυτό το pattern γιατί στα M3/M8 έδειξες..."

**Αρχείο αναφοράς:** `DTP_Documentation_Mar2026.docx` — current DTP spec (γιατί η επέκταση πρέπει να σέβεται το pattern detection principle).

#### D.4 — Dashboard UNESCO Matrix 5×3 + RTM Heatmap
- UI work, ανεξάρτητο από content
- Visual representation της UNESCO matrix
- Δείχνει progress ανά Aspect × Level
- Ενσωματωμένο RTM heatmap (16 subjects × 15 modules)
- Παρουσιάζεται στη διατριβή και σε screenshots

---

### Phase E — Multi-agent Refactor

**Στόχος:** Wrap των υπαρχουσών functions σε agent classes. Μηδέν χαμένη δουλειά.

#### E.1 — Agent abstractions
Κάθε feature γίνεται agent με σαφές contract:
- `RAGFeedbackAgent`
- `RTMAgent`
- `PeerSynthesisAgent`
- `DTPAgent`
- `XAIAgent` (cross-cutting)

#### E.2 — Shared infrastructure
- Common AI provenance metadata
- Unified HITL pipeline
- Centralised cost tracking
- Logging + audit trail

#### E.3 — Παιδαγωγικό όφελος
- Κάθε agent έχει το δικό του XAI panel + AI disclosure
- Νέα features (Multimodal reflection, Epilogue) γράφονται ως νέοι agents χωρίς να αγγίζουν τους υπάρχοντες

#### E.4 — Δικαίωση για τη διατριβή
Ολόκληρο chapter "Multi-agent architecture for Trustworthy AI in Teacher PD" γίνεται εφικτό.

**Αρχεία αναφοράς:**
- `rag_query_system.py` — current monolithic implementation
- `views.py` — current view-level orchestration

---

### Phase F — Multimodal Reflection (voice + image)

**Στόχος:** Επέκταση του TAB5 reflection input πέρα από text.

#### F.1 — Voice input
- Web Speech API integration στο reflection form
- Greek + English support
- Speech-to-text → standard reflection text → ίδιο RAG/RTM/DTP pipeline
- Cognitive load reduction για εκπαιδευτικούς που σκέφτονται καλύτερα προφορικά

#### F.2 — Image input
- Upload classroom artefacts (lesson plans, student work, classroom photos)
- Gemini multimodal για ανάλυση
- Νέα διάσταση reflection: "Show me what you tried, don't just describe it"

#### F.3 — Παιδαγωγικό όφελος
- Inclusive design (διαφορετικά modalities ταιριάζουν σε διαφορετικούς εκπαιδευτικούς)
- Reflection becomes situated in classroom artefacts
- Νέα ερευνητική διάσταση: comparison between voice / text / image reflections

#### F.4 — Δικαίωση για τη διατριβή
Άμεση απάντηση σε critique της literature ότι το AI-mediated PD είναι text-heavy.

**Αρχεία αναφοράς:**
- `tab5_reflection.html` — current text-only form
- `Literature_Review_Synthesis_Note.md` — critique + Mayer multimedia learning principles

---

### Phase G — PROODOS Epilogue

**Στόχος:** Post-completion synthesis feature.

#### G.1 — Stage 0 — Personal Evolution Dashboard
- DTP longitudinal curve visualisation
- RTM tension trajectories
- Quantitative summary

#### G.2 — Stages 1, 2, 3 — Socratic dialogue
- Look Back / Look In / Look Forward
- Gemini chat UI με ≤150 λέξεις per response, max 5 turns ανά phase

#### G.3 — Learning Portrait PDF
- 300-400 λέξεις narrative
- Embed dashboard screenshots
- AI provenance markers στο footer
- Download button

**Αρχεία αναφοράς:**
- `M16_CAPSTONE_REFLECTION_SPEC.md` — αρχικό spec
- `PROODOS_EPILOGUE_PATCH_APR2026.md` — naming + 4-stage architecture update

---

### Phase H — Closing Flow (Post-Programme Measurement & Certification)

**Στόχος:** Καλά σχεδιασμένη ροή τέλους που μεγιστοποιεί τόσο τη research value όσο και την εμπειρία του εκπαιδευτικού.

Η ροή αυτή ακολουθεί μια διεθνώς αναγνωρισμένη παράδοση στην εκπαιδευτική έρευνα: τρι-φασικό post-test (immediate + delayed) που διαχωρίζει την άμεση από τη διατηρούμενη επίδραση.

#### H.1 — Πλήρης ροή τέλους

```
M15 ολοκλήρωση
    ↓
PROODOS Epilogue (Stage 0–3 + Learning Portrait PDF)
    ↓
AILST T2a — Immediate post-test (36 items, υποχρεωτικό για βεβαίωση)
    ↓
[προαιρετικά] Σύντομο satisfaction/UX survey (5–7 items)
    ↓
Βεβαίωση Παρακολούθησης (auto-generated PDF)
    ↓
[4–6 εβδομάδες αργότερα] AILST T2b — Delayed post-test
    + Email reminder
    + Classroom integration questions (5–7 items)
    ↓
[προαιρετικά για όσους απαντούν] Cohort entry για follow-up interviews
```

#### H.2 — Γιατί έτσι (research justification)

**Άμεσο post-test (T2a):**
- 100% response rate → καθαρή σύγκριση T0 → T1 → T2a (immediate gains)
- Μετράει γνώση + αυτο-αποτελεσματικότητα + στάσεις στην κορύφωση της εμπειρίας
- Συνδέεται με τη βεβαίωση → ηθικά καθαρό (μέρος του deal που συμφώνησαν στο consent), αλλά εξασφαλίζει το primary research variable

**Καθυστερημένο post-test (T2b):**
- ~50–60% response rate (αναμενόμενο)
- Μετράει knowledge retention + sustained efficacy + real classroom integration
- Δείχνει τι ενσωματώθηκε στην πράξη, όχι "μνήμη της εκπαίδευσης"
- Απαντάει ευθέως στο gap που η βιβλιογραφία αναγνωρίζει: *"Longitudinal evidence λείπει"* (Erhardt et al., 2025) και *"It cannot evaluate the long-term effects"* (TAB1 chapter limitation)

**Διπλή ανάλυση στη διατριβή:**
- "Άμεση επίδραση" (T0 → T2a) — ασφαλές, υποχρεωτικό research finding
- "Διατηρούμενη επίδραση" (T2a → T2b) — ισχυρότερο, βιβλιογραφικά πιο "ακριβό" finding
- Δύο διαφορετικά research questions με ένα design

#### H.3 — Σχεδιασμός βεβαίωσης παρακολούθησης

- Auto-generated PDF μετά την υποβολή του T2a
- Περιλαμβάνει: όνομα, ημερομηνία ολοκλήρωσης, λίστα 15 modules με τίτλους UNESCO Aspect/Level, διάρκεια συμμετοχής
- Κωδικός επαλήθευσης (verification code) που δένει το PDF με συγκεκριμένο user_id
- Δεν αναφέρει AILST scores — η βεβαίωση πιστοποιεί συμμετοχή, όχι επίδοση
- AI provenance footer (συνέπεια με Phase C.3)

#### H.4 — Σχεδιασμός delayed follow-up

**Email infrastructure (1–2 μέρες δουλειάς):**
- Cron job που 4 εβδομάδες μετά το T2a στέλνει email πρόσκληση
- Reminder στις 6 εβδομάδες αν δεν έχει απαντήσει
- Cutoff στις 8 εβδομάδες (τελευταία ευκαιρία)

**Περιεχόμενο T2b:**
- AILST 36 items (ταυτόσημο με T0/T1/T2a — απαραίτητο για direct comparison)
- 5–7 classroom integration questions: "Έχεις χρησιμοποιήσει AI tools στην τάξη μετά την εκπαίδευση;", "Ποιο module σε επηρέασε περισσότερο στην πράξη;", κλπ
- Optional: ενδιαφέρον για follow-up interview

**Cohort για interviews (qualitative material):**
- Όσοι απαντούν στο T2b και δηλώνουν διαθεσιμότητα → καλούνται σε 30-λεπτη συνέντευξη
- Ημι-δομημένη: focus σε classroom integration patterns, identity shifts, RTM tensions που έλυσαν ή όχι
- Qualitative material για το dissertation discussion chapter

#### H.5 — Τι κερδίζει η διατριβή

| Διάσταση | Πριν την Phase H | Μετά την Phase H |
|---|---|---|
| Measurement | Pre/Post (T0, T1, T2) | Pre/Post + Delayed (T0, T1, T2a, T2b) |
| Research questions | 1 (immediate gains) | 2 (immediate + sustained) |
| Limitations | "Cannot evaluate long-term effects" | Limitation αφαιρείται από τη διατριβή |
| Qualitative corpus | Reflections + RTM comments + dispute comments + Learning Portraits | + classroom integration responses + interview transcripts |
| Νοβελλιστική συμβολή | RTM/DTP/Peer/TCS/AILST | + delayed follow-up design pattern για AI-mediated PD |

#### H.6 — Κόστος και τradeoffs

- **Email infrastructure:** 1–2 μέρες implementation
- **Παράταση χρόνου διατριβής:** 4–6 εβδομάδες πριν τα T2b data είναι έτοιμα
- **Πτώση response rate στο T2b:** αναγνωρίζεται ρητά ως limitation, μετριάζεται με follow-up reminders
- **Interview overhead:** ~30 λεπτά × N εκπαιδευτικοί που δηλώνουν διαθεσιμότητα

**Αρχεία αναφοράς:**
- `Literature_Review_Synthesis_Note.md` Section 5 — AILST measurement plan + longitudinal evidence gap
- `TAB1_DISSERTATION_CHAPTER_FULL_v2.md` Section 7.4 — limitations που αφαιρούνται
- `M16_CAPSTONE_REFLECTION_SPEC.md` — Epilogue ως pre-T2a synthesis moment
- `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 4) — GDPR-compliant data retention για τα T2b data

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
- Onboarding & AILST measurement framework
- Closing Flow & Delayed Post-test Design (Phase H)
- Multimodal Reflection (Phase F)
- Discussion + limitations + future work

#### I.5 — Παράλληλα: δημοσιεύσεις
- "Implementing EU AI Act Limited Risk Compliance in Teacher PD Platforms" (AIED 2027 / EC-TEL)
- "Multi-agent architecture for Reflective Teacher PD"
- "Multimodal Reflection in AI-Mediated Teacher Development"
- "Immediate vs Delayed Post-test Effects in AI-Mediated Teacher PD" (αν τα T2b data δείξουν divergence από T2a)

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

### 4.3 Multi-agent Refactor → Phase E

**Γιατί.** Δεν είναι απλώς code cleanup. Είναι αρχιτεκτονική επιλογή που:
- Δίνει υλικό για ένα ολόκληρο dissertation chapter
- Καθιστά τα νέα features (Multimodal, Epilogue) πιο εύκολα να υλοποιηθούν
- Επιτρέπει cleaner integration με το EU AI Act compliance work
- Ευθυγραμμίζεται με την κατεύθυνση της βιβλιογραφίας (multi-agent systems σε education)

### 4.4 Multimodal Reflection (voice + image) → Phase F

**Γιατί.** Άμεση απάντηση σε critique της literature ότι το AI-mediated PD είναι text-heavy. Δίνει:
- Inclusive design contribution
- Νέα ερευνητική διάσταση (text vs voice vs image reflection patterns)
- Ευθυγράμμιση με Mayer multimedia learning principles

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
