"""
URL routes for the compliance app.
"""

from django.urls import path

from apps.compliance import views


app_name = 'compliance'

urlpatterns = [
    path(
        'onboarding/ai-disclosure/',
        views.ai_disclosure_view,
        name='ai_disclosure',
    ),
    path(
        'about/ai-act-compliance/',
        views.ai_act_compliance_stub_view,
        name='ai_act_compliance',
    ),
]
