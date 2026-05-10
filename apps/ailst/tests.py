"""
Tests for the AILST instrument.

These tests validate that the EN seed loaded by migration 0002_seed_ailst_en
preserves the invariants required by the validated instrument (Ning et al.
2025). Django's test runner builds a fresh test DB by re-running all
migrations, so these tests catch regressions where the seed JSON or the
loader logic drift from the paper-validated set.

M5 adds two more test classes: ScoringTest (pure-function correctness for
apps.ailst.scoring.compute_factor_scores) and AilstResponseLifecycleTest
(model constraints, state machine, idempotency).
"""

from collections import Counter
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.utils import timezone

from apps.ailst.models import AilstItem, AilstResponse
from apps.ailst.scoring import compute_factor_scores


EN_V1_FILTER = {'language': 'en', 'instrument_version': 'ning_2025_v1'}

EXPECTED_PAPER_CODES = {
    'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10',
    'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10',
    'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10',
    'E1', 'E3', 'E4', 'E5', 'E7', 'E8', 'E9', 'E10',
}
EXPECTED_REVERSE_CODES = {'K1', 'A3', 'E3'}
EXPECTED_FACTOR_COUNTS = {
    'perception': 10,
    'knowledge_skills': 10,
    'applications_innovation': 8,
    'ethics': 8,
}


class AilstSeedInvariantsTest(TestCase):
    """Migration 0002 must produce a 36-item EN seed that matches the
    Ning et al. 2025 validated instrument exactly. Any drift here
    invalidates downstream T0/T1/T2 measurement.
    """

    def test_seed_total_count_is_36(self):
        self.assertEqual(
            AilstItem.objects.filter(**EN_V1_FILTER).count(),
            36,
            "EN/v1 seed must contain exactly 36 items.",
        )

    def test_paper_codes_match_expected_set(self):
        actual = set(
            AilstItem.objects.filter(**EN_V1_FILTER).values_list('paper_code', flat=True)
        )
        self.assertEqual(
            actual,
            EXPECTED_PAPER_CODES,
            "EN/v1 paper_codes must match the paper-validated 36-code set "
            "(P1-P10, K1-K10, A3-A10, E1+E3-E5+E7-E10).",
        )

    def test_reverse_scored_set_is_K1_A3_E3(self):
        actual = set(
            AilstItem.objects.filter(is_reverse_scored=True, **EN_V1_FILTER)
            .values_list('paper_code', flat=True)
        )
        self.assertEqual(
            actual,
            EXPECTED_REVERSE_CODES,
            "Reverse-scored set must be exactly {K1, A3, E3}. Drift here "
            "would invert scoring direction and corrupt all subsequent analyses.",
        )

    def test_per_factor_counts(self):
        actual = dict(Counter(
            AilstItem.objects.filter(**EN_V1_FILTER).values_list('factor', flat=True)
        ))
        self.assertEqual(
            actual,
            EXPECTED_FACTOR_COUNTS,
            "Factor distribution must be perception=10, knowledge_skills=10, "
            "applications_innovation=8, ethics=8.",
        )

    def test_item_numbers_are_1_to_36_no_gaps(self):
        numbers = list(
            AilstItem.objects.filter(**EN_V1_FILTER)
            .order_by('item_number').values_list('item_number', flat=True)
        )
        self.assertEqual(
            numbers,
            list(range(1, 37)),
            "item_number must be a monotonic 1-36 sequence with no gaps.",
        )

    def test_factor_grouping_by_item_number_block(self):
        """Verify the block layout: 1-10 perception, 11-20 knowledge_skills,
        21-28 applications_innovation, 29-36 ethics.
        """
        blocks = {
            'perception':              range(1, 11),
            'knowledge_skills':        range(11, 21),
            'applications_innovation': range(21, 29),
            'ethics':                  range(29, 37),
        }
        for factor, expected_range in blocks.items():
            actual_numbers = sorted(
                AilstItem.objects.filter(factor=factor, **EN_V1_FILTER)
                .values_list('item_number', flat=True)
            )
            self.assertEqual(
                actual_numbers,
                list(expected_range),
                f"Factor '{factor}' should occupy item_numbers {list(expected_range)}.",
            )

    def test_reverse_items_have_negation_wording(self):
        """Spot-check: each reverse item's text contains a negation marker.
        Defensive check against accidental swap of texts between rows.
        """
        markers = {
            'K1': 'not fully versed',
            'A3': "don't know",
            'E3': 'rely entirely',
        }
        for code, marker in markers.items():
            item = AilstItem.objects.get(paper_code=code, **EN_V1_FILTER)
            self.assertIn(
                marker,
                item.item_text,
                f"{code} must contain its negation marker '{marker}' "
                "to remain semantically reverse-coded.",
            )


