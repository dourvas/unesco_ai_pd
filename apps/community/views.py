"""
apps/community/views.py
=======================
Forum views for PROODOS EduAI Platform.

Views:
1. community_home      - Full community page (/community/)
2. thread_detail       - Full thread page (/community/M1/)
3. post_create         - AJAX: create a new post
4. post_reply          - AJAX: reply to a post
5. post_helpful_vote   - AJAX: toggle helpful vote
6. forum_preview       - AJAX partial: 3 posts for inline tab triggers
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.utils import timezone

from .models import ForumThread, ForumPost, ForumHelpfulVote


# ============================================================================
# 1. COMMUNITY HOME PAGE
# ============================================================================

@login_required
def community_home(request):
    """
    Full community page showing all active threads across modules.
    URL: /community/
    
    Context:
    - threads: All active ForumThreads with post counts
    - trending: Top 3 threads by recent activity
    - user_post_count: How many posts this user has made
    """
    threads = ForumThread.objects.filter(
        is_active=True,
        module__is_published=True
    ).select_related('module').order_by('module__order_index')

    # Trending: threads with most posts in last 7 days
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    trending = ForumThread.objects.filter(
        is_active=True,
        last_activity_at__gte=week_ago
    ).order_by('-post_count')[:3]

    user_post_count = ForumPost.objects.filter(
        author=request.user,
        is_deleted=False
    ).count()

    # Get user's voted post IDs for this session
    user_voted_ids = list(
        ForumHelpfulVote.objects.filter(
            user=request.user
        ).values_list('post_id', flat=True)
    )

    context = {
        'threads': threads,
        'trending': trending,
        'user_post_count': user_post_count,
        'user_voted_ids': user_voted_ids,
    }
    return render(request, 'community/community_home.html', context)


# ============================================================================
# 2. THREAD DETAIL (FULL FORUM PAGE PER MODULE)
# ============================================================================

@login_required
def thread_detail(request, module_code):
    """
    Full forum page for a specific module.
    URL: /community/<module_code>/
    
    Shows:
    - Seeded question(s) from researcher
    - All top-level posts (newest first)
    - Nested replies per post
    - Inline post form
    """
    thread = get_object_or_404(
        ForumThread,
        module__code=module_code.upper(),
        is_active=True
    )

    # Top-level posts (pinned first, then newest)
    top_posts = ForumPost.objects.filter(
        thread=thread,
        parent_post=None,
        is_deleted=False
    ).prefetch_related(
        'replies',
        'helpful_votes'
    ).order_by('-is_pinned', '-is_seeded', '-created_at')

    # User's voted post IDs (for UI state)
    user_voted_ids = set(
        ForumHelpfulVote.objects.filter(
            user=request.user,
            post__thread=thread
        ).values_list('post_id', flat=True)
    )

    context = {
        'thread': thread,
        'module': thread.module,
        'top_posts': top_posts,
        'user_voted_ids': user_voted_ids,
        'is_locked': thread.is_locked,
        'participant_count': thread.participant_count,
    }
    return render(request, 'community/thread_detail.html', context)


# ============================================================================
# 3. CREATE POST (AJAX)
# ============================================================================

@login_required
@require_POST
def post_create(request, module_code):
    """
    AJAX endpoint to create a new top-level post.
    URL: /community/<module_code>/post/
    Method: POST
    
    Body (JSON):
        content: str (required, 10-2000 chars)
        source_tab: str (optional, for research tracking)
    
    Returns:
        JSON: {success, post_id, pseudonym, subject, grade, content, created_at, post_count}
    """
    thread = get_object_or_404(
        ForumThread,
        module__code=module_code.upper(),
        is_active=True
    )

    if thread.is_locked:
        return JsonResponse({'success': False, 'error': 'This discussion is locked.'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    content = data.get('content', '').strip()
    source_tab = data.get('source_tab', 'community_page')

    # Validation
    if len(content) < 10:
        return JsonResponse({
            'success': False,
            'error': 'The post must be at least 10 characters long.'
        }, status=400)

    if len(content) > 2000:
        return JsonResponse({
            'success': False,
            'error': 'The post cannot exceed 2000 characters.'
        }, status=400)

    # Valid source_tab values
    valid_tabs = ['introduction', 'main_content', 'activity', 'assessment', 'reflection', 'community_page']
    if source_tab not in valid_tabs:
        source_tab = 'community_page'

    with transaction.atomic():
        post = ForumPost.objects.create(
            thread=thread,
            author=request.user,
            content=content,
            source_tab=source_tab,
        )

    return JsonResponse({
        'success': True,
        'post_id': post.id,
        'pseudonym': post.author_pseudonym,
        'subject': post.author_subject,
        'grade': post.author_grade,
        'context_label': post.author_context_label,
        'content': post.content,
        'created_at': post.created_at.strftime('%d/%m/%Y %H:%M'),
        'post_count': thread.post_count,
        'source_tab': post.source_tab,
    })


# ============================================================================
# 4. REPLY TO POST (AJAX)
# ============================================================================

@login_required
@require_POST
def post_reply(request, post_id):
    """
    AJAX endpoint to reply to an existing post.
    URL: /community/post/<post_id>/reply/
    Method: POST
    
    Body (JSON):
        content: str (required)
    """
    parent = get_object_or_404(ForumPost, id=post_id, is_deleted=False)
    thread = parent.thread

    if thread.is_locked:
        return JsonResponse({'success': False, 'error': 'This discussion is locked.'}, status=403)

    # Don't allow replies to replies (keep it one level deep for UX)
    if parent.parent_post is not None:
        return JsonResponse({
            'success': False,
            'error': 'Replies to replies are not allowed.'
        }, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    content = data.get('content', '').strip()

    if len(content) < 10:
        return JsonResponse({
            'success': False,
            'error': 'The reply must be at least 10 characters long.'
        }, status=400)

    if len(content) > 1000:
        return JsonResponse({
            'success': False,
            'error': 'The reply cannot exceed 1000 characters.'
        }, status=400)

    with transaction.atomic():
        reply = ForumPost.objects.create(
            thread=thread,
            author=request.user,
            content=content,
            parent_post=parent,
            source_tab='community_page',
        )

    return JsonResponse({
        'success': True,
        'reply_id': reply.id,
        'pseudonym': reply.author_pseudonym,
        'context_label': reply.author_context_label,
        'content': reply.content,
        'created_at': reply.created_at.strftime('%d/%m/%Y %H:%M'),
    })


# ============================================================================
# 5. HELPFUL VOTE TOGGLE (AJAX)
# ============================================================================

@login_required
@require_POST
def post_helpful_vote(request, post_id):
    """
    Toggle helpful vote on a post. One vote per user per post.
    URL: /community/post/<post_id>/vote/
    Method: POST
    
    Returns:
        JSON: {success, voted (bool), new_count}
    """
    post = get_object_or_404(ForumPost, id=post_id, is_deleted=False)

    # Can't vote on own post
    if post.author == request.user:
        return JsonResponse({
            'success': False,
            'error': 'You cannot vote for your own post.'
        }, status=400)

    with transaction.atomic():
        vote, created = ForumHelpfulVote.objects.get_or_create(
            post=post,
            user=request.user
        )

        if created:
            # Added vote
            post.helpful_count = ForumHelpfulVote.objects.filter(post=post).count()
            post.save(update_fields=['helpful_count'])
            voted = True
        else:
            # Remove vote (toggle)
            vote.delete()
            post.helpful_count = ForumHelpfulVote.objects.filter(post=post).count()
            post.save(update_fields=['helpful_count'])
            voted = False

    return JsonResponse({
        'success': True,
        'voted': voted,
        'new_count': post.helpful_count,
    })


# ============================================================================
# 6. FORUM PREVIEW PARTIAL (AJAX - for inline tab triggers)
# ============================================================================

@login_required
@require_GET
def forum_preview(request, module_code):
    """
    Returns 3 most recent posts for inline contextual preview within module tabs.
    URL: /community/<module_code>/preview/
    Method: GET
    
    Used by the ambient community triggers in Tab 1, Tab 2, Tab 3, Tab 4.
    Returns minimal HTML partial (not JSON) for easy injection into page.
    """
    try:
        thread = ForumThread.objects.get(
            module__code=module_code.upper(),
            is_active=True
        )
        preview_posts = thread.get_preview_posts(count=3)
        post_count = thread.post_count
        participant_count = thread.participant_count
    except ForumThread.DoesNotExist:
        preview_posts = []
        post_count = 0
        participant_count = 0

    context = {
        'posts': preview_posts,
        'post_count': post_count,
        'participant_count': participant_count,
        'module_code': module_code.upper(),
    }
    return render(request, 'community/partials/forum_preview.html', context)

@login_required
def thread_info(request, module_code):
    """
    Returns forum thread info for a module.
    Used by quick_post_modal.html for dynamic trigger text and seeded questions.
    GET /community/<module_code>/thread-info/
    """
    from apps.modules.models import Module
    module = get_object_or_404(Module, code=module_code)
    thread = ForumThread.objects.filter(module=module).first()
    if thread:
        return JsonResponse({
            'seeded_question':   thread.seeded_question or '',
            'seeded_question_2': thread.seeded_question_2 or '',
            'title':             thread.title,
            'trigger_title':     thread.trigger_title or 'Join the discussion!',
            'trigger_hint':      thread.trigger_hint or 'Share your thoughts with your colleagues.',
            'trigger_example':   thread.trigger_example or '',
        })
    return JsonResponse({
        'seeded_question': '', 'seeded_question_2': '', 'title': '',
        'trigger_title': 'Join the discussion!',
        'trigger_hint': 'Share your thoughts with your colleagues.',
        'trigger_example': '',
    })

