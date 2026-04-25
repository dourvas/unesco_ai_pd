# SUBJECT_INTRO HOOKS — Architecture Patch
## April 2026 — Subject-specific resistance reduction in TAB1

**Status:** Specification (Phase 1 of 5)
**Source:** Zhou, Lavicza & Chiu (2026), Idea 2 — Subject Definition Hooks
**Scope:** All 15 modules × 16 subjects = 240 records
**Code change:** Required — new view + URL + template partial

---

## 1. Background

### Why this exists

Zhou et al. (2026) found that teachers resist AI integration when they perceive it as foreign to their subject. A philologist refuses machine learning because she sees it as computer science. A PE teacher dismisses AI ethics as a desk-job concern. A primary school teacher feels prompt engineering belongs to secondary specialists.

This resistance is silent. It happens before the teacher even reaches the main content. By the time they open TAB2, they have already decided "this isn't for me."

The Subject Definition Hook is a small, discipline-specific card placed in TAB1 (the introduction tab). It does three things in sequence:

1. **Names the resistance** — explicitly acknowledges what the teacher might be thinking
2. **Bridges to their subject** — concrete, classroom-recognisable connection
3. **Promises something specific** — what they will gain that matters to their teaching

The block runs about 80–120 words. It sits below the existing Universal "About this module" card, which justifies the content selection process across all subjects.

### Relationship to existing TAB1 content

| Block | Scope | Personalisation | Purpose |
|---|---|---|---|
| Hero image + title | Module | Universal | Visual anchor |
| Framework badge | Module | Universal | UNESCO Aspect/Level |
| About this module card | All modules | Universal | Validation of content choice |
| **Subject Intro hook** (new) | **All modules** | **Per subject (16)** | **Resistance reduction** |
| Forum trigger card | Module | Universal | Community entry |

The new card sits between "About this module" and the forum trigger.

---

## 2. Database changes

### New content_type

A new content_type `subject_intro` is added to `modules_modulecontent`. The schema does not change. Only new rows.

| Field | Value |
|---|---|
| `content_type` | `subject_intro` |
| `subject_area` | All 16 lowercase values + `'Universal'` for fallback |
| `grade_level` | `'all'` (lowercase) |
| `module_id` | M1–M15 (all modules) |
| `metadata` | `'{}'::jsonb` |
| `content_data` | HTML card content (see Section 5) |

**Records per module:** 17 (16 subjects + 1 Universal fallback)
**Total records:** 15 modules × 17 = **255 records**

### SQL pattern

```sql
INSERT INTO modules_modulecontent (
    module_id, content_type, subject_area, grade_level,
    content_data, metadata, created_at, updated_at
)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">[Resistance acknowledgement.]</p>
    <p class="text-sm mb-2">[Bridge to the subject.]</p>
    <p class="text-sm">[What you will gain.]</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';
```

---

## 3. Backend changes

### New view in `apps/modules/views.py`

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def subject_intro_view(request, code):
    """
    Returns the subject-specific intro hook for TAB1.
    Falls back to Universal if no subject-specific record exists.
    """
    try:
        module = Module.objects.get(code=code)
    except Module.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Module not found'}, status=404)

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        subject = teacher_profile.subject_area
    except TeacherProfile.DoesNotExist:
        subject = None

    intro = None
    if subject:
        intro = ModuleContent.objects.filter(
            module=module,
            content_type='subject_intro',
            subject_area=subject,
            grade_level='all'
        ).first()

    if not intro:
        intro = ModuleContent.objects.filter(
            module=module,
            content_type='subject_intro',
            subject_area='Universal',
            grade_level='all'
        ).first()

    if not intro:
        return JsonResponse({'success': False, 'error': 'No intro found'})

    return JsonResponse({
        'success': True,
        'html': intro.content_data,
        'subject': subject or 'Universal'
    })
```

### New URL in `apps/modules/urls.py`

Add to existing patterns:

```python
path('modules/<str:code>/subject-intro/', views.subject_intro_view, name='subject_intro'),
```

Final URL: `/modules/modules/<code>/subject-intro/`

---

## 4. Frontend changes

### New partial: `templates/modules/partials/subject_intro_card.html`

```html
{% comment %}
  Subject-specific intro card for TAB1.
  Loaded via AJAX based on user's subject_area.
  Pattern follows tab_forum_trigger.html / thread_info.
{% endcomment %}

<div id="subject-intro-card" class="my-6" data-module-code="{{ module.code }}">
  <div class="text-center text-sm text-base-content/50 py-4">
    <span class="loading loading-dots loading-sm"></span>
  </div>
