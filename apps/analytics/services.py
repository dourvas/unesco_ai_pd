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

Every aggregation is scoped by `_scope()` to the research-consenting
population (`research_consent=True`) and, optionally, to a `created_at`
date range and a single subject area — the page-level filters of the
staff analytics dashboard. Restricting to consenting teachers is
unconditional: the dashboard is a research instrument and reports only
the population whose data may be used for research.

Nothing here mutates data or calls an LLM; it is pure ORM aggregation.
"""

import statistics

from django.contrib.auth.models import User
from django.db.models import Count, Q

from apps.modules.models import (
    AIOutputDispute,
    Module,
    ReflectionTension,
    UserModuleProgress,
)
from apps.users.models import TeacherProfile


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


def _scope(qs, filters):
    """Restrict an analytics queryset to the consenting research
    population, and optionally to a `created_at` date range and a
    single subject area.

    The `research_consent=True` restriction is unconditional — the
    analytics dashboard reports only the consented population. `filters`
    is a dict (or None) that may carry 'start' / 'end' (`date` objects)
    and 'subject' (a `TeacherProfile.subject_area` value); each is
    applied only when present and truthy.

    Both querysets this is used on — AIOutputDispute and
    ReflectionTension — expose `user` and `created_at`, so the same
    helper scopes D.1 and D.2 identically.
    """
    qs = qs.filter(user__teacher_profile__research_consent=True)
    filters = filters or {}
    if filters.get('start'):
        qs = qs.filter(created_at__date__gte=filters['start'])
    if filters.get('end'):
        qs = qs.filter(created_at__date__lte=filters['end'])
    if filters.get('subject'):
        qs = qs.filter(
            user__teacher_profile__subject_area=filters['subject'],
        )
    return qs


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
def cohort_relevance_profile(filters=None):
    """Cohort-wide perceived-relevance distributions.

    `filters` is the optional date-range / subject scope (see _scope).

    Returns a dict with:
      - by_feature: {feature: {yes, partial, no, total, relevance_rate}}
      - by_module:  [ {module_code, module_title, features: {...}} ]
      - by_subject: [ {subject, features: {...}} ]
      - reasons:    {reason_code: count} for partial/no ratings
      - totals:     {ratings, teachers}
    """
    qs = _scope(
        AIOutputDispute.objects.filter(feature_type__in=ALIGNMENT_FEATURES),
        filters,
    )

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
def per_teacher_relevance_profiles(filters=None):
    """One perceived-relevance profile per teacher who has rated.

    `filters` is the optional date-range / subject scope (see _scope).

    Returns a list, sorted by username, of:
      {user_id, username, features: {feature: {...}}, reasons: {...},
       rated_modules, completed_modules}

    rated_modules / completed_modules is the coverage (non-response)
    indicator: how many modules the teacher rated against how many they
    completed. The denominator is approximate — not every module emits
    every feature — so it is reported as context, not a precise rate.
    completed_modules is a cumulative count for the teacher; it is not
    narrowed by the date filter (module completion is a standing state,
    not an event within the window).
    """
    qs = _scope(
        AIOutputDispute.objects.filter(feature_type__in=ALIGNMENT_FEATURES),
        filters,
    )

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
def peer_usefulness_summary(filters=None):
    """The peer-synthesis usefulness signal — reported apart from the
    relevance profile because it is a different construct (TD-019).

    `filters` is the optional date-range / subject scope (see _scope).

    Returns {yes, partial, no, total, relevance_rate, with_comment}.
    'relevance_rate' here is the proportion who found the synthesis
    useful; the field name is shared with the alignment tallies only
    for template uniformity.
    """
    qs = _scope(AIOutputDispute.objects.filter(feature_type='peer'), filters)
    counts = _empty_counts()
    for row in qs.values('rating').annotate(n=Count('id')):
        counts[row['rating']] = row['n']
    _finalise(counts)
    counts['with_comment'] = (
        qs.exclude(comment__isnull=True).exclude(comment='').count()
    )
    return counts


# ======================================================================
# D.2 — Engagement Depth (Position Confirmation Analytics)
#
# Read-only aggregations over apps.modules.ReflectionTension. The
# Engagement Depth Score (EDS) is the proportion of RTM tensions a
# teacher actively engaged with — position_confirmed is set true only
# for a tension whose slider the teacher touched (the RTM auto-saves
# every tension at the neutral default with position_confirmed false).
# EDS separates surface engagement (the RTM step completed, nothing
# touched) from deep engagement. Researcher-facing; design:
# proodos_files/D2_ENGAGEMENT_DEPTH_DESIGN_PROPOSAL_v1_20260520.md.
# ======================================================================

# The neutral mid-point of the RTM 1-5 positioning slider; also the
# auto-save default. A confirmed tension resting here is engaged but
# neutral — see non_neutral_rate.
RTM_NEUTRAL_POSITION = 3


def _rate(numerator, denominator):
    """A descriptive proportion rounded to 3 dp, or None when the
    denominator is zero (so the template shows 'no data', not 0%)."""
    return round(numerator / denominator, 3) if denominator else None


def _median_ms(values):
    """Median of the non-null millisecond values, rounded; None if the
    set is empty. time_spent_ms is frontend-reported and nullable."""
    vals = [v for v in values if v is not None]
    return round(statistics.median(vals)) if vals else None


def cohort_engagement_depth(filters=None):
    """Cohort-wide RTM engagement-depth aggregation.

    `filters` is the optional date-range / subject scope (see _scope).

    Returns a dict with:
      - total_tensions / confirmed / eds — the headline confirmation rate
      - comment_use_rate — share of tensions carrying an optional comment
      - non_neutral_rate — among confirmed tensions, the share placed
        off the neutral mid-point
      - median_time_ms — median RTM-card interaction time
      - by_module / by_subject — [ {..., total, confirmed, eds} ]
    """
    qs = _scope(ReflectionTension.objects.all(), filters)
    total = qs.count()
    confirmed = qs.filter(position_confirmed=True).count()
    confirmed_non_neutral = (
        qs.filter(position_confirmed=True)
        .exclude(selected_position=RTM_NEUTRAL_POSITION)
        .count()
    )

    by_module = [
        {
            'module_code': row['module__code'],
            'module_title': row['module__title'],
            'total': row['total'],
            'confirmed': row['confirmed'],
            'eds': _rate(row['confirmed'], row['total']),
        }
        for row in qs.values('module__code', 'module__title').annotate(
            total=Count('id'),
            confirmed=Count('id', filter=Q(position_confirmed=True)),
        ).order_by('module__code')
    ]

    by_subject = [
        {
            'subject': row['user__teacher_profile__subject_area'] or 'Unknown',
            'total': row['total'],
            'confirmed': row['confirmed'],
            'eds': _rate(row['confirmed'], row['total']),
        }
        for row in qs.values(
            'user__teacher_profile__subject_area',
        ).annotate(
            total=Count('id'),
            confirmed=Count('id', filter=Q(position_confirmed=True)),
        ).order_by('user__teacher_profile__subject_area')
    ]

    return {
        'total_tensions': total,
        'confirmed': confirmed,
        'eds': _rate(confirmed, total),
        'comment_use_rate': _rate(qs.filter(comment_used=True).count(), total),
        'non_neutral_rate': _rate(confirmed_non_neutral, confirmed),
        'median_time_ms': _median_ms(
            qs.values_list('time_spent_ms', flat=True),
        ),
        'by_module': by_module,
        'by_subject': by_subject,
    }


def per_teacher_engagement_depth(filters=None):
    """One engagement-depth profile per teacher who has RTM data.

    `filters` is the optional date-range / subject scope (see _scope).

    Returns a list, sorted by username, of:
      {user_id, username, total, confirmed, eds, comment_use_rate,
       non_neutral_rate, median_time_ms}
    """
    qs = _scope(ReflectionTension.objects.all(), filters)

    teachers = {}
    for row in qs.values('user_id', 'user__username').annotate(
        total=Count('id'),
        confirmed=Count('id', filter=Q(position_confirmed=True)),
        commented=Count('id', filter=Q(comment_used=True)),
        confirmed_non_neutral=Count(
            'id',
            filter=Q(position_confirmed=True)
            & ~Q(selected_position=RTM_NEUTRAL_POSITION),
        ),
    ):
        teachers[row['user_id']] = {
            'user_id': row['user_id'],
            'username': row['user__username'],
            'total': row['total'],
            'confirmed': row['confirmed'],
            'eds': _rate(row['confirmed'], row['total']),
            'comment_use_rate': _rate(row['commented'], row['total']),
            'non_neutral_rate': _rate(
                row['confirmed_non_neutral'], row['confirmed'],
            ),
        }

    times = {}
    for user_id, ms in qs.values_list('user_id', 'time_spent_ms'):
        times.setdefault(user_id, []).append(ms)
    for user_id, entry in teachers.items():
        entry['median_time_ms'] = _median_ms(times.get(user_id, []))

    return sorted(teachers.values(), key=lambda d: d['username'].lower())


# ======================================================================
# D.4 — Dashboard: UNESCO Matrix + RTM Heatmap
#
# Two cohort-level visualisations over data the platform already holds.
# The UNESCO matrix shows module completion across the 5x3 competency
# grid; the RTM heatmap shows where the RTM instrument has coverage
# across subjects x modules. Researcher-facing; design:
# proodos_files/D4_DASHBOARD_DESIGN_PROPOSAL_v1_20260520.md.
# ======================================================================

# Aspect / level orders derived from the Module model so the matrix
# stays in step with the schema.
ASPECT_LABELS = dict(Module._meta.get_field('unesco_aspect').choices)
ASPECT_ORDER = list(ASPECT_LABELS)
LEVEL_ORDER = [c[0] for c in Module._meta.get_field('proficiency_level').choices]


def cohort_unesco_matrix(filters=None):
    """The UNESCO 5x3 competency matrix of cohort module completion.

    Each of the 15 cells is one module; the value is the cohort
    completion rate — consenting teachers who completed it over all
    consenting teachers. The matrix is *cumulative*: consent and the
    subject filter apply, but the date filter does NOT narrow it
    (date-windowing a standing state is incoherent — design §4).

    Returns:
      {levels: [...], total_teachers: int,
       rows: [ {aspect, aspect_label,
                cells: [ {module_code, module_title, completed, total,
                          rate} | None ]} ]}
    """
    filters = filters or {}
    subject = filters.get('subject')

    # Denominator — consenting teachers, optionally of one subject.
    teacher_qs = User.objects.filter(teacher_profile__research_consent=True)
    if subject:
        teacher_qs = teacher_qs.filter(teacher_profile__subject_area=subject)
    total_teachers = teacher_qs.count()

    # Completed-teacher count per module (consent + optional subject;
    # cumulative — not date-narrowed).
    progress = UserModuleProgress.objects.filter(
        completed_at__isnull=False,
        user__teacher_profile__research_consent=True,
    )
    if subject:
        progress = progress.filter(
            user__teacher_profile__subject_area=subject,
        )
    completed_by_module = {
        row['module_id']: row['n']
        for row in progress.values('module_id').annotate(
            n=Count('user', distinct=True),
        )
    }

    by_cell = {
        (m.unesco_aspect, m.proficiency_level): m
        for m in Module.objects.filter(is_published=True)
    }

    rows = []
    for aspect in ASPECT_ORDER:
        cells = []
        for level in LEVEL_ORDER:
            module = by_cell.get((aspect, level))
            if module is None:
                cells.append(None)
                continue
            completed = completed_by_module.get(module.id, 0)
            cells.append({
                'module_code': module.code,
                'module_title': module.title,
                'completed': completed,
                'total': total_teachers,
                'rate': _rate(completed, total_teachers),
            })
        rows.append({
            'aspect': aspect,
            'aspect_label': ASPECT_LABELS[aspect],
            'cells': cells,
        })

    return {
        # Phase H.7 (2026-05-25): 'kind' added so the shared partial
        # templates/partials/_unesco_matrix.html can branch its cell
        # rendering between cohort (heat-shaded rate) and personal
        # (state badge + module link). The cohort callers always pass
        # 'cohort'; the per-teacher callers pass 'personal'.
        'kind': 'cohort',
        'levels': list(LEVEL_ORDER),
        'rows': rows,
        'total_teachers': total_teachers,
    }


def cohort_rtm_heatmap(filters=None):
    """The RTM coverage heatmap — subjects x modules.

    Each cell counts the distinct consenting teachers of that subject
    with at least one ReflectionTension on that module. Fully scoped
    (consent + subject + date). At pilot scale this is a coverage map,
    not a comparative measure (design §7).

    Returns:
      {modules: [code, ...], max_count: int,
       rows: [ {subject, subject_label,
                cells: [ {module_code, count} ]} ]}
    """
    qs = _scope(ReflectionTension.objects.all(), filters)

    counts = {}
    for row in qs.values(
        'user__teacher_profile__subject_area', 'module__code',
    ).annotate(n=Count('user', distinct=True)):
        subject = row['user__teacher_profile__subject_area'] or 'Unknown'
        counts[(subject, row['module__code'])] = row['n']

    module_codes = list(
        Module.objects.filter(is_published=True)
        .order_by('order_index')
        .values_list('code', flat=True)
    )

    rows = [
        {
            'subject': value,
            'subject_label': label,
            'cells': [
                {'module_code': code, 'count': counts.get((value, code), 0)}
                for code in module_codes
            ],
        }
        for value, label in TeacherProfile._meta.get_field(
            'subject_area',
        ).choices
    ]

    return {
        'modules': module_codes,
        'rows': rows,
        'max_count': max(counts.values(), default=0),
    }
