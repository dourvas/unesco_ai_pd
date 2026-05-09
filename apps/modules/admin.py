from django.contrib import admin
from django.utils import timezone
from .models import Module, ModuleContent, UserModuleProgress
# apps/modules/admin.py
from .models import Tab3PromptLibrary, Tab3UserActivity, Tab3UserToolkit, Tab3RepositorySubmission

admin.site.register(Tab3PromptLibrary)
admin.site.register(Tab3UserActivity)
admin.site.register(Tab3UserToolkit)


# ============================================================
# Phase A Tier 2 Step 4 — Tab3RepositorySubmission admin
# Phase A Tier 3 (D5+D6): admin curation actions DISABLED.
# Submissions go straight to the M13 Practice Workshop (peer_blog).
# Schema preserved (per D6) for research observation. Reactive
# moderation lives on BlogPost (apps.peer_blog) per
# REACTIVE_MODERATION_POLICY.md.
# ============================================================
@admin.register(Tab3RepositorySubmission)
class Tab3RepositorySubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'module', 'subject_area', 'grade_level',
        'review_status', 'submitted_at', 'reviewed_at',
    )
    list_filter = ('review_status', 'module', 'subject_area', 'grade_level', 'submitted_at')
    search_fields = ('title', 'summary', 'user__email', 'user__username')
    # Tier 3: review_status now read-only in admin too — no curation in Tier 3.
    readonly_fields = (
        'submitted_at', 'canvas_data', 'user', 'module', 'challenge_id',
        'review_status', 'reviewer_notes', 'reviewed_by', 'reviewed_at',
    )
    fieldsets = (
        ('Submission', {
            'fields': (
                'user', 'module', 'challenge_id',
                'title', 'summary',
                'subject_area', 'grade_level', 'contact_email',
                'canvas_data',
            )
        }),
        ('Status (research observation only)', {
            'fields': (
                'review_status', 'reviewer_notes',
                'reviewed_by', 'submitted_at', 'reviewed_at',
            ),
            'description': (
                "Tier 3: admin curation disabled. New submissions are auto-set "
                "to 'community_shared' and surface immediately in the M13 Practice "
                "Workshop. Legacy 'pending' rows from Tier 2 retained for research."
            ),
        }),
    )
    # Tier 3 (D5+D6): curation actions removed from the admin UI.
    actions = []

    # Curation methods preserved (commented out) — reinstate if peer-review evolution
    # path (Tier 3 future evolution notes / Level 1 reviewer role) is taken up.
    # def approve_selected(self, request, queryset):
    #     n = queryset.update(
    #         review_status='approved',
    #         reviewed_by=request.user,
    #         reviewed_at=timezone.now(),
    #     )
    #     self.message_user(request, f"Approved {n} submission(s).")
    # approve_selected.short_description = "Approve selected submissions"
    #
    # def reject_selected(self, request, queryset):
    #     n = queryset.update(
    #         review_status='rejected',
    #         reviewed_by=request.user,
    #         reviewed_at=timezone.now(),
    #     )
    #     self.message_user(request, f"Rejected {n} submission(s).")
    # reject_selected.short_description = "Reject selected submissions"
    #
    # def request_revision(self, request, queryset):
    #     n = queryset.update(
    #         review_status='needs_revision',
    #         reviewed_by=request.user,
    #         reviewed_at=timezone.now(),
    #     )
    #     self.message_user(request, f"Marked {n} submission(s) as needing revision.")
    # request_revision.short_description = "Request revisions on selected"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'unesco_aspect', 'proficiency_level', 'order_index', 'is_published')
    list_filter = ('unesco_aspect', 'proficiency_level', 'is_published')
    search_fields = ('code', 'title', 'description')
    ordering = ('order_index',)
    
    fieldsets = (
        ('Identity', {
            'fields': ('code', 'title', 'description')
        }),
        ('UNESCO Alignment', {
            'fields': ('unesco_aspect', 'proficiency_level', 'order_index')
        }),
        ('Tab 1 Content', {
            'fields': ('hero_image_url', 'learning_objectives', 'module_overview', 'prerequisites')
        }),
        ('Settings', {
            'fields': ('estimated_hours', 'is_published')
        }),
    )


@admin.register(ModuleContent)
class ModuleContentAdmin(admin.ModelAdmin):
    list_display = ('module', 'content_type', 'subject_area', 'grade_level', 'updated_at')
    list_filter = ('content_type', 'subject_area', 'grade_level', 'module')
    search_fields = ('content_data',)
    ordering = ('module__order_index', 'content_type')
    
    fieldsets = (
        ('Module', {
            'fields': ('module', 'content_type')
        }),
        ('Personalization', {
            'fields': ('subject_area', 'grade_level')
        }),
        ('Content', {
            'fields': ('content_data', 'metadata')
        }),
    )


@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'status', 'completion_percentage', 'last_accessed_at')
    list_filter = ('status', 'module')
    search_fields = ('user__username', 'module__code')
    ordering = ('-last_accessed_at',)
    
    readonly_fields = ('enrolled_at', 'started_at', 'completed_at', 'last_accessed_at',
                      'introduction_completed_at', 'main_content_completed_at',
                      'activity_completed_at', 'assessment_completed_at', 'reflection_completed_at')
    
    fieldsets = (
        ('User & Module', {
            'fields': ('user', 'module', 'status')
        }),
        ('Progress', {
            'fields': ('completion_percentage',)
        }),
        ('Tab Completion', {
            'fields': (
                ('introduction_completed', 'introduction_completed_at'),
                ('main_content_completed', 'main_content_completed_at'),
                ('activity_completed', 'activity_completed_at'),
                ('assessment_completed', 'assessment_completed_at'),
                ('reflection_completed', 'reflection_completed_at'),
            )
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'started_at', 'completed_at', 'last_accessed_at')
        }),
    )
