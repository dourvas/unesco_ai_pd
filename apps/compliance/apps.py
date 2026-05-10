from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    name = 'apps.compliance'

    def ready(self):
        # Register signal handlers (sync_teacher_profile_booleans).
        from . import signals  # noqa: F401
