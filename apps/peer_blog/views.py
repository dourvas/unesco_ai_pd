"""
Practice Workshop views.

User-facing label is "Practice Workshop" everywhere (D12).
Comments are flat (D14) — no nesting.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.modules.models import Module

from .models import BlogComment, BlogPost
from .services import add_comment, toggle_thumbs_up
from .subject_mappings import get_adjacency_rationales, get_filtered_subjects


def _resolve_filter_mode(profile):
    """Read filter mode from teacher_profile, default 'adjacent' if missing."""
    if profile is None:
        return 'adjacent'
    return getattr(profile, 'blog_subject_filter_preference', None) or 'adjacent'


def moderation_policy(request):
    """Public-facing reactive moderation policy page (Step 12, post-Tier-3).

    Intentionally NOT @login_required — the policy is informed-consent
    transparency surface and should be reachable from share-modal links
    even if the user's session expires while reading.
    """
    return render(request, 'peer_blog/moderation_policy.html')


@login_required
def blog_index(request, module_code):
    """Render the module Practice Workshop feed with subject filter applied."""
    module = get_object_or_404(Module, code=module_code)
    profile = getattr(request.user, 'teacher_profile', None)
    user_subject = profile.subject_area if profile else None
    mode = _resolve_filter_mode(profile)

    queryset = BlogPost.objects.filter(module=module, is_hidden=False)
    subject_filter = get_filtered_subjects(user_subject, mode)
    if subject_filter is not None:
        queryset = queryset.filter(subject_area__in=subject_filter)

    sort = request.GET.get('sort', 'recent')
    if sort == 'thumbs_up':
        queryset = queryset.order_by('-thumbs_up_count', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')

    posts = list(queryset[:50])

    rationales = {}
    if mode == 'adjacent':
        rationales = get_adjacency_rationales(user_subject)

    return render(
        request,
        'peer_blog/index.html',
        {
            'module': module,
            'posts': posts,
            'mode': mode,
            'sort': sort,
            'rationales': rationales,
            'user_subject': user_subject,
        },
    )


@login_required
@require_POST
def update_filter_mode(request):
    """AJAX endpoint to update user's filter preference."""
    new_mode = request.POST.get('mode')
    if new_mode not in ('my_subject', 'adjacent', 'all'):
        return JsonResponse({'error': 'Invalid mode'}, status=400)
    profile = getattr(request.user, 'teacher_profile', None)
    if profile is None:
        return JsonResponse({'error': 'No profile'}, status=400)
    profile.blog_subject_filter_preference = new_mode
    profile.save(update_fields=['blog_subject_filter_preference'])
    return JsonResponse({'mode': new_mode})


@login_required
def blog_post_detail(request, post_id):
    """Render a single post with flat comments list (D14).

    Tier 3 Step 3.5: surfaces is_author flag for self-service UI; if
    a withdrawn post is fetched directly, render a 'withdrawn' template
    state instead of a hard 404 (researcher access path preserved).
    """
    post = get_object_or_404(BlogPost, pk=post_id)
    is_author = post.user_id == request.user.id

    if post.is_hidden and not is_author and not request.user.is_staff:
        return render(
            request,
            'peer_blog/post_withdrawn.html',
            {'post': post},
            status=410,
        )

    comments = post.comments.filter(is_hidden=False).order_by('created_at')
    user_thumbed = post.blogthumbsup_set.filter(user=request.user).exists()

    return render(
        request,
        'peer_blog/post_detail.html',
        {
            'post': post,
            'comments': comments,
            'user_thumbed': user_thumbed,
            'is_author': is_author,
        },
    )


@login_required
@require_POST
def submit_comment(request, post_id):
    """AJAX endpoint to submit a flat comment (no nesting per D14)."""
    post = get_object_or_404(BlogPost, pk=post_id, is_hidden=False)
    body = (request.POST.get('body') or '').strip()
    if not body:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    comment = add_comment(post, request.user, body)
    return JsonResponse(
        {
            'id': comment.id,
            'body': comment.body,
            'author': comment.author_pseudonym,
            'subject_area': comment.subject_area,
            'created_at': comment.created_at.isoformat(),
        }
    )


