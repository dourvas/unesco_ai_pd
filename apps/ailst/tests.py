"""
Tests for the AILST instrument.

These tests validate that the EN seed loaded by migration 0002_seed_ailst_en
preserves the invariants required by the validated instrument (Ning et al.
2025). Django's test runner builds a fresh test DB by re-running all
migrations, so these tests catch regressions where the seed JSON or the
loader logic drift from the paper-validated set.
"""

from collections import Counter

from django.test import TestCase

from apps.ailst.models import AilstItem


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
