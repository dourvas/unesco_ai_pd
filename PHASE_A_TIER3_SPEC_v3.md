# PHASE_A_TIER3_SPEC_v3.md
## Phase A Tier 3 — Practice Workshop + M8 Patches + Polish

**Status:** v3 — Gemini external review applied — ready for Claude Code execution
**Date:** May 3, 2026
**Predecessors:**
- PHASE_A_TIER3_SPEC.md (v1, archived — forum-based approach abandoned)
- PHASE_A_TIER3_SPEC_v2.md (v2, archived — pre-Gemini review)
**Audit baseline:** TIER3_M6_M8_AUDIT_REPORT.md
**Coverage:** 138/170 (~81.2%) → projected ~83.5% post-Tier-3

---

## Why v3 (vs v2)

v2 introduced the blog approach. v3 incorporates Gemini external review (May 3, 2026) with 4 adopted suggestions:

1. **User-facing label changed** — "Peer Dialogue" → "Practice Workshop" (keeps technical app name `peer_blog`, but UI emphasises reflective workshop mindset over polished gallery)
2. **"Why are these subjects adjacent?" rationales** — `ADJACENT_SUBJECTS` mapping now includes rationale strings; small modal explains adjacency to scaffold cross-specialty synthesis
3. **Defence rationale paragraph** — explicit architecture decision history captured for dissertation viva
4. **Flat comments only** — `BlogComment.parent_comment` FK removed; pilot scale (110 teachers, ~5 comments avg per post) doesn't need nested replies; saves ~1h development effort, simplifies code, cleaner research data

Effort revised: **~9h → ~8h** due to flat comments simplification.

---

## Why v2 (vs v1)

The v1 spec proposed using the existing community forum as the peer dialogue channel. After review (May 3 conversation):

**Problems with forum approach:**
- Threads "wake up" with each reply, creating noise/drama amplification
- Continuous moderation burden on researcher (50-150 threads in pilot would require weekly review)
- Flat thread architecture doesn't suit discrete artefact peer dialogue
- Author has no agency over their own thread once it goes live

**Blog approach solves all four:**
- Posts are anchored chronologically; comments are secondary
- Sub-specialty filtering at the user's discretion (not researcher curation)
- Author owns their post
- Thumbs-up = single-action endorsement (no Reddit-style voting wars)

**v2 architecture:** A new `apps.peer_blog` Django app providing module-scoped blog feeds with discrete posts, comments, and thumbs-up reactions. Forum app is untouched.

---

## Document scope

This document specifies all Tier 3 components in execution order:

| # | Component | Pattern | Effort | Indicator impact |
|---|-----------|---------|--------|------------------|
| 1 | Audit table corrections | Audit fix only | 5 min | +2 STRONG (CG1.2.4, LO3.2.2) — flagged in logs |
| 2 | Practice Workshop app (generic) | New Django app | ~4h | CA3.3.3 community-coordination defendable |
| 3 | M13 simplification + wiring | Disable status workflow + auto-post | ~30 min | M13 native peer dialogue |
| 4 | M9 wiring | Opt-in challenge → blog post | ~30 min | Cross-aspect contribution |
| 5 | M14 wiring (Gamified UP only) | Opt-in challenge → blog post | ~20 min | Cross-aspect contribution |
| 6 | M8 ethics-by-design subsection | Type A patch | ~30 min | CG3.2.4 PARTIAL → STRONG |
| 7 | M8 cross-ref to M3 | Type A patch | ~30 min | CG3.2.1 PARTIAL → STRONG |
| 8 | Reactive moderation policy doc | New doc | ~15 min | Defendability |
| 9 | CONTRIBUTING.md alignment | Doc update | ~30 min | Honesty, no indicator |
| 10 | PDF reconsideration | Decision doc | ~30 min | Operational |
| 11 | Logs + audit projection | Logs | ~30 min | — |
| **TOTAL** | | | **~8h** | **+4 STRONG** (audit +2, M8 +2) |

**Stop-and-report protocol:** Same as Tier 1+2. Stops after each major component (peer blog app, M13 simplification, each module wiring, M8 patches).

---

## Decisions consolidated (final)

| ID | Topic | Decision |
|----|-------|----------|
| D1 | Tier 3 scope option | β refined — peer blog + M8 patches + audit fixes + polish |
| D2 | M8 patch granularity | Both CG3.2.1 + CG3.2.4 |
| D3 | Audit corrections timing | In Tier 3 closure logs (with **explicit reminder** flag) |
| D4 | Wiring scope | M13 + M9 + M14 (Gamified UP only) |
| D5 | Status workflow philosophy | Unified — all opt-in formative peer dialogue, no admin curation |
| D6 | Tab3RepositorySubmission fields | Option B — keep schema, disable in UI |
| D7 | Reactive moderation | Yes — keep as safety net |
| D8 | **Discussion architecture** | **Blog (NOT forum)** — discrete posts, comments, thumbs-up |
| D9 | **Subject filtering** | **3-mode toggle** (My subject / Adjacent / All) — default Adjacent |
| D10 | **Filter persistence** | **User profile field** (cross-session) |
| D11 | **Adjacent mapping** | Hand-curated (see Section 2.3) |
| D12 | **User-facing label (Gemini)** | **"Practice Workshop"** in UI; technical app name `peer_blog` |
| D13 | **Adjacency rationales (Gemini)** | Each adjacency includes pedagogical rationale; "Why these?" modal |
| D14 | **Comment threading (Gemini)** | **Flat only** — no nested replies; pilot scale doesn't need it |
| D15 | **Defence rationale (Gemini)** | Architecture decision history captured in Tier 3 logs |

---

# Section 1 — Audit Table Corrections

**Status:** No platform changes required. Master audit table updates only.

## CG1.2.4 — Special needs in M6

**Current label:** PARTIAL
**Correct label:** STRONG (DISTRIBUTED: M6 + M9 + M5/M10/M15 Tier 2)
**Justification:** Special needs cumulative coverage post-Tier-2 disabilities patches. M6 covers Black Box Problem + explainability natively. M9 adds UDL + SEN scenario. M5/M10/M15 Tier 2 patches add teachers-with-disabilities subsections. Cumulative coverage is now strong.

## LO3.2.2 — Visually represent AI systems

**Current label:** PARTIAL
**Correct label:** STRONG (DISTRIBUTED: M3 + M8)
**Justification:** M3 Part 1A "How LLMs Generate Text" 4-step diagram + M3 Part 1B Teacher's Conceptual Map (4-stage AI lifecycle) cover LLM internals visualisation. M8 adds Studio-specific visualisations on top. The PARTIAL flag was set before Day 3 patches.

## ⚠️ EXPLICIT REMINDER FOR CLAUDE CODE

**These corrections MUST appear in the Tier 3 closure logs.** Do not skip them. They contribute +2 STRONG indicators to the post-Tier-3 coverage projection. Place them in `CONTENT_GAPS_LOG_TIER3_UPDATE.md` Section 1 with high visibility.

---

# Section 2 — Practice Workshop Infrastructure (NEW APP)

**Goal:** Build a new Django app `apps.peer_blog` (technical name) presented as **"Practice Workshop"** in the UI, providing module-scoped feeds for discrete artefact peer dialogue.

**Critical:** The existing `apps.community` (forum) is **NOT modified**. Two separate discussion patterns coexist: forum for casual / cross-module discussion, Practice Workshop for artefact-anchored peer dialogue.

