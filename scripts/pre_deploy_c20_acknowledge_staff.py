"""
Pre-deploy script: auto-acknowledge AI Disclosure for staff/superusers.

Phase C C.2.0 introduces the AI Disclosure middleware which redirects
every authenticated user to the disclosure modal until they have
acknowledged it. Without this script, deploying C.2.0 would lock John
(and any other staff) out of normal workflows on their next request,
mid-development.

This script:
  1. Iterates auth_user where is_staff=True OR is_superuser=True
  2. For each staff user without an acknowledgment, writes a
     ConsentRecord row via record_consent (idempotent) and stamps
     TeacherProfile.ai_disclosure_acknowledged_at = NOW().
  3. Skips users who already have an acknowledgment.
  4. Does NOT touch non-staff users — they are real pilot participants
     and must see the modal on first authenticated request (the test
     scenario for the middleware flow).

Run modes:
  --dry-run (default) : print what would happen, no DB changes.
  --commit            : execute changes inside one transaction per user.

Run from repo root, after applying C.2.0 code, before notifying users:

    python scripts/pre_deploy_c20_acknowledge_staff.py
    python scripts/pre_deploy_c20_acknowledge_staff.py --commit
"""

import argparse
import os
import sys

import django

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.compliance.copy import AI_DISCLOSURE_TEXT_V1_PRE_IRB  # noqa: E402
from apps.compliance.services import record_consent  # noqa: E402
from apps.users.models import TeacherProfile  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Persist changes. Default is dry-run.',
    )
    args = parser.parse_args()
    dry_run = not args.commit

    staff_users = User.objects.filter(
        is_staff=True,
    ).union(User.objects.filter(is_superuser=True)).order_by('id')

    print('=' * 60)
    print('Phase C C.2.0 — staff auto-acknowledge AI Disclosure')
    print(f'Mode: {"DRY-RUN (no changes)" if dry_run else "COMMIT (executing)"}')
    print(f'Disclosure version: {settings.AI_DISCLOSURE_CURRENT_VERSION}')
    print('=' * 60)
    print()

    examined = 0
    acknowledged = 0
    already = 0

    for user in staff_users:
        examined += 1
        try:
            profile = TeacherProfile.objects.get(user=user)
            already_acked = profile.ai_disclosure_acknowledged_at is not None
        except TeacherProfile.DoesNotExist:
            profile = None
            already_acked = False

        if already_acked:
            already += 1
            print(f'  - id={user.id} {user.username:30s}  already acknowledged at {profile.ai_disclosure_acknowledged_at}')
            continue

        print(f'  - id={user.id} {user.username:30s}  WILL ACK')
        acknowledged += 1

        if not dry_run:
            with transaction.atomic():
                record_consent(
                    user=user,
                    consent_type='ai_disclosure',
                    consent_text=AI_DISCLOSURE_TEXT_V1_PRE_IRB,
                    version=settings.AI_DISCLOSURE_CURRENT_VERSION,
                    ip_address=None,  # script-driven, not user-driven
                )
                if profile is None:
                    profile, _ = TeacherProfile.objects.get_or_create(user=user)
                profile.ai_disclosure_acknowledged_at = timezone.now()
                profile.save(update_fields=['ai_disclosure_acknowledged_at'])

    print()
    print(f'Examined: {examined} staff/superuser accounts')
    print(f'Already acknowledged: {already}')
    print(f'{"Would acknowledge" if dry_run else "Acknowledged"}: {acknowledged}')

    if dry_run:
        print()
        print('Dry-run only. Re-run with --commit to execute.')


if __name__ == '__main__':
    main()
