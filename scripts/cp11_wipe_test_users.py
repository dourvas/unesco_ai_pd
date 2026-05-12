"""
Pre-pilot wipe script: delete all non-staff test users and their data.

Phase C plan §2.1 CP 11 — Option B: before recruiting real pilot
participants, wipe every non-staff non-superuser auth_user from the
development DB. Staff and superusers are preserved (they are the
research team, not pilot participants).

The deletion cascades through ConsentRecord (FK on_delete=CASCADE),
TeacherProfile (OneToOneField on_delete=CASCADE), AilstResponse
(FK CASCADE), UserModuleProgress (FK CASCADE), EpilogueCompletion
(OneToOneField CASCADE), ReflectionTension and AIOutputDispute
(FK CASCADE). The raw-SQL rag_queries table sits outside the Django
ORM and is cleaned up via explicit DELETE (defensive — the column
has no FK CASCADE in production).

Run modes:
  --dry-run (default): list users to delete + per-table row counts,
                       no DB changes.
  --commit           : execute the wipe inside one atomic transaction.

This is destructive. Always run --dry-run first and eyeball the
list. Backup the DB before --commit.

Run from repo root:

    python scripts/cp11_wipe_test_users.py
    python scripts/cp11_wipe_test_users.py --commit
"""

import argparse
import os
import sys

import django


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.db import connection, transaction  # noqa: E402
from django.db.utils import ProgrammingError  # noqa: E402


def _count_orm(qs):
    """Safe count helper — returns 0 if the table is missing in this env."""
    try:
        return qs.count()
    except ProgrammingError:
        return 0


def _count_rag_queries(user_ids):
    """rag_queries lives outside the ORM; defensively count via cursor.
    Returns 0 if the table is absent (some test/dev environments)."""
    if not user_ids:
        return 0
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM rag_queries WHERE user_id = ANY(%s)",
                [list(user_ids)],
            )
            return cur.fetchone()[0]
    except ProgrammingError:
        return 0


def _delete_rag_queries(user_ids):
    if not user_ids:
        return 0
    try:
        with connection.cursor() as cur:
            cur.execute(
                "DELETE FROM rag_queries WHERE user_id = ANY(%s)",
                [list(user_ids)],
            )
            return cur.rowcount
    except ProgrammingError:
        return 0


def wipe_non_staff_users(*, commit: bool, require_typed_confirmation: bool = True,
                          output=print) -> dict:
    """Core wipe logic, callable directly from tests and from main().

    Args:
        commit: False -> dry-run (no DB writes). True -> execute.
        require_typed_confirmation: when True (CLI default), prompt for
            an interactive "YES" before committing. Tests pass False.
        output: callable used for progress / report lines. Defaults to
            print; tests pass a list.append-style sink to capture lines.

    Returns:
        Dict with the wipe summary:
            {
              'examined': int,
              'wiped': int,
              'rag_queries_removed': int,
              'cascade_breakdown': {model_label: count},
              'aborted': bool,
            }
    """
    targets = User.objects.filter(
        is_staff=False, is_superuser=False,
    ).order_by('id')
    target_count = targets.count()
    target_ids = list(targets.values_list('id', flat=True))

    summary = {
        'examined': target_count,
        'wiped': 0,
        'rag_queries_removed': 0,
        'cascade_breakdown': {},
        'aborted': False,
    }

    if target_count == 0:
        output('No non-staff users to wipe. Nothing to do.')
        return summary

    output(f'Users to delete: {target_count}')

    if not commit:
        output('Dry-run: no changes applied. Re-run with --commit to wipe.')
        return summary

    if require_typed_confirmation:
        answer = input('Type YES (uppercase) to confirm the wipe: ').strip()
        if answer != 'YES':
            output('Aborted. No changes made.')
            summary['aborted'] = True
            return summary

    with transaction.atomic():
        rag_removed = _delete_rag_queries(target_ids)
        users_removed, per_model_breakdown = targets.delete()
        summary['rag_queries_removed'] = rag_removed
        summary['wiped'] = users_removed
        summary['cascade_breakdown'] = dict(per_model_breakdown)
        output(f'rag_queries rows removed: {rag_removed}')
        output(f'total objects removed: {users_removed}')

    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Persist changes. Default is dry-run.',
    )
    args = parser.parse_args()
    commit = args.commit

    print('=' * 60)
    print('Phase C CP-11 — non-staff user wipe (Option B)')
    print('Mode:', 'COMMIT (executing)' if commit else 'DRY-RUN (no changes)')
    print('=' * 60)
    print()

    # Show users + cascade footprint before the wipe runs (the CLI
    # reporting overhead; the core wipe is in wipe_non_staff_users).
    targets = User.objects.filter(
        is_staff=False, is_superuser=False,
    ).order_by('id')
    target_count = targets.count()
    target_ids = list(targets.values_list('id', flat=True))

    if target_count:
        print(f'Users to delete: {target_count}')
        for u in targets[:50]:
            print(f'  id={u.id:>5}  username={u.username!r:<40}  email={u.email!r}')
        if target_count > 50:
            print(f'  ... and {target_count - 50} more (only the first 50 shown)')
        print()

        from apps.ailst.models import AilstResponse
        from apps.compliance.models import ConsentRecord
        from apps.epilogue.models import EpilogueCompletion
        from apps.modules.models import (
            AIOutputDispute, ReflectionTension, UserModuleProgress,
        )
        from apps.users.models import TeacherProfile, TeacherProfileHistory

        print('Cascade footprint (rows that will be deleted alongside the users):')
        rows = [
            ('teacher_profiles',           _count_orm(TeacherProfile.objects.filter(user_id__in=target_ids))),
            ('teacher_profile_history',    _count_orm(TeacherProfileHistory.objects.filter(user_id__in=target_ids))),
            ('consent_records',            _count_orm(ConsentRecord.objects.filter(user_id__in=target_ids))),
            ('ailst_responses',            _count_orm(AilstResponse.objects.filter(user_id__in=target_ids))),
            ('modules_usermoduleprogress', _count_orm(UserModuleProgress.objects.filter(user_id__in=target_ids))),
            ('epilogue_completions',       _count_orm(EpilogueCompletion.objects.filter(user_id__in=target_ids))),
            ('modules_reflectiontension',  _count_orm(ReflectionTension.objects.filter(user_id__in=target_ids))),
            ('modules_aioutputdispute',    _count_orm(AIOutputDispute.objects.filter(user_id__in=target_ids))),
            ('rag_queries (raw SQL)',      _count_rag_queries(target_ids)),
        ]
        for name, count in rows:
            print(f'  {name:<32} {count:>6}')
        print()

    summary = wipe_non_staff_users(commit=commit, require_typed_confirmation=True)
    if commit and not summary['aborted']:
        print()
        print('Wipe complete.')


if __name__ == '__main__':
    main()