**Naming convention (Gemini D12):**
- Technical: `apps.peer_blog`, `BlogPost`, `BlogComment`, `BlogThumbsUp` (kept for clean schema)
- User-facing: "Practice Workshop", "Workshop posts", "Workshop comments"
- Rationale: encourages reflective practice mindset (Schön) over polished gallery mindset

## 2.1 — Schema

```python
# apps/peer_blog/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.modules.models import Module


class BlogPost(models.Model):
    """A single peer-dialogue post anchored to a specific user artefact."""

    # Author + module
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    # Linked artefact (generic FK pattern, not polymorphic)
    artefact_type = models.CharField(
        max_length=50,
        help_text="Artefact type identifier: 'm13_workflow', 'm9_lesson', 'm14_gamified_unit'."
    )
    artefact_id = models.IntegerField(
        help_text="ID of the artefact in its source table (Tab3RepositorySubmission, Tab3UserActivity, etc.)."
    )

    # Content
    title = models.CharField(max_length=200)
    body = models.TextField(help_text="The artefact summary or description shown to peers.")

    # Author context (snapshot at post time, immutable)
    author_pseudonym = models.CharField(max_length=50)
    subject_area = models.CharField(max_length=50, db_index=True)
    grade_level = models.CharField(max_length=20)

    # Engagement (denormalised counters)
    thumbs_up_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    # Reactive moderation
    is_hidden = models.BooleanField(
        default=False,
        help_text="Researcher reactive moderation flag. Hidden posts don't appear in feeds."
    )
    hidden_reason = models.CharField(
        max_length=100, blank=True, null=True,
        choices=[
            ('safety_violation', 'Platform safety violation'),
            ('off_topic_spam', 'Off-topic / spam'),
            ('contains_pii', 'Contains real student PII'),
            ('copyright_violation', 'Copyright violation'),
        ],
        help_text="If hidden, the policy category triggering the action."
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['module', 'subject_area', '-created_at'],
                         name='blog_module_subject_idx'),
            models.Index(fields=['module', '-thumbs_up_count'],
                         name='blog_module_thumbs_idx'),
            models.Index(fields=['artefact_type', 'artefact_id'],
                         name='blog_artefact_idx'),
        ]

    def __str__(self):
        return f"{self.title} — {self.author_pseudonym} ({self.subject_area})"


class BlogComment(models.Model):
    """A flat comment on a BlogPost. No nesting (D14 — pilot scale doesn't need it)."""

    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    body = models.TextField()
    author_pseudonym = models.CharField(max_length=50)
    subject_area = models.CharField(max_length=50)

    thumbs_up_count = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]


class BlogThumbsUp(models.Model):
    """Single-action thumbs-up. One per user per post or comment."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(BlogComment, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_user_post_thumbs_up'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_user_comment_thumbs_up'
            ),
            models.CheckConstraint(
                check=(
                    models.Q(post__isnull=False, comment__isnull=True) |
                    models.Q(post__isnull=True, comment__isnull=False)
                ),
                name='thumbs_up_post_xor_comment'
            ),
        ]
```

**Migration:** `peer_blog/migrations/0001_initial.py` (auto-generated). Tested in dry-run before apply.

## 2.2 — Subject filter preference field

Add to existing `apps.users.models.TeacherProfile` (or wherever user profile lives):

```python
class TeacherProfile(models.Model):
    # ... existing fields ...

    # Tier 3 addition
    blog_subject_filter_preference = models.CharField(
        max_length=20,
        choices=[
            ('my_subject', 'My subject only'),
            ('adjacent', 'Adjacent subjects'),
            ('all', 'All subjects'),
        ],
        default='adjacent',
        help_text="User's preferred blog subject filter mode (persisted across sessions)."
    )
```

**Migration:** `users/migrations/00XX_add_blog_filter_preference.py` (auto-generated).

**Pre-flight task:** Confirm exact path for TeacherProfile model in current codebase. If model is named differently, adjust accordingly.

## 2.3 — Adjacent subjects mapping (with rationales — Gemini D13)

New file `apps/peer_blog/subject_mappings.py`:

```python
"""
Hand-curated adjacent-subjects mapping for blog feed filtering.
Tier 3 — May 2026, v3 (with rationales per Gemini review).

Each subject maps to:
  'subjects': list of subject_areas to include in 'adjacent' mode
  'rationales': dict mapping each adjacent subject to a pedagogical rationale
                (used by 'Why these?' modal in UI)

Mapping is intuitive (no formal taxonomy); revisit based on pilot data.
"""

ADJACENT_SUBJECTS = {
    'mathematics': {
        'subjects': ['mathematics', 'science', 'physics', 'computer_science'],
        'rationales': {
            'science': 'Both rely on AI for hypothesis exploration and data modelling',
            'physics': 'Shared mathematical reasoning and problem-solving patterns',
            'computer_science': 'Algorithmic thinking common to both domains',
        }
    },
    'language_arts': {
        'subjects': ['language_arts', 'foreign_languages', 'social_studies'],
        'rationales': {
            'foreign_languages': 'Both work with text generation, comprehension, and language structure',
            'social_studies': 'Critical reading and source evaluation transfer between domains',
        }
    },
    'science': {
        'subjects': ['science', 'mathematics', 'physics', 'biology', 'chemistry'],
        'rationales': {
            'mathematics': 'Both rely on AI for hypothesis exploration and data modelling',
            'physics': 'Both apply scientific method with AI-assisted experimentation',
            'biology': 'Both use AI for pattern recognition in natural systems',
            'chemistry': 'Both work with AI tools for molecular and process visualisation',
        }
    },
    'physics': {
        'subjects': ['physics', 'mathematics', 'science', 'chemistry'],
        'rationales': {
            'mathematics': 'Shared mathematical reasoning and problem-solving patterns',
            'science': 'Both apply scientific method with AI-assisted experimentation',
            'chemistry': 'Both involve AI-assisted modelling of physical phenomena',
        }
    },
    'chemistry': {
        'subjects': ['chemistry', 'science', 'physics', 'biology'],
        'rationales': {
            'science': 'Both work with AI tools for molecular and process visualisation',
            'physics': 'Both involve AI-assisted modelling of physical phenomena',
            'biology': 'Both apply AI to molecular and biochemical analysis',
        }
    },
    'biology': {
        'subjects': ['biology', 'science', 'chemistry', 'physical_education'],
        'rationales': {
            'science': 'Both use AI for pattern recognition in natural systems',
            'chemistry': 'Both apply AI to molecular and biochemical analysis',
            'physical_education': 'Both connect biology to human movement and health',
        }
    },
    'social_studies': {
        'subjects': ['social_studies', 'language_arts', 'history', 'geography'],
        'rationales': {
            'language_arts': 'Critical reading and source evaluation transfer between domains',
            'history': 'Both engage AI in source analysis and narrative construction',
            'geography': 'Both apply AI to spatial and contextual reasoning',
        }
    },
    'history': {
        'subjects': ['history', 'social_studies', 'geography', 'language_arts'],
        'rationales': {
            'social_studies': 'Both engage AI in source analysis and narrative construction',
            'geography': 'Both connect events to places and contexts',
            'language_arts': 'Both work with primary text analysis and interpretation',
        }
    },
    'geography': {
        'subjects': ['geography', 'social_studies', 'history', 'science'],
        'rationales': {
            'social_studies': 'Both apply AI to spatial and contextual reasoning',
            'history': 'Both connect events to places and contexts',
            'science': 'Both use AI for environmental and earth-system analysis',
        }
    },
    'foreign_languages': {
        'subjects': ['foreign_languages', 'language_arts'],
        'rationales': {
            'language_arts': 'Both work with text generation, comprehension, and language structure',
        }
    },
    'arts': {
        'subjects': ['arts', 'language_arts', 'early_childhood'],
        'rationales': {
            'language_arts': 'Both engage AI in creative expression and narrative',
            'early_childhood': 'Both prioritise developmental and creative pedagogy',
        }
    },
    'physical_education': {
        'subjects': ['physical_education', 'biology', 'early_childhood'],
        'rationales': {
            'biology': 'Both connect biology to human movement and health',
            'early_childhood': 'Both apply movement-based pedagogy with developmental focus',
        }
    },
    'early_childhood': {
        'subjects': ['early_childhood', 'arts', 'language_arts',
                     'physical_education', 'special_education'],
        'rationales': {
            'arts': 'Both prioritise developmental and creative pedagogy',
            'language_arts': 'Both build foundational literacy with AI scaffolds',
            'physical_education': 'Both apply movement-based pedagogy with developmental focus',
            'special_education': 'Both centre individualised learner needs',
        }
    },
    'special_education': {
        'subjects': ['special_education', 'early_childhood', 'language_arts'],
        'rationales': {
            'early_childhood': 'Both centre individualised learner needs',
            'language_arts': 'Both adapt AI to communication and literacy support',
        }
    },
    'computer_science': {
        'subjects': ['computer_science', 'mathematics'],
        'rationales': {
            'mathematics': 'Algorithmic thinking common to both domains',
        }
    },
    'other': {
        'subjects': ['other'],  # Conservative — fallback to same only
        'rationales': {}
    },
}


def get_filtered_subjects(user_subject, mode):
    """
    Return list of subject_areas to include in blog feed based on user's mode.

    Args:
        user_subject: User's primary subject_area (str)
        mode: 'my_subject', 'adjacent', or 'all'

    Returns:
        list of subject_area strings, or None for 'all' (no filter)
    """
    if mode == 'all':
        return None  # No filter
    if mode == 'my_subject':
        return [user_subject]
    if mode == 'adjacent':
        config = ADJACENT_SUBJECTS.get(user_subject, {})
        return config.get('subjects', [user_subject])
    return [user_subject]  # Fallback: same as my_subject


def get_adjacency_rationales(user_subject):
    """
    Return rationales dict for the user's subject in adjacent mode.
    Used by the 'Why these?' modal in the blog UI.

    Returns: dict mapping subject_area → rationale string, or empty dict.
    """
    config = ADJACENT_SUBJECTS.get(user_subject, {})
    return config.get('rationales', {})
```

