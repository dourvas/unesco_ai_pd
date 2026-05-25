"""
Services for apps.certification — Phase H.3 part 2.

Eligibility, issuance, and PDF rendering for the Certificate of
Attendance. The teacher-facing download view is a thin wrapper around
`get_or_issue_certificate(user)` + `render_certificate_pdf(certificate)`.

Design proposal:
  proodos_files/PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md
  §5 (Certificate of Attendance).

Article 50(2) machinery preserved from the dormant
`apps/epilogue/views.py::_generate_portrait_pdf` helper (Phase G
closure §3.3): JSON-LD body block + PDF document metadata via
`<meta>` tags read by xhtml2pdf. The certificate is NOT an AI
artefact (no LLM call generates any part of it); the JSON-LD body
therefore asserts `aiInvolved: false` with a `programmeUsesAI: true`
companion key pointing to the AI Impact Assessment URL.
"""

import io

from django.template.loader import render_to_string

from apps.certification.models import (
    CertificateOfAttendance,
    generate_verification_code,
)


# ----------------------------------------------------------------------
# Eligibility
# ----------------------------------------------------------------------

def teacher_is_eligible(user) -> bool:
    """Has the user completed the closing AILST administration (T2)?

    Uses `completed_at__isnull=False` rather than a generic submission
    timestamp: per AilstResponse model docstring
    (apps/ailst/models.py:113-115), `completed_at` is set only when
    `responses` has all 36 paper_code keys and the derived scores are
    filled. So this gate already guarantees a complete T2, not a
    partial submission. No `is_complete` flag needed.
    """
    from apps.ailst.models import AilstResponse

    return AilstResponse.objects.filter(
        user=user,
        timepoint='T2',
        completed_at__isnull=False,
    ).exists()


# ----------------------------------------------------------------------
# Frozen-state builders
# ----------------------------------------------------------------------

def build_modules_summary() -> list:
    """Snapshot the 15-module catalogue at issuance time.

    Returned shape (frozen onto CertificateOfAttendance.modules_summary):

        [
            {"code": "M1", "title": "...",
             "aspect": "Human-Centred Mindset", "level": "Acquire"},
            ...
        ]

    Uses the human-readable display values for aspect + level (not the
    raw enum keys) so the PDF template renders them directly without
    needing to map. Order: by Module.order_index.
    """
    from apps.modules.models import Module

    rows = []
    for module in Module.objects.order_by('order_index'):
        rows.append({
            'code': module.code,
            'title': module.title,
            'aspect': module.get_unesco_aspect_display(),
            'level': module.get_proficiency_level_display(),
        })
    return rows


def _build_teacher_display(user) -> str:
    """Standard cascade for the human-readable teacher name."""
    return user.get_full_name() or user.username or 'PROODOS teacher'


def _instrument_version_for_t2(user) -> str:
    """The AILST instrument_version of the user's T2 row.

    Used to pin which AILST validation envelope the certificate was
    issued against (typically 'ning_2025_v1'). If multiple T2 rows
    exist (defensive — there should be at most one per AilstResponse
    Meta constraint), takes the most-recently completed.
    """
    from apps.ailst.models import AilstResponse

    row = (
        AilstResponse.objects
        .filter(user=user, timepoint='T2', completed_at__isnull=False)
        .order_by('-completed_at')
        .first()
    )
    if row is None:
        # Caller should have already gated on teacher_is_eligible(); this
        # is a defensive default that lets the certificate still issue
        # rather than crashing on an inconsistent state.
        return 'unknown'
    return row.instrument_version


# ----------------------------------------------------------------------
# Issuance
# ----------------------------------------------------------------------

def get_or_issue_certificate(user) -> CertificateOfAttendance:
    """Idempotent: returns the existing certificate or issues a new one.

    Frozen snapshot at issue time: teacher_display + modules_summary +
    instrument_version_t2. Later profile renames or M15 content edits
    do not alter the issued certificate (matches the
    EpilogueCompletion.stage0_snapshot first-entry-freeze pattern).

    Raises RuntimeError if the user is not yet eligible — the
    download view gates on `teacher_is_eligible(user)` before calling
    this helper, so a RuntimeError here indicates a programming bug
    (gate bypassed) rather than a user-facing error.
    """
    existing = CertificateOfAttendance.objects.filter(user=user).first()
    if existing is not None:
        return existing

    if not teacher_is_eligible(user):
        raise RuntimeError(
            'get_or_issue_certificate called for an ineligible user; '
            'call site must gate on teacher_is_eligible() first.'
        )

    return CertificateOfAttendance.objects.create(
        user=user,
        verification_code=generate_verification_code(),
        teacher_display=_build_teacher_display(user),
        modules_summary=build_modules_summary(),
        instrument_version_t2=_instrument_version_for_t2(user),
    )


# ----------------------------------------------------------------------
# PDF rendering
# ----------------------------------------------------------------------

def render_certificate_pdf(certificate) -> tuple:
    """Render the certificate as a PDF via xhtml2pdf.

    Returns `(pdf_bytes, filename)`. Raises RuntimeError on pisa
    errors so the caller (download view) can decide between failing
    the request and re-rendering on demand.

    Article 50(2) PDF document metadata (Title / Author / Subject /
    Creator) is set via `<meta>` tags in the template head; xhtml2pdf
    reads these and writes them into the PDF metadata layer. The
    template also carries a JSON-LD body block asserting
    `aiInvolved: false` for this artefact kind with a
    `programmeUsesAI: true` companion key pointing to the AI Impact
    Assessment URL.

    Bilingual template per the Phase H Path A decision (proposal §5.5):
    English front + Greek block below in the same PDF. The Greek
    block currently renders the DRAFT placeholder text with a
    visible "DRAFT — pending IRB review" watermark; a follow-up
    commit replaces the placeholder with the Kokkonis-reviewed final
    translation and flips the PDF metadata version + JSON-LD
    `certificate_translation_status` key.
    """
    from xhtml2pdf import pisa

    context = {
        'certificate': certificate,
        'teacher_display': certificate.teacher_display,
        'modules': certificate.modules_summary,
        'verification_code': certificate.verification_code,
        'issued_at': certificate.issued_at,
        'instrument_version_t2': certificate.instrument_version_t2,
        'pdf_metadata_version': certificate.pdf_metadata_version,
        # Path A: ship with DRAFT Greek placeholder; flip when final
        # translation lands. The template renders the watermark band
        # only when this key is 'draft_pending_review'.
        'translation_status': 'draft_pending_review',
    }

    html = render_to_string('pdf/certificate_of_attendance.html', context)

    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
    if result.err:
        raise RuntimeError(
            f'pisa.CreatePDF reported {result.err} errors while '
            f'rendering certificate {certificate.pk}'
        )

    filename = f'PROODOS_Certificate_of_Attendance_{certificate.verification_code}.pdf'
    return buf.getvalue(), filename
