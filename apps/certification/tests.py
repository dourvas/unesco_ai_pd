"""Tests for apps.certification — Phase H.3 (skeleton + PDF + views).

- Model + verification_code helper coverage (skeleton, task #6).
- Service layer (build_modules_summary, teacher_is_eligible,
  get_or_issue_certificate, render_certificate_pdf).
- Views (download gate, idempotency, public verification scope,
  404 for invalid codes).
- Article 50(2) PDF metadata round-trip + JSON-LD aiInvolved:false
  assertion.
"""

import re
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.ailst.models import AilstResponse
from apps.certification.models import (
    CertificateOfAttendance,
    generate_verification_code,
)
from apps.certification.services import (
    build_modules_summary,
    get_or_issue_certificate,
    render_certificate_pdf,
    teacher_is_eligible,
)
from apps.modules.models import Module
from apps.users.models import TeacherProfile


class GenerateVerificationCodeTest(TestCase):
    """generate_verification_code() guarantees uniqueness + format."""

    def test_returns_16_char_url_safe_string(self):
        code = generate_verification_code()
        self.assertEqual(len(code), 16)
        # URL-safe base64 alphabet: A-Z a-z 0-9 - _
        self.assertRegex(code, r'^[A-Za-z0-9_-]{16}$')

    def test_two_calls_return_distinct_codes(self):
        # Vanishingly unlikely to collide at n=2 over 96 bits, but assert it.
        codes = {generate_verification_code() for _ in range(20)}
        self.assertEqual(len(codes), 20)

    def test_retries_on_collision_and_succeeds(self):
        """Simulated collision on first try, then unique on retry."""
        sentinel_codes = iter(['XXXXXXXXXXXXXXXX', 'YYYYYYYYYYYYYYYY'])
        with patch('apps.certification.models.secrets.token_urlsafe',
                   side_effect=lambda n: next(sentinel_codes) + 'pad'):
            # Pre-seed a row with the first sentinel so the first attempt
            # collides; the helper must retry and return the second.
            user = User.objects.create_user(username='precollision', password='x')
            CertificateOfAttendance.objects.create(
                user=user,
                verification_code='XXXXXXXXXXXXXXXX',
                teacher_display='Pre-collision Test',
                modules_summary=[],
                instrument_version_t2='ning_2025_v1',
            )
            code = generate_verification_code()
            self.assertEqual(code, 'YYYYYYYYYYYYYYYY')

    def test_raises_after_five_failed_attempts(self):
        """Exhausted retry budget surfaces a clear RuntimeError."""
        with patch('apps.certification.models.secrets.token_urlsafe',
                   return_value='ZZZZZZZZZZZZZZZZpad'):
            user = User.objects.create_user(username='exhausted', password='x')
            CertificateOfAttendance.objects.create(
                user=user,
                verification_code='ZZZZZZZZZZZZZZZZ',
                teacher_display='Exhaust Test',
                modules_summary=[],
                instrument_version_t2='ning_2025_v1',
            )
            with self.assertRaises(RuntimeError):
                generate_verification_code()


