"""
Stage 0 aggregation for the PROODOS Epilogue (Phase G, G.1).

`build_stage0_snapshot(user)` reads the teacher's already-stored DTP
composites (`UserModuleProgress.reflection_dtp` — the D.3a `dtp_dual_v1`
JSON) and RTM tensions (`ReflectionTension`), and returns the Stage 0
payload that the Personal Evolution Dashboard renders.

No LLM calls: this is pure aggregation of data the platform already
holds. The payload is computed once, on the user's first entry to the
Epilogue, and stored in `EpilogueCompletion.stage0_snapshot`; it is
never recomputed (design proposal v2 section 5.4 — first-entry-only
freeze). Rendering is always live from this JSON via
`templates/epilogue/_stage0_panel.html`.

Descriptive only: the raw DTP cosine similarities are deliberately NOT
surfaced (D.3a section 4.4 / 7.4 — continuity is not quality). The
snapshot carries themes and narratives, never a numeric DTP score.

Snapshot schema (`epilogue_stage0_v1`):

    {
      "schema": "epilogue_stage0_v1",
      "generated_at": "<ISO timestamp>",
      "quantitative": {
        "modules_completed": int,
        "reflections_written": int,
        "distinct_tensions": int,
        "tensions_engaged": int,
        "dtp_composites": int,
        "dtp_composites_with_shift": int,
        "input_modality": {"text": int, "voice": int,
                           "mixed": int, "unspecified": int}
      },
      "theme_evolution": {
        "grown":     [{"theme": str, "count": int}, ...],
        "recurring": [{"theme": str, "count": int}, ...],
        "faded":     [{"theme": str, "count": int}, ...]
      },
      "narrative_timeline": [
        {"module": "M2", "order": 2, "narrative": str}, ...
      ],
      "rtm_trajectories": [
        {"tension_label": str, "recurring": bool,
         "points": [{"module": "M3", "order": 3, "position": 2,
                     "position_label": "Leaning Left",
                     "confirmed": true}, ...]}, ...
      ]
    }
"""

import json
import logging
from collections import Counter

from django.utils import timezone

logger = logging.getLogger(__name__)

SNAPSHOT_SCHEMA = 'epilogue_stage0_v1'

# The DTP composite schema this aggregator understands (D.3a).
_DTP_SCHEMA = 'dtp_dual_v1'


def build_stage0_snapshot(user) -> dict:
    """Aggregate the user's DTP + RTM data into the Stage 0 payload.

    Pure read-only aggregation; never raises on missing or malformed
    data — a teacher with a thin reflective record simply yields a
    snapshot with empty sections (Q6 — show what exists).
    """
    from apps.modules.models import ReflectionTension, UserModuleProgress

    progress = list(
        UserModuleProgress.objects
        .filter(user=user)
        .select_related('module')
        .order_by('module__order_index')
    )
    tensions = list(
        ReflectionTension.objects
        .filter(user=user)
        .select_related('module')
        .order_by('module__order_index', 'created_at')
    )

    # Parse each DTP composite exactly once and reuse the result across
    # every section builder. `parsed` is a list of (progress_row,
    # composite_dict_or_None) pairs, in module order.
    parsed = [(p, _parse_dtp(p)) for p in progress]

    return {
        'schema': SNAPSHOT_SCHEMA,
        'generated_at': timezone.now().isoformat(),
        'quantitative': _quantitative_summary(parsed, tensions),
        'theme_evolution': _theme_evolution(parsed),
        'narrative_timeline': _narrative_timeline(parsed),
        'rtm_trajectories': _rtm_trajectories(tensions),
    }


# ----------------------------------------------------------------------
# DTP composite parsing
# ----------------------------------------------------------------------
def _parse_dtp(progress_row) -> dict | None:
    """Parse a UserModuleProgress.reflection_dtp JSON string.

    Returns the composite dict, or None when the field is empty,
    unparseable, or not a recognised dual-signal composite. A malformed
    composite is logged once and skipped — it never aborts the snapshot.
    """
    raw = (progress_row.reflection_dtp or '').strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning(
            'Stage 0: unparseable reflection_dtp for module %s',
            getattr(progress_row.module, 'code', '?'),
        )
        return None
    if not isinstance(data, dict) or data.get('schema') != _DTP_SCHEMA:
        return None
    return data


