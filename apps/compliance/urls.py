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
    # Phase C C.4 — Privacy dashboard + per-consent revocation endpoints.
    path(
        'profile/privacy/',
        views.privacy_dashboard_view,
        name='privacy_dashboard',
    ),
    path(
        'profile/privacy/revoke/ai-disclosure/',
        views.revoke_ai_disclosure_view,
        name='revoke_ai_disclosure',
    ),
    path(
        'profile/privacy/revoke/research/',
        views.revoke_research_view,
        name='revoke_research',
    ),
    path(
        'profile/privacy/revoke/data-sharing/',
        views.revoke_data_sharing_view,
        name='revoke_data_sharing',
    ),
    # Phase H H.6 — Optional follow-up recruitment consent revoke.
    path(
        'profile/privacy/revoke/followup-recruitment/',
        views.revoke_followup_recruitment_view,
        name='revoke_followup_recruitment',
    ),
    path(
        'profile/privacy/export/',
        views.export_data_view,
        name='export_data',
    ),
    path(
        'profile/privacy/erase/',
        views.erasure_confirm_view,
        name='erasure_confirm',
    ),
    path(
        'profile/privacy/erase/confirm/',
        views.erasure_execute_view,
        name='erasure_execute',
    ),
]
