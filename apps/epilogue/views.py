"""
Views for the PROODOS Epilogue (post-deprecation).

Phase G closure (2026-05-24) — the Aletheia reflective dialogue
(Stages 1-3) and the Learning Portrait HITL flow (review / regenerate
/ accept / PDF) were strategically removed from the teacher-facing
Epilogue. See `proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md`
for the decision rationale (reflection fatigue + RPE framework
dilution + technical fragility) and the master design proposal v2
§25 for the pointer.

Two teacher-facing views remain:

  - `epilogue_placeholder_view` (GET): renders Stage 0, the Personal
    Evolution Dashboard. On the user's first entry it aggregates and
    freezes the Stage 0 snapshot.
  - `epilogue_complete_view` (POST): flips `completed_at = NOW`, then
    redirects to /ailst/t2/ if the user has active research_consent
    and has not yet completed T2; otherwise sends them to the
    dashboard.

Per D4 of the C.2.5 design proposal, the Epilogue itself has no
consent gate: it is a pedagogical feature, not a research instrument.
The T2 gate is enforced downstream by the AILST entry view.

Preserved Phase H assets (dormant, no live caller):
  - `_generate_portrait_pdf` — xhtml2pdf + Article 50(2) PDF metadata
    pattern, retained as the seed for the Phase H certificate of
    attendance generator. The Portrait template it references was
    removed (`templates/pdf/learning_portrait.html`); the helper
    cannot be called as-is and will need a new template + a different
    payload composition when Phase H lands. See deprecation doc §3.3.
"""

import io
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.epilogue.models import EpilogueCompletion
from apps.epilogue.services_stage0 import build_stage0_snapshot


def _is_m15_completed(user) -> bool:
    """Phase C TD-013 — M15 completion is the prerequisite for entering
    the Epilogue. Helper isolates the dependency on apps.modules so
    the import remains lazy and the test suites stay decoupled.
    """
    from apps.modules.services import user_has_completed_module
    return user_has_completed_module(user, 'M15')


@login_required
def epilogue_placeholder_view(request):
    """GET /epilogue/ — the PROODOS Epilogue entry point (Stage 0).

    Phase G G.1: renders Stage 0, the Personal Evolution Dashboard.
    On the user's first entry the Stage 0 snapshot is aggregated from
    their DTP and RTM data and frozen into
    EpilogueCompletion.stage0_snapshot (first-entry-only — design
    proposal v2 section 5.4). Revisits render the stored snapshot
    unchanged.

    Phase C TD-013: blocked unless the user has completed M15. Staff
    and superusers bypass for support; a blocked user is redirected
    to the dashboard with an informational flash.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    with transaction.atomic():
        completion, _ = EpilogueCompletion.objects.select_for_update().get_or_create(
            user=request.user,
        )
        # First-entry-only freeze: compute the Stage 0 snapshot once.
        if not completion.stage0_snapshot:
            completion.stage0_snapshot = build_stage0_snapshot(request.user)
            completion.stage0_seen_at = timezone.now()
            completion.save(
                update_fields=['stage0_snapshot', 'stage0_seen_at'],
            )

    return render(request, 'epilogue/stage0.html', {
        'completion': completion,
        'snapshot': completion.stage0_snapshot,
        'already_completed': completion.completed_at is not None,
    })


@login_required
@require_POST
def epilogue_complete_view(request):
    """POST /epilogue/complete/ — flip completed_at, then route forward.

    Forward routing:
      - if user has research_consent and T2 not yet completed -> /ailst/t2/
      - otherwise -> /dashboard/

    Idempotent: a second POST after the row is already completed does
    not change completed_at and still routes the user forward according
    to the same rules.

    Phase C TD-013: defensive mirror of the GET gate. Even though a
    crafted POST without M15 completion would fail the GET gate first
    (the user would never see the Submit button), accept the request
    only when M15 is done. Staff and superusers bypass.

    Phase G closure (2026-05-24): the dialogue-stage-completion side
    effects (stage1/2/3_completed_at) were removed together with the
    dialogue views. A teacher submitting this form has only Stage 0
    state to record (`stage0_snapshot` + `stage0_seen_at` set by the
    placeholder view) — `completed_at` is the single field touched
    here.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        if not _is_m15_completed(request.user):
            messages.info(
                request,
                'The PROODOS Epilogue is available after you complete Module 15.',
            )
            return redirect('users:dashboard')

    with transaction.atomic():
        completion, _ = EpilogueCompletion.objects.select_for_update().get_or_create(
            user=request.user,
        )
        if completion.completed_at is None:
            completion.completed_at = timezone.now()
            completion.save(update_fields=['completed_at'])

    return redirect(_post_epilogue_destination(request.user))


