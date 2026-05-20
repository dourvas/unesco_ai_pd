"""
D.1 — AI Output Relevance Profile: aggregation services.

Read-only aggregations over apps.modules.AIOutputDispute. The profile
describes teachers' *perceived relevance* of the RAG / RTM / DTP AI
outputs — a researcher-facing analytic, never shown to teachers.
Design: proodos_files/D1_AI_RELEVANCE_PROFILE_DESIGN_PROPOSAL_v1_20260519.md.

Two constructs share the AIOutputDispute table; this module touches
only the alignment one:
  - 'rag' / 'rtm' / 'dtp' — the alignment instrument. Each AI output
    makes a claim about the teacher's own reflection, so the rating
    ('yes' / 'partial' / 'no' relevant) is a clean perceived-relevance
    signal. These three, and only these, feed the relevance profile.
  - 'peer' — a usefulness signal (TD-019), a different construct.
    Reported by peer_usefulness_summary(), never mixed into the
    profile. The alignment queries whitelist ALIGNMENT_FEATURES.

Nothing here mutates data or calls an LLM; it is pure ORM aggregation.
"""

from django.db.models import Count

from apps.modules.models import AIOutputDispute, UserModuleProgress


# Only these feed the relevance profile — 'peer' is a different
# construct and is deliberately excluded (see module docstring, TD-019).
ALIGNMENT_FEATURES = ('rag', 'rtm', 'dtp')
RATINGS = ('yes', 'partial', 'no')

# Human labels for the three alignment features (mirrors
# AIOutputDispute.FEATURE_CHOICES) — used by the staff template.
FEATURE_LABELS = {
    'rag': 'RAG Feedback',
    'rtm': 'Reflective Tension Mapper',
    'dtp': 'Developmental Trajectory Predictor',
}


def _empty_counts():
    """A fresh {rating: 0} tally for the three rating values."""
    return {r: 0 for r in RATINGS}


def _finalise(counts):
    """Add 'total' and 'relevance_rate' to a {rating: n} tally, in place.

    relevance_rate is the descriptive proportion rated 'relevant'
    (yes / total) — a property of the AI output as the teacher
    perceived it, never an evaluation of the teacher. None when there
    are no ratings, so the template can show 'no data' rather than 0%.
    """
    total = sum(counts[r] for r in RATINGS)
    counts['total'] = total
    counts['relevance_rate'] = (
        round(counts['yes'] / total, 3) if total else None
    )
    return counts


# ----------------------------------------------------------------------
# Cohort-level profile
# ----------------------------------------------------------------------
def cohort_relevance_profile():
    """Cohort-wide perceived-relevance distributions.

    Returns a dict with:
      - by_feature: {feature: {yes, partial, no, total, relevance_rate}}
      - by_module:  [ {module_code, module_title, features: {...}} ]
      - by_subject: [ {subject, features: {...}} ]
      - reasons:    {reason_code: count} for partial/no ratings
      - totals:     {ratings, teachers}
    """
    qs = AIOutputDispute.objects.filter(feature_type__in=ALIGNMENT_FEATURES)

    by_feature = {f: _empty_counts() for f in ALIGNMENT_FEATURES}
    for row in qs.values('feature_type', 'rating').annotate(n=Count('id')):
        by_feature[row['feature_type']][row['rating']] = row['n']
    for f in ALIGNMENT_FEATURES:
        _finalise(by_feature[f])

    # Per module x feature.
    modules = {}
    for row in qs.values(
        'module__code', 'module__title', 'feature_type', 'rating',
    ).annotate(n=Count('id')):
        entry = modules.setdefault(row['module__code'], {
            'module_code': row['module__code'],
            'module_title': row['module__title'],
            'features': {f: _empty_counts() for f in ALIGNMENT_FEATURES},
        })
        entry['features'][row['feature_type']][row['rating']] = row['n']
    for entry in modules.values():
        for f in ALIGNMENT_FEATURES:
            _finalise(entry['features'][f])
    by_module = sorted(modules.values(), key=lambda d: d['module_code'])

    # Per subject x feature. A teacher with no profile/subject is 'Unknown'.
    subjects = {}
    for row in qs.values(
        'user__teacher_profile__subject_area', 'feature_type', 'rating',
    ).annotate(n=Count('id')):
        subject = row['user__teacher_profile__subject_area'] or 'Unknown'
        entry = subjects.setdefault(subject, {
            'subject': subject,
            'features': {f: _empty_counts() for f in ALIGNMENT_FEATURES},
        })
        entry['features'][row['feature_type']][row['rating']] = row['n']
    for entry in subjects.values():
        for f in ALIGNMENT_FEATURES:
            _finalise(entry['features'][f])
    by_subject = sorted(subjects.values(), key=lambda d: d['subject'])

    # Why outputs were found wanting — partial/no ratings only.
    reasons = {}
    for row in qs.filter(rating__in=('partial', 'no')).values(
        'reason',
    ).annotate(n=Count('id')):
        reasons[row['reason'] or 'unspecified'] = row['n']

    return {
        'by_feature': by_feature,
        'by_module': by_module,
        'by_subject': by_subject,
        'reasons': reasons,
        'totals': {
            'ratings': qs.count(),
            'teachers': qs.values('user_id').distinct().count(),
        },
    }


