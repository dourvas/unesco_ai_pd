"""
Practice Workshop service layer.

Single source of truth for blog post creation, comment creation, and
thumbs-up toggle. Cross-module wiring (M13/M9/M14) calls into these.
"""

from django.db import transaction
from django.db.models import F

from apps.modules.models import Module

from .models import BlogComment, BlogPost, BlogThumbsUp


ARTEFACT_TYPES = {
    'm13_workflow': {
        'module_code': 'M13',
        'title_template': '{title}',
    },
    'm9_lesson': {
        'module_code': 'M9',
        'title_template': '{title}',
    },
    'm14_gamified_unit': {
        'module_code': 'M14',
        'title_template': '{title}',
    },
}


# Phase A Tier 3 — modules with a live Practice Workshop wiring.
# Step 3: M13. Step 4: M9. Step 5: M14.
# Powers the top-nav dropdown and the modules-list "Workshop active" badge.
WORKSHOP_ACTIVE_MODULES = ['M13', 'M9', 'M14']


def get_workshop_active_modules():
    """Return Module queryset (preserving WORKSHOP_ACTIVE_MODULES order)."""
    qs = Module.objects.filter(code__in=WORKSHOP_ACTIVE_MODULES)
    by_code = {m.code: m for m in qs}
    return [by_code[c] for c in WORKSHOP_ACTIVE_MODULES if c in by_code]


def _author_snapshot(user):
    """
    Snapshot author display fields at post-creation time.

    Uses TeacherProfile.pseudonym property (Tier 3 Blocker 1 — Option B):
    returns display_name if set, otherwise f"Educator_{user.id}".
    """
    profile = getattr(user, 'teacher_profile', None)
    if profile is None:
        return {
            'pseudonym': f'Educator_{user.id}',
            'subject_area': '',
            'grade_level': '',
        }
    return {
        'pseudonym': profile.pseudonym,
        'subject_area': profile.subject_area or '',
        'grade_level': profile.grade_level or '',
    }


def create_blog_post(artefact_type, artefact_id, title, body, author_user):
    """
    Create a new BlogPost for an opt-in user artefact.

    Args:
        artefact_type: One of ARTEFACT_TYPES keys
        artefact_id: ID of source artefact
        title: Short title of the artefact
        body: Full body / summary text
        author_user: Django User instance

    Returns: BlogPost instance
    """
    if artefact_type not in ARTEFACT_TYPES:
        raise ValueError(f"Unknown artefact_type: {artefact_type}")

    config = ARTEFACT_TYPES[artefact_type]
    module = Module.objects.get(code=config['module_code'])
    snapshot = _author_snapshot(author_user)

    return BlogPost.objects.create(
        user=author_user,
        module=module,
        artefact_type=artefact_type,
        artefact_id=artefact_id,
        title=config['title_template'].format(title=title),
        body=body,
        author_pseudonym=snapshot['pseudonym'],
        subject_area=snapshot['subject_area'],
        grade_level=snapshot['grade_level'],
    )


def add_comment(post, author_user, body):
    """Create a flat BlogComment (D14 — no nesting). Increments post.comments_count."""
    snapshot = _author_snapshot(author_user)
    with transaction.atomic():
        comment = BlogComment.objects.create(
            post=post,
            user=author_user,
            body=body,
            author_pseudonym=snapshot['pseudonym'],
            subject_area=snapshot['subject_area'],
        )
        BlogPost.objects.filter(pk=post.pk).update(
            comments_count=F('comments_count') + 1
        )
    return comment


def toggle_thumbs_up(user, post=None, comment=None):
    """
    Idempotent toggle. If user already thumbs-up'd, removes it. Otherwise adds.
    Updates denormalised counter on the target.

    Returns: (is_now_thumbed, new_count) tuple
    """
    if (post is None) == (comment is None):
        raise ValueError("Must provide exactly one of post or comment")

    target = post if post is not None else comment
    target_model = type(target)

    with transaction.atomic():
        if post is not None:
            existing = BlogThumbsUp.objects.filter(user=user, post=post).first()
        else:
            existing = BlogThumbsUp.objects.filter(user=user, comment=comment).first()

        if existing:
            existing.delete()
            target_model.objects.filter(pk=target.pk).update(
                thumbs_up_count=F('thumbs_up_count') - 1
            )
            target.refresh_from_db()
            return False, target.thumbs_up_count

        BlogThumbsUp.objects.create(user=user, post=post, comment=comment)
        target_model.objects.filter(pk=target.pk).update(
            thumbs_up_count=F('thumbs_up_count') + 1
        )
        target.refresh_from_db()
        return True, target.thumbs_up_count
