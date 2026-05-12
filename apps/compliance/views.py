"""
Compliance views.

Phase C C.2.0:
  - ai_disclosure_view: GET shows modal, POST acknowledges via record_consent
    and stamps TeacherProfile.ai_disclosure_acknowledged_at.
  - ai_act_compliance_stub_view: minimal placeholder for the "Learn more"
    link target. The full AI Impact Assessment (C.1) replaces this view
    later in Phase C.

Phase C C.4 (commit 1):
  - privacy_dashboard_view: GET renders the participant's privacy
    self-service hub.
  - revoke_ai_disclosure_view (POST): closes TD-008. Atomic transaction
    that revokes the ConsentRecord row AND clears
    TeacherProfile.ai_disclosure_acknowledged_at, then logs the user
    out. The next request hits the middleware and re-shows the modal.
  - revoke_research_view (POST): revokes research_participation
    consent. Sets TeacherProfile.research_data_opted_out=True (durable
    opt-out signal for future research analyses). User stays logged
    in; redirect back to /profile/privacy/.
  - revoke_data_sharing_view (POST): revokes data_sharing consent
    only. Does NOT touch research_data_opted_out (narrower scope per
    DATA_SHARING_TEXT_V1_PRE_IRB). User stays logged in.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST

from apps.compliance.copy import (
    AI_DISCLOSURE_HTML_BULLETS_V1_PRE_IRB,
    AI_DISCLOSURE_TEXT_V1_PRE_IRB,
)
from apps.compliance.models import ConsentRecord
from apps.compliance.services import (
    gather_user_export,
    record_consent,
    revoke_consent,
)


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


# ============================================================================
# Phase C C.4 — Privacy dashboard + per-consent revocation endpoints
# ============================================================================


def _consent_state(user, consent_type):
    """Inspect the active ConsentRecord (if any) for (user, consent_type)
    and return a small dict describing the current state for templates.
    """
    active = ConsentRecord.objects.filter(
        user=user, consent_type=consent_type, revoked_at__isnull=True,
    ).order_by('-granted_at').first()
    most_recent = ConsentRecord.objects.filter(
        user=user, consent_type=consent_type,
    ).order_by('-granted_at').first()

    if active and active.granted:
        return {
            'state': 'active',
            'granted_at': active.granted_at,
            'version': active.version,
            'row': active,
        }
    if most_recent and most_recent.revoked_at:
        return {
            'state': 'revoked',
            'granted_at': most_recent.granted_at,
            'revoked_at': most_recent.revoked_at,
            'version': most_recent.version,
            'row': most_recent,
        }
    return {'state': 'never_granted', 'row': None}


@login_required
def privacy_dashboard_view(request):
    """GET /profile/privacy/ — render the participant privacy dashboard.

    Top-level page surfaces:
      - Active / revoked state for each of the three consent types.
      - Summary counts of personal data + AI-generated insights, plus
        a download-as-JSON button (commit 2 of C.4).
      - 'Delete my account' action (commit 3 of C.4).
    """
    snapshot = gather_user_export(request.user)
    ai_outputs = snapshot.get('ai_outputs') or {}
    counts = {
        'ailst': len(snapshot.get('ailst_responses') or []),
        'modules': len(snapshot.get('module_progress') or []),
        'consents': len(snapshot.get('consents') or []),
        'ai_outputs': (
            len(ai_outputs.get('rtm_positions') or [])
            + len(ai_outputs.get('dtp_narratives') or [])
            + len(ai_outputs.get('rag_feedback') or [])
            + len(ai_outputs.get('peer_synthesis') or [])
            + len(ai_outputs.get('rag_queries') or [])
        ),
    }

    return render(request, 'compliance/privacy_dashboard.html', {
        'ai_disclosure_state': _consent_state(request.user, 'ai_disclosure'),
        'research_state': _consent_state(request.user, 'research_participation'),
        'data_sharing_state': _consent_state(request.user, 'data_sharing'),
        'profile': getattr(request.user, 'teacher_profile', None),
        'counts': counts,
        'ai_outputs': ai_outputs,
    })


@login_required
@require_POST
def revoke_ai_disclosure_view(request):
    """POST /profile/privacy/revoke/ai-disclosure/.

    Closes TD-008. Atomic flow:

      1. Revoke the active ConsentRecord row for consent_type='ai_disclosure'.
      2. Clear TeacherProfile.ai_disclosure_acknowledged_at — the
         AIDisclosureMiddleware checks this timestamp, not the
         ConsentRecord state. Without clearing it, the user would still
         pass through the middleware after revoking consent, which is
         contradictory.
      3. Log the user out. The next anonymous request will trip the
         middleware re-acknowledge flow on next login attempt.

    select_for_update on the TeacherProfile row guards against the
    rare race where the user double-clicks the revoke button.
    """
    from apps.users.models import TeacherProfile

    with transaction.atomic():
        profile = TeacherProfile.objects.select_for_update().get(
            user=request.user,
        )
        revoke_consent(user=request.user, consent_type='ai_disclosure')
        profile.ai_disclosure_acknowledged_at = None
        profile.save(update_fields=['ai_disclosure_acknowledged_at'])

    logout(request)
    messages.info(
        request,
        _('AI Disclosure consent withdrawn. You have been logged out. '
          'To use the platform again, please log in and acknowledge the '
          'disclosure.'),
    )
    return redirect('users:landing')


@login_required
@require_POST
def revoke_research_view(request):
    """POST /profile/privacy/revoke/research/.

    Cascade per D9a:
      - Revoke ConsentRecord row for consent_type='research_participation'.
      - M6 signal auto-syncs TeacherProfile.research_consent = False.
      - Set TeacherProfile.research_data_opted_out = True (durable
        opt-out flag for future research analyses; existing data is
        not deleted by this action).
      - User stays logged in; redirect to /profile/privacy/ with flash.

    Future AILST timepoints will be blocked by the C.2.3 AILST entry
    view (it already gates on profile.research_consent). To delete
    already-collected data, the user must use the separate erasure
    action (commit 3 of C.4).
    """
    from apps.users.models import TeacherProfile

    with transaction.atomic():
        profile = TeacherProfile.objects.select_for_update().get(
            user=request.user,
        )
        revoke_consent(user=request.user, consent_type='research_participation')
        profile.research_data_opted_out = True
        profile.save(update_fields=['research_data_opted_out'])

    messages.info(
        request,
        _('Research participation consent withdrawn. We will not include '
          'new data from your activity in research analyses, and the '
          'remaining AI Literacy assessments will be unavailable. Your '
          'existing data remains until you ask us to delete it via the '
          '"Delete my account" option below.'),
    )
    return redirect('compliance:privacy_dashboard')


@login_required
def export_data_view(request):
    """GET /profile/privacy/export/ — GDPR Art. 15 JSON download.

    Builds the full personal-data snapshot via
    apps.compliance.services.gather_user_export and serves it as a
    file attachment. Synchronous (the snapshot is small even for
    completed participants — single-digit kilobytes typically). The
    export includes data even when `research_data_opted_out=True`
    because Art. 15 is a personal right that does not depend on
    research participation.
    """
    import json

    from django.http import HttpResponse

    payload = gather_user_export(request.user)
    body = json.dumps(payload, indent=2, ensure_ascii=False, default=str)

    filename = 'proodos_export_{username}_{date}.json'.format(
        username=request.user.username or 'user',
        date=timezone.now().strftime('%Y%m%d'),
    )
    response = HttpResponse(body, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


@login_required
@require_POST
def revoke_data_sharing_view(request):
    """POST /profile/privacy/revoke/data-sharing/.

    Per D9b: data_sharing is the OPTIONAL secondary consent
    (DATA_SHARING_TEXT_V1_PRE_IRB). Revoking it:
      - Marks the ConsentRecord row revoked.
      - M6 signal auto-syncs TeacherProfile.consent_data_sharing = False.
      - Does NOT touch research_data_opted_out (narrower scope).
      - Does NOT affect AILST gating or platform access.
      - User stays logged in.
    """
    revoke_consent(user=request.user, consent_type='data_sharing')

    messages.info(
        request,
        _('Data sharing consent withdrawn. We will not share your data '
          'with affiliated researchers beyond the primary study. Your '
          'participation in the research itself is unaffected.'),
    )
    return redirect('compliance:privacy_dashboard')
