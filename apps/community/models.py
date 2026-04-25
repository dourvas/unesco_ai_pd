"""
apps/community/models.py
========================
Forum & Community models for PROODOS EduAI Platform.

Architecture: Ambient Community Layer
- ForumThread: One per module (created automatically when module is published)
- ForumPost: User posts + nested replies (via parent_post_id)
- ForumHelpfulVote: Upvoting system (one per user per post)

Design Principles:
- approved by default (no moderation queue)
- pseudonym display (GDPR-friendly)
- subject_area + grade_level context shown alongside posts
- supports seeded questions (is_seeded flag)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ForumThread(models.Model):
    """
    One discussion thread per module.
    Created automatically when a module is published (via signal or management command).
    
    Each thread has a 'seeded_question' - the prompt that starts the discussion,
    set by the researcher to guide community engagement.
    """

    # Link to module
    module = models.OneToOneField(
        'modules.Module',
        on_delete=models.CASCADE,
        related_name='forum_thread',
        verbose_name='Module'
    )

    # Thread metadata
    title = models.CharField(
        max_length=200,
        verbose_name='Thread Title',
        help_text='Auto-generated from module title, e.g. "Discussion: Understanding AI in Education"'
    )

    # The researcher-seeded opening question(s)
    seeded_question = models.TextField(
        verbose_name='Seeded Question',
        help_text='The discussion prompt set by the researcher to kickstart community engagement.',
        blank=True
    )

    # Secondary seeded question (optional - for richer discussion)
    seeded_question_2 = models.TextField(
        verbose_name='Secondary Seeded Question',
        blank=True,
        help_text='Optional second prompt for deeper discussion.'
    )

    trigger_title   = models.CharField(max_length=200, default='Join the discussion!')
    trigger_hint    = models.TextField(default='Share your thoughts with your colleagues.')
    trigger_example = models.TextField(blank=True, default='')

    # Status
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_locked = models.BooleanField(
        default=False,
        verbose_name='Locked',
        help_text='Locked threads prevent new posts (use for completed cohorts)'
    )

    # Denormalized counters (updated via signal for performance)
    post_count = models.PositiveIntegerField(default=0, verbose_name='Post Count')
    last_activity_at = models.DateTimeField(null=True, blank=True, verbose_name='Last Activity')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Forum Thread'
        verbose_name_plural = 'Forum Threads'
        ordering = ['module__order_index']

    def __str__(self):
        return f"Forum: {self.module.code} - {self.title}"

    @property
    def participant_count(self):
        """Unique users who posted in this thread."""
        return self.posts.filter(
            is_deleted=False
        ).values('author').distinct().count()

    def get_preview_posts(self, count=3):
        """
        Returns the most recent approved top-level posts for inline preview.
        Used in the contextual triggers within module tabs.
        """
        return self.posts.filter(
            parent_post=None,
            is_deleted=False,
            is_seeded=False  # Don't show seeded posts in preview
        ).select_related(
            'author',
            ).order_by('-created_at')[:count]

    def update_counters(self):
        """Recalculate denormalized counters. Called after post save/delete."""
        self.post_count = self.posts.filter(is_deleted=False, is_seeded=False).count()
        latest = self.posts.filter(is_deleted=False).order_by('-created_at').first()
        self.last_activity_at = latest.created_at if latest else None
        self.save(update_fields=['post_count', 'last_activity_at'])


class ForumPost(models.Model):
    """
    A post within a ForumThread.
    Supports nested replies via parent_post (one level deep recommended for UX).
    
    Key features:
    - pseudonym shown (not real name) for GDPR compliance
    - subject_area + grade_level context shown for community dynamics
    - is_seeded flag for researcher-planted questions
    - approved by default (no moderation overhead for pilot)
    """

    # Thread this post belongs to
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Thread'
    )

    # Author (Django auth user)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='forum_posts',
        verbose_name='Author'
    )

    # Cached profile data for display (avoids JOIN on every render)
    author_pseudonym = models.CharField(
        max_length=100,
        verbose_name='Author Pseudonym',
        help_text='Snapshot of pseudonym at time of posting (GDPR-safe display name)'
    )
    author_subject = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Author Subject Area',
        help_text='Snapshot of subject_area at time of posting'
    )
    author_grade = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Author Grade Level',
        help_text='Snapshot of grade_level at time of posting'
    )

    # Content
    content = models.TextField(verbose_name='Content')

    # Nesting (one level recommended: post -> reply)
    parent_post = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Parent Post'
    )

    # Special flags
    is_seeded = models.BooleanField(
        default=False,
        verbose_name='Seeded by Researcher',
        help_text='Researcher-planted post to kickstart discussion. Shown with special styling.'
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name='Pinned',
        help_text='Pinned posts appear at the top of the thread'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Deleted',
        help_text='Soft delete - content hidden but record preserved for research integrity'
    )

    # Helpful votes (denormalized for performance)
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Helpful Votes')

    # Which module tab triggered this post (research data)
    source_tab = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Source Tab',
        help_text='Which tab the user clicked "Post to Forum" from',
        choices=[
            ('introduction', 'Tab 1 - Introduction'),
            ('main_content', 'Tab 2 - Main Content'),
            ('activity', 'Tab 3 - Activity'),
            ('assessment', 'Tab 4 - Assessment'),
            ('reflection', 'Tab 5 - Reflection'),
            ('community_page', 'Community Page'),
        ]
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Forum Post'
        verbose_name_plural = 'Forum Posts'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['thread', '-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['parent_post']),
            models.Index(fields=['is_seeded']),
        ]

    def __str__(self):
        return f"Post by {self.author_pseudonym} in {self.thread.module.code} ({self.created_at.strftime('%d/%m/%Y')})"

    @property
    def is_reply(self):
        return self.parent_post is not None

    @property
    def display_content(self):
        """Returns content or '[This post has been deleted]' if deleted."""
        if self.is_deleted:
            return '[This post has been deleted]'
        return self.content

    @property
    def author_context_label(self):
        """
        Returns a display string like 'Mathematics | Secondary School'
        Used in post header for community context awareness.
        """
        parts = []
        if self.author_subject:
            parts.append(self.author_subject)
        if self.author_grade:
            parts.append(self.author_grade)
        return ' · '.join(parts)

    def save(self, *args, **kwargs):
        """Auto-populate author context from TeacherProfile on first save."""
        if not self.pk and self.author:
            try:
                profile = self.author.teacherprofile
                if not self.author_pseudonym:
                    self.author_pseudonym = profile.pseudonym or f"Educator_{self.author.id}"
                if not self.author_subject:
                    self.author_subject = profile.subject_area or ''
                if not self.author_grade:
                    self.author_grade = profile.grade_level or ''
            except Exception:
                if not self.author_pseudonym:
                    self.author_pseudonym = f"Educator_{self.author.id}"
        super().save(*args, **kwargs)
        # Update thread counters
        self.thread.update_counters()


class ForumHelpfulVote(models.Model):
    """
    Upvote system: one vote per user per post.
    Toggle behavior: voting again removes the vote.
    
    Research value: tracks which posts resonate across subjects/grades.
    """

    post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name='Post'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_votes',
        verbose_name='User'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Helpful Vote'
        verbose_name_plural = 'Helpful Votes'
        unique_together = [('post', 'user')]  # One vote per user per post
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user} → Post #{self.post.id}"