</div>

<script>
(function() {
  const card = document.getElementById('subject-intro-card');
  if (!card) return;

  const moduleCode = card.dataset.moduleCode;
  const url = `/modules/modules/${moduleCode}/subject-intro/`;

  fetch(url, { credentials: 'same-origin' })
    .then(r => r.json())
    .then(data => {
      if (data.success && data.html) {
        card.innerHTML = data.html;
      } else {
        card.style.display = 'none';
      }
    })
    .catch(() => {
      card.style.display = 'none';
    });
})();
</script>
```

### Inclusion in `tab_introduction.html`

Add the partial **directly below** the "About this module" card and **above** the forum trigger:

```html
<!-- existing About this module card -->
{% include "modules/partials/about_this_module.html" %}

<!-- NEW: Subject intro hook -->
{% include "modules/partials/subject_intro_card.html" %}

<!-- existing forum trigger -->
{% include "community/partials/tab_forum_trigger.html" with tab_name="introduction" %}
```

---

## 5. Card design specification

### Visual style

Distinct from TAB2 subject boxes (which are educational content). This card is welcoming and conversational.

- Container: `card bg-base-100 border-l-4 border-info shadow-sm`
- Border colour: `border-info` (cyan-blue) — different from part2 (`border-secondary` purple), part3 (`border-amber-400`), part4 (`border-warning` yellow)
- Header: subject badge + "Why this matters for you" label
- Body: 3 short paragraphs

### HTML template (canonical form)

```html
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">[Subject Display Name]</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">[Para 1: Resistance acknowledgement — name the doubt directly.]</p>
    <p class="text-sm mb-2">[Para 2: Bridge — connect the module topic to the subject in concrete terms.]</p>
    <p class="text-sm">[Para 3: Promise — one specific gain from this module for this subject.]</p>
  </div>
