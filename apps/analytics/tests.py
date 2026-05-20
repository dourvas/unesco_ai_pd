"""
Tests for the D.1 AI Output Relevance Profile aggregation services.

These verify the read-only aggregation logic over AIOutputDispute:
per-feature and per-teacher tallies, the reason breakdown, and — the
load-bearing construct guard — that 'peer' rows are excluded from the
relevance profile and surface only in peer_usefulness_summary().
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.analytics import services
from apps.modules.models import (
    AIOutputDispute,
    Module,
    ReflectionTension,
    UserModuleProgress,
)
from apps.users.models import TeacherProfile


class RelevanceProfileServiceTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user('analytics_a', password='pw')
        cls.user_b = User.objects.create_user('analytics_b', password='pw')
        TeacherProfile.objects.create(
            user=cls.user_a, subject_area='mathematics',
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        TeacherProfile.objects.create(
            user=cls.user_b, subject_area='science',
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        cls.m1 = Module.objects.create(
            code='AN1', title='Analytics module 1', description='t',
            order_index=940, unesco_aspect='ethics',
            proficiency_level='Acquire', is_published=True,
        )
        cls.m2 = Module.objects.create(
            code='AN2', title='Analytics module 2', description='t',
            order_index=941, unesco_aspect='ethics',
            proficiency_level='Acquire', is_published=True,
        )

        def dispute(user, module, feature, rating, reason=None):
            return AIOutputDispute.objects.create(
                user=user, module=module, feature_type=feature,
                rating=rating, reason=reason,
            )

        # Alignment features (rag/rtm/dtp) — these feed the profile.
        dispute(cls.user_a, cls.m1, 'rag', 'yes')
        dispute(cls.user_a, cls.m2, 'rag', 'no', reason='generic')
        dispute(cls.user_a, cls.m1, 'rtm', 'partial', reason='mismatch')
        dispute(cls.user_a, cls.m1, 'dtp', 'yes')
        dispute(cls.user_b, cls.m1, 'rag', 'yes')
        dispute(cls.user_b, cls.m2, 'rag', 'partial', reason='pedagogical')
        # Peer — a different construct; must NOT enter the profile.
        dispute(cls.user_a, cls.m1, 'peer', 'no')
        dispute(cls.user_b, cls.m1, 'peer', 'yes')

    # ------------------------------------------------------------------
    # Cohort profile
    # ------------------------------------------------------------------
    def test_cohort_by_feature_counts_and_rate(self):
        profile = services.cohort_relevance_profile()
        rag = profile['by_feature']['rag']
        self.assertEqual((rag['yes'], rag['partial'], rag['no']), (2, 1, 1))
        self.assertEqual(rag['total'], 4)
        self.assertEqual(rag['relevance_rate'], 0.5)

        dtp = profile['by_feature']['dtp']
        self.assertEqual(dtp['total'], 1)
        self.assertEqual(dtp['relevance_rate'], 1.0)

    def test_peer_rows_excluded_from_cohort_profile(self):
        """The two peer rows must not inflate any alignment tally."""
        profile = services.cohort_relevance_profile()
        # 6 alignment ratings exist; the 2 peer rows are not counted.
        self.assertEqual(profile['totals']['ratings'], 6)
        self.assertNotIn('peer', profile['by_feature'])

    def test_cohort_reason_breakdown(self):
        profile = services.cohort_relevance_profile()
        self.assertEqual(
            profile['reasons'],
            {'generic': 1, 'mismatch': 1, 'pedagogical': 1},
        )

    def test_cohort_slices_by_module_and_subject(self):
        profile = services.cohort_relevance_profile()
        module_codes = {m['module_code'] for m in profile['by_module']}
        self.assertEqual(module_codes, {'AN1', 'AN2'})
        subjects = {s['subject'] for s in profile['by_subject']}
        self.assertEqual(subjects, {'mathematics', 'science'})

    # ------------------------------------------------------------------
    # Per-teacher profiles
    # ------------------------------------------------------------------
    def test_per_teacher_profiles_group_by_teacher(self):
        profiles = services.per_teacher_relevance_profiles()
        self.assertEqual(len(profiles), 2)
        by_name = {p['username']: p for p in profiles}

        a = by_name['analytics_a']
        self.assertEqual(a['features']['rag']['total'], 2)
        self.assertEqual(a['features']['dtp']['yes'], 1)
        self.assertEqual(a['reasons'], {'generic': 1, 'mismatch': 1})

        b = by_name['analytics_b']
        self.assertEqual(b['features']['rag']['total'], 2)
        self.assertEqual(b['features']['dtp']['total'], 0)

    def test_per_teacher_coverage_counts_completed_modules(self):
        UserModuleProgress.objects.create(
            user=self.user_a, module=self.m1,
            completed_at=timezone.now(),
        )
        profiles = services.per_teacher_relevance_profiles()
        a = next(p for p in profiles if p['username'] == 'analytics_a')
        # user_a rated in 2 distinct modules, completed 1.
        self.assertEqual(a['rated_modules'], 2)
        self.assertEqual(a['completed_modules'], 1)

    # ------------------------------------------------------------------
    # Peer usefulness — separate construct
    # ------------------------------------------------------------------
    def test_peer_usefulness_summary_counts_peer_only(self):
        summary = services.peer_usefulness_summary()
        self.assertEqual(summary['yes'], 1)
        self.assertEqual(summary['no'], 1)
        self.assertEqual(summary['total'], 2)
        self.assertEqual(summary['relevance_rate'], 0.5)


class ResearchAnalyticsViewTest(TestCase):
    """The staff analytics dashboard: staff-gated, renders both the D.1
    relevance-profile and the D.2 engagement-depth sections, and keeps
    the peer panel visibly separate from the relevance profile."""

    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            'analytics_staff', password='pw', is_staff=True,
        )
        # A disclosure-acknowledged profile so the AI-disclosure
        # middleware does not redirect the staff request.
        TeacherProfile.objects.create(
            user=self.staff, ai_disclosure_acknowledged_at=timezone.now(),
        )
        self.url = reverse('analytics:dashboard')

    def test_staff_user_can_view_the_dashboard(self):
        self.client.force_login(self.staff)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        # Both Phase D sections render on the one page.
        self.assertContains(resp, 'AI Output Relevance Profile')
        self.assertContains(resp, 'Engagement Depth')
        # The peer usefulness panel is present and flagged as separate.
        self.assertContains(resp, 'usefulness signal')

    def test_non_staff_user_is_redirected(self):
        non_staff = User.objects.create_user(
            'analytics_plain', password='pw', is_staff=False,
        )
        TeacherProfile.objects.create(
            user=non_staff, ai_disclosure_acknowledged_at=timezone.now(),
        )
        self.client.force_login(non_staff)
        resp = self.client.get(self.url)
        # staff_member_required bounces a non-staff user — not a 200.
        self.assertEqual(resp.status_code, 302)

    def test_anonymous_user_is_redirected(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class EngagementDepthServiceTest(TestCase):
    """D.2 — the engagement-depth aggregation over ReflectionTension.

    Verifies the headline EDS (confirmed / total), the supporting
    signals (comment-use rate, non-neutral rate, median time) and the
    per-teacher grouping.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user('eds_a', password='pw')
        cls.user_b = User.objects.create_user('eds_b', password='pw')
        TeacherProfile.objects.create(
            user=cls.user_a, subject_area='mathematics',
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        TeacherProfile.objects.create(
            user=cls.user_b, subject_area='science',
            ai_disclosure_acknowledged_at=timezone.now(),
        )
        cls.m1 = Module.objects.create(
            code='ED1', title='Engagement module 1', description='t',
            order_index=950, unesco_aspect='ethics',
            proficiency_level='Acquire', is_published=True,
        )

        def tension(user, label, position, confirmed, commented, time_ms):
            return ReflectionTension.objects.create(
                user=user, module=cls.m1, tension_label=label,
                left_pole='L', right_pole='R', grounding_quote='q',
                selected_position=position, position_confirmed=confirmed,
                comment_used=commented, time_spent_ms=time_ms,
            )

        # user_a — 3 tensions: 2 confirmed (one non-neutral, one neutral),
        # 1 not confirmed.
        tension(cls.user_a, 'a-t1', 5, True, True, 4000)
        tension(cls.user_a, 'a-t2', 3, True, False, 2000)
        tension(cls.user_a, 'a-t3', 3, False, False, 500)
        # user_b — 2 tensions, both confirmed and non-neutral.
        tension(cls.user_b, 'b-t1', 4, True, False, 3000)
        tension(cls.user_b, 'b-t2', 2, True, False, 1000)

    def test_cohort_eds_headline(self):
        depth = services.cohort_engagement_depth()
        self.assertEqual(depth['total_tensions'], 5)
        self.assertEqual(depth['confirmed'], 4)
        self.assertEqual(depth['eds'], 0.8)

    def test_cohort_supporting_signals(self):
        depth = services.cohort_engagement_depth()
        # 3 of the 4 confirmed tensions are off the neutral mid-point.
        self.assertEqual(depth['non_neutral_rate'], 0.75)
        # 1 of 5 tensions carried a comment.
        self.assertEqual(depth['comment_use_rate'], 0.2)
        self.assertEqual(depth['median_time_ms'], 2000)

    def test_cohort_slices(self):
        depth = services.cohort_engagement_depth()
        self.assertEqual({m['module_code'] for m in depth['by_module']}, {'ED1'})
        self.assertEqual(
            {s['subject'] for s in depth['by_subject']},
            {'mathematics', 'science'},
        )

    def test_per_teacher_engagement_depth(self):
        profiles = services.per_teacher_engagement_depth()
        by_name = {p['username']: p for p in profiles}

        a = by_name['eds_a']
        self.assertEqual(a['total'], 3)
        self.assertEqual(a['confirmed'], 2)
        self.assertEqual(a['eds'], 0.667)
        # One of the two confirmed tensions is non-neutral.
        self.assertEqual(a['non_neutral_rate'], 0.5)

        b = by_name['eds_b']
        self.assertEqual(b['eds'], 1.0)
        self.assertEqual(b['non_neutral_rate'], 1.0)


class AnalyticsFilterTest(TestCase):
    """The _scope filter: the unconditional research-consent restriction,
    and the optional date-range and subject filters — applied uniformly
    to the D.1 and D.2 aggregations."""

    @classmethod
    def setUpTestData(cls):
        cls.module = Module.objects.create(
            code='FLT', title='Filter test module', description='t',
            order_index=960, unesco_aspect='ethics',
            proficiency_level='Acquire', is_published=True,
        )

        def teacher(username, subject, consent):
            user = User.objects.create_user(username, password='pw')
            TeacherProfile.objects.create(
                user=user, subject_area=subject, research_consent=consent,
                ai_disclosure_acknowledged_at=timezone.now(),
            )
            return user

        cls.maths = teacher('flt_maths', 'mathematics', True)
        cls.science = teacher('flt_science', 'science', True)
        cls.noconsent = teacher('flt_noconsent', 'mathematics', False)

    def _dispute(self, user, feature='rag', rating='yes'):
        return AIOutputDispute.objects.create(
            user=user, module=self.module, feature_type=feature,
            rating=rating,
        )

    def test_consent_filter_excludes_non_consenting(self):
        self._dispute(self.maths)
        self._dispute(self.noconsent)
        profile = services.cohort_relevance_profile()
        # Only the consenting teacher's rating is counted.
        self.assertEqual(profile['totals']['ratings'], 1)

    def test_subject_filter_narrows_to_one_subject(self):
        self._dispute(self.maths)
        self._dispute(self.science)
        profile = services.cohort_relevance_profile(
            filters={'subject': 'mathematics'},
        )
        self.assertEqual(profile['totals']['ratings'], 1)

    def test_date_filter_window(self):
        self._dispute(self.maths)
        old = self._dispute(self.science)
        # Push the science rating two months back (created_at is
        # auto_now_add, so it must be set with an UPDATE).
        AIOutputDispute.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=60),
        )
        last_week = (timezone.now() - timedelta(days=7)).date()
        profile = services.cohort_relevance_profile(
            filters={'start': last_week},
        )
        # Only the recent rating falls inside the window.
        self.assertEqual(profile['totals']['ratings'], 1)

    def test_consent_filter_applies_to_engagement_depth(self):
        def tension(user, label):
            ReflectionTension.objects.create(
                user=user, module=self.module, tension_label=label,
                left_pole='L', right_pole='R', grounding_quote='q',
                selected_position=4, position_confirmed=True,
            )

        tension(self.maths, 't-consenting')
        tension(self.noconsent, 't-noconsent')
        depth = services.cohort_engagement_depth()
        # The non-consenting teacher's tension is excluded.
        self.assertEqual(depth['total_tensions'], 1)
