"""
Retroactively populate `AIArtefactProvenance` rows for existing AI artefacts.

Phase C C.3 commit 1 — backfill management command. Walks the five
sources of AI-generated artefacts (RTM tensions, DTP narratives, RAG
feedback, peer synthesis, and the raw-SQL rag_queries log) and creates
one provenance row per artefact. Idempotent: `get_or_create` keyed by
(artefact_kind, artefact_pk) skips silently if a row already exists
(CP-7) — safe to rerun, safe under mixed forward/retroactive scenarios.

Strategy (justified by `proodos_files/audit_rag_queries_provenance_20260512.md`):

  - `model_name` = 'gemini-2.5-flash' constant for all rows. The audit
    verified no model-standardisation transition in git history and zero
    rows in the fallback-path proxy bucket.
  - `generated_at` = source row's `created_at` (best available signal).
  - `prompt_hash` = None (the prompt is not reconstructible retroactively).

Orphan rag_queries rows (74 rows in the audit) whose user_id does not
reference a current auth_user are skipped — AIArtefactProvenance.user is
a required FK.

Run modes:
  --dry-run (default): counts targets per kind + flags potential
                       fallback-path rag_queries rows, no DB changes.
  --commit           : creates AIArtefactProvenance rows inside an
                       atomic transaction, after typed YES confirmation.

Examples:
    python manage.py backfill_ai_provenance
    python manage.py backfill_ai_provenance --commit
"""

import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.utils import ProgrammingError

from apps.compliance.models import AIArtefactProvenance
from apps.compliance.services import record_ai_provenance


logger = logging.getLogger('compliance.ai_provenance_backfill')

BACKFILL_MODEL_NAME = 'gemini-2.5-flash'


def _collect_dtp_targets():
    """Yield (artefact_kind, source_row) for each UserModuleProgress with non-empty DTP."""
    from apps.modules.models import UserModuleProgress
    qs = (
        UserModuleProgress.objects
        .exclude(reflection_dtp__isnull=True)
        .exclude(reflection_dtp='')
        .select_related('user', 'module')
    )
    for p in qs:
        yield 'dtp_narrative', p


def _collect_rag_feedback_targets():
    from apps.modules.models import UserModuleProgress
    qs = (
        UserModuleProgress.objects
        .exclude(reflection_rag_feedback__isnull=True)
        .exclude(reflection_rag_feedback='')
        .select_related('user', 'module')
    )
    for p in qs:
        yield 'rag_feedback', p


def _collect_peer_synthesis_targets():
    from apps.modules.models import UserModuleProgress
    qs = (
        UserModuleProgress.objects
        .exclude(reflection_peer_synthesis__isnull=True)
        .exclude(reflection_peer_synthesis='')
        .select_related('user', 'module')
    )
    for p in qs:
        yield 'peer_synthesis', p


def _collect_rtm_targets():
    from apps.modules.models import ReflectionTension
    qs = ReflectionTension.objects.select_related('user', 'module').all()
    for t in qs:
        yield 'rtm_position', t


