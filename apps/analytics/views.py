"""
The PROODOS Research Analytics dashboard — staff-only.

One page with the Phase D researcher-facing analytics: the D.1 AI
Output Relevance Profile and the D.2 Engagement Depth sections. Designs:
proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md and
proodos_files/D2_ENGAGEMENT_DEPTH_DESIGN_PROPOSAL_v1_20260520.md.

Every section is restricted to research-consenting teachers and obeys
the page-level date-range and subject filters (see services._scope).
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.dateparse import parse_date

from apps.analytics import services
from apps.users.models import TeacherProfile


def _cells(features):
    """The per-feature dicts in fixed rag/rtm/dtp column order — the
    services return a feature-keyed dict; the template wants an ordered
    list so the three columns line up."""
    return [features[f] for f in services.ALIGNMENT_FEATURES]


def _subject_choices():
    """The TeacherProfile.subject_area choices — used for the filter
    <select> and to validate the incoming subject parameter."""
    return TeacherProfile._meta.get_field('subject_area').choices


def _read_filters(request):
    """Parse the date-range and subject filters from the query string.

    Returns (filters, form_state):
      filters    — the dict passed to the services (services._scope shape);
      form_state — the raw values for re-populating the filter form.
    An unrecognised subject is ignored rather than silently emptying the
    page for a typo'd query string.
    """
    raw_start = request.GET.get('start', '').strip()
    raw_end = request.GET.get('end', '').strip()
    raw_subject = request.GET.get('subject', '').strip()

    valid_subjects = {value for value, _ in _subject_choices()}
    subject = raw_subject if raw_subject in valid_subjects else ''

    filters = {
        'start': parse_date(raw_start) if raw_start else None,
        'end': parse_date(raw_end) if raw_end else None,
        'subject': subject or None,
    }
    form_state = {
        'start': raw_start,
        'end': raw_end,
        'subject': subject,
        'active': any(filters.values()),
    }
    return filters, form_state


@staff_member_required
def research_analytics_view(request):
    """The PROODOS Research Analytics dashboard — researcher-facing.

    Staff-only by design. The analytics are derived from teachers' own
    ratings and engagement telemetry; showing them back to teachers
    would contaminate those instruments through measurement reactivity
    (D.1 §4, D.2 §4). `staff_member_required` keeps the page on the
    researcher side — it is never linked from a teacher-facing surface.

    Every section is scoped to the research-consenting population and
    to the page-level date-range / subject filters.
    """
    filters, filter_form = _read_filters(request)

    # --- D.1: AI Output Relevance Profile -----------------------------
    cohort = services.cohort_relevance_profile(filters)
    teachers = services.per_teacher_relevance_profiles(filters)
    cohort_feature_rows = [
        {
            'feature': f,
            'label': services.FEATURE_LABELS[f],
            'counts': cohort['by_feature'][f],
        }
        for f in services.ALIGNMENT_FEATURES
    ]
    for module_row in cohort['by_module']:
        module_row['cells'] = _cells(module_row['features'])
    for subject_row in cohort['by_subject']:
        subject_row['cells'] = _cells(subject_row['features'])
    for teacher in teachers:
        teacher['cells'] = _cells(teacher['features'])

    context = {
        'cohort': cohort,
        'cohort_feature_rows': cohort_feature_rows,
        'teachers': teachers,
        'peer': services.peer_usefulness_summary(filters),
        # --- D.2: Engagement Depth ------------------------------------
        'engagement': services.cohort_engagement_depth(filters),
        'engagement_teachers': services.per_teacher_engagement_depth(filters),
        # --- Filter bar -----------------------------------------------
        'filter_form': filter_form,
        'subject_choices': _subject_choices(),
    }
    return render(request, 'analytics/research_analytics.html', context)
