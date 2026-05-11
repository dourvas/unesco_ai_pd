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

import re
from collections import Counter
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.ailst.models import AilstItem, AilstResponse
from apps.ailst.scoring import compute_factor_scores
from apps.users.models import TeacherProfile


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


# ============================================================================
# C.2.3 view-layer tests
# ============================================================================
#
# Conventions for AILST view tests (mirrors C.2.2 onboarding tests):
#   - Client + force_login on a fresh user.
#   - TeacherProfile pre-populated with ai_disclosure_acknowledged_at and
#     profile_completed=True so AIDisclosureMiddleware passes through.
#   - research_consent True by default; per-test override for D7 gating.
#   - Session has onboarding_step=4 to mirror post-Summary state. Tests
#     of the onboarding gate explicitly clear this.


PAGE_CODES = {
    1: ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'],
    2: ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10'],
    3: ['A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10'],
    4: ['E1', 'E3', 'E4', 'E5', 'E7', 'E8', 'E9', 'E10'],
}


class _AilstViewTestBase(TestCase):
    """Shared setUp for AILST view tests."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ailst_view_user', password='pw')
        self.profile = TeacherProfile.objects.create(
            user=self.user,
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True,
            research_consent=True,
        )
        self.client.force_login(self.user)
        session = self.client.session
        session['onboarding_step'] = 4
        session.save()

    def _set_onboarding_incomplete(self):
        """Roll back the user's state to pre-Summary."""
        self.profile.profile_completed = False
        self.profile.save(update_fields=['profile_completed'])
        session = self.client.session
        session.pop('onboarding_step', None)
        session.save()

    def _post_page(self, page, *, timepoint='t0', answers=None):
        """POST a page form. answers is a dict of paper_code -> int.

        If answers is None, defaults to value 4 for every code on that page.
        """
        if answers is None:
            answers = {code: 4 for code in PAGE_CODES[page]}
        return self.client.post(
            reverse('ailst:page', kwargs={'timepoint': timepoint, 'page': page}),
            data={code: str(value) for code, value in answers.items()},
        )

    def _seed_responses(self, *, timepoint='T0', through_page):
        """Create an AilstResponse with answers filled through `through_page`."""
        responses = {}
        for p in range(1, through_page + 1):
            for code in PAGE_CODES[p]:
                responses[code] = 4
        return AilstResponse.objects.create(
            user=self.user,
            timepoint=timepoint,
            language='en',
            instrument_version='ning_2025_v1',
            responses=responses,
        )


class AilstEntryViewTest(_AilstViewTestBase):

    def test_entry_redirects_when_onboarding_incomplete(self):
        self._set_onboarding_incomplete()
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertRedirects(resp, reverse('users:onboarding_welcome'),
                             fetch_redirect_response=False)

    def test_entry_renders_intro_for_first_visit(self):
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'ailst/intro.html')
        self.assertEqual(
            AilstResponse.objects.filter(user=self.user, timepoint='T0').count(),
            0,
            "Entry GET must not create an AilstResponse row.",
        )

    def test_entry_post_creates_response_and_redirects_to_page_1(self):
        resp = self.client.post(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            AilstResponse.objects.filter(user=self.user, timepoint='T0').exists()
        )

    def test_entry_redirects_to_first_incomplete_page_on_resume(self):
        self._seed_responses(through_page=1)  # 10 answers, page 2 is next
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 2}),
            fetch_redirect_response=False,
        )

    def test_entry_redirects_to_complete_when_done(self):
        resp_row = self._seed_responses(through_page=4)
        resp_row.compute_and_save_scores()
        resp_row.completed_at = timezone.now()
        resp_row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:complete', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )

    def test_invalid_timepoint_returns_404(self):
        resp = self.client.get('/ailst/t9/')
        self.assertEqual(resp.status_code, 404)