## 2.4 — Helper functions (`apps/peer_blog/services.py`)

Single source of truth for blog operations:

```python
"""
Peer blog service layer for cross-module integration.
Tier 3 infrastructure — May 2026.
"""
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import BlogPost, BlogComment, BlogThumbsUp
from apps.modules.models import Module

User = get_user_model()


ARTEFACT_TYPES = {
    'm13_workflow': {
        'module_code': 'M13',
        'title_template': 'Workflow: {title}',
    },
    'm9_lesson': {
        'module_code': 'M9',
        'title_template': 'Lesson: {title}',
    },
    'm14_gamified_unit': {
        'module_code': 'M14',
        'title_template': 'Gamified Unit: {title}',
    },
}


def create_blog_post(artefact_type, artefact_id, title, body, author_user):
    """
    Create a new BlogPost for an opt-in user artefact.

    Args:
        artefact_type: One of ARTEFACT_TYPES keys
        artefact_id: ID of source artefact (Tab3RepositorySubmission, Tab3UserActivity, etc.)
        title: Short title of the artefact
        body: Full body / summary text
        author_user: Django User instance (must have .profile)

    Returns: BlogPost instance
    """
    config = ARTEFACT_TYPES[artefact_type]
    module = Module.objects.get(code=config['module_code'])
    profile = author_user.profile  # adjust if profile relation differs

    post = BlogPost.objects.create(
        user=author_user,
        module=module,
        artefact_type=artefact_type,
        artefact_id=artefact_id,
        title=config['title_template'].format(title=title),
        body=body,
        author_pseudonym=profile.pseudonym,
        subject_area=profile.subject_area,
        grade_level=profile.grade_level,
    )
    return post


def add_comment(post, author_user, body):
    """Create a flat BlogComment (D14 — no nesting). Increments post.comments_count."""
    profile = author_user.profile
    with transaction.atomic():
        comment = BlogComment.objects.create(
            post=post,
            user=author_user,
            body=body,
            author_pseudonym=profile.pseudonym,
            subject_area=profile.subject_area,
        )
        BlogPost.objects.filter(pk=post.pk).update(
            comments_count=models.F('comments_count') + 1
        )
    return comment


def toggle_thumbs_up(user, post=None, comment=None):
    """
    Idempotent toggle. If user already thumbs-up'd, removes it. Otherwise adds.
    Updates denormalised counter.

    Returns: (is_now_thumbed, new_count) tuple
    """
    from django.db.models import F

    if post:
        existing = BlogThumbsUp.objects.filter(user=user, post=post).first()
        target = post
    elif comment:
        existing = BlogThumbsUp.objects.filter(user=user, comment=comment).first()
        target = comment
    else:
        raise ValueError("Must provide either post or comment")

    with transaction.atomic():
        if existing:
            existing.delete()
            type(target).objects.filter(pk=target.pk).update(
                thumbs_up_count=F('thumbs_up_count') - 1
            )
            target.refresh_from_db()
            return False, target.thumbs_up_count
        else:
            BlogThumbsUp.objects.create(
                user=user,
                post=post if post else None,
                comment=comment if comment else None,
            )
            type(target).objects.filter(pk=target.pk).update(
                thumbs_up_count=F('thumbs_up_count') + 1
            )
            target.refresh_from_db()
            return True, target.thumbs_up_count
```

## 2.5 — Views

