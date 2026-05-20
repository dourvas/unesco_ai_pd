"""
URL configuration for the researcher-facing analytics app.

D.1 contributes one route; D.2 (Position Confirmation Analytics) will
add its own here later.
"""

from django.urls import path

from apps.analytics import views


app_name = 'analytics'

urlpatterns = [
    path(
        'ai-relevance/',
        views.ai_relevance_profile_view,
        name='ai_relevance_profile',
    ),
]
