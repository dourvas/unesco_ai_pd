"""
Admin Interface for User Management
"""

from django.contrib import admin
from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin interface for Teacher Profiles"""
    
    list_display = [
        'user',
        'subject_area',
        'grade_level',
        'ai_experience',
        'profile_completed',
        'created_at'
    ]
    
    list_filter = [
        'subject_area',
        'grade_level',
        'ai_experience',
        'profile_completed',
        'profile_skipped',
        'research_consent'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'subject_area',
        'notes'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_profile_update',
        'completion_percentage',
        'profile_summary'
    ]
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Teaching Context', {
            'fields': (
                'subject_area',
                'subject_area_other',
                'grade_level',
                'teaching_years',
                'school_location',
                'average_class_size'
            )
        }),
        ('AI Experience', {
            'fields': (
                'ai_experience',
                'ai_tools_used',
                'ai_teaching_integration'
            )
        }),
        ('Goals & Preferences', {
            'fields': (
                'primary_goals',
                'preferred_communication_style'
            )
        }),
        ('Status', {
            'fields': (
                'profile_completed',
                'profile_completion_date',
                'profile_skipped',
                'completion_percentage',
                'profile_summary'
            )
        }),
        ('Research', {
            'fields': (
                'research_consent',
                'contact_for_research',
                'consent_data_sharing',
                'consent_timestamp'
            )
        }),
        ('Demographics (Optional)', {
            'fields': (
                'age_range',
                'gender',
                'language_primary'
            ),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'last_profile_update'
            ),
            'classes': ('collapse',)
        })
    )