```python
# apps/peer_blog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import BlogPost, BlogComment
from .services import add_comment, toggle_thumbs_up
from .subject_mappings import get_filtered_subjects
from apps.modules.models import Module


@login_required
def blog_index(request, module_code):
    """Render module blog feed with subject filter applied."""
    module = get_object_or_404(Module, code=module_code)
    profile = request.user.profile
    mode = profile.blog_subject_filter_preference

    # Apply subject filter
    subject_filter = get_filtered_subjects(profile.subject_area, mode)
    queryset = BlogPost.objects.filter(module=module, is_hidden=False)
    if subject_filter is not None:
        queryset = queryset.filter(subject_area__in=subject_filter)

    # Sort
    sort = request.GET.get('sort', 'recent')
    if sort == 'thumbs_up':
        queryset = queryset.order_by('-thumbs_up_count', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')

    posts = queryset[:50]  # Top 50 only; pagination if needed later

    # Adjacency rationales for "Why these?" modal (only relevant in 'adjacent' mode)
    from .subject_mappings import get_adjacency_rationales
    rationales = {}
    if mode == 'adjacent':
        rationales = get_adjacency_rationales(profile.subject_area)

    return render(request, 'peer_blog/index.html', {
        'module': module,
        'posts': posts,
        'mode': mode,
        'sort': sort,
        'rationales': rationales,
        'user_subject': profile.subject_area,
    })


@login_required
@require_POST
def update_filter_mode(request):
    """AJAX endpoint to update user's filter preference."""
    new_mode = request.POST.get('mode')
    if new_mode not in ('my_subject', 'adjacent', 'all'):
        return JsonResponse({'error': 'Invalid mode'}, status=400)
    profile = request.user.profile
    profile.blog_subject_filter_preference = new_mode
    profile.save(update_fields=['blog_subject_filter_preference'])
    return JsonResponse({'mode': new_mode})


@login_required
def blog_post_detail(request, post_id):
    """Render single post with flat comments list (D14)."""
    post = get_object_or_404(BlogPost, pk=post_id, is_hidden=False)
    comments = post.comments.filter(is_hidden=False).order_by('created_at')

    # Check if current user thumbs-up'd this post
    user_thumbed = False
    if request.user.is_authenticated:
        user_thumbed = post.blogthumbsup_set.filter(user=request.user).exists()

    return render(request, 'peer_blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'user_thumbed': user_thumbed,
    })


@login_required
@require_POST
def submit_comment(request, post_id):
    """AJAX endpoint to submit a flat comment (no nesting per D14)."""
    post = get_object_or_404(BlogPost, pk=post_id, is_hidden=False)
    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    comment = add_comment(post, request.user, body)
    return JsonResponse({
        'id': comment.id,
        'body': comment.body,
        'author': comment.author_pseudonym,
        'subject_area': comment.subject_area,
        'created_at': comment.created_at.isoformat(),
    })


@login_required
@require_POST
def toggle_post_thumbs_up(request, post_id):
    """AJAX endpoint for thumbs-up toggle on post."""
    post = get_object_or_404(BlogPost, pk=post_id, is_hidden=False)
    is_thumbed, count = toggle_thumbs_up(request.user, post=post)
    return JsonResponse({'is_thumbed': is_thumbed, 'count': count})


@login_required
@require_POST
def toggle_comment_thumbs_up(request, comment_id):
    """AJAX endpoint for thumbs-up toggle on comment."""
    comment = get_object_or_404(BlogComment, pk=comment_id, is_hidden=False)
    is_thumbed, count = toggle_thumbs_up(request.user, comment=comment)
    return JsonResponse({'is_thumbed': is_thumbed, 'count': count})
```

## 2.6 — URLs

```python
# apps/peer_blog/urls.py

from django.urls import path
from . import views

app_name = 'peer_blog'

urlpatterns = [
    path('module/<str:module_code>/', views.blog_index, name='index'),
    path('post/<int:post_id>/', views.blog_post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.submit_comment, name='submit_comment'),
    path('post/<int:post_id>/thumbs-up/', views.toggle_post_thumbs_up, name='post_thumbs_up'),
    path('comment/<int:comment_id>/thumbs-up/', views.toggle_comment_thumbs_up, name='comment_thumbs_up'),
    path('settings/filter-mode/', views.update_filter_mode, name='update_filter_mode'),
]
```

Mount in main `urls.py`: `path('blog/', include('apps.peer_blog.urls', namespace='peer_blog'))`.

## 2.7 — Templates (Tailwind + DaisyUI)

### `templates/peer_blog/index.html`

Module workshop feed with Practice Workshop framing, filter toggle, sort options, "Why these?" modal.

```html
{% extends 'base.html' %}
{% block content %}
<div class="container mx-auto px-4 py-6">
  <h1 class="text-3xl font-bold mb-2">{{ module.code }} — Practice Workshop</h1>
  <p class="text-base-content/70 mb-6">
    A space to share work-in-progress and reflect with peers. Post your workflow,
    lesson, or unit; comment on what colleagues are exploring; mark what you find useful.
  </p>

  <!-- Filter mode toggle -->
  <div class="mb-4 flex flex-col sm:flex-row gap-2 sm:items-center">
    <span class="text-sm font-semibold">Show posts from:</span>
    <div class="join" role="tablist" aria-label="Subject filter mode">
      <button class="btn btn-sm join-item {% if mode == 'my_subject' %}btn-primary{% endif %}"
              data-mode="my_subject">My subject</button>
      <button class="btn btn-sm join-item {% if mode == 'adjacent' %}btn-primary{% endif %}"
              data-mode="adjacent">Adjacent subjects</button>
      <button class="btn btn-sm join-item {% if mode == 'all' %}btn-primary{% endif %}"
              data-mode="all">All subjects</button>
    </div>

    <!-- "Why these?" link only in Adjacent mode -->
    {% if mode == 'adjacent' and rationales %}
      <button class="btn btn-sm btn-ghost text-info" id="why-these-btn"
              onclick="document.getElementById('why-these-modal').showModal()">
        Why these subjects?
      </button>
    {% endif %}
  </div>

  <!-- Sort -->
  <div class="mb-6 flex gap-3 text-sm">
    <a href="?sort=recent" class="{% if sort == 'recent' %}font-bold{% endif %}">Most recent</a>
    <span class="text-base-content/40">|</span>
    <a href="?sort=thumbs_up" class="{% if sort == 'thumbs_up' %}font-bold{% endif %}">Most thumbs-up</a>
  </div>

  <!-- Posts list -->
  <div class="space-y-4">
    {% for post in posts %}
      <article class="card bg-base-100 shadow-sm border border-base-300 p-5"
               aria-labelledby="post-{{ post.id }}-title">
        <h2 id="post-{{ post.id }}-title" class="text-xl font-semibold mb-1">
          <a href="{% url 'peer_blog:post_detail' post.id %}" class="hover:underline">
            {{ post.title }}
          </a>
        </h2>
        <p class="text-sm text-base-content/70 mb-3">
          {{ post.author_pseudonym }} — {{ post.subject_area|title }}, {{ post.grade_level }}
          · {{ post.created_at|timesince }} ago
        </p>
        <p class="text-base mb-3">{{ post.body|truncatewords:40 }}</p>
        <div class="flex gap-4 text-sm">
          <span>👍 {{ post.thumbs_up_count }}</span>
          <span>💬 {{ post.comments_count }}</span>
        </div>
      </article>
    {% empty %}
      <p class="text-center text-base-content/60 py-8">
        No posts yet in this filter. Try a wider filter mode or check back later.
      </p>
    {% endfor %}
  </div>
</div>

<!-- "Why these?" modal (only renders when adjacent mode + rationales exist) -->
{% if mode == 'adjacent' and rationales %}
  <dialog id="why-these-modal" class="modal">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-3">Why these subjects?</h3>
      <p class="mb-3">
        You're seeing posts from your subject ({{ user_subject|title }}) plus subjects
        that share pedagogical patterns. Cross-specialty perspectives often reveal
        new angles on AI integration.
      </p>
      <ul class="space-y-2">
        {% for subject, rationale in rationales.items %}
          <li class="bg-base-200 p-3 rounded">
            <strong>{{ subject|title }}:</strong> {{ rationale }}
          </li>
        {% endfor %}
      </ul>
      <div class="modal-action">
        <form method="dialog">
          <button class="btn">Close</button>
        </form>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
{% endif %}

<script>
// Filter mode toggle
document.querySelectorAll('[data-mode]').forEach(btn => {
  btn.addEventListener('click', async () => {
    const mode = btn.dataset.mode;
    const response = await fetch("{% url 'peer_blog:update_filter_mode' %}", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': '{{ csrf_token }}',
      },
      body: `mode=${mode}`,
    });
    if (response.ok) location.reload();
  });
});
</script>
{% endblock %}
```

### `templates/peer_blog/post_detail.html`

Single post + flat comments list + thumbs-up.

