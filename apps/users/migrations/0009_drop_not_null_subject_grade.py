"""
Hotfix migration: drop the lingering NOT NULL constraints on
teacher_profiles.subject_area and teacher_profiles.grade_level so the
DB schema matches what apps.users.models.TeacherProfile already
declares (null=True, blank=True on both fields).

Background
----------
A new registrant who clicks "I acknowledge and continue" on the AI
Disclosure modal hits apps.compliance.views.ai_disclosure_view, which
runs `TeacherProfile.objects.get_or_create(user=request.user)`. The
create path does not pass values for subject_area or grade_level
(those are collected in onboarding Step 1, which has not run yet).
The model declares both columns as nullable, but the database table
still carries NOT NULL constraints from an earlier schema version.
The INSERT fails with IntegrityError and the whole disclosure POST
crashes — blocking every fresh-user registration flow.

makemigrations --dry-run reported "No changes detected", which means
the Django migration history believes the columns are already
nullable; the on-disk DB drifted out of sync, presumably by a
historical manual ALTER that was never captured as a migration.
This migration captures the intended state so the DB and the model
agree.

The CHECK constraints (valid_subject_area, valid_grade_level) are
unaffected: in PostgreSQL, CHECK constraints accept NULL by default
(NULL <> value for any value, and CHECK passes unless explicitly
"IS NOT NULL"). They keep validating the choice list for non-NULL
inserts.

The reverse_sql path restores NOT NULL. It is unsafe to run if any
NULL rows exist; that is the standard caveat for an enum-to-not-null
back-migration. If you ever need to reverse, first populate NULLs
with a default value (e.g., 'other' / 'primary') before migrating
backwards.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_teacherprofilehistory'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE teacher_profiles ALTER COLUMN subject_area DROP NOT NULL;",
                "ALTER TABLE teacher_profiles ALTER COLUMN grade_level DROP NOT NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE teacher_profiles ALTER COLUMN grade_level SET NOT NULL;",
                "ALTER TABLE teacher_profiles ALTER COLUMN subject_area SET NOT NULL;",
            ],
        ),
    ]
