"""
Redact ip_address on ConsentRecord rows older than 30 days.

GDPR data minimization: IPs are useful only for short-window fraud /
abuse detection at consent time. Beyond that, retain only the consent
record (user_id, consent_type, granted_at) without the IP.

Replaces the dropped raw-SQL `cleanup_old_analytics()` function.

Examples:
    python manage.py redact_old_consent_ips           # dry-run, default 30 days
    python manage.py redact_old_consent_ips --commit  # persist redactions
    python manage.py redact_old_consent_ips --commit --days 14
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.compliance.models import ConsentRecord


logger = logging.getLogger('compliance.ip_redaction')


class Command(BaseCommand):
    help = "Redact ip_address on ConsentRecord rows older than N days (default 30)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Persist changes. Without it, dry-run.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Redaction threshold in days (default 30).',
        )

    def handle(self, *args, **opts):
        commit = bool(opts['commit'])
        days = opts['days']
        cutoff = timezone.now() - timedelta(days=days)

        qs = ConsentRecord.objects.filter(
            granted_at__lt=cutoff,
            ip_address__isnull=False,
        )
        candidate_count = qs.count()

        if commit:
            updated = qs.update(ip_address=None)
            logger.info(
                "IP redaction executed: %d rows redacted (threshold %d days, "
                "cutoff %s).",
                updated, days, cutoff.isoformat(),
            )
            self.stdout.write(self.style.SUCCESS(
                f"Redacted ip_address on {updated} rows older than {days} days."
            ))
        else:
            logger.info(
                "IP redaction dry-run: %d candidate rows (threshold %d days, "
                "cutoff %s). Use --commit to persist.",
                candidate_count, days, cutoff.isoformat(),
            )
            self.stdout.write(
                f"Dry-run: would redact {candidate_count} rows older than "
                f"{days} days. Run with --commit to persist."
            )
