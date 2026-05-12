# Handoff prompt — επόμενο παράθυρο για το ολοκληρωμένο κλείσιμο του Phase C

**Όταν ανοίγεις νέο Claude Code παράθυρο, αντιγράφεις το text μέσα στο `>>>` block και το επικολλάς ως πρώτη προτροπή. Το prompt είναι αυτάρκες — βασίζεται μόνο σε αρχεία του repo, όχι σε προηγούμενο context.**

---

>>>

Συνεχίζουμε το Phase C work. Διάβασε ΠΡΩΤΑ, με αυτή τη σειρά, και χωρίς να γράψεις κώδικα ακόμα:

1. `PROODOS_UNIFIED_ROADMAP.md` — sections **2.8**, **3.C.3**, **3.C.5**, **3.C.6**, **3.C.7**, **3.C.x**. Αυτά δίνουν την πλήρη Phase C status και τι έμεινε.
2. `proodos_files/TECH_DEBT_LOG.md` — entries **TD-017** (αν υπάρχει· αν όχι, το πρώτο σου deliverable σε αυτή τη συνεδρία είναι να το δημιουργήσεις) και τα ήδη resolved **TD-008 / TD-012 / TD-013** για να καταλάβεις το pattern.
3. `proodos_files/SESSION_LOG_PHASE_C_C4_C1_CP11_20260512.md` — το πιο πρόσφατο session log· δίνει context για τη ροή των τελευταίων commits.
4. `apps/compliance/templates/compliance/privacy_dashboard.html` γραμμές 200-260 — οι 4 spots όπου ήδη υπάρχει `data-ai-generated="true"` ως partial forward-compat marker.
5. `apps/compliance/copy.py::AI_DISCLOSURE_TEXT_V1_PRE_IRB` — το ισχύον AI Disclosure text αναφέρει Article 50(2) machine-readable marking· είναι η εξωτερική αιτιολόγηση για το C.3.

Όταν τελειώσεις το reading, γράψε στο chat μια σύντομη επιβεβαίωση 5-10 γραμμών με: τι έγινε ως τώρα στο Phase C, ποια κομμάτια έμειναν, και ποιο είναι το επόμενο που πιάνεις.

---

## Επόμενα — με σαφή σειρά προτεραιότητας

### Α. Έλεγχος εξωτερικών εξαρτήσεων (πρώτο πράγμα)

Ρώτησε τον John αν έχει φτάσει IHU IRB feedback (CP 7 + CP 10) ή κάποιο άλλο piece έχει προτεραιότητα. Αν ναι, ακολούθησε το post-IRB checklist στο **roadmap §3.C.5** πρώτα — προηγείται του C.3 γιατί επηρεάζει copy text που μπαίνει στις V2 constants.

Αν όχι, προχώρα στο Β.

### Β. C.3 — Machine-readable AI content markers (TD-017)

Το main piece. Spec αναφορά: `EU_AI_ACT_COMPLIANCE_PLAN_APR2026.md` Section 5 (Συμπλήρωμα 3) + `PROODOS_UNIFIED_ROADMAP.md` §3.C.3.

**Β.1 Design proposal πρώτα.** Δημιούργησε `proodos_files/C3_DESIGN_PROPOSAL_AI_PROVENANCE.md` που:

- Απαντά τα 5 open design questions από §3.C.3:
  1. Provenance storage location (νέο `AIArtefactProvenance` model με FKs / denormalised fields / hybrid)
  2. Template tag signature (`{% ai_provenance for=artefact %}` vs explicit args)
  3. JSON-LD schema (schema.org/CreativeWork / SoftwareApplication / custom / none)
  4. Coverage scope για το pilot (όλα τα AI rendering sites ή μόνο τα 4 main)
  5. Retroactive backfill (καμία / management command / lazy on next view)
- Επιπρόσθετα D-style decisions για:
  - HTML attribute names + value format (consistent με EU AI Act recommendation αν υπάρχει)
  - Template tag location (νέο `apps/compliance/templatetags/ai_provenance.py` ή reuse `consent_format.py`)
  - Test plan (~10-15 tests target)
- Παρουσιάζει 🛑 markers σε αποφάσεις που χρειάζονται John's input
- Sketches files-to-create / files-to-modify list με LOC estimates

Στείλε το proposal στο chat για approval ΠΡΙΝ ξεκινήσεις implementation. Ο John θα κάνει CP-style refinements όπως στο C.4.

**Β.2 Implementation σε 2 commits μετά την approval:**

- Commit 1: provenance metadata storage + HTML data-attrs εφαρμοσμένα σε όλα τα AI rendering sites (tab5_reflection.html RAG/RTM/DTP/peer + privacy_dashboard.html existing markers expanded + ίσως module content templates).
- Commit 2: JSON-LD page-level metadata + `{% ai_provenance %}` template tag + 10-15 tests + TD-017 status update σε RESOLVED + roadmap update να κουνήσει C.3 από §3.C.7 carry-over σε §3.C.3 status DONE + plan changelog entry.

Test target ~15 tests. Use `--noinput` στο test runner. Full Phase C suite μετά (στόχος 195+/-).

### Γ. Career Stage RAG personalisation (gap C.2 Step 2)

