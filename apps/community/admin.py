"""
apps/community/admin.py
=======================
Django admin configuration for the Community (Forum) app.
Provides researcher-friendly interface for:
- Managing forum threads per module
- Seeding discussion questions
- Monitoring community engagement
- Reviewing posts (soft-delete capability)
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ForumThread, ForumPost, ForumHelpfulVote


class ForumPostInline(admin.TabularInline):
    """Show top-level posts inline within ForumThread admin."""
    model = ForumPost
    fields = ['author_pseudonym', 'author_subject', 'author_grade', 'content', 'is_seeded', 'is_pinned', 'helpful_count', 'created_at']
    readonly_fields = ['author_pseudonym', 'author_subject', 'author_grade', 'helpful_count', 'created_at']
    extra = 0
    show_change_link = True

    def get_queryset(self, request):
        # Only show top-level posts (no replies) in inline
        return super().get_queryset(request).filter(parent_post=None)


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    """
    Forum Thread admin - researcher's primary interface.
    Key actions: set seeded questions, monitor engagement.
    """
    list_display = [
        'module_code', 'title', 'post_count', 'participant_count_display',
        'last_activity_at', 'is_active', 'is_locked'
    ]
    list_filter = ['is_active', 'is_locked', 'module__proficiency_level']
    search_fields = ['title', 'module__code', 'module__title']
    readonly_fields = ['post_count', 'last_activity_at', 'created_at', 'updated_at', 'participant_count_display']

    fieldsets = (
        ('Module Link', {
            'fields': ('module', 'title')
        }),
        ('Seeded Questions (Researcher)', {
            'fields': ('seeded_question', 'seeded_question_2'),
            'description': 'These questions are planted by the researcher to kickstart discussion. '
                           'They appear with a special "Researcher Question" badge.'
        }),
        ('Status', {
            'fields': ('is_active', 'is_locked')
        }),
        ('Statistics (Read-only)', {
            'fields': ('post_count', 'participant_count_display', 'last_activity_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ForumPostInline]

    def module_code(self, obj):
        return format_html('<strong>{}</strong>', obj.module.code)
    module_code.short_description = 'Module'

    def participant_count_display(self, obj):
        return obj.participant_count
    participant_count_display.short_description = 'Participants'

    actions = ['seed_m1_questions']

    def seed_m1_questions(self, request, queryset):
        """Quick action to seed M1 with default questions."""
        for thread in queryset:
            if thread.module.code == 'M1' and not thread.seeded_question:
                thread.seeded_question = (
                    "How do you feel about integrating AI into your teaching? "
                    "What inspires you and what concerns you?"
                )
                thread.seeded_question_2 = (
                    "Have you already used an AI tool in your classroom? "
                    "Share an experience — positive or negative!"
                )
                thread.save()
        self.message_user(request, "Seeded questions added to selected M1 threads.")
    seed_m1_questions.short_description = "🌱 Seed M1 discussion questions"


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """
    Forum Post admin - for monitoring and research data review.
    """
    list_display = [
        'id', 'thread_module', 'author_pseudonym', 'author_subject',
        'source_tab', 'is_seeded', 'is_pinned', 'helpful_count',
        'is_deleted', 'created_at'
    ]
    list_filter = [
        'is_seeded', 'is_pinned', 'is_deleted',
        'source_tab', 'author_subject', 'author_grade',
        'thread__module__code'
    ]
    search_fields = ['content', 'author_pseudonym', 'author_subject']
    readonly_fields = ['author_pseudonym', 'author_subject', 'author_grade', 'helpful_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Post', {
            'fields': ('thread', 'author', 'parent_post', 'content')
        }),
        ('Author Context (Auto-populated)', {
            'fields': ('author_pseudonym', 'author_subject', 'author_grade'),
            'classes': ('collapse',)
        }),
        ('Flags', {
            'fields': ('is_seeded', 'is_pinned', 'is_deleted', 'source_tab')
        }),
        ('Stats', {
            'fields': ('helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thread_module(self, obj):
        return obj.thread.module.code
    thread_module.short_description = 'Module'

    actions = ['soft_delete_posts', 'restore_posts', 'mark_as_seeded']

    def soft_delete_posts(self, request, queryset):
        queryset.update(is_deleted=True)
        self.message_user(request, f"{queryset.count()} posts soft-deleted.")
    soft_delete_posts.short_description = "🗑️ Soft-delete selected posts"

    def restore_posts(self, request, queryset):
        queryset.update(is_deleted=False)
        self.message_user(request, f"{queryset.count()} posts restored.")
    restore_posts.short_description = "♻️ Restore selected posts"

    def mark_as_seeded(self, request, queryset):
        queryset.update(is_seeded=True)
        self.message_user(request, f"{queryset.count()} posts marked as seeded.")
    mark_as_seeded.short_description = "🌱 Mark as seeded (researcher) post"


@admin.register(ForumHelpfulVote)
class ForumHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['post', 'user', 'created_at']