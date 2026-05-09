from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'apps.users'

    def ready(self):
        # Wire up Phase C M3 change-tracking signals.
        from . import signals  # noqa: F401