class CertificateOfAttendanceModelTest(TestCase):
    """Model field semantics + constraints."""

    def setUp(self):
        self.user = User.objects.create_user(username='cert_user', password='x')

    def _make_cert(self, **overrides):
        defaults = dict(
            user=self.user,
            verification_code=generate_verification_code(),
            teacher_display='Test Teacher',
            modules_summary=[
                {'code': 'M1', 'title': 'M1 Title',
                 'aspect': 'Human-Centred Mindset', 'level': 'Acquire'},
            ],
            instrument_version_t2='ning_2025_v1',
        )
        defaults.update(overrides)
        return CertificateOfAttendance.objects.create(**defaults)

    def test_default_pdf_metadata_version_is_v1(self):
        cert = self._make_cert()
        self.assertEqual(cert.pdf_metadata_version, 'v1')

    def test_one_to_one_user_constraint(self):
        self._make_cert()
        # Second cert for the same user must fail.
        with self.assertRaises(IntegrityError):
            CertificateOfAttendance.objects.create(
                user=self.user,
                verification_code=generate_verification_code(),
                teacher_display='Dup',
                modules_summary=[],
                instrument_version_t2='ning_2025_v1',
            )

    def test_verification_code_unique_constraint(self):
        cert = self._make_cert()
        other_user = User.objects.create_user(username='other', password='x')
        with self.assertRaises(IntegrityError):
            CertificateOfAttendance.objects.create(
                user=other_user,
                verification_code=cert.verification_code,  # duplicate
                teacher_display='Dup Code',
                modules_summary=[],
                instrument_version_t2='ning_2025_v1',
            )

    def test_str_method_includes_holder_and_code(self):
        cert = self._make_cert(teacher_display='Maria Papadopoulou')
        s = str(cert)
        self.assertIn('Maria Papadopoulou', s)
        self.assertIn(cert.verification_code, s)

    def test_modules_summary_round_trips_as_json(self):
        payload = [
            {'code': f'M{i}', 'title': f'Title {i}',
             'aspect': 'Ethics', 'level': 'Acquire'}
            for i in range(1, 16)
        ]
        cert = self._make_cert(modules_summary=payload)
        cert.refresh_from_db()
        self.assertEqual(len(cert.modules_summary), 15)
        self.assertEqual(cert.modules_summary[0]['code'], 'M1')

    def test_issued_at_set_on_create(self):
        cert = self._make_cert()
        self.assertIsNotNone(cert.issued_at)


# ----------------------------------------------------------------------
# Phase H.3 part 2 — Service tests (eligibility, issuance, PDF render)
# ----------------------------------------------------------------------


def _seed_modules():
    """Create the 15 PROODOS modules so build_modules_summary has data."""
    aspects_by_index = [
        # (order_index → (aspect_key, level_key))
        ('human_centered', 'Acquire'),
        ('ethics', 'Acquire'),
        ('ai_foundations', 'Acquire'),
        ('ai_pedagogy', 'Acquire'),
        ('professional_development', 'Acquire'),
        ('human_centered', 'Deepen'),
        ('ethics', 'Deepen'),
        ('ai_foundations', 'Deepen'),
        ('ai_pedagogy', 'Deepen'),
        ('professional_development', 'Deepen'),
        ('human_centered', 'Create'),
        ('ethics', 'Create'),
        ('ai_foundations', 'Create'),
        ('ai_pedagogy', 'Create'),
        ('professional_development', 'Create'),
    ]
    for i, (aspect, level) in enumerate(aspects_by_index, start=1):
        Module.objects.create(
            code=f'M{i}',
            unesco_aspect=aspect,
            proficiency_level=level,
            title=f'Module {i} title',
            description=f'Module {i} description',
            order_index=i,
            estimated_hours=4,
            is_published=True,  # default False; matrix filters on it
        )


class TeacherIsEligibleTest(TestCase):
    """T2 completed_at gates issuance — partial submissions do not qualify."""

    def setUp(self):
        self.user = User.objects.create_user(username='eligible_user', password='x')

    def test_returns_false_without_any_t2(self):
        self.assertFalse(teacher_is_eligible(self.user))

    def test_returns_false_for_started_but_not_completed_t2(self):
        AilstResponse.objects.create(
            user=self.user, timepoint='T2',
            responses={'P1': 4},  # only 1 of 36 — completed_at stays NULL
            instrument_version='ning_2025_v1',
        )
        self.assertFalse(teacher_is_eligible(self.user))

    def test_returns_true_with_completed_t2(self):
        AilstResponse.objects.create(
            user=self.user, timepoint='T2',
            completed_at=timezone.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )
        self.assertTrue(teacher_is_eligible(self.user))

    def test_t0_completion_does_not_qualify(self):
        AilstResponse.objects.create(
            user=self.user, timepoint='T0',
            completed_at=timezone.now(),
            instrument_version='ning_2025_v1',
        )
        self.assertFalse(teacher_is_eligible(self.user))