class ScoringTest(TestCase):
    """Validates compute_factor_scores correctness against CP 5 + CP 6.

    The seeded AilstItem rows from migration 0002 are reused as the
    reverse-scoring + factor lookup ground truth.
    """

    def setUp(self):
        self.items_by_code = {
            it.paper_code: it
            for it in AilstItem.objects.filter(**EN_V1_FILTER)
        }

    def test_anchor_mapping_high_value_means_high_tail(self):
        """Regression test for CP 5: 5='Fully applicable' yields high TAIL.

        TRUE perfect-score scenario:
          - positive items: raw=5 ('Fully applicable')
          - reverse items K1/A3/E3: raw=1 ('Completely not applicable' to
            the negation, i.e., 'I disagree that I am NOT versed' which
            implies high TAIL after reversal)
        After reversal: all 36 contribute 5.
        Mean per factor: 5.00 across all four. Overall: 5.00.

        This test fails if anchor mapping is ever flipped (e.g., (6 - raw)
        becomes (raw - 6) or storage interprets 1 as high-applicability).
        Load-bearing test for the entire dissertation analysis chain.
        """
        responses = {
            code: (1 if code in EXPECTED_REVERSE_CODES else 5)
            for code in EXPECTED_PAPER_CODES
        }
        scores = compute_factor_scores(responses, self.items_by_code)
        self.assertEqual(scores['perception_score'], Decimal('5.00'))
        self.assertEqual(scores['knowledge_skills_score'], Decimal('5.00'))
        self.assertEqual(scores['applications_innovation_score'], Decimal('5.00'))
        self.assertEqual(scores['ethics_score'], Decimal('5.00'))
        self.assertEqual(scores['overall_score'], Decimal('5.00'))

    def test_all_fully_applicable_yields_mixed_scores(self):
        """All raw=5 represents a teacher who AGREES with EVERY statement,
        including the negation-phrased K1/A3/E3.

        This is NOT a 'perfect score' scenario - agreeing with K1
        ('I am NOT fully versed') means LOW TAIL on knowledge.

        After reverse-scoring:
          - 33 positive items: scored=5
          - 3 reverse items (K1, A3, E3): scored=(6-5)=1
        Means per factor:
          - P (10 positive):                5.00
          - K (9 positive + K1 reversed):   (9*5 + 1)/10 = 4.60
          - A (7 positive + A3 reversed):   (7*5 + 1)/8  = 4.50
          - E (7 positive + E3 reversed):   (7*5 + 1)/8  = 4.50
        Overall:                            mean of factor means = 4.65
        """
        responses = {code: 5 for code in EXPECTED_PAPER_CODES}
        scores = compute_factor_scores(responses, self.items_by_code)
        self.assertEqual(scores['perception_score'], Decimal('5.00'))
        self.assertEqual(scores['knowledge_skills_score'], Decimal('4.60'))
        self.assertEqual(scores['applications_innovation_score'], Decimal('4.50'))
        self.assertEqual(scores['ethics_score'], Decimal('4.50'))
        self.assertEqual(scores['overall_score'], Decimal('4.65'))

    def test_partial_responses_yield_partial_scores_and_none_overall(self):
        """Only P1-P10 answered: only perception_score is non-None.
        Defensive check: overall_score is None if any factor lacks data.
        """
        responses = {f'P{i}': 4 for i in range(1, 11)}
        scores = compute_factor_scores(responses, self.items_by_code)
        self.assertEqual(scores['perception_score'], Decimal('4.00'))
        self.assertIsNone(scores['knowledge_skills_score'])
        self.assertIsNone(scores['applications_innovation_score'])
        self.assertIsNone(scores['ethics_score'])
        self.assertIsNone(
            scores['overall_score'],
            "overall_score must be None when any factor lacks responses.",
        )

    def test_invalid_response_key_raises(self):
        """Response key not present in items_by_code raises ValueError."""
        responses = {'P1': 4, 'foo': 3}
        with self.assertRaises(ValueError):
            compute_factor_scores(responses, self.items_by_code)

    def test_out_of_range_response_value_raises(self):
        """Response value outside [1, 5] raises ValueError."""
        responses = {'P1': 9}
        with self.assertRaises(ValueError):
            compute_factor_scores(responses, self.items_by_code)


