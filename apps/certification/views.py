"""
Views for the certification app — Phase H.3 part 2.

Two surfaces:

  - certificate_download_view (GET, login_required): issues the
    certificate on first call (idempotent get_or_issue), renders the
    bilingual PDF, returns it as an attachment.

  - certificate_verify_view (GET, public): given a verification code,
    returns the holder's name + issue date + 15-module summary so
    third parties (employers, postgraduate admissions panels) can
    confirm authenticity. No AILST scores, no factor breakdowns.

Design proposal:
  proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md
  §5.4 (eligibility gate), §5.6 (public verification scope).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.certification.models import CertificateOfAttendance
from apps.certification.services import (
    get_or_issue_certificate,
    render_certificate_pdf,
    teacher_is_eligible,
)


@login_required
def certificate_download_view(request):
    """GET /certification/download/.

    Issues the certificate on first call (frozen snapshot), then
    re-renders the PDF from the issued row. Subsequent calls re-use
    the same row + the same verification code — the PDF bytes may
    vary if `pdf_metadata_version` has been bumped (e.g. when the
    final Greek translation lands per Path A), but the row identity
    is stable.

    Eligibility: AilstResponse.completed_at__isnull=False for T2.
    Ineligible users are redirected to the dashboard with a flash
    message rather than a 403 — the gate is pedagogically framed
    ("complete the closing AILST first"), not a hostile access denial.
    """
    if not teacher_is_eligible(request.user):
        messages.info(
            request,
            'Your Certificate of Attendance will be available after you '
            'complete the closing AILST measurement.',
        )
        return redirect('/dashboard/')

    certificate = get_or_issue_certificate(request.user)

    try:
        pdf_bytes, filename = render_certificate_pdf(certificate)
    except RuntimeError:
        # xhtml2pdf pisa errors — surface as a soft failure rather than
        # 500. The certificate row is already issued and stable; the
        # user can retry the download once the template issue is fixed.
        messages.error(
            request,
            'The certificate PDF could not be rendered right now. '
            'Please try again shortly; the research team has been notified.',
        )
        return redirect('/dashboard/')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def certificate_verify_view(request, code):
    """GET /certification/verify/<code>/.

    Public verification surface (no login required). The 16-char
    verification code is high-entropy (~96 bits) and not enumerable;
    reaching this URL implies the verifier holds the certificate PDF
    or has been given the code by the holder. The endpoint discloses:

      - The holder's display name
      - The date of issuance
      - The list of 15 modules with UNESCO aspect/level tags

    The endpoint does NOT disclose AILST scores, factor breakdowns,
    or any other research data. The disclosure scope is recorded on
    the rendered page so the verifier understands what they are
    looking at.

    404 if the code does not correspond to an issued certificate —
    no information leak about whether a code was "almost right".
    """
    certificate = get_object_or_404(
        CertificateOfAttendance, verification_code=code,
    )
    return render(request, 'certification/verify.html', {
        'certificate': certificate,
        'teacher_display': certificate.teacher_display,
        'issued_at': certificate.issued_at,
        'modules': certificate.modules_summary,
        'verification_code': certificate.verification_code,
    })