</div>
```

### Subject display names (for badges)

Database `subject_area` value → Display name in badge:

| DB value | Badge label |
|---|---|
| mathematics | Mathematics |
| language_arts | Language Arts |
| science | Science |
| physics | Physics |
| chemistry | Chemistry |
| biology | Biology |
| history | History |
| geography | Geography |
| foreign_languages | Foreign Languages |
| social_studies | Social Studies |
| computer_science | Computer Science |
| physical_education | Physical Education |
| arts | Arts |
| special_education | Special Education |
| early_childhood | Early Childhood |
| other | Primary Generalist |

### Important: the meaning of `other`

The `other` value is **not** a generic "doesn't fit any category" bucket. It represents the **primary school generalist teacher** — someone who teaches all subjects to one age group, typically Years 1–6.

This is established across the platform:
- In `subject_box_part2` and `subject_box_part4` (M1–M15), the `other` records use the **Dimitris primary generalist persona** — multi-subject, single age cohort
- In `subject_box_part3` (M5), the `other` record uses the mathematics fallback (Dimitris teaching fractions)
- The 16 teacher personas defined for subject boxes treat `other` as the primary generalist slot, not a residual

This means the `other` hooks face a **distinct resistance pattern** that no other subject shares: the teacher juggles 5+ subjects × 1 age group, while a secondary specialist juggles 1 subject × 3+ year groups. AI tooling, examples, and prompts in the broader ecosystem are heavily biased toward secondary specialists.

The badge label "Primary Generalist" names this directly. The hooks acknowledge it explicitly. See Phase 3 resistance matrix for the `other` column treatment per module.

---

## 6. Content writing rules

These rules govern all 240+15 hooks (15 modules × 16 subjects + 15 Universal fallbacks).

### Rule 1 — Name the resistance directly
Open with what the teacher might be thinking, in their own internal voice. Examples:
- "You might think research leadership belongs to administrators, not to a maths classroom."
- "Ethics in AI sounds like a topic for philosophers, not for someone teaching PE."

Never generic. Never "this module is important." Always specific to the imagined doubt.

### Rule 2 — Bridge in classroom terms
Use objects, situations, or tasks the teacher already recognises. Examples:
- A philologist's bridge to AI Foundations: morphology, syntax, semantics
- A PE teacher's bridge to ethics: fairness in team selection, data on student fitness
- An early childhood educator's bridge to prompt engineering: how you scaffold a 5-year-old's question
- A primary generalist's bridge to lesson design: switching between 5 subjects in one morning, with the same 25 children

### Rule 3 — Promise something specific
Not generic competence. A concrete gain for that subject. Examples:
- "You'll see why AI struggles with long literary texts and learn how to use it on shorter passages."
- "You'll learn one classroom routine that uses AI to free 20 minutes a week from differentiation prep."

### Rule 4 — Style constraints
- Plain English. Sentences under 25 words.
- No m-dashes. Use commas, semicolons, or new sentences.
- Contractions: "isn't", "doesn't", "won't" instead of "is not", etc.
- Total word count per hook: 80–120 words across the three paragraphs.
- No exclamation marks. Calm, confident tone.
- Never patronising. The teacher is a professional.

### Rule 5 — Universal fallback
Each module has 1 Universal hook (`subject_area='Universal'`). Used only as a safety net if a teacher's `subject_area` value somehow doesn't match any of the 16 known values (data corruption, schema drift, future subjects). Tone: subject-agnostic, addresses "any teacher reading this." It exists for resilience, not for a real audience.

**Important:** Universal is not the same as `other`. The `other` records target primary generalists (a real, named audience with a specific resistance). Universal is the catch-all for cases where neither the 16 subjects nor `other` apply. In normal operation, Universal hooks should rarely render.

---

## 7. RAG ingest

The new `subject_intro` records are **not ingested** into RAG.

Reasoning:
- The hooks are framing content, not pedagogical content
- Including them would bias TAB5 reflections toward the resistance language
- They are not corpus material — they are user interface

Confirmed: the existing RAG ingest scripts filter by content_type and do not include `subject_intro`.

---

## 8. Resistance Matrix (Phase 3 deliverable)

Before writing 240 hooks, a resistance matrix is produced. It is a 15×16 grid where each cell answers three questions:

1. **What might this teacher be thinking when they see this module?** (the resistance)
2. **What classroom reality bridges to this module's topic?** (the bridge)
3. **What concrete gain matters for this subject in this module?** (the promise)

The matrix is the source from which all hooks are written. It lives as `RESISTANCE_MATRIX_APR2026.md`.

Without this matrix, hooks become generic. With it, every hook lands.

---

## 9. Status tracker

| Phase | Deliverable | Status |
|---|---|---|
| Phase 1 | This architecture spec | ✅ Complete |
| Phase 2 | Backend code (views.py, urls.py, partial) | ⬜ Pending |
| Phase 3 | Resistance matrix (15×16 grid) | ⬜ Pending |
| Phase 4 | Content batch 1: M1–M5 (Acquire) | ⬜ Pending |
| Phase 5 | Content batches 2+3: M6–M15 (Deepen + Create) | ⬜ Pending |

---

## 10. Verification plan

After all phases complete:

```sql
-- Confirm 17 records per module
SELECT m.code, COUNT(*) AS subject_intro_count
FROM modules_modulecontent mc
JOIN modules_module m ON mc.module_id = m.id
WHERE mc.content_type = 'subject_intro'
GROUP BY m.code
ORDER BY m.code;
-- Expected: M1=17, M2=17, ..., M15=17
```

Browser test:
1. Login as Mathematics user → open M1 TAB1 → verify Mathematics badge appears
2. Login as Language Arts user → open M3 TAB1 → verify Language Arts badge + different content
3. Login as Other user (primary generalist) → open M15 TAB1 → verify "Primary Generalist" badge + content speaks to multi-subject reality
4. Test fallback: temporarily delete a subject record → verify Universal fallback appears

---

## 11. Academic value

The Subject Definition hooks operationalise Zhou, Lavicza & Chiu (2026) Idea 2 (Subject Definition resistance reduction) at scale. This is the first teacher PD platform to implement discipline-specific resistance handling at the module entry point. It produces a measurable variable for the pilot:

> Comparison of TAB1→TAB2 progression rates before/after deployment, segmented by subject_area.

If progression rates increase post-deployment, this is direct empirical support for the belief-driven model in Zhou et al. (2026).

Citation in dissertation:

> "The Subject Definition Hook layer addresses an empirical finding by Zhou, Lavicza & Chiu (2026): teachers resist AI integration when they perceive it as foreign to their subject. The PROODOS platform implements 240 discipline-specific resistance handlers at the module entry point — one of the first known operationalisations of belief-aware design in teacher PD."

---

*Patch created: April 2026*
*Phase: 1 of 5 (architecture spec)*
*Next: Phase 2 — backend code*
*Read alongside: MODULE_CONTENT_GUIDE.md, MODULE_CONTENT_GUIDE_PATCH_M5_PART3_APR2026.md, FORUM_THREAD_INFO_GUIDE.md*
