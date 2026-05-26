"""
Services for apps.users — Phase H.7 dashboard redesign helpers.

Three pure-function builders that the redesigned /dashboard/ view
composes into its context:

  - build_personal_unesco_matrix(user) — per-teacher UNESCO 5x3
    progress matrix. Completion-state grid (locked / in_progress /
    complete), NOT developmental-evolution. Hard constraint per
    TD-021 line 435: the Epilogue Stage 0 owns evolution; the
    dashboard owns standing state.

  - next_action_for_dashboard(user) — single contextual card with
    one of four states: continue current module, visit Epilogue
    (post-M15 pre-Epilogue gate), complete closing AILST (post-Epilogue
    pre-T2 gate), or programme complete + cert link (post-T2).

  - certificate_state_for_dashboard(user) — locked / available /
    issued metadata for the certificate panel.

Design proposal: PHASE_H_CLOSING_FLOW_DESIGN_PROPOSAL_v1_20260525.md
§7 (dashboard redesign).
"""

from typing import Optional


# ----------------------------------------------------------------------
# Helpers — shared aspect / level orders
# ----------------------------------------------------------------------

def _aspect_and_level_orders():
    """Return (ASPECT_LABELS dict, ASPECT_ORDER list, LEVEL_ORDER list)
    derived from the Module model so the matrix stays in step with
    the schema (mirror of apps.analytics.services pattern).
    """
    from apps.modules.models import Module
    aspect_labels = dict(Module._meta.get_field('unesco_aspect').choices)
    aspect_order = list(aspect_labels)
    level_order = [c[0] for c in Module._meta.get_field('proficiency_level').choices]
    return aspect_labels, aspect_order, level_order


# ----------------------------------------------------------------------
# Personal UNESCO matrix
# ----------------------------------------------------------------------

def build_personal_unesco_matrix(user) -> dict:
    """Per-teacher 5x3 progress matrix.

    Cell schema:
      {
        'module_code': 'M1',
        'module_title': '...',
        'state': 'locked' | 'in_progress' | 'complete',
        'url': '/modules/M1/',
        # Cohort-only fields are None on personal cells:
        'rate': None, 'completed': None, 'total': None,
      }

    State derivation from UserModuleProgress:
      - row missing                              → 'locked' if the module
        is not the next-up, else 'in_progress' (an "available" item)
      - row exists, completed_at IS NULL         → 'in_progress'
      - row exists, completed_at NOT NULL        → 'complete'

    Note: 'locked' here is a UI affordance, not a DB-level gate. The
    platform does not currently gate module access by completion of
    a predecessor (the user can navigate to any module). The matrix
    classifies a module as 'locked' purely so the visual makes sense
    as a progress map; treat it as "not started yet" rather than as
    "forbidden to start". This avoids surfacing an enforcement
    semantic that does not exist downstream.

    Returns a dict shaped identically to apps.analytics.services
    cohort_unesco_matrix, with `kind='personal'`:

      {
        'kind': 'personal',
        'levels': ['Acquire', 'Deepen', 'Create'],
        'total_teachers': None,           # not meaningful for personal
        'rows': [
          {'aspect': 'human_centered', 'aspect_label': 'Human-Centred Mindset',
           'cells': [<cell>, <cell>, <cell>]},
          ...
        ],
      }
    """
    from django.urls import reverse

    from apps.modules.models import Module, UserModuleProgress

    aspect_labels, aspect_order, level_order = _aspect_and_level_orders()

    by_cell = {
        (m.unesco_aspect, m.proficiency_level): m
        for m in Module.objects.filter(is_published=True)
    }

    progress_by_module = {
        p.module_id: p
        for p in UserModuleProgress.objects.filter(user=user)
    }

    rows = []
    for aspect in aspect_order:
        cells = []
        for level in level_order:
            module = by_cell.get((aspect, level))
            if module is None:
                cells.append(None)
                continue

            progress = progress_by_module.get(module.id)
            if progress is None:
                state = 'locked'
            elif progress.completed_at is not None:
                state = 'complete'
            else:
                state = 'in_progress'

            cells.append({
                'module_code': module.code,
                'module_title': module.title,
                'state': state,
                'url': reverse('modules:detail', kwargs={'code': module.code}),
                # cohort-only — None on personal cells
                'rate': None,
                'completed': None,
                'total': None,
            })
        rows.append({
            'aspect': aspect,
            'aspect_label': aspect_labels[aspect],
            'cells': cells,
        })

    return {
        'kind': 'personal',
        'levels': list(level_order),
        'total_teachers': None,
        'rows': rows,
    }