```html
{% extends 'base.html' %}
{% block content %}
<div class="container mx-auto px-4 py-6 max-w-3xl">
  <a href="{% url 'peer_blog:index' post.module.code %}" class="text-sm">
    ← Back to {{ post.module.code }} Practice Workshop
  </a>

  <article class="mt-4 mb-8">
    <h1 class="text-3xl font-bold mb-2">{{ post.title }}</h1>
    <p class="text-sm text-base-content/70 mb-4">
      {{ post.author_pseudonym }} — {{ post.subject_area|title }}, {{ post.grade_level }}
      · {{ post.created_at|date:"M j, Y" }}
    </p>

    <div class="prose max-w-none mb-6">
      {{ post.body|linebreaks }}
    </div>

    <!-- Thumbs-up button -->
    <div class="flex items-center gap-3">
      <button class="btn btn-sm {% if user_thumbed %}btn-primary{% else %}btn-outline{% endif %}"
              id="post-thumbs-up-btn" data-post-id="{{ post.id }}">
        👍 <span id="post-thumbs-count">{{ post.thumbs_up_count }}</span>
      </button>
    </div>
  </article>

  <hr class="my-6">

  <h2 class="text-2xl font-semibold mb-4">
    Comments ({{ post.comments_count }})
  </h2>

  <!-- Add comment form -->
  <form id="comment-form" class="mb-6">
    {% csrf_token %}
    <textarea name="body" rows="3" required maxlength="2000"
              class="textarea textarea-bordered w-full"
              placeholder="Share your thoughts on this..."></textarea>
    <button type="submit" class="btn btn-primary mt-2">Post comment</button>
  </form>

  <!-- Flat comments list (D14 — no nesting) -->
  <div id="comments-list" class="space-y-4">
    {% for comment in comments %}
      <div class="card bg-base-200 p-4">
        <p class="text-sm text-base-content/70 mb-2">
          {{ comment.author_pseudonym }} — {{ comment.subject_area|title }}
          · {{ comment.created_at|timesince }} ago
        </p>
        <p>{{ comment.body|linebreaks }}</p>
        <div class="flex gap-3 text-sm mt-2">
          <button class="link comment-thumbs-btn"
                  data-comment-id="{{ comment.id }}">
            👍 <span class="comment-thumbs-count">{{ comment.thumbs_up_count }}</span>
          </button>
        </div>
      </div>
    {% empty %}
      <p class="text-center text-base-content/60 py-4">
        No comments yet. Be the first to share thoughts.
      </p>
    {% endfor %}
  </div>
</div>

<script>
// Thumbs-up on post
document.getElementById('post-thumbs-up-btn').addEventListener('click', async (e) => {
  const btn = e.currentTarget;
  const postId = btn.dataset.postId;
  const response = await fetch(`/blog/post/${postId}/thumbs-up/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': '{{ csrf_token }}' },
  });
  const data = await response.json();
  document.getElementById('post-thumbs-count').textContent = data.count;
  btn.classList.toggle('btn-primary', data.is_thumbed);
  btn.classList.toggle('btn-outline', !data.is_thumbed);
});

