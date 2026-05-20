"""
D.1 — AI Output Relevance Profile: the staff-only analytics view.

Renders the perceived-relevance profile aggregated by services.py.
Design: proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md.
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
def ai_relevance_profile_view(request):
    """The AI Output Relevance Profile — researcher-facing (D.1).

    Staff-only by design. The profile is derived from teachers' own
    AIOutputDispute ratings; showing it back to teachers would
    contaminate that instrument through measurement reactivity (design
    proposal section 4). `staff_member_required` keeps it on the
    researcher side — it is never linked from a teacher-facing page.
    """
    cohort = services.cohort_relevance_profile()
    teachers = services.per_teacher_relevance_profiles()

    # Shape the feature-keyed aggregates into ordered lists for the
    # three-column tables.
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
    }
    return render(request, 'analytics/ai_relevance_profile.html', context)
