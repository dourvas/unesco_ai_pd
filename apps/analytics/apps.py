from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Phase D analytics layer — researcher-facing, read-only.

    Home for the staff-only analytic views over data the platform
    already collects: D.1 (AI Output Relevance Profile) and, later,
    D.2 (Position Confirmation Analytics). The app owns no models — it
    only aggregates and displays.
    """

    name = 'apps.analytics'
