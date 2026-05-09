"""
Phase C M1 — OBSOLETE (no-op placeholder).

Originally extended the consent_records.valid_consent_type CHECK constraint
to include 'ai_disclosure'. Both the constraint and the consent_records
table were dropped in Γ.1 (apps/compliance/migrations/0002_drop_dead_schema.py)
on 2026-05-09 after a read-only audit (audits/DEAD_SCHEMA_AUDIT_20260509.md)
established that consent_records was an abandoned pre-Django artefact.

This file is retained as a placeholder rather than deleted because Django's
migration graph requires every applied migration to remain importable.
0002 depends on 0001 to satisfy graph-leaf-node rules. The operations list
is empty; re-applying or fresh-applying this migration is a guaranteed
no-op.

The original RunSQL forward + reverse blocks are preserved in git history
under commit 06357f2 if ever needed for forensic reference.
"""

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = []
