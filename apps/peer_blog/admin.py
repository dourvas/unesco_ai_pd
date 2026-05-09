"""
Practice Workshop admin — research observation + reactive moderation.

Hide actions implement the 4 hide-trigger criteria documented in
REACTIVE_MODERATION_POLICY.md.
"""

from django.contrib import admin

from .models import BlogComment, BlogPost, BlogThumbsUp


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author_pseudonym',
        'module',
        'subject_area',
        'grade_level',
        'thumbs_up_count',
        'comments_count',
        'is_hidden',
        'created_at',
    )
    list_filter = (
        'module',
        'subject_area',
        'grade_level',
        'is_hidden',
        'hidden_reason',
    )
    search_fields = ('title', 'body', 'author_pseudonym')
    readonly_fields = (
        'user',
        'module',
        'artefact_type',
        'artefact_id',
        'thumbs_up_count',
        'comments_count',
        'created_at',
        'updated_at',
    )
    actions = ['hide_selected', 'unhide_selected']

    def hide_selected(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(
            request,
            f"{updated} post(s) hidden. Set hidden_reason manually per policy.",
        )

    hide_selected.short_description = "Hide selected (set reason manually)"

    def unhide_selected(self, request, queryset):
        updated = queryset.update(is_hidden=False, hidden_reason=None)
        self.message_user(request, f"{updated} post(s) unhidden.")

    unhide_selected.short_description = "Unhide selected"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author_pseudonym',
        'thumbs_up_count',
        'is_hidden',
        'created_at',
    )
    list_filter = ('is_hidden',)
    search_fields = ('body', 'author_pseudonym')
    actions = ['hide_selected', 'unhide_selected']

    def hide_selected(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"{updated} comment(s) hidden.")

    def unhide_selected(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"{updated} comment(s) unhidden.")


@admin.register(BlogThumbsUp)
class BlogThumbsUpAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('user', 'post', 'comment', 'created_at')