// Thumbs-up on comments
document.querySelectorAll('.comment-thumbs-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    const commentId = btn.dataset.commentId;
    const response = await fetch(`/blog/comment/${commentId}/thumbs-up/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': '{{ csrf_token }}' },
    });
    const data = await response.json();
    btn.querySelector('.comment-thumbs-count').textContent = data.count;
  });
});

// Comment submit
document.getElementById('comment-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const response = await fetch(`/blog/post/{{ post.id }}/comment/`, {
    method: 'POST',
    body: formData,
    headers: { 'X-CSRFToken': '{{ csrf_token }}' },
  });
  if (response.ok) location.reload();
});
</script>
{% endblock %}
```

**Note (D14):** No `_comment.html` recursive partial needed. Flat comments render inline in `post_detail.html`. Significantly simpler than nested approach.

## 2.8 — Django admin (research observation)

```python
# apps/peer_blog/admin.py

from django.contrib import admin
from .models import BlogPost, BlogComment, BlogThumbsUp


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_pseudonym', 'subject_area', 'grade_level',
                    'thumbs_up_count', 'comments_count', 'is_hidden', 'created_at')
    list_filter = ('module', 'subject_area', 'grade_level', 'is_hidden', 'hidden_reason')
    search_fields = ('title', 'body', 'author_pseudonym')
    readonly_fields = ('user', 'module', 'artefact_type', 'artefact_id',
                       'thumbs_up_count', 'comments_count', 'created_at')
    actions = ['hide_selected', 'unhide_selected']

    def hide_selected(self, request, queryset):
        # Reactive moderation: requires manual setting of hidden_reason in next step
        queryset.update(is_hidden=True)
    hide_selected.short_description = "Hide selected (set reason manually)"

    def unhide_selected(self, request, queryset):
        queryset.update(is_hidden=False, hidden_reason=None)
    unhide_selected.short_description = "Unhide selected"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author_pseudonym', 'thumbs_up_count', 'is_hidden', 'created_at')
    list_filter = ('is_hidden',)
    search_fields = ('body', 'author_pseudonym')
    actions = ['hide_selected', 'unhide_selected']

    def hide_selected(self, request, queryset):
        queryset.update(is_hidden=True)

    def unhide_selected(self, request, queryset):
        queryset.update(is_hidden=False)


@admin.register(BlogThumbsUp)
class BlogThumbsUpAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('user', 'post', 'comment', 'created_at')
```

## 2.9 — Pre-flight checklist for Section 2

Before coding the app:

- [ ] Confirm `TeacherProfile` model location and field names (especially `pseudonym`, `subject_area`, `grade_level`)
- [ ] Confirm User → Profile relation (`request.user.profile` or `.teacher_profile` etc.)
- [ ] Verify `apps.modules.models.Module` is importable as expected
- [ ] Test that base.html template provides necessary structure (navigation, CSS includes)
- [ ] Confirm CSRF middleware is enabled

---

# Section 3 — M13 Simplification + Wiring

**Goal:** Disable admin curation. Submission button creates BlogPost via opt-in flow.

## 3.1 — Tab3RepositorySubmission updates (no migration)

Same as v1 spec Section 3:

- `review_status` default value remains `'pending'` (schema unchanged)
- Submission view sets it directly to `'community_shared'` immediately on creation
- Admin actions `approve_selected`, `reject_selected`, `request_revision` get **commented out** with preservation note
- Admin retains list/filter for research observation

## 3.2 — M13 view handler

```python
# apps/modules/views.py — updated submit_to_repository

from apps.peer_blog.services import create_blog_post

def submit_to_repository(request):
    if request.method == 'POST':
        form = ...  # existing form
        if form.is_valid():
            with transaction.atomic():
                submission = Tab3RepositorySubmission.objects.create(
                    user=request.user,
                    module=module,
                    challenge_id=2,
                    title=form.cleaned_data['title'],
                    summary=form.cleaned_data['summary'],
                    subject_area=form.cleaned_data['subject_area'],
                    grade_level=form.cleaned_data['grade_level'],
                    contact_email=form.cleaned_data.get('contact_email', ''),
                    canvas_data=request.session.get('m13_canvas_data', {}),
                    review_status='community_shared',
                )

                # Create blog post for community peer dialogue
                post = create_blog_post(
                    artefact_type='m13_workflow',
                    artefact_id=submission.id,
                    title=submission.title,
                    body=f"{submission.summary}\n\n[Canvas details available in author's account]",
                    author_user=request.user,
                )

            return redirect('peer_blog:post_detail', post_id=post.id)
```

## 3.3 — M13 UI updates

**Button text:** "🛠️ Share to Practice Workshop" (Gemini D12 — Workshop framing)

**Footer text:**
> "Your workflow goes straight to the M13 Practice Workshop, where colleagues across disciplines can offer formative feedback through comments and thumbs-up. There is no approval gate — community dialogue is the value. Share work-in-progress freely; the Workshop is a space for reflection, not a polished gallery."

## 3.4 — Browser test checklist (M13)

- [ ] User completes M13 Challenge 2 → clicks "Share with Community"
- [ ] `Tab3RepositorySubmission` record created with `review_status='community_shared'`
- [ ] BlogPost created with correct artefact link
- [ ] Author redirected to blog post detail page
- [ ] Other users see post in M13 blog index (filtered by their subject mode)
- [ ] Other users can comment + reply
- [ ] Thumbs-up works on posts and comments
- [ ] Researcher can hide post via admin (reactive moderation)

---

# Section 4 — M9 Wiring

**Goal:** Opt-in checkbox on M9 challenge completion creates BlogPost.

## 4.1 — Challenge structure

M9 has 3 TAB3 challenges. All produce lesson-design artefacts and are eligible for sharing.

**Pre-flight task:** Confirm exact challenge titles + JSONB field names in `Tab3UserActivity.challenge_data`.

## 4.2 — Opt-in checkbox in challenge completion flow

After challenge submission, completion modal shows:

```html
<label class="label cursor-pointer">
  <input type="checkbox" name="share_to_blog" class="checkbox" />
  <span class="label-text ml-2">
    Share my lesson design to the M9 Practice Workshop.
    Colleagues can offer formative feedback. No approval gate — share work-in-progress freely.
  </span>
</label>
```

If checked: server-side handler calls `create_blog_post('m9_lesson', activity.id, ...)`.

## 4.3 — Server-side handler

```python
# apps/modules/views.py — challenge completion handler

def m9_challenge_complete(request, challenge_id):
    if request.method == 'POST':
        # ... existing challenge save logic ...

        share_to_blog = request.POST.get('share_to_blog') == 'on'

        if share_to_blog:
            from apps.peer_blog.services import create_blog_post
            post = create_blog_post(
                artefact_type='m9_lesson',
                artefact_id=activity.id,
                title=activity.challenge_data.get('lesson_title', f'Lesson — Challenge {challenge_id}'),
                body=activity.challenge_data.get('lesson_summary', ''),
                author_user=request.user,
            )
            # Update challenge_data with blog post link
            activity.challenge_data['shared_to_blog'] = True
            activity.challenge_data['blog_post_id'] = post.id
            activity.save()
        else:
            activity.challenge_data['shared_to_blog'] = False
            activity.save()

        return redirect(...)
```

## 4.4 — Browser test checklist (M9)

- [ ] User completes M9 Challenge 1 → checkbox visible
- [ ] User checks box + submits → BlogPost created
- [ ] User leaves checkbox empty + submits → no BlogPost (no spam)
- [ ] Post appears in M9 blog index for users matching subject filter
- [ ] Comments and thumbs-up work

---

# Section 5 — M14 Wiring (Gamified Unit Planner Only)

**Goal:** Same as M9 but ONLY for challenge_id == 3 (Gamified Unit Planner).

**Important:** Do NOT wire M14 Challenge 1 (SAMR Audit) or Challenge 2 (Five Roles Matcher).

## 5.1 — Implementation

```python
def m14_challenge_complete(request, challenge_id):
    if request.method == 'POST':
        # ... existing logic ...

        # Only Challenge 3 (Gamified UP) supports peer blog sharing
        if challenge_id == 3:
            share_to_blog = request.POST.get('share_to_blog') == 'on'
            if share_to_blog:
                from apps.peer_blog.services import create_blog_post
                post = create_blog_post(
                    artefact_type='m14_gamified_unit',
                    artefact_id=activity.id,
                    title=activity.challenge_data.get('unit_title', 'Gamified Unit'),
                    body=activity.challenge_data.get('unit_summary', ''),
                    author_user=request.user,
                )
                activity.challenge_data['shared_to_blog'] = True
                activity.challenge_data['blog_post_id'] = post.id
                activity.save()
        # Challenge 1 + 2 don't show the checkbox at all (template conditional)
```

## 5.2 — Template conditional

In challenge completion template:

```html
{% if challenge.id == 3 %}
  <label class="label cursor-pointer">
    <input type="checkbox" name="share_to_blog" class="checkbox" />
    <span class="label-text ml-2">
      Share my gamified unit to the M14 Practice Workshop.
      Colleagues can offer formative feedback.
    </span>
  </label>
{% endif %}
```

## 5.3 — Browser test checklist (M14)

- [ ] M14 Challenge 1 (SAMR Audit) → no checkbox shown
- [ ] M14 Challenge 2 (Five Roles Matcher) → no checkbox shown
- [ ] M14 Challenge 3 (Gamified UP) → checkbox shown
- [ ] Checked + submitted → BlogPost created
- [ ] M14 blog index shows post correctly

---

# Section 6 — M8 Ethics-by-Design Subsection (CG3.2.4)

**Target indicator:** CG3.2.4 PARTIAL → STRONG

**Module:** M8 (mod_id and main_content row TBD pre-flight)

**Anchor:** M8 main_content TAB2, end of Part 4 (Ethics by Design in Prompting). Add new subsection before Part 5.

**Pre-flight:** Sample 200-300 chars around anchor.

## Wording (~120 words)

> **Hands-on Ethics in Your Prompts.** Ethics-by-design isn't an abstract goal — it's a daily practice in how you write prompts. Three concrete checks you can apply to any prompt before sending it:
>
> **Bias check.** Does your prompt assume student demographics, abilities, or backgrounds? "Write an example for a typical student" carries hidden assumptions. "Write an example accessible to learners with diverse strengths" is more inclusive.
>
> **Privacy check.** Does your prompt include real student names, identifiable details, or sensitive information? Replace with anonymised placeholders ("Student A", "a learner with reading difficulties").
>
> **Inclusivity check.** Does your prompt's tone or framing exclude any group? Test by reading aloud — if it sounds othering, rewrite.
>
> Apply these checks habitually, and your Studio templates will embody ethics-by-design without conscious effort.

## HTML structure

```html
<!-- M8_ETHICS_BY_DESIGN_PATCH -->
<div class="card bg-base-200 border-l-4 border-warning p-4 my-4"
     role="region" aria-label="Hands-on ethics checks for prompts">
  <h4 class="font-bold text-warning mb-2">Hands-on Ethics in Your Prompts</h4>
  <p>Ethics-by-design isn't an abstract goal — it's a daily practice in how you write prompts. Three concrete checks you can apply to any prompt before sending it:</p>

  <div class="space-y-3 mt-3">
    <div>
      <p class="font-semibold">Bias check.</p>
      <p>Does your prompt assume student demographics, abilities, or backgrounds? "Write an example for a typical student" carries hidden assumptions. "Write an example accessible to learners with diverse strengths" is more inclusive.</p>
    </div>

    <div>
      <p class="font-semibold">Privacy check.</p>
      <p>Does your prompt include real student names, identifiable details, or sensitive information? Replace with anonymised placeholders ("Student A", "a learner with reading difficulties").</p>
    </div>

    <div>
      <p class="font-semibold">Inclusivity check.</p>
      <p>Does your prompt's tone or framing exclude any group? Test by reading aloud — if it sounds othering, rewrite.</p>
    </div>
  </div>

  <p class="mt-3">Apply these checks habitually, and your Studio templates will embody ethics-by-design without conscious effort.</p>
</div>
<!-- /M8_ETHICS_BY_DESIGN_PATCH -->
```

**Patch marker:** `<!-- M8_ETHICS_BY_DESIGN_PATCH -->`

**RAG ingest:** Required.

**RAG verification query:** "How can I check my prompts for bias and privacy?" → expected rank #1 mod-scoped, sim ≥ 0.78.

---

# Section 7 — M8 Cross-Reference to M3 (CG3.2.1)

**Target indicator:** CG3.2.1 PARTIAL → STRONG

**Anchor:** M8 main_content TAB2, beginning of Part 1, immediately after H2 heading.

**Pre-flight:** Sample 200-300 chars around anchor.

## Wording (~60 words)

> **A note on AI techniques.** M8 specialises in **generative AI** — the LLM-based prompt engineering you'll do most often as a teacher. For a broader comparison of AI techniques (symbolic AI, predictive AI, generative AI) and when to use each, refer to **M3 Part 2** (AI Categories and the Reliability Framework). M8 builds on that foundation; here we go deeper on the generative side.

## HTML structure

```html
<!-- M8_CROSS_REF_M3_PATCH -->
<div class="card bg-base-200 border-l-4 border-info p-4 my-4"
     role="note" aria-label="Cross-reference to M3 on AI techniques">
  <h4 class="font-bold text-info mb-2">A note on AI techniques</h4>
  <p>M8 specialises in <strong>generative AI</strong> — the LLM-based prompt engineering you'll do most often as a teacher. For a broader comparison of AI techniques (symbolic AI, predictive AI, generative AI) and when to use each, refer to <strong>M3 Part 2</strong> (AI Categories and the Reliability Framework). M8 builds on that foundation; here we go deeper on the generative side.</p>
</div>
<!-- /M8_CROSS_REF_M3_PATCH -->
```

**Patch marker:** `<!-- M8_CROSS_REF_M3_PATCH -->`

**RAG ingest:** Required.

**RAG verification query:** "How does M8 relate to M3 on AI techniques?" → expected rank #1 mod-scoped, sim ≥ 0.78.

---

# Section 8 — Reactive Moderation Policy (NEW DOCUMENT)

**File:** `REACTIVE_MODERATION_POLICY.md` (project root)

## Content

```markdown
# Reactive Moderation Policy
**PROODOS EduAI — Phase A Tier 3, May 2026**

## Philosophy

PROODOS adopts **reactive moderation** for community-shared content (workflows, lesson designs, gamified units, comments). This is a deliberate philosophical choice that contrasts with **proactive curation**.

### Reactive moderation
- Content is visible immediately when shared.
- Researcher (or trusted moderators) can hide problematic content after the fact.
- The community sees content, dialogues, and self-coordinates.
- Hide actions are documented (`hidden_reason` field) and reversible (`unhide_selected` admin action).

### Why not proactive curation?
- Proactive curation creates aspirational/reality mismatch.
- Proactive curation introduces researcher bias into pilot study data.
- Proactive curation contradicts the Wenger Communities of Practice framing central to PROODOS Aspect 5.
- Proactive curation creates a researcher bottleneck.

## Hide-trigger criteria (the only reasons to hide)

Content is hidden if and only if it falls in one of these 4 categories:

1. **Platform safety violation (`safety_violation`)** — content that promotes harm to students, ignores child safeguarding, recommends illegal AI use cases, or proposes AI-only decisions on consequential outcomes (e.g., final grading, admission, special-needs placement) without human oversight (M6 4 Rights violation).

2. **Off-topic spam (`off_topic_spam`)** — content not related to AI in education, promotional content for unrelated products/services, or duplicate/automated submissions.

3. **Real student PII (`contains_pii`)** — content that includes identifying student information (real names, photos, identifying anecdotes) that should be anonymised before sharing.

4. **Copyright violation (`copyright_violation`)** — explicit infringement of third-party content (lyrics, full articles, copyrighted curricula, trademarked imagery).

## Hide-NEVER criteria (do NOT hide for these reasons)

- Pedagogical disagreement
- Quality concerns ("not good enough")
- Different theoretical orientations
- Beginner-level work
- Subject-area unfamiliarity
- Personal aesthetic preferences
- Disagreement with the author's framing

## Researcher monitoring cadence

The researcher reviews the moderation queue **weekly** during the pilot study (n=110 teachers, ~6-month duration).

**Weekly review activities:**
1. Scan posts created since last review for the 4 hide-trigger criteria.
2. Document any hide actions in the moderation log (auto-generated by Django admin).
3. Note patterns (which categories trigger hides most often) for dissertation analysis.
4. Reconsider any prior hide actions if author has revised content.

**Estimated time:** ~30 minutes per week. Manageable load.

## Pilot study integrity

The reactive moderation log is itself research data:

- Patterns of hidden content reveal community dynamics, not researcher curation outcomes.
- Hide rates per category indicate where the community needs better onboarding (e.g., if PII hides spike, improve the share-flow PII reminder).
- Researcher self-discipline (only hide for the 4 criteria) protects against bias.

## Defendability for dissertation

The reactive moderation policy:
- Aligns with platform-wide community-driven philosophy
- Avoids proactive bias in pilot data
- Provides safety net for legal/ethical concerns
- Documents transparent decision criteria
- Makes researcher actions auditable
```

---

# Section 9 — CONTRIBUTING.md Alignment

**Goal:** Update GitHub repo `proodos-eduai/teacher-workflows/CONTRIBUTING.md` to reflect blog-based community-driven peer dialogue.

## Updates

**Old (Tier 2):**
> "Submissions are reviewed by master teachers for pedagogical soundness, ethical alignment, and reproducibility before publication. Review SLA: ~2 weeks."

**New (Tier 3, v3):**
> "Workflows are shared with the PROODOS community immediately through the M13 Practice Workshop — a space dedicated to reflective sharing of work-in-progress. Each shared workflow becomes a workshop post where subject peers and colleagues across disciplines can offer formative feedback through comments and thumbs-up endorsements.
>
> There is no approval gate. The Workshop is intentionally framed as practice, not gallery — share rough drafts, half-formed ideas, and refined workflows alike. Community dialogue is the value. Researcher moderation is **reactive only**: problematic content (off-topic, spam, real student PII, or content that conflicts with platform safety guidelines) may be hidden after the fact, but no submission requires pre-approval to be visible.
>
> When you submit, expect:
> - Immediate visibility in the M13 Practice Workshop
> - Subject-peer responses within days (varies by community activity)
> - No grading or pass/fail outcome — this is dialogue, not assessment
> - Cross-specialty perspectives by default (you can switch to subject-only if preferred)
>
> See `REACTIVE_MODERATION_POLICY.md` for the full transparency policy."

---

# Section 10 — PDF Reconsideration

**Same as v1 spec Section 10.** xhtml2pdf vs weasyprint smoke test, decision document, recommendation logic.

---

# Section 11 — Logs + Audit Projection

## 11.1 — `PLATFORM_CHANGES_LOG_TIER3_APPEND.md`

Sections:
- Executive summary table
- Pre-flight blockers + resolutions
- Each step in execution sequence with apply / browser test / verification
- Files inventory (created/modified)
- Operational notes
- **Tier 3 architecture decision history** (forum approach abandoned, blog approach chosen, Gemini revisions integrated — important record for dissertation)

### Required defence rationale paragraph (Gemini D15)

The PLATFORM_CHANGES_LOG must include this explicit defence rationale for the architecture decision, written in research-defendable prose:

> **Architecture Decision: Practice Workshop App vs Forum Reuse**
>
> Phase A Tier 3 introduces a new Django app (`apps.peer_blog`, presented as "Practice Workshop") rather than reusing the existing community forum for artefact peer dialogue. This decision adds approximately one hour of development effort but is justified by three research-grade considerations:
>
> 1. **Researcher data quality.** A forum thread "wakes up" with each reply, creating noise that interferes with chronological analysis of artefact-specific feedback. Workshop posts remain anchored to their creation timestamp; comments are secondary signal. This produces cleaner research data on how peers respond to specific artefacts.
>
> 2. **Reactive moderation footprint.** Forum threads in a 110-teacher pilot would generate 50–150 active threads requiring weekly researcher attention to prevent drift. Workshop posts with reactive moderation require ~30 minutes of weekly review, freeing the researcher for data analysis rather than community management.
>
> 3. **Cross-Specialty Peer Synthesizer alignment.** The Workshop's "Adjacent subjects" default filter (with pedagogical rationales surfaced through a 'Why these?' modal) directly operationalises the cross-specialty interaction research instrument. The forum's flat thread structure could not provide this scaffolding without significant retrofit.
>
> The existing forum app is preserved for general module discussion and Q&A. The two channels coexist with distinct purposes: forum for casual / cross-module discussion, Workshop for artefact-anchored peer dialogue.

## 11.2 — `CONTENT_GAPS_LOG_TIER3_UPDATE.md`

**⚠️ CRITICAL Section 1:** Audit table corrections (this spec Section 1) — high visibility, top of document.

Sections:
- Headline coverage table (pre/post Tier 3)
- Indicator status changes:
  - 2 audit corrections (CG1.2.4, LO3.2.2)
  - 2 M8 patches (CG3.2.1, CG3.2.4)
  - 1 reinforcement (CA3.3.3) — community-coordination defendable
- Methodology notes
- Aspect-level coverage shift

## 11.3 — Coverage projection

| State | STRONG | % |
|-------|--------|---|
| Pre-Tier-3 (post-Tier-2) | 138/170 | 81.2% |
| + Audit corrections | 140/170 | 82.4% |
| + M8 patches | 142/170 | 83.5% |
| **Post-Tier-3** | **142/170** | **~83.5%** |

---

# Section 12 — Execution Sequence

```
Step 0 — Tier 2 master log merges (DONE per John, May 2026)
─────────────────────────────────────────────────────────────
Step 1 — Pre-flight all components, consolidated report
         Critical checks:
         (a) M8 mod_id, main_content row_id, Part 1 + Part 4 anchors
         (b) M9 + M14 Tab3UserActivity field structures
         (c) TeacherProfile model location, fields (pseudonym, subject_area, grade_level)
         (d) User → Profile relation (request.user.profile vs .teacher_profile)
         (e) base.html template structure for blog templates
         (f) PDF stack (xhtml2pdf) version + Linux test viability
         STOP and report. Wait for sign-off before proceeding.
─────────────────────────────────────────────────────────────
Step 2 — Peer Blog app (Section 2)
         Create app, models, migrations (peer_blog 0001 + users 00XX),
         views, URLs, templates, admin, subject_mappings, services
         Browser test: navigate to /blog/module/M13/, see empty index;
         filter modes work; admin lists empty
─────────────────────────────────────────────────────────────
Step 3 — M13 simplification + wiring (Section 3)
         Disable admin actions, update view, update UI text
         Browser test: full M13 share flow per Section 3.4
─────────────────────────────────────────────────────────────
Step 4 — M9 wiring (Section 4)
         Add checkbox to challenge completion templates,
         update server handler
         Browser test: per Section 4.4
─────────────────────────────────────────────────────────────
Step 5 — M14 wiring (Section 5, Gamified UP only)
         Conditional checkbox + handler
         Browser test: per Section 5.3
─────────────────────────────────────────────────────────────
Step 6 — M8 patches (Sections 6 + 7)
         Apply both Type A patches + RAG ingest
         Browser test: subsection + callout render
─────────────────────────────────────────────────────────────
Step 7 — Reactive moderation policy doc (Section 8)
         Create REACTIVE_MODERATION_POLICY.md in project root
─────────────────────────────────────────────────────────────
Step 8 — CONTRIBUTING.md alignment (Section 9)
         Edit + commit GitHub repo
─────────────────────────────────────────────────────────────
Step 9 — PDF reconsideration (Section 10)
         Smoke test + decision document
─────────────────────────────────────────────────────────────
Step 10 — Logs + audit projection update (Section 11)
          ⚠️ INCLUDE AUDIT TABLE CORRECTIONS PROMINENTLY
          Coverage 81.2% → 83.5% confirmed
─────────────────────────────────────────────────────────────
Step 11 — Final summary report
          STOP. John signs off Tier 3 closure.
```

---

# Section 13 — Risk Register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| TeacherProfile field names differ from assumptions | Medium | Pre-flight check (c) catches it |
| Tab3UserActivity JSON structure differs across modules | Medium | Pre-flight check (b) catches it |
| User → Profile relation differs (`.profile` vs `.teacher_profile`) | Medium | Pre-flight check (d) catches it |
| Template inheritance issues with new blog templates | Low | Pre-flight check (e) catches it |
| Adjacent mapping creates dead corners (e.g., `other` users see nothing in Adjacent) | Low | Mapping reviewed; `other` falls back to itself |
| weasyprint Linux test fails | Low | Default: stay with xhtml2pdf |
| RAG sim threshold miss for M8 patches | Low | Patches are short and topical |
| Workshop framing confused with "informal/lower quality" | Low | Footer text explicitly invites work-in-progress |
| "Why these?" modal increases UI complexity | Very Low | Modal is opt-in (only opens on click) |

---

# Section 14 — Final Notes for Claude Code

- **Trust your judgment** per Tier 1+2 patterns.
- **Stop-and-report** at each major step (especially Steps 1, 2, 3, 4, 5, 6, 9, 10).
- **Use existing patterns** (named dollar-quoting, backup tables, anchor sampling) for SQL.
- **Audit corrections must not be skipped** — Section 1 + Section 11 reminder.
- **User-facing labels:** "Practice Workshop" (D12). Technical names stay `peer_blog`, `BlogPost`, etc. for clean schema.
- **Comments are flat** (D14) — no `parent_comment` FK, no `_comment.html` recursive partial.
- **"Why these?" modal** required in Adjacent mode (D13) — show pedagogical rationales for each adjacent subject.
- **Defence rationale paragraph** (D15) must appear verbatim in PLATFORM_CHANGES_LOG_TIER3_APPEND.md.
- **Reactive moderation** documented in project root.
- **Cost discipline:** Zero new Gemini API calls.
- **Test account:** mavros@example.com (Vaggelis Mavros, mathematics, upper secondary).
- **Architecture decision history:** Document v1 → v2 → v3 transitions in PLATFORM_CHANGES_LOG to preserve reasoning for dissertation.

---

**End of PHASE_A_TIER3_SPEC_v3.md (Gemini external review applied, ready for Claude Code execution).**

Open questions before execution: none (D1-D15 resolved).