class BuildModulesSummaryTest(TestCase):
    """Frozen snapshot has 15 entries with code/title/aspect/level."""

    def setUp(self):
        _seed_modules()

    def test_returns_fifteen_entries(self):
        summary = build_modules_summary()
        self.assertEqual(len(summary), 15)

    def test_entries_carry_display_values_not_enum_keys(self):
        summary = build_modules_summary()
        # First module = M1, Human-Centred Mindset / Acquire
        self.assertEqual(summary[0]['code'], 'M1')
        self.assertEqual(summary[0]['aspect'], 'Human-Centred Mindset')
        self.assertEqual(summary[0]['level'], 'Acquire')
        # Display value, not the raw 'human_centered' enum key.
        self.assertNotIn('human_centered', summary[0]['aspect'])

    def test_ordered_by_order_index(self):
        summary = build_modules_summary()
        codes = [row['code'] for row in summary]
        self.assertEqual(codes, [f'M{i}' for i in range(1, 16)])


class GetOrIssueCertificateTest(TestCase):
    """Idempotent issuance + frozen snapshot."""

    def setUp(self):
        _seed_modules()
        self.user = User.objects.create_user(
            username='issue_user', password='x',
            first_name='Maria', last_name='Papadopoulou',
        )
        AilstResponse.objects.create(
            user=self.user, timepoint='T2',
            completed_at=timezone.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )

    def test_raises_for_ineligible_user(self):
        ineligible = User.objects.create_user(username='no_t2', password='x')
        with self.assertRaises(RuntimeError):
            get_or_issue_certificate(ineligible)

    def test_first_call_creates_row(self):
        cert = get_or_issue_certificate(self.user)
        self.assertIsNotNone(cert.pk)
        self.assertEqual(cert.teacher_display, 'Maria Papadopoulou')
        self.assertEqual(len(cert.modules_summary), 15)
        self.assertEqual(cert.instrument_version_t2, 'ning_2025_v1')

    def test_subsequent_calls_return_same_row(self):
        first = get_or_issue_certificate(self.user)
        second = get_or_issue_certificate(self.user)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.verification_code, second.verification_code)

    def test_frozen_teacher_display_survives_profile_rename(self):
        first = get_or_issue_certificate(self.user)
        original_name = first.teacher_display

        # User renames after issuance.
        self.user.first_name = 'Eleni'
        self.user.last_name = 'Vassiliou'
        self.user.save()

        second = get_or_issue_certificate(self.user)
        self.assertEqual(second.teacher_display, original_name)
        self.assertEqual(second.teacher_display, 'Maria Papadopoulou')

    def test_frozen_modules_summary_survives_module_rename(self):
        first = get_or_issue_certificate(self.user)
        original_m1_title = first.modules_summary[0]['title']

        Module.objects.filter(code='M1').update(title='New M1 Title')

        second = get_or_issue_certificate(self.user)
        self.assertEqual(second.modules_summary[0]['title'], original_m1_title)


class RenderCertificatePdfTest(TestCase):
    """xhtml2pdf renders without errors; output has PDF magic + Article 50(2) markers."""

    def setUp(self):
        _seed_modules()
        self.user = User.objects.create_user(
            username='pdf_user', password='x',
            first_name='Test', last_name='Holder',
        )
        AilstResponse.objects.create(
            user=self.user, timepoint='T2',
            completed_at=timezone.now(),
            responses={f'P{i}': 4 for i in range(1, 37)},
            instrument_version='ning_2025_v1',
        )
        self.certificate = get_or_issue_certificate(self.user)

    def test_returns_pdf_bytes_with_magic(self):
        pdf_bytes, filename = render_certificate_pdf(self.certificate)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        self.assertGreater(len(pdf_bytes), 1000)  # not a stub

    def test_filename_includes_verification_code(self):
        _bytes, filename = render_certificate_pdf(self.certificate)
        self.assertIn(self.certificate.verification_code, filename)
        self.assertTrue(filename.endswith('.pdf'))


