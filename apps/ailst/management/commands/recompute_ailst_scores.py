"""
Recompute AILST scores from raw `responses` JSONB.

Use after a scoring formula change (e.g., overall = mean of items instead
of mean of factor means), or when auditing one user's responses for IRB.
Idempotent: running twice on unchanged data is a no-op.

Examples:
    python manage.py recompute_ailst_scores --dry-run
    python manage.py recompute_ailst_scores --commit
    python manage.py recompute_ailst_scores --commit --instrument-version ning_2025_v1
    python manage.py recompute_ailst_scores --commit --user-id 42
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ailst.models import AilstItem, AilstResponse
from apps.ailst.scoring import compute_factor_scores


SCORE_FIELDS = (
    'perception_score',
    'knowledge_skills_score',
    'applications_innovation_score',
    'ethics_score',
    'overall_score',
)


class Command(BaseCommand):
    help = (
        "Recompute factor and overall scores for all completed AilstResponse "
        "rows from their raw `responses` JSONB. Idempotent."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Persist changes. Without this flag, the command is dry-run.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Explicit dry-run flag (default behaviour without --commit).',
        )
        parser.add_argument(
            '--instrument-version',
            default=None,
            help='Limit to one instrument_version (e.g., ning_2025_v1).',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=None,
            help='Limit to one user (for IRB audit / per-user debug).',
        )

    def handle(self, *args, **opts):
        commit = bool(opts['commit'])
        # --dry-run is informational; default is dry-run unless --commit set.
        dry_run = not commit

        qs = AilstResponse.objects.filter(completed_at__isnull=False)
        if opts['instrument_version']:
            qs = qs.filter(instrument_version=opts['instrument_version'])
        if opts['user_id'] is not None:
            qs = qs.filter(user_id=opts['user_id'])

        items_cache = {}
        examined = 0
        changed = 0

        for resp in qs.iterator():
            examined += 1
            cache_key = (resp.language, resp.instrument_version)
            if cache_key not in items_cache:
                items_cache[cache_key] = {
                    it.paper_code: it
                    for it in AilstItem.objects.filter(
                        language=resp.language,
                        instrument_version=resp.instrument_version,
                    )
                }
            scores = compute_factor_scores(resp.responses, items_cache[cache_key])

            differs = any(getattr(resp, field) != scores[field] for field in SCORE_FIELDS)
            if not differs:
                continue

            changed += 1
            self.stdout.write(
                f"  user_id={resp.user_id} timepoint={resp.timepoint} "
                f"version={resp.instrument_version} -> would update"
            )
            if commit:
                with transaction.atomic():
                    for field in SCORE_FIELDS:
                        setattr(resp, field, scores[field])
                    resp.save(update_fields=list(SCORE_FIELDS))

        mode = 'DRY-RUN (no writes)' if dry_run else 'COMMIT'
        self.stdout.write(
            f"\nMode: {mode}. Examined {examined} completed rows; "
            f"{changed} {'would change' if dry_run else 'changed'}."
        )