# ----------------------------------------------------------------------
# Per-teacher profiles
# ----------------------------------------------------------------------
def per_teacher_relevance_profiles():
    """One perceived-relevance profile per teacher who has rated.

    Returns a list, sorted by username, of:
      {user_id, username, features: {feature: {...}}, reasons: {...},
       rated_modules, completed_modules}

    rated_modules / completed_modules is the coverage (non-response)
    indicator: how many modules the teacher rated against how many they
    completed. The denominator is approximate — not every module emits
    every feature — so it is reported as context, not a precise rate.
    """
    qs = AIOutputDispute.objects.filter(feature_type__in=ALIGNMENT_FEATURES)

    teachers = {}
    for row in qs.values(
        'user_id', 'user__username', 'feature_type', 'rating',
    ).annotate(n=Count('id')):
        entry = teachers.setdefault(row['user_id'], {
            'user_id': row['user_id'],
            'username': row['user__username'],
            'features': {f: _empty_counts() for f in ALIGNMENT_FEATURES},
            'reasons': {},
        })
        entry['features'][row['feature_type']][row['rating']] = row['n']

    for row in qs.filter(rating__in=('partial', 'no')).values(
        'user_id', 'reason',
    ).annotate(n=Count('id')):
        entry = teachers.get(row['user_id'])
        if entry is not None:
            entry['reasons'][row['reason'] or 'unspecified'] = row['n']

    for user_id, entry in teachers.items():
        for f in ALIGNMENT_FEATURES:
            _finalise(entry['features'][f])
        entry['rated_modules'] = (
            qs.filter(user_id=user_id).values('module_id').distinct().count()
        )
        entry['completed_modules'] = UserModuleProgress.objects.filter(
            user_id=user_id, completed_at__isnull=False,
        ).count()

    return sorted(teachers.values(), key=lambda d: d['username'].lower())


# ----------------------------------------------------------------------
# Peer usefulness — separate construct (TD-019)
# ----------------------------------------------------------------------
def peer_usefulness_summary():
    """The peer-synthesis usefulness signal — reported apart from the
    relevance profile because it is a different construct (TD-019).

    Returns {yes, partial, no, total, relevance_rate, with_comment}.
    'relevance_rate' here is the proportion who found the synthesis
    useful; the field name is shared with the alignment tallies only
    for template uniformity.
    """
    qs = AIOutputDispute.objects.filter(feature_type='peer')
    counts = _empty_counts()
    for row in qs.values('rating').annotate(n=Count('id')):
        counts[row['rating']] = row['n']
    _finalise(counts)
    counts['with_comment'] = (
        qs.exclude(comment__isnull=True).exclude(comment='').count()
    )
    return counts