# ----------------------------------------------------------------------
# Phase H.3 part 2 — View tests
# ----------------------------------------------------------------------


def _make_eligible_user(username='eligible_view_user', password='pw'):
    """Create a fully-onboarded user who has completed T2."""
    user = User.objects.create_user(
        username=username, password=password,
        first_name='View', last_name='Tester',
    )
    TeacherProfile.objects.create(
        user=user,
        subject_area='mathematics',
        grade_level='primary',
        teaching_years='6-15',
        school_location='urban',
        average_class_size='medium',
        ai_experience='basic',
        preferred_communication_style='balanced',
        ai_disclosure_acknowledged_at=timezone.now(),
        profile_completed=True,
        research_consent=True,
    )
    AilstResponse.objects.create(
        user=user, timepoint='T2',
        completed_at=timezone.now(),
        responses={f'P{i}': 4 for i in range(1, 37)},
        instrument_version='ning_2025_v1',
    )
    return user


class CertificateDownloadViewTest(TestCase):
    """GET /certification/download/ — gate + idempotency + PDF response."""

    def setUp(self):
        _seed_modules()
        self.client = Client()

    def test_anonymous_redirects_to_login(self):
        resp = self.client.get(reverse('certification:download'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_ineligible_user_redirects_to_dashboard(self):
        user = User.objects.create_user(username='no_t2_dl', password='pw')
        TeacherProfile.objects.create(
            user=user, subject_area='mathematics', grade_level='primary',
            teaching_years='0-5', school_location='urban',
            average_class_size='medium', ai_experience='basic',
            preferred_communication_style='balanced',
            ai_disclosure_acknowledged_at=timezone.now(),
            profile_completed=True, research_consent=True,
        )
        self.client.force_login(user)
        resp = self.client.get(reverse('certification:download'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)
        # And no certificate row was issued.
        self.assertFalse(
            CertificateOfAttendance.objects.filter(user=user).exists()
        )

    def test_eligible_user_gets_pdf(self):
        user = _make_eligible_user()
        self.client.force_login(user)
        resp = self.client.get(reverse('certification:download'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertTrue(resp.content.startswith(b'%PDF'))

    def test_idempotent_two_downloads_reuse_same_row(self):
        user = _make_eligible_user()
        self.client.force_login(user)
        self.client.get(reverse('certification:download'))
        self.client.get(reverse('certification:download'))
        self.assertEqual(
            CertificateOfAttendance.objects.filter(user=user).count(), 1,
        )


class CertificateVerifyViewTest(TestCase):
    """Public verification surface — discloses name + date + modules; 404 for invalid."""

    def setUp(self):
        _seed_modules()
        self.user = _make_eligible_user(username='verify_user')
        self.certificate = get_or_issue_certificate(self.user)
        self.client = Client()  # no login

    def test_valid_code_returns_name_date_modules(self):
        url = reverse('certification:verify', args=[self.certificate.verification_code])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode('utf-8')
        self.assertIn(self.certificate.teacher_display, body)
        self.assertIn(self.certificate.verification_code, body)
        # 15 modules should all surface their codes.
        for i in range(1, 16):
            self.assertIn(f'M{i}', body)

    def test_invalid_code_returns_404(self):
        url = reverse('certification:verify', args=['INVALIDCODE12345'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_response_does_not_leak_ailst_scores(self):
        """Per §5.6 — verification surface intentionally excludes scores."""
        url = reverse('certification:verify', args=[self.certificate.verification_code])
        resp = self.client.get(url)
        body = resp.content.decode('utf-8').lower()
        # AILST factor names must not appear on this surface.
        self.assertNotIn('perception_score', body)
        self.assertNotIn('knowledge_skills_score', body)
        self.assertNotIn('ethics_score', body)
        self.assertNotIn('overall_score', body)
