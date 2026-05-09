"""
Phase C M3 — TeacherProfile change-tracking signals.

Captures changes to a fixed list of research-relevant TeacherProfile
fields and writes one TeacherProfileHistory row per changed field per
save event. Multi-field saves share a single `change_event_id` UUID.

Mechanism:
    pre_save  : fetch the prior DB snapshot, compare each tracked field
                against the in-memory instance, stash diffs (and a fresh
                event UUID) on transient instance attributes.
    post_save : on successful save (created=False, diffs present),
                bulk_create the history rows. Then clear all transients.

Orphan history rows are avoided: if save() raises and the DB transaction
rolls back, post_save never fires, so no rows are written for changes
that did not commit.

To attach a change_source label, set instance._change_source before
save(); the signal reads and propagates it. Default empty.
"""

import json
import uuid

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import TeacherProfile, TeacherProfileHistory


TRACKED_FIELDS = (
    # Step 1: Teaching Context
    'subject_area',
    'grade_level',
    'teaching_years',
    'school_location',
    'average_class_size',
    # Step 2 + 3: AI experience and goals
    'ai_experience',
    'ai_tools_used',
    'primary_goals',
    # Phase C personalization
    'current_curriculum_pressure',
    'student_population_special_needs',
    'institutional_ai_policy',
)


def _serialize(value):
    """Always returns valid JSON. None becomes the string 'null'."""
    return json.dumps(value, default=str, ensure_ascii=False)


@receiver(pre_save, sender=TeacherProfile)
def capture_profile_changes(sender, instance, **kwargs):
    """Compare tracked fields against the DB snapshot; stash diffs."""
    instance._pending_history = []
    instance._change_event_id = uuid.uuid4()

    if not instance.pk:
        return  # new profile — no prior state to compare

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    for field in TRACKED_FIELDS:
        old_v = getattr(old, field)
        new_v = getattr(instance, field)
        if old_v != new_v:
            instance._pending_history.append({
                'field_name': field,
                'old_value': _serialize(old_v),
                'new_value': _serialize(new_v),
            })


@receiver(post_save, sender=TeacherProfile)
def write_profile_history(sender, instance, created, **kwargs):
    """Persist captured diffs as TeacherProfileHistory rows, then clear."""
    pending = getattr(instance, '_pending_history', None)

    if created or not pending:
        # Clean up transients even on the no-op path so the instance
        # doesn't carry stale state into a subsequent save in the same
        # request lifecycle.
        if hasattr(instance, '_pending_history'):
            instance._pending_history = []
        if hasattr(instance, '_change_event_id'):
            delattr(instance, '_change_event_id')
        if hasattr(instance, '_change_source'):
            delattr(instance, '_change_source')
        return

    event_id = instance._change_event_id
    source = getattr(instance, '_change_source', '')

    rows = [
        TeacherProfileHistory(
            user_id=instance.user_id,
            field_name=item['field_name'],
            old_value=item['old_value'],
            new_value=item['new_value'],
            change_event_id=event_id,
            change_source=source,
        )
        for item in pending
    ]
    TeacherProfileHistory.objects.bulk_create(rows)

    # Clean up transients to avoid leaking across re-saves.
    instance._pending_history = []
    if hasattr(instance, '_change_event_id'):
        delattr(instance, '_change_event_id')
    if hasattr(instance, '_change_source'):
        delattr(instance, '_change_source')
