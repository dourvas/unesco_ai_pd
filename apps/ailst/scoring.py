"""
AILST scoring logic — pure functions for unit testability.

Per CP 5 + CP 6 decisions (chat session 2026-05-09):
  - Anchor mapping: 5='Fully applicable', 1='Completely not applicable',
    higher final score = higher TAIL (Teacher AI Literacy).
  - Storage: raw 1-5 in `responses` JSONB.
  - Reverse-scoring (scored = 6 - raw) applies ONLY to the 3 negation-framed
    items: K1, A3, E3.
  - Factor score = mean of scored values within the factor.
  - Overall score = mean of factor means (NOT mean of items). This gives
    each of the 4 factors equal weight, consistent with the paper's
    theoretical 4-factor structure. Mean-of-items would impose
    28/28/22/22 weighting from item count alone.
  - Defensive: if any factor lacks a score (e.g., partial response),
    overall is also None. The four factors are mutually-required for
    a valid overall.
"""

from decimal import Decimal, ROUND_HALF_UP


FACTORS = ('perception', 'knowledge_skills', 'applications_innovation', 'ethics')


def _quantize_mean(values):
    """Mean of a non-empty list, rounded to 2 decimals (HALF_UP).

    Returns None for empty input.
    """
    if not values:
        return None
    mean = sum(values) / len(values)
    return Decimal(str(mean)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def compute_factor_scores(responses, items_by_code):
    """Compute factor and overall scores from raw responses.

    Args:
        responses: dict like {"P1": 4, "K10": 2, ...} with int 1-5 values.
        items_by_code: dict {paper_code: AilstItem-like} with attributes
            `is_reverse_scored` (bool) and `factor` (str). Provides the
            metadata for reverse-scoring and factor grouping.

    Returns:
        dict with keys:
            perception_score, knowledge_skills_score,
            applications_innovation_score, ethics_score,
            overall_score
        Values are Decimal('X.YY') or None.
        overall_score is None if any factor score is None.

    Raises:
        ValueError: if a response key is not present in items_by_code, or
            if a response value is not an int in [1, 5].
    """
    by_factor = {f: [] for f in FACTORS}

    for code, raw in responses.items():
        item = items_by_code.get(code)
        if item is None:
            raise ValueError(
                f"Response key '{code}' not present in items table for the "
                "given language/instrument_version. Refusing to score."
            )
        if not isinstance(raw, int) or not 1 <= raw <= 5:
            raise ValueError(
                f"Response value for '{code}' out of range: {raw!r}. "
                "Expected int in [1, 5]."
            )
        scored = (6 - raw) if item.is_reverse_scored else raw
        by_factor[item.factor].append(scored)

    factor_means = {factor: _quantize_mean(vals) for factor, vals in by_factor.items()}

    # Overall = mean of factor means, IF all four factors have scores.
    # Defensive: partial response (any factor None) yields overall=None.
    if all(v is not None for v in factor_means.values()):
        overall_raw = sum(factor_means.values()) / Decimal(len(FACTORS))
        overall = overall_raw.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        overall = None

    return {
        'perception_score': factor_means['perception'],
        'knowledge_skills_score': factor_means['knowledge_skills'],
        'applications_innovation_score': factor_means['applications_innovation'],
        'ethics_score': factor_means['ethics'],
        'overall_score': overall,
    }
