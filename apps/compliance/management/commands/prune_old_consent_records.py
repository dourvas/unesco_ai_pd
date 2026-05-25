"""
Prune ConsentRecord rows older than 7 years that belong to anonymised users.

GDPR data minimisation + IRB audit-window completion:
  - ConsentRecord rows are kept for 7 years post-erasure as the IRB
    audit window (see TD-016 + apps/compliance/services.py::anonymize_user
    step 3 docstring + AI_IMPACT_ASSESSMENT §5 "Retention and identifiers").
  - Beyond 7 years, the IRB / GDPR retention basis lapses and rows
    must be deleted under data-minimisation principles.

Eligibility criteria for deletion (both must hold):
  1. granted_at < NOW - 7 years.
  2. The owning auth_user is anonymised — detected via the sentinel
     pattern set by anonymize_user(): is_active=False AND username
     matches the f'anonymized_{user_id}' pattern. Rows belonging to
     active users are kept regardless of age (active users may still
     be on the platform 7+ years later; their consent records are
     audit-live).

Mirror of the existing redact_old_consent_ips command pattern:
default dry-run, explicit --commit flag to persist deletions.

Intended to be run by an external scheduler (cron, Windows Task
Scheduler) on an annual or quarterly cadence. The platform itself
does not schedule it — keeping the management-command form
preserves composability.

Closes TD-016 (logged 2026 in apps/compliance/services.py:706 and
proodos_files/TECH_DEBT_LOG.md:324).

Examples:
    python manage.py prune_old_consent_records           # dry-run, default 7 years
    python manage.py prune_old_consent_records --commit  # persist deletions
    python manage.py prune_old_consent_records --commit --years 7
"""

import logging
from collections import Counter
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.compliance.models import ConsentRecord
from apps.compliance.services import ERASURE_USERNAME_TEMPLATE


logger = logging.getLogger('compliance.consent_retention')


# Pattern used by anonymize_user() — see services.py:633.
# We match by prefix because the suffix is the user_id (variable).
ANONYMIZED_USERNAME_PREFIX = ERASURE_USERNAME_TEMPLATE.format(user_id='').rstrip('_')
# ERASURE_USERNAME_TEMPLATE is 'anonymized_{user_id}', so the prefix is
# 'anonymized'. Anchor with the trailing underscore to avoid catching a
# hypothetical legitimate 'anonymizedXYZ' username:
ANONYMIZED_USERNAME_PREFIX_WITH_UNDERSCORE = f'{ANONYMIZED_USERNAME_PREFIX}_'


class Command(BaseCommand):
    help = (
        "Prune ConsentRecord rows older than N years (default 7) that belong "
        "to anonymised users. Default dry-run; pass --commit to delete."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Persist deletions. Without it, dry-run.',
        )
        parser.add_argument(
            '--years',
            type=int,
            default=7,
            help='Retention threshold in years (default 7, the IRB audit window).',
        )

    def handle(self, *args, **opts):
        commit = bool(opts['commit'])
        years = opts['years']
        # 365.25 days/year averaged over leap-year cycles. Calendar-precise
        # "N years ago" via relativedelta would also work; the day-count
        # form keeps the command dependency-free (no python-dateutil).
        cutoff = timezone.now() - timedelta(days=int(365.25 * years))

        qs = ConsentRecord.objects.filter(
            granted_at__lt=cutoff,
            user__is_active=False,
            user__username__startswith=ANONYMIZED_USERNAME_PREFIX_WITH_UNDERSCORE,
        )

        candidate_rows = list(
            qs.values('id', 'consent_type', 'granted_at', 'user__username')
        )
        candidate_count = len(candidate_rows)
        type_breakdown = Counter(row['consent_type'] for row in candidate_rows)

        breakdown_line = (
            ', '.join(f'{t}={n}' for t, n in sorted(type_breakdown.items()))
            or '(none)'
        )

        if commit:
            deleted_count, deleted_breakdown = qs.delete()
            logger.info(
                "Consent-retention pruning executed: %d rows deleted "
                "(threshold %d years, cutoff %s). Per-type: %s.",
                deleted_count, years, cutoff.isoformat(), breakdown_line,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Deleted {deleted_count} ConsentRecord rows older than '
                f'{years} years belonging to anonymised users. '
                f'Per-type: {breakdown_line}.'
            ))
        else:
            logger.info(
                "Consent-retention dry-run: %d candidate rows "
                "(threshold %d years, cutoff %s). Per-type: %s. "
                "Use --commit to persist.",
                candidate_count, years, cutoff.isoformat(), breakdown_line,
            )
            self.stdout.write(
                f'Dry-run: would delete {candidate_count} ConsentRecord rows '
                f'older than {years} years belonging to anonymised users. '
                f'Per-type: {breakdown_line}. '
                f'Run with --commit to persist.'
            )
