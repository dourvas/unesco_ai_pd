from django.contrib import admin

from apps.certification.models import CertificateOfAttendance


@admin.register(CertificateOfAttendance)
class CertificateOfAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'teacher_display', 'issued_at', 'verification_code',
        'instrument_version_t2', 'pdf_metadata_version',
    )
    list_filter = ('instrument_version_t2', 'pdf_metadata_version')
    search_fields = ('teacher_display', 'verification_code', 'user__username')
    readonly_fields = (
        'issued_at', 'verification_code', 'teacher_display',
        'modules_summary', 'instrument_version_t2',
    )
    # pdf_metadata_version stays editable — admins can bump it manually
    # if a template re-render under a new version is needed.
