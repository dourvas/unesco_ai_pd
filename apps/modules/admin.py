from django.contrib import admin
from .models import Module, ModuleContent, UserModuleProgress
# apps/modules/admin.py
from .models import Tab3PromptLibrary, Tab3UserActivity, Tab3UserToolkit

admin.site.register(Tab3PromptLibrary)
admin.site.register(Tab3UserActivity)
admin.site.register(Tab3UserToolkit)


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