def _composite_has_shift(composite: dict) -> bool:
    """True when any signal of the composite reports a thematic shift
    (a non-empty increased or decreased theme list)."""
    for signal in (composite.get('signals') or {}).values():
        themes = (signal or {}).get('themes') or {}
        if themes.get('increased_themes') or themes.get('decreased_themes'):
            return True
    return False


# ----------------------------------------------------------------------
# Section builders — each takes `parsed`, the pre-parsed
# [(progress_row, composite_or_None), ...] list.
# ----------------------------------------------------------------------
def _quantitative_summary(parsed, tensions) -> dict:
    modules_completed = sum(
        1 for p, _ in parsed if p.completed_at is not None
    )
    reflections_written = sum(
        1 for p, _ in parsed if p.reflection_completed
    )

    modality = {'text': 0, 'voice': 0, 'mixed': 0, 'unspecified': 0}
    for p, _ in parsed:
        if not p.reflection_completed:
            continue
        key = p.reflection_input_modality or 'unspecified'
        modality[key] = modality.get(key, 0) + 1

    dtp_composites = 0
    dtp_composites_with_shift = 0
    for _, composite in parsed:
        if composite is None:
            continue
        dtp_composites += 1
        if _composite_has_shift(composite):
            dtp_composites_with_shift += 1

    return {
        'modules_completed': modules_completed,
        'reflections_written': reflections_written,
        'distinct_tensions': len({t.tension_label for t in tensions}),
        'tensions_engaged': sum(1 for t in tensions if t.position_confirmed),
        'dtp_composites': dtp_composites,
        'dtp_composites_with_shift': dtp_composites_with_shift,
        'input_modality': modality,
    }


def _theme_evolution(parsed) -> dict:
    """Aggregate the DTP themes across every composite into three
    descriptive groups. Free-text theme phrases are normalised only for
    whitespace — they are not interpreted or scored."""
    grown, recurring, faded = Counter(), Counter(), Counter()
    for _, composite in parsed:
        if composite is None:
            continue
        for signal in (composite.get('signals') or {}).values():
            themes = (signal or {}).get('themes') or {}
            for phrase in themes.get('increased_themes') or []:
                _tally(grown, phrase)
            for phrase in themes.get('stable_themes') or []:
                _tally(recurring, phrase)
            for phrase in themes.get('decreased_themes') or []:
                _tally(faded, phrase)
    return {
        'grown': _counter_to_list(grown),
        'recurring': _counter_to_list(recurring),
        'faded': _counter_to_list(faded),
    }


def _narrative_timeline(parsed) -> list:
    """The DTP descriptive narrative for each module that has one,
    in module order. The trajectory as a story spine, no numbers."""
    timeline = []
    for p, composite in parsed:
        if composite is None:
            continue
        narrative = (composite.get('narrative') or '').strip()
        if not narrative:
            continue
        timeline.append({
            'module': p.module.code,
            'order': p.module.order_index,
            'narrative': narrative,
        })
    return timeline


def _rtm_trajectories(tensions) -> list:
    """Group the RTM tensions by label. Each label carries the teacher's
    self-positioning across the modules where it appeared, in module
    order. Labels seen in more than one module are marked `recurring`
    and sorted first."""
    by_label: dict[str, list] = {}
    for t in tensions:
        by_label.setdefault(t.tension_label, []).append({
            'module': t.module.code,
            'order': t.module.order_index,
            'position': t.selected_position,
            'position_label': t.position_label,
            'confirmed': t.position_confirmed,
        })

    result = []
    for label, points in by_label.items():
        points.sort(key=lambda pt: pt['order'])
        result.append({
            'tension_label': label,
            'recurring': len(points) > 1,
            'points': points,
        })
    result.sort(key=lambda r: (not r['recurring'], r['tension_label']))
    return result


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _tally(counter: Counter, phrase) -> None:
    """Add a normalised, non-empty theme phrase to a counter."""
    normalised = ' '.join(str(phrase).split())
    if normalised:
        counter[normalised] += 1


def _counter_to_list(counter: Counter) -> list:
    """Counter -> list of {theme, count}, most frequent first, then
    alphabetical for a stable, reproducible ordering."""
    return [
        {'theme': theme, 'count': count}
        for theme, count in sorted(
            counter.items(), key=lambda kv: (-kv[1], kv[0]),
        )
    ]