@login_required
@require_POST
def toggle_post_thumbs_up(request, post_id):
    """AJAX endpoint for thumbs-up toggle on a post."""
    post = get_object_or_404(BlogPost, pk=post_id, is_hidden=False)
    is_thumbed, count = toggle_thumbs_up(request.user, post=post)
    return JsonResponse({'is_thumbed': is_thumbed, 'count': count})


@login_required
@require_POST
def toggle_comment_thumbs_up(request, comment_id):
    """AJAX endpoint for thumbs-up toggle on a comment."""
    comment = get_object_or_404(BlogComment, pk=comment_id, is_hidden=False)
    is_thumbed, count = toggle_thumbs_up(request.user, comment=comment)
    return JsonResponse({'is_thumbed': is_thumbed, 'count': count})


# ============================================================
# Phase A Tier 3 Step 3.5 — Author self-service
# Authors can edit their post title, withdraw their post, and
# edit/delete their own comments. Withdrawal/deletion is a soft
# delete (is_hidden=True) — researcher can still observe the
# record. Edits update the body in-place; updated_at tracks the
# revision.
# ============================================================


def _ensure_author(request, obj):
    """Return None if request.user owns obj; else a 403 JsonResponse."""
    if obj.user_id != request.user.id:
        return JsonResponse({'error': 'Not the author.'}, status=403)
    return None


@login_required
@require_POST
def edit_post_title(request, post_id):
    """Author-only: update BlogPost.title in place."""
    post = get_object_or_404(BlogPost, pk=post_id)
    forbidden = _ensure_author(request, post)
    if forbidden:
        return forbidden

    new_title = (request.POST.get('title') or '').strip()
    if not new_title:
        return JsonResponse({'error': 'Title required.'}, status=400)
    if len(new_title) > 200:
        return JsonResponse({'error': 'Title must be ≤ 200 characters.'}, status=400)

    post.title = new_title
    post.save(update_fields=['title', 'updated_at'])
    return JsonResponse({'title': post.title, 'updated_at': post.updated_at.isoformat()})


@login_required
@require_POST
def withdraw_post(request, post_id):
    """Author-only: soft-delete (is_hidden + reason='author_withdrawn')."""
    post = get_object_or_404(BlogPost, pk=post_id)
    forbidden = _ensure_author(request, post)
    if forbidden:
        return forbidden

    post.is_hidden = True
    post.hidden_reason = 'author_withdrawn'
    post.save(update_fields=['is_hidden', 'hidden_reason', 'updated_at'])
    return JsonResponse({
        'withdrawn': True,
        'redirect_url': reverse('peer_blog:index', kwargs={'module_code': post.module.code}),
    })


@login_required
@require_POST
def edit_comment(request, comment_id):
    """Author-only: update BlogComment.body in place."""
    comment = get_object_or_404(BlogComment, pk=comment_id)
    forbidden = _ensure_author(request, comment)
    if forbidden:
        return forbidden

    new_body = (request.POST.get('body') or '').strip()
    if not new_body:
        return JsonResponse({'error': 'Comment body required.'}, status=400)

    comment.body = new_body
    comment.save(update_fields=['body', 'updated_at'])
    return JsonResponse({
        'body': comment.body,
        'updated_at': comment.updated_at.isoformat(),
    })


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Author-only: soft-delete (is_hidden + reason='author_deleted')."""
    comment = get_object_or_404(BlogComment, pk=comment_id)
    forbidden = _ensure_author(request, comment)
    if forbidden:
        return forbidden

    comment.is_hidden = True
    comment.hidden_reason = 'author_deleted'
    comment.save(update_fields=['is_hidden', 'hidden_reason', 'updated_at'])

    # Decrement denormalised counter on the parent post if the comment
    # was visible (it was, since we don't allow deleting hidden comments).
    BlogPost.objects.filter(pk=comment.post_id, comments_count__gt=0).update(
        comments_count=F('comments_count') - 1
    )
    return JsonResponse({'deleted': True})