# ----------------------------------------------------------------------
# Next-action card — 4 contextual states
# ----------------------------------------------------------------------

def next_action_for_dashboard(user) -> dict:
    """Single contextual card pointing the user at their next step.

    Four states, ordered by precedence (first match wins):

      1. 'continue_module'   — at least one M1..M15 not yet completed
      2. 'visit_epilogue'    — all 15 done, Epilogue not yet completed
      3. 'complete_ailst_t2' — Epilogue done, T2 not yet completed
      4. 'programme_complete'— T2 done; certificate link surfaced

    Returns:
      {
        'state': str,
        'title': str (teacher-facing),
        'body': str (teacher-facing),
        'cta_label': str,
        'cta_url': str,
      }

    Teacher-facing strings only — no "Stage 0/1/2/3", no "T2", no
    "AILST" acronym, no "DTP/RTM". Per the project-wide
    no-internal-labels rule.
    """
    from django.urls import reverse

    from apps.ailst.models import AilstResponse
    from apps.epilogue.models import EpilogueCompletion
    from apps.modules.models import Module, UserModuleProgress

    # State 1 — modules remaining?
    published_codes = list(
        Module.objects.filter(is_published=True)
        .order_by('order_index').values_list('code', flat=True)
    )
    completed_codes = set(
        UserModuleProgress.objects.filter(
            user=user, completed_at__isnull=False,
        ).values_list('module__code', flat=True)
    )
    remaining = [c for c in published_codes if c not in completed_codes]
    if remaining:
        next_code = remaining[0]
        return {
            'state': 'continue_module',
            'title': f'Continue with module {next_code}',
            'body': 'Pick up where you left off in the programme.',
            'cta_label': 'Open module',
            'cta_url': reverse('modules:detail', kwargs={'code': next_code}),
        }

    # State 2 — all modules done, Epilogue not yet completed?
    epilogue = EpilogueCompletion.objects.filter(user=user).first()
    if epilogue is None or epilogue.completed_at is None:
        return {
            'state': 'visit_epilogue',
            'title': 'Visit your Personal Evolution dashboard',
            'body': (
                'You have completed all 15 modules. Take a moment with '
                'the synthesis surface before the closing measurement.'
            ),
            'cta_label': 'Open the Epilogue',
            'cta_url': '/epilogue/',
        }

    # State 3 — Epilogue done, closing AILST not yet completed?
    t2_done = AilstResponse.objects.filter(
        user=user, timepoint='T2', completed_at__isnull=False,
    ).exists()
    if not t2_done:
        return {
            'state': 'complete_ailst_t2',
            'title': 'Complete the closing measurement',
            'body': (
                'A short self-assessment (about 7 minutes) is the final '
                'step before your certificate becomes available.'
            ),
            'cta_label': 'Start the closing measurement',
            'cta_url': '/ailst/t2/',
        }

    # State 4 — programme complete + cert available.
    return {
        'state': 'programme_complete',
        'title': 'Programme complete',
        'body': (
            'You have finished the PROODOS programme. Your Certificate '
            'of Attendance is ready to download.'
        ),
        'cta_label': 'Download your certificate',
        'cta_url': '/certification/download/',
    }


# ----------------------------------------------------------------------
# Certificate panel state
# ----------------------------------------------------------------------

def certificate_state_for_dashboard(user) -> dict:
    """Certificate panel state for the dashboard.

    Three states:

      - 'locked'  — T2 not yet completed; show locked card with a
                    "available after the closing measurement" notice.
      - 'available' — T2 completed but no CertificateOfAttendance row
                    issued yet; show download button (clicking issues
                    the row via get_or_issue_certificate).
      - 'issued'  — CertificateOfAttendance row exists; show download
                    button + verification code + issue date for
                    re-download / verification reference.

    Returns:
      {
        'state': str,
        'verification_code': str | None,
        'issued_at': datetime | None,
        'download_url': '/certification/download/',
      }
    """
    from apps.ailst.models import AilstResponse
    from apps.certification.models import CertificateOfAttendance

    t2_done = AilstResponse.objects.filter(
        user=user, timepoint='T2', completed_at__isnull=False,
    ).exists()

    if not t2_done:
        return {
            'state': 'locked',
            'verification_code': None,
            'issued_at': None,
            'download_url': '/certification/download/',
        }

    existing = CertificateOfAttendance.objects.filter(user=user).first()
    if existing is None:
        return {
            'state': 'available',
            'verification_code': None,
            'issued_at': None,
            'download_url': '/certification/download/',
        }

    return {
        'state': 'issued',
        'verification_code': existing.verification_code,
        'issued_at': existing.issued_at,
        'download_url': '/certification/download/',
    }