class AilstResponseLifecycleTest(TestCase):
    """Tests for AilstResponse model constraints and lifecycle."""

    def setUp(self):
        self.user = User.objects.create_user(username='ailst_test', password='x')

    def test_unique_user_timepoint_constraint(self):
        """Cannot have two AilstResponse rows for the same (user, timepoint)."""
        AilstResponse.objects.create(user=self.user, timepoint='T0')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AilstResponse.objects.create(user=self.user, timepoint='T0')

    def test_db_check_rejects_invalid_timepoint(self):
        """DB-level CHECK constraint rejects timepoint outside {T0, T1, T2}.

        Bypasses Django choices validation by inserting raw SQL with a
        bogus timepoint value. CHECK must catch it.
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic(), connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO ailst_responses "
                    "(user_id, timepoint, language, instrument_version, "
                    "responses, started_at, last_saved_at) "
                    "VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                    [self.user.id, 'T9', 'en', 'ning_2025_v1', '{}'],
                )

    def test_partial_then_complete_lifecycle(self):
        """Lifecycle: empty -> partial -> complete with scores filled."""
        resp = AilstResponse.objects.create(user=self.user, timepoint='T0')
        self.assertEqual(resp.responses, {})
        self.assertIsNone(resp.completed_at)
        self.assertIsNone(resp.perception_score)

        # Full submission of valid responses (perfect-score scenario)
        resp.responses = {
            code: (1 if code in EXPECTED_REVERSE_CODES else 5)
            for code in EXPECTED_PAPER_CODES
        }
        resp.save()
        resp.compute_and_save_scores()
        resp.completed_at = timezone.now()
        resp.save()

        resp.refresh_from_db()
        self.assertEqual(resp.perception_score, Decimal('5.00'))
        self.assertEqual(resp.overall_score, Decimal('5.00'))
        self.assertIsNotNone(resp.completed_at)

    def test_compute_and_save_scores_is_idempotent(self):
        """Running compute twice on unchanged responses gives identical scores."""
        resp = AilstResponse.objects.create(user=self.user, timepoint='T0')
        resp.responses = {code: 4 for code in EXPECTED_PAPER_CODES}
        resp.save()

        resp.compute_and_save_scores()
        resp.refresh_from_db()
        first = (
            resp.perception_score, resp.knowledge_skills_score,
            resp.applications_innovation_score, resp.ethics_score,
            resp.overall_score,
        )

        resp.compute_and_save_scores()
        resp.refresh_from_db()
        second = (
            resp.perception_score, resp.knowledge_skills_score,
            resp.applications_innovation_score, resp.ethics_score,
            resp.overall_score,
        )
        self.assertEqual(first, second)
