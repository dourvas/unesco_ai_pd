"""
Phase C M6 data migration — backfill ConsentRecord from TeacherProfile booleans.

For each pre-existing TeacherProfile where research_consent=True or
consent_data_sharing=True, create a corresponding ConsentRecord row
with version='v0_pre_phase_c' and explanatory consent_text.

Idempotent: re-running skips users who already have an active row for
the matching (user, consent_type, version).

Note: TeacherProfile.contact_for_research is NOT migrated. It is a
contact preference ('available for research interviews'), not a consent
event. Documented in apps/compliance/services.py::LEGACY_BOOLEAN_MAP.

Pre-Phase-C limitation: original Step 3 consent text was not preserved
(consent was tracked as a boolean field). Migrated rows reference the
boolean field name in their consent_text and use version='v0_pre_phase_c'
to make the synthesized origin obvious to any future reviewer.

Reverse: deletes only the v0_pre_phase_c rows that this migration could
have created. Future v1+ rows from C.2 onwards are untouched.
"""

from django.db import migrations


def migrate_step3_consents(apps, schema_editor):
    """Forward: backfill ConsentRecord rows for TeacherProfile booleans."""
    from apps.compliance.services import migrate_legacy_teacher_consents

    TeacherProfile = apps.get_model('users', 'TeacherProfile')
    ConsentRecord = apps.get_model('compliance', 'ConsentRecord')
    migrate_legacy_teacher_consents(
        TeacherProfile=TeacherProfile,
        ConsentRecord=ConsentRecord,
    )


def reverse_migrate_step3_consents(apps, schema_editor):
    """Reverse: delete only the v0_pre_phase_c rows we synthesised."""
    ConsentRecord = apps.get_model('compliance', 'ConsentRecord')
    ConsentRecord.objects.filter(version='v0_pre_phase_c').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0003_consentrecord'),
        ('users', '0008_teacherprofilehistory'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_step3_consents,
            reverse_code=reverse_migrate_step3_consents,
        ),
    ]
