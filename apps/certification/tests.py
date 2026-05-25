"""Tests for apps.certification — Phase H.3 skeleton.

Model + verification_code helper coverage. PDF rendering, download
view, eligibility gate, and public verification view tests land in
task #7 alongside the implementations.
"""

import re
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.certification.models import (
    CertificateOfAttendance,
    generate_verification_code,
)


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