def _post_epilogue_destination(user):
    """Compute the URL to send the user to after Epilogue completion.

    Mirrors the AILST gating philosophy: T2 is only reachable for
    research-consenting users who have not already completed it. The
    AILST entry view also enforces this; the check here is to avoid
    the unnecessary redirect hop for the common 'non-consenting' /
    'already done' cases.
    """
    from apps.ailst.models import AilstResponse

    profile = getattr(user, 'teacher_profile', None)
    if profile is None or not profile.research_consent:
        return '/dashboard/'

    t2_completed = AilstResponse.objects.filter(
        user=user, timepoint='T2', completed_at__isnull=False,
    ).exists()
    if t2_completed:
        return '/dashboard/'

    return '/ailst/t2/'


# ======================================================================
# Preserved Phase H asset — Learning Portrait PDF generator (DORMANT)
# ======================================================================
#
# Phase G closure (2026-05-24): the Learning Portrait teacher-facing
# flow was deactivated. This helper is retained as the seed for the
# Phase H certificate of attendance PDF generator. It currently has
# no live caller and cannot be invoked as-is — the
# `templates/pdf/learning_portrait.html` template it renders was
# removed in the same closure. Re-activation under Phase H requires:
#
#   1. A new template (`templates/pdf/certificate.html` or similar)
#      patterned after the deleted Portrait template (eyebrow + serif
#      numeral + standfirst + body + AI provenance footer + olive
#      ornament).
#   2. A new payload composition appropriate to "βεβαίωση
#      παρακολούθησης" (teacher name + 15 modules completed +
#      completion date + UNESCO ICT-CFT alignment statement).
#   3. The Article 50(2) machinery (JSON-LD body block + PDF Info
#      dict via <meta> tags + AIArtefactProvenance row) preserved
#      verbatim — that pattern is the reusable contribution.
#
# See deprecation doc §3.3 for the full rationale on why this is
# preserved rather than deleted.

def _generate_portrait_pdf(completion, user) -> tuple:
    """[DORMANT — Phase H seed] Render a teacher PDF via xhtml2pdf.

    Original docstring preserved verbatim below as the design
    reference for the Phase H certificate generator. The Portrait
    template (`templates/pdf/learning_portrait.html`) referenced
    in the implementation has been removed; calling this helper
    will raise `TemplateDoesNotExist`. Kept for the Article 50(2)
    pattern (JSON-LD + PDF Info dict via `<meta>` tags) and the
    xhtml2pdf wiring.

    --- original docstring ---
    Render the Learning Portrait as a PDF via xhtml2pdf.

    Returns `(pdf_bytes, filename)`. Raises on pisa error so the caller
    can decide between "fail this request" (download view) and
    "swallow and let regen-on-demand handle it later" (accept view).

    Article 50(2) marker (design proposal v2 sections 8.5 and 22.3):
    the rendered HTML carries the `{% ai_provenance_jsonld %}` block;
    PDF document metadata (Title / Author / Subject / Creator) is set
    via `<meta>` tags in the template head — xhtml2pdf reads these and
    writes them into the PDF metadata layer.
    """
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa

    from apps.agents.epilogue_portrait import EpiloguePortraitAgent
    from apps.compliance.models import AIArtefactProvenance

    provenance = AIArtefactProvenance.objects.filter(
        artefact_kind=EpiloguePortraitAgent.artefact_kind,
        artefact_pk=str(completion.pk),
        user=user,
    ).first()

    teacher_display = (
        user.get_full_name() or user.username or 'PROODOS teacher'
    )

    context = {
        'portrait_text': completion.learning_portrait_text,
        'snapshot': completion.stage0_snapshot or {},
        'teacher_display': teacher_display,
        'generated_at': completion.learning_portrait_generated_at,
        'model_name': EpiloguePortraitAgent.model_name,
        'provenance': provenance,
        'provenances': [provenance] if provenance else [],
    }
    html = render_to_string('pdf/learning_portrait.html', context)

    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
    if result.err:
        raise RuntimeError(f'pisa.CreatePDF reported {result.err} errors')

    filename = f'PROODOS_Learning_Portrait_{user.username}.pdf'
    return buf.getvalue(), filename


# Silence the unused-import linter on `logging` — the module is kept
# imported so re-activation code (Phase H) need not re-discover the
# logging-warning pattern from the deleted view bodies.
_LOGGER = logging.getLogger(__name__)
