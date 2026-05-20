"""
URL configuration for the researcher-facing analytics app.

One staff-only dashboard page hosts every Phase D analytic — currently
the D.1 AI Output Relevance Profile and the D.2 Engagement Depth
sections.
"""

from django.urls import path

from apps.analytics import views


app_name = 'analytics'

urlpatterns = [
    path('', views.research_analytics_view, name='dashboard'),
]
