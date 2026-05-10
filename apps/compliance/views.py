"""
Compliance views.

Phase C C.2.0:
  - ai_disclosure_view: GET shows modal, POST acknowledges via record_consent
    and stamps TeacherProfile.ai_disclosure_acknowledged_at.
  - ai_act_compliance_stub_view: minimal placeholder for the "Learn more"
    link target. The full AI Impact Assessment (C.1) replaces this view
    later in Phase C.
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.compliance.copy import (
    AI_DISCLOSURE_HTML_BULLETS_V1_PRE_IRB,
    AI_DISCLOSURE_TEXT_V1_PRE_IRB,
)
from apps.compliance.services import record_consent


def _client_ip(request):
    """Best-effort client IP. May be auto-redacted after 30 days."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _safe_next(next_url, fallback='/dashboard/'):
    """Open-redirect protection: only accept same-origin path-style URLs."""
    if not next_url or not next_url.startswith('/') or next_url.startswith('//'):
        return fallback
    return next_url


@login_required
@require_http_methods(['GET', 'POST'])
def ai_disclosure_view(request):
    next_url = _safe_next(request.GET.get('next'))

    if request.method == 'POST':
        # Late import to avoid circular dependency at app load time.
        from apps.users.models import TeacherProfile

        record_consent(
            user=request.user,
            consent_type='ai_disclosure',
            consent_text=AI_DISCLOSURE_TEXT_V1_PRE_IRB,
            version=settings.AI_DISCLOSURE_CURRENT_VERSION,
            ip_address=_client_ip(request),
        )
        # Ensure profile exists so middleware sees the timestamp on next req.
        profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
        profile.ai_disclosure_acknowledged_at = timezone.now()
        profile.save(update_fields=['ai_disclosure_acknowledged_at'])
        return redirect(_safe_next(request.POST.get('next') or next_url))

    return render(request, 'onboarding/ai_disclosure.html', {
        'next_url': next_url,
        'disclosure_html_bullets': AI_DISCLOSURE_HTML_BULLETS_V1_PRE_IRB,
        'disclosure_version': settings.AI_DISCLOSURE_CURRENT_VERSION,
    })


def ai_act_compliance_stub_view(request):
    """Placeholder for /about/ai-act-compliance/ until C.1 ships the full
    AI Impact Assessment page. Public; no auth required.
    """
    return render(request, 'about/ai_act_compliance_stub.html')