def _collect_rag_queries_targets():
    """rag_queries is raw-SQL, savepoint-wrapped (matches services._rag_queries_to_list)."""
    rows = []
    try:
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT rq.id, rq.user_id, rq.module_id, rq.created_at, rq.generation_tokens
                    FROM rag_queries rq
                    INNER JOIN auth_user u ON u.id = rq.user_id
                    ORDER BY rq.created_at
                    """
                )
                rows = cur.fetchall()
    except ProgrammingError:
        # rag_queries table absent in this environment — fresh test DB.
        return
    for row in rows:
        rq_id, user_id, module_id, created_at, generation_tokens = row
        yield 'rag_query', {
            'pk': rq_id,
            'user_id': user_id,
            'module_id': module_id,
            'generated_at': created_at,
            'generation_tokens': generation_tokens,
        }


def _count_fallback_proxy() -> int:
    """Count rag_queries rows whose generation_tokens is NULL or 0 — proxy for
    the 1.5-flash fallback path having fired. Per the audit (§3.4) this is
    zero in production today. If it ever becomes nonzero, the constant
    backfill strategy needs re-evaluation."""
    try:
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM rag_queries "
                    "WHERE generation_tokens IS NULL OR generation_tokens = 0"
                )
                return cur.fetchone()[0]
    except ProgrammingError:
        return 0


class Command(BaseCommand):
    help = (
        "Backfill AIArtefactProvenance rows for existing AI artefacts. "
        "Dry-run by default; --commit persists after typed YES."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help='Persist the new provenance rows. Without --commit, dry-run.',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip the typed YES confirmation (tests).',
        )

    def handle(self, *args, **opts):
        commit = bool(opts['commit'])
        require_typed = not bool(opts['no-input'.replace('-', '_')])

        # Inventory pass — count targets per kind without writing anything.
        plan = self._build_plan()
        # artefact_pk is stored as string (CharField) in the model — compare
        # the source pk via str() so the lookup matches (UUID, int, etc.).
        existing_provenance_pks = set(
            AIArtefactProvenance.objects.values_list('artefact_kind', 'artefact_pk')
        )
        new_per_kind = {k: 0 for k in plan}
        skip_per_kind = {k: 0 for k in plan}
        for kind, items in plan.items():
            for item in items:
                pk = self._extract_pk(kind, item)
                if (kind, str(pk)) in existing_provenance_pks:
                    skip_per_kind[kind] += 1
                else:
                    new_per_kind[kind] += 1

        total_new = sum(new_per_kind.values())
        total_skip = sum(skip_per_kind.values())
        fallback_proxy_count = _count_fallback_proxy()

        self._print_plan(new_per_kind, skip_per_kind, fallback_proxy_count)

        if not commit:
            self.stdout.write(
                f"\nDry-run: would create {total_new} provenance rows, "
                f"skip {total_skip} already-present. Run with --commit to persist."
            )
            return

        # Commit path — typed confirmation then atomic write.
        if require_typed:
            answer = input(
                f'Type YES (uppercase) to write {total_new} provenance rows: '
            ).strip()
            if answer != 'YES':
                self.stdout.write(self.style.WARNING(
                    "Aborted: confirmation not received."
                ))
                return

        created = 0
        skipped = 0
        with transaction.atomic():
            for kind, items in plan.items():
                for item in items:
                    pk, user, module, generated_at = self._extract_fields(kind, item)
                    if user is None:
                        # Defensive: rag_queries orphan filtered in the INNER JOIN
                        # already, but the helpers may yield None for edge cases.
                        skipped += 1
                        continue
                    before = AIArtefactProvenance.objects.filter(
                        artefact_kind=kind, artefact_pk=str(pk)
                    ).exists()
                    if before:
                        skipped += 1
                        continue
                    record_ai_provenance(
                        artefact_kind=kind,
                        artefact_pk=pk,
                        user=user,
                        module=module,
                        model_name=BACKFILL_MODEL_NAME,
                        generated_at=generated_at,
                        prompt_hash=None,
                    )
                    created += 1

        logger.info(
            "Backfill committed: created=%d skipped=%d (existing) "
            "fallback_proxy_count=%d.",
            created, skipped, fallback_proxy_count,
        )
        self.stdout.write(self.style.SUCCESS(
            f"\nBackfill complete: created {created} new provenance rows; "
            f"skipped {skipped} already-present."
        ))

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _build_plan(self):
        return {
            'rtm_position': list(_collect_rtm_targets()),
            'dtp_narrative': list(_collect_dtp_targets()),
            'rag_feedback': list(_collect_rag_feedback_targets()),
            'peer_synthesis': list(_collect_peer_synthesis_targets()),
            'rag_query': list(_collect_rag_queries_targets()),
        }

    def _extract_pk(self, kind, item):
        if kind == 'rag_query':
            return item[1]['pk'] if isinstance(item, tuple) else item['pk']
        # Django model instance — item is a tuple (kind, instance)
        # because _collect_* generators yield (kind, instance). But by
        # the time we get here from _build_plan, the caller already
        # accumulated `items` which are tuples (kind, source_row). Unify.
        if isinstance(item, tuple):
            return item[1].pk
        return item.pk

    def _extract_fields(self, kind, item):
        """Return (pk, user, module, generated_at) for any source-row item."""
        if kind == 'rag_query':
            data = item[1] if isinstance(item, tuple) else item
            pk = data['pk']
            user = User.objects.filter(pk=data['user_id']).first()
            module = None
            if data.get('module_id'):
                from apps.modules.models import Module
                module = Module.objects.filter(pk=data['module_id']).first()
            return pk, user, module, data['generated_at']
        # Django-managed kinds: item is (kind, instance)
        instance = item[1] if isinstance(item, tuple) else item
        pk = instance.pk
        user = instance.user
        module = instance.module
        # Per-model timestamp lookup — UserModuleProgress carries
        # started_at / completed_at; ReflectionTension carries created_at
        # (auto_now_add). When all the candidate timestamps are missing
        # (edge cases: rows created via raw SQL or test fixtures that
        # bypassed save() hooks), fall back to timezone.now() so the
        # provenance row's NOT NULL invariant is preserved. The exact
        # generated_at is best-effort retroactive — the audit doc spells
        # this out.
        from django.utils import timezone
        generated_at = (
            getattr(instance, 'created_at', None)
            or getattr(instance, 'started_at', None)
            or getattr(instance, 'completed_at', None)
            or getattr(instance, 'updated_at', None)
            or timezone.now()
        )
        return pk, user, module, generated_at

    def _print_plan(self, new_per_kind, skip_per_kind, fallback_proxy_count):
        self.stdout.write("AI Artefact Provenance backfill plan:")
        self.stdout.write(
            "  {:<18} {:>10} {:>14}".format("kind", "new rows", "already present")
        )
        for kind in ('rtm_position', 'dtp_narrative', 'rag_feedback',
                     'peer_synthesis', 'rag_query'):
            self.stdout.write(
                "  {:<18} {:>10} {:>14}".format(
                    kind, new_per_kind.get(kind, 0), skip_per_kind.get(kind, 0)
                )
            )
        if fallback_proxy_count:
            self.stdout.write(self.style.WARNING(
                f"\nWARNING: {fallback_proxy_count} rag_queries rows have "
                f"NULL or zero generation_tokens. This is a proxy for the "
                f"gemini-1.5-flash fallback path having fired. The audit "
                f"of 2026-05-12 reported zero such rows; if this number is "
                f"nonzero, the constant '{BACKFILL_MODEL_NAME}' backfill "
                f"strategy may mis-attribute those rows. Review before commit."
            ))
        else:
            self.stdout.write(
                f"\nFallback-path proxy clean (0 rows). "
                f"'{BACKFILL_MODEL_NAME}' constant backfill is safe."
            )