Roadmap αναφορά: **§3.C.2 Step 2 + §3.C.x table**. Μικρό piece (~50-80 LOC).

- Add `career_stage` parameter to RAG query function στο `rag_query_system.py`. Map από `teacher_profile.teaching_years` σε `early_career` ('0-5') / `mid_career` ('6-15') / `experienced` ('16-25') / `veteran' ('25+').
- Differentiate RAG feedback emphasis per career stage (νέοι: critical trust + ethics framing· έμπειροι: workload relief + identity reframing framing). Αυτό είναι prompt-template work, όχι new architecture.
- Add tests verifying the parameter reaches the prompt context correctly.
- New TD entry για το full feedback-emphasis differentiation (αν δεν υλοποιηθεί όλο τώρα, καθόρισε σαφή scope cut).
- 1 commit, follow the existing C.x naming convention.

### Δ. Cleanup + close-out

- Update `PROODOS_UNIFIED_ROADMAP.md`:
  - Move C.3 από §3.C.7 carry-over σε §3.C.3 με status DONE badge.
  - Update §2.8 με τα νέα commits.
  - Mark Career Stage gap σαν RESOLVED σε §3.C.2 Step 2.
- Update `TECH_DEBT_LOG.md`: TD-017 RESOLVED.
- Update `PHASE_C_MIGRATION_PLAN_v1_20260509.md` changelog.
- Νέο session log: `proodos_files/SESSION_LOG_PHASE_C_C3_<date>.md` που καλύπτει αυτή τη συνεδρία.

---

## Σταθερές της δουλειάς (μην τις παραβιάσεις)

- **Absolute paths** στο main repo για file edits — `C:/Users/dourv/unesco_ai_pd/...`. Το shell cwd flips ανάμεσα στο worktree και το main όταν τρέχεις cross-directory commands.
- **Factual tone** στο code και στα commit messages — όχι "successfully implemented" / "great", όχι emojis εκτός αν αλλάζεις template content που ήδη τα έχει.
- **Greek στο chat με John, English στα artefacts** (commits, docs, code comments, tests).
- **Design proposal first** για κάθε piece >100 LOC. Implementation ξεκινά αφού John εγκρίνει D-decisions.
- **One commit per logical concern**, με descriptive commit message που εξηγεί το "γιατί" όχι το "τι".
- **Run the full Phase C test suite** μετά από κάθε commit· κανένα piece δεν κλείνει αν τα tests είναι κόκκινα.
- **dry-run + pg_dump backup** πριν από οποιαδήποτε DB migration, ακόμα και additive.
- **Worktree workflow**: δουλεύεις στο worktree, commit στο `claude/<name>` branch, fast-forward merge στο `main` μετά από κάθε commit.

---

## Files που θα αγγίξει το C.3 (preview για design proposal)

| File | Action |
|---|---|
| `apps/compliance/templatetags/ai_provenance.py` (NEW) | Template tag implementation |
| `apps/compliance/models.py` | Νέο `AIArtefactProvenance` model (αν Design D1 επιλέξει separate model) |
| `apps/compliance/migrations/0005_*.py` (NEW) | Migration για το νέο model (αν εφαρμόζεται) |
| `apps/compliance/tests.py` | +10-15 tests για data-attrs + JSON-LD + template tag |
| `templates/modules/tabs/tab5_reflection.html` | Add data-attrs σε RAG/RTM/DTP/peer cards |
| `templates/compliance/privacy_dashboard.html` | Expand existing 4 markers με model + timestamp |
| `templates/onboarding/ai_disclosure.html` | Add page-level JSON-LD αν Design D3 επιλέξει inclusion |
| `templates/base.html` ή `base_authenticated.html` | Page-level meta tags αν εφαρμόζεται |
| `proodos_files/C3_DESIGN_PROPOSAL_AI_PROVENANCE.md` (NEW) | Design doc |
| `proodos_files/TECH_DEBT_LOG.md` | TD-017 entry + status updates |
| `proodos_files/PHASE_C_MIGRATION_PLAN_v1_20260509.md` | Changelog entry |
| `PROODOS_UNIFIED_ROADMAP.md` | Status moves |
| `proodos_files/SESSION_LOG_PHASE_C_C3_*.md` (NEW) | Session log |

Estimate: ~350-500 LOC συνολικά για το C.3 (κώδικας + tests + docs).

---

## Αν φύγουμε εκτός χρόνου

Αν το context window του παραθύρου τελειώνει πριν ολοκληρωθούν Α + Β + Γ, **το ελάχιστο αποδεκτό deliverable είναι**:

- Α (έλεγχος IRB) ολοκληρωμένος
- Β.1 (C.3 design proposal) committed στο main
- Σαφές handoff comment στο chat για το επόμενο παράθυρο

Όχι half-finished implementation. Καλύτερα να σταματήσει στο design και να συνεχίσει σε καθαρό context.

>>>

---

*Συντάχθηκε: 2026-05-12, τέλος του Phase C arc που έκλεισε C.4 + C.1 + C.6 + CP-11. Το αρχείο είναι ζωντανό μέχρι το πρώτο μήνυμα του επόμενου παραθύρου που θα ξεκινήσει το C.3.*
