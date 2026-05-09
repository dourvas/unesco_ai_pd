"""
Practice Workshop (peer_blog) models.

Technical schema names use 'BlogPost', 'BlogComment', 'BlogThumbsUp'
for clean DB naming. UI labels are "Practice Workshop", "Workshop posts",
"Workshop comments" (Tier 3 Gemini revision D12).

Comments are FLAT (D14) — no parent_comment FK.
"""

from django.conf import settings
from django.db import models

from apps.modules.models import Module


class BlogPost(models.Model):
    """A peer-dialogue post anchored to a specific user artefact."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    artefact_type = models.CharField(
        max_length=50,
        help_text="Artefact type identifier: 'm13_workflow', 'm9_lesson', 'm14_gamified_unit'.",
    )
    artefact_id = models.IntegerField(
        help_text="ID of the artefact in its source table (Tab3RepositorySubmission, Tab3UserActivity, etc.).",
    )

    title = models.CharField(max_length=200)
    body = models.TextField(help_text="The artefact summary or description shown to peers.")

    # Author context snapshot at post time (immutable for research integrity)
    author_pseudonym = models.CharField(max_length=50)
    subject_area = models.CharField(max_length=50, db_index=True)
    grade_level = models.CharField(max_length=20)

    thumbs_up_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    is_hidden = models.BooleanField(
        default=False,
        help_text="Researcher reactive moderation flag. Hidden posts don't appear in feeds.",
    )
    HIDDEN_REASON_CHOICES = [
        # Researcher reactive moderation (REACTIVE_MODERATION_POLICY.md)
        ('safety_violation', 'Platform safety violation'),
        ('off_topic_spam', 'Off-topic / spam'),
        ('contains_pii', 'Contains real student PII'),
        ('copyright_violation', 'Copyright violation'),
        # Author self-service (Tier 3 Step 3.5)
        ('author_withdrawn', 'Withdrawn by author'),
    ]

    hidden_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HIDDEN_REASON_CHOICES,
        help_text="If hidden, the policy category or author action triggering the action.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['module', 'subject_area', '-created_at'],
                name='blog_module_subject_idx',
            ),
            models.Index(
                fields=['module', '-thumbs_up_count'],
                name='blog_module_thumbs_idx',
            ),
            models.Index(
                fields=['artefact_type', 'artefact_id'],
                name='blog_artefact_idx',
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.author_pseudonym} ({self.subject_area})"


class BlogComment(models.Model):
    """A flat comment on a BlogPost. No nesting (D14 — pilot scale doesn't need it)."""

    HIDDEN_REASON_CHOICES = [
        ('safety_violation', 'Platform safety violation'),
        ('off_topic_spam', 'Off-topic / spam'),
        ('contains_pii', 'Contains real student PII'),
        ('copyright_violation', 'Copyright violation'),
        ('author_deleted', 'Deleted by author'),
    ]

    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    body = models.TextField()
    author_pseudonym = models.CharField(max_length=50)
    subject_area = models.CharField(max_length=50)

    thumbs_up_count = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    hidden_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HIDDEN_REASON_CHOICES,
        help_text="If hidden, the policy category or author action triggering the action.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author_pseudonym} on post #{self.post_id}"


class BlogThumbsUp(models.Model):
    """Single-action thumbs-up. One per user per post or comment (XOR)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(
        BlogPost, null=True, blank=True, on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        BlogComment, null=True, blank=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_user_post_thumbs_up',
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_user_comment_thumbs_up',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(post__isnull=False, comment__isnull=True)
                    | models.Q(post__isnull=True, comment__isnull=False)
                ),
                name='thumbs_up_post_xor_comment',
            ),
        ]
