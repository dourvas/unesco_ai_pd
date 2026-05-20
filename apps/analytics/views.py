"""
The PROODOS Research Analytics dashboard — staff-only.

One page with the Phase D researcher-facing analytics: the D.1 AI
Output Relevance Profile and the D.2 Engagement Depth sections. Designs:
proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md and
proodos_files/D2_ENGAGEMENT_DEPTH_DESIGN_PROPOSAL_v1_20260520.md.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from apps.analytics import services


def _cells(features):
    """The per-feature dicts in fixed rag/rtm/dtp column order — the
    services return a feature-keyed dict; the template wants an ordered
    list so the three columns line up."""
    return [features[f] for f in services.ALIGNMENT_FEATURES]


@staff_member_required
def research_analytics_view(request):
    """The PROODOS Research Analytics dashboard — researcher-facing.

    Staff-only by design. The analytics are derived from teachers' own
    ratings and engagement telemetry; showing them back to teachers
    would contaminate those instruments through measurement reactivity
    (D.1 §4, D.2 §4). `staff_member_required` keeps the page on the
    researcher side — it is never linked from a teacher-facing surface.
    """
    # --- D.1: AI Output Relevance Profile -----------------------------
    cohort = services.cohort_relevance_profile()
    teachers = services.per_teacher_relevance_profiles()
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
        'peer': services.peer_usefulness_summary(),
        # --- D.2: Engagement Depth ------------------------------------
        'engagement': services.cohort_engagement_depth(),
        'engagement_teachers': services.per_teacher_engagement_depth(),
    }
    return render(request, 'analytics/research_analytics.html', context)
