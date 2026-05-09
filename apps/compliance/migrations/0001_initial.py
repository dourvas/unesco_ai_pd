"""
Phase C — Migration 1
Extends the consent_records.valid_consent_type CHECK constraint to include
'ai_disclosure', enabling EU AI Act Article 50(1) acknowledgment records.

Notes:
    - consent_records is a raw-SQL artefact created outside Django migrations.
      It exists in the live DB (proodos_backup_m15_complete_20260417_1152.sql,
      line 740). Therefore this migration uses RunSQL rather than AlterField.
    - Reverse SQL restores the prior 4-value constraint exactly.
"""

from django.db import migrations


SQL_FORWARD = """
ALTER TABLE consent_records DROP CONSTRAINT valid_consent_type;
ALTER TABLE consent_records
    ADD CONSTRAINT valid_consent_type CHECK (
        consent_type::text = ANY (
            ARRAY[
                'platform_use'::varchar,
                'research_participation'::varchar,
                'data_sharing'::varchar,
                'video_recording'::varchar,
                'ai_disclosure'::varchar
            ]::text[]
        )
    );
"""

SQL_REVERSE = """
ALTER TABLE consent_records DROP CONSTRAINT valid_consent_type;
ALTER TABLE consent_records
    ADD CONSTRAINT valid_consent_type CHECK (
        consent_type::text = ANY (
            ARRAY[
                'platform_use'::varchar,
                'research_participation'::varchar,
                'data_sharing'::varchar,
                'video_recording'::varchar
            ]::text[]
        )
    );
"""


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=SQL_FORWARD,
            reverse_sql=SQL_REVERSE,
        ),
    ]