class AilstPageViewTest(_AilstViewTestBase):

    def setUp(self):
        super().setUp()
        # Seed an empty AilstResponse so the page view is reachable.
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T0',
            language='en',
            instrument_version='ning_2025_v1',
        )

    def test_get_page_1_renders_10_perception_items(self):
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'ailst/page.html')
        for code in PAGE_CODES[1]:
            self.assertContains(resp, f'name="{code}"')

    def test_post_page_1_valid_redirects_to_page_2(self):
        resp = self._post_page(1)
        self.assertRedirects(
            resp,
            reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 2}),
            fetch_redirect_response=False,
        )
        row = AilstResponse.objects.get(user=self.user, timepoint='T0')
        self.assertEqual(set(row.responses.keys()), set(PAGE_CODES[1]))

    def test_post_page_with_missing_item_re_renders_with_error(self):
        partial = {code: 4 for code in PAGE_CODES[1] if code != 'P5'}
        resp = self.client.post(
            reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}),
            data={code: str(value) for code, value in partial.items()},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'before continuing')
        row = AilstResponse.objects.get(user=self.user, timepoint='T0')
        self.assertEqual(row.responses, {}, "Partial submit must not persist.")

    def test_post_final_page_finalises_and_redirects_to_complete(self):
        for p in range(1, 4):
            self._post_page(p)
        resp = self._post_page(4)
        self.assertRedirects(
            resp,
            reverse('ailst:complete', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )
        row = AilstResponse.objects.get(user=self.user, timepoint='T0')
        self.assertIsNotNone(row.completed_at)
        self.assertIsNotNone(row.perception_score)
        self.assertIsNotNone(row.overall_score)

    def test_resume_pre_populates_form_with_stored_answers(self):
        # Manually seed page 1 partially via direct row update.
        row = AilstResponse.objects.get(user=self.user, timepoint='T0')
        row.responses = {code: 5 for code in PAGE_CODES[1]}
        row.save(update_fields=['responses'])
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        body = resp.content.decode('utf-8')
        # Each P-field's value=5 radio must be the checked one. Django
        # may serialise attributes in any order, so match within an input tag.
        for code in PAGE_CODES[1]:
            pattern = (
                r'<input[^>]*\bname="' + re.escape(code)
                + r'"[^>]*\bvalue="5"[^>]*\bchecked\b'
                + r'|<input[^>]*\bvalue="5"[^>]*\bname="' + re.escape(code)
                + r'"[^>]*\bchecked\b'
                + r'|<input[^>]*\bchecked\b[^>]*\bname="' + re.escape(code)
                + r'"[^>]*\bvalue="5"'
            )
            self.assertRegex(
                body, pattern,
                f'Expected the value="5" radio for {code} to be checked on resume.',
            )

    def test_invalid_page_number_returns_404(self):
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 9}))
        self.assertEqual(resp.status_code, 404)


class AilstStateMachineTest(_AilstViewTestBase):

    def test_skip_ahead_redirects_to_first_incomplete(self):
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T0',
            language='en',
            instrument_version='ning_2025_v1',
        )
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 3}))
        self.assertRedirects(
            resp,
            reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}),
            fetch_redirect_response=False,
        )

    def test_back_to_completed_page_is_allowed_and_pre_populates(self):
        self._seed_responses(through_page=2)  # pages 1 and 2 fully answered
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        # Spot-check P1: stored value=4 must be the pre-checked radio.
        pattern = (
            r'<input[^>]*\bname="P1"[^>]*\bvalue="4"[^>]*\bchecked\b'
            r'|<input[^>]*\bvalue="4"[^>]*\bname="P1"[^>]*\bchecked\b'
            r'|<input[^>]*\bchecked\b[^>]*\bname="P1"[^>]*\bvalue="4"'
        )
        self.assertRegex(body, pattern)

    def test_completed_response_redirects_from_page_view(self):
        row = self._seed_responses(through_page=4)
        row.compute_and_save_scores()
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        self.assertRedirects(
            resp,
            reverse('ailst:complete', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )


class AilstResearchConsentGatingTest(_AilstViewTestBase):
    """D7 gating: research_consent=False blocks AILST entry on every route.

    GDPR / IRB rationale: AILST is the primary research instrument;
    collecting responses without active research_participation consent
    would breach Article 9 special-category data requirements.
    """

    def _revoke_consent(self):
        self.profile.research_consent = False
        self.profile.save(update_fields=['research_consent'])

    def test_entry_redirects_to_research_consent_required(self):
        self._revoke_consent()
        resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:research_consent_required', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )

    def test_page_view_redirects_to_research_consent_required(self):
        self._revoke_consent()
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        self.assertRedirects(
            resp,
            reverse('ailst:research_consent_required', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )

    def test_partial_responses_preserved_on_consent_revocation(self):
        """No auto-delete: GDPR audit trail and user-work preservation."""
        seeded = self._seed_responses(through_page=1)
        self._revoke_consent()
        # User hits AILST → blocked, but row must still exist.
        self.client.get(reverse('ailst:entry', kwargs={'timepoint': 't0'}))
        self.assertTrue(
            AilstResponse.objects.filter(pk=seeded.pk).exists(),
            "Partial AilstResponse must NOT be auto-deleted on consent revoke.",
        )

    def test_consent_required_page_renders(self):
        self._revoke_consent()
        resp = self.client.get(
            reverse('ailst:research_consent_required', kwargs={'timepoint': 't0'})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'ailst/research_consent_required.html')


class AilstCompleteViewTest(_AilstViewTestBase):

    def test_complete_renders_for_completed_response(self):
        row = self._seed_responses(through_page=4)
        row.compute_and_save_scores()
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('ailst:complete', kwargs={'timepoint': 't0'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'ailst/complete.html')

    def test_complete_404_for_incomplete_response(self):
        self._seed_responses(through_page=2)  # not completed
        resp = self.client.get(reverse('ailst:complete', kwargs={'timepoint': 't0'}))
        self.assertEqual(resp.status_code, 404)

    def test_complete_does_not_show_factor_scores(self):
        """D4: scores hidden during pilot for all timepoints (TD-010)."""
        row = self._seed_responses(through_page=4)
        row.compute_and_save_scores()
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('ailst:complete', kwargs={'timepoint': 't0'}))
        body = resp.content.decode('utf-8')
        # Decimal-formatted scores must not leak into the page.
        for label in ('perception_score', '4.00', '4.50', '4.65', 'AI Perception'):
            self.assertNotIn(
                label, body,
                f"Score-related token {label!r} must not appear on T0 complete page.",
            )


class AilstRestartViewTest(_AilstViewTestBase):

    def test_restart_post_deletes_partial_and_redirects_to_entry(self):
        seeded = self._seed_responses(through_page=2)
        resp = self.client.post(reverse('ailst:restart', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:entry', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )
        self.assertFalse(AilstResponse.objects.filter(pk=seeded.pk).exists())

    def test_restart_get_redirects_without_deleting(self):
        seeded = self._seed_responses(through_page=2)
        resp = self.client.get(reverse('ailst:restart', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:entry', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )
        self.assertTrue(AilstResponse.objects.filter(pk=seeded.pk).exists())

    def test_restart_does_not_delete_completed_response(self):
        row = self._seed_responses(through_page=4)
        row.compute_and_save_scores()
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.post(reverse('ailst:restart', kwargs={'timepoint': 't0'}))
        self.assertRedirects(
            resp,
            reverse('ailst:complete', kwargs={'timepoint': 't0'}),
            fetch_redirect_response=False,
        )
        self.assertTrue(AilstResponse.objects.filter(pk=row.pk).exists())


class AilstTimepointParameterisationTest(_AilstViewTestBase):

    def test_t1_and_t2_routes_resolve(self):
        for tp_url in ('t1', 't2'):
            resp = self.client.get(reverse('ailst:entry', kwargs={'timepoint': tp_url}))
            # First visit (no row) → intro page rendered, 200.
            self.assertEqual(
                resp.status_code, 200,
                f"Entry view must work for timepoint {tp_url}",
            )
            self.assertTemplateUsed(resp, 'ailst/intro.html')

    def test_t1_complete_flow_persists_with_correct_timepoint(self):
        self.client.post(reverse('ailst:entry', kwargs={'timepoint': 't1'}))
        for p in range(1, 4):
            self._post_page(p, timepoint='t1')
        self._post_page(4, timepoint='t1')
        row = AilstResponse.objects.get(user=self.user, timepoint='T1')
        self.assertIsNotNone(row.completed_at)


class AilstMobileLikertRenderTest(_AilstViewTestBase):
    """CP 5: full anchors must appear at every breakpoint, not numeric only."""

    def test_page_renders_all_five_verbal_anchors(self):
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T0',
            language='en',
            instrument_version='ning_2025_v1',
        )
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        body = resp.content.decode('utf-8')
        for anchor in (
            'Fully applicable',
            'Applicable',
            'Uncertain',
            'Not applicable',
            'Completely not applicable',
        ):
            self.assertIn(
                anchor, body,
                f"Anchor {anchor!r} must be rendered (CP 5: full anchors required).",
            )


class AilstTemplateCommentLeakTest(_AilstViewTestBase):
    """Regression for the multi-line {# ... #} comment leak bug found in
    browser smoke test (2026-05-10). Django's {# ... #} is single-line only;
    multi-line comments must use {% comment %} ... {% endcomment %} or they
    render as plain text in the page body."""

    def _assert_no_comment_leak(self, body, *, where):
        # Specific phrases that appear inside our template comments. If any
        # of these appear in rendered HTML, a {# ... #} multi-line was used
        # by mistake. (We intentionally check for the comment-text contents
        # rather than the {# delimiter so the test catches the actual leak.)
        leaked_phrases = (
            'Single AILST item: prompt text on the left',
            'Per C.2.3 design decision D4',
            'Desktop (md+): two-column grid',
            '{% comment %}',
            '{% endcomment %}',
        )
        for phrase in leaked_phrases:
            self.assertNotIn(
                phrase, body,
                f"Template-comment text {phrase!r} leaked into rendered "
                f"HTML on {where}. Multi-line Django comments must use "
                f"{{% comment %}}...{{% endcomment %}}, not {{# ... #}}.",
            )

    def test_page_template_does_not_leak_comments(self):
        AilstResponse.objects.create(
            user=self.user,
            timepoint='T0',
            language='en',
            instrument_version='ning_2025_v1',
        )
        resp = self.client.get(reverse('ailst:page', kwargs={'timepoint': 't0', 'page': 1}))
        self._assert_no_comment_leak(resp.content.decode('utf-8'), where='page.html')

    def test_complete_template_does_not_leak_comments(self):
        row = self._seed_responses(through_page=4)
        row.compute_and_save_scores()
        row.completed_at = timezone.now()
        row.save(update_fields=['completed_at'])
        resp = self.client.get(reverse('ailst:complete', kwargs={'timepoint': 't0'}))
        self._assert_no_comment_leak(resp.content.decode('utf-8'), where='complete.html')
