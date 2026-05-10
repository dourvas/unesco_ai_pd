"""
Phase C M4 — Seed the EN AILST instrument (Ning et al. 2025, v1).

Loads 36 items from apps/ailst/seeds/ning_2025_v1_en.json into the
ailst_items table with language='en', instrument_version='ning_2025_v1'.

Five invariants are enforced. If any invariant fails, the migration
crashes with a descriptive error rather than silently loading bad data:

  1. Seed file present at expected path.
  2. Exactly 36 items in the seed.
  3. Exactly 3 items have is_reverse_scored=True.
  4. The set of paper_codes matches the expected 36-code identity
     (P1-P10, K1-K10, A3-A10, E1+E3-E5+E7-E10) — protects against the
     case where someone replaces the JSON with wrongly-numbered items.
  5. _meta.removed_items in the JSON exactly matches {A1, A2, E2, E6} —
     protects the historical-record block against accidental deletion.

For EL or future versions: do NOT add another data migration. Add a
new seed JSON (e.g., ning_2025_v1_el.json), then load it via a
management command. Schema is i18n-ready by design.
"""

import json
from pathlib import Path

from django.db import migrations


SEED_FILENAME = 'ning_2025_v1_en.json'

EXPECTED_ITEM_COUNT = 36
EXPECTED_REVERSE_CODES = {'K1', 'A3', 'E3'}
EXPECTED_PAPER_CODES = {
    'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10',
    'K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10',
    'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10',
    'E1', 'E3', 'E4', 'E5', 'E7', 'E8', 'E9', 'E10',
}
EXPECTED_REMOVED_CODES = {'A1', 'A2', 'E2', 'E6'}


def load_ailst_en_seed(apps, schema_editor):
    from django.conf import settings

    seed_path = Path(settings.BASE_DIR) / 'apps' / 'ailst' / 'seeds' / SEED_FILENAME

    # Invariant 1: seed file present
    if not seed_path.exists():
        raise RuntimeError(
            f"AILST EN seed not found at {seed_path}. This migration "
            "cannot proceed without it. Verify file is present and "
            "committed; do not skip via --fake."
        )

    data = json.loads(seed_path.read_text(encoding='utf-8'))
    items = data.get('items') or []
    meta = data.get('_meta') or {}

    # Invariant 2: exactly 36 items
    if len(items) != EXPECTED_ITEM_COUNT:
        raise RuntimeError(
            f"AILST EN seed must contain exactly {EXPECTED_ITEM_COUNT} items. "
            f"Found {len(items)}."
        )

    # Invariant 3: reverse-scored set
    reverse_codes = {it['paper_code'] for it in items if it.get('is_reverse_scored')}
    if reverse_codes != EXPECTED_REVERSE_CODES:
        raise RuntimeError(
            f"AILST EN seed reverse-scored items mismatch. "
            f"Expected {EXPECTED_REVERSE_CODES}, got {reverse_codes}. "
            "Per Ning et al. 2025 only K1, A3, E3 are reverse-scored."
        )

    # Invariant 4: paper_codes identity
    actual_codes = {it['paper_code'] for it in items}
    if actual_codes != EXPECTED_PAPER_CODES:
        missing = EXPECTED_PAPER_CODES - actual_codes
        extra = actual_codes - EXPECTED_PAPER_CODES
        raise RuntimeError(
            "AILST EN seed paper_codes mismatch. "
            f"Missing: {sorted(missing)}. Extra: {sorted(extra)}. "
            "The 36-code identity must match the paper-validated set."
        )

    # Invariant 5: _meta.removed_items
    removed_in_meta = set((meta.get('removed_items') or {}).keys())
    if removed_in_meta != EXPECTED_REMOVED_CODES:
        raise RuntimeError(
            f"AILST EN seed _meta.removed_items mismatch. "
            f"Expected {EXPECTED_REMOVED_CODES}, got {removed_in_meta}. "
            "This is a documentation invariant — the seed file's _meta "
            "block records the historical full set (Ning et al. 40 -> 36)."
        )

    AilstItem = apps.get_model('ailst', 'AilstItem')
    AilstItem.objects.bulk_create([
        AilstItem(
            item_number=it['item_number'],
            paper_code=it['paper_code'],
            factor=it['factor'],
            language='en',
            item_text=it['item_text'],
            is_reverse_scored=it['is_reverse_scored'],
            instrument_version=meta['instrument_version'],
        )
        for it in items
    ])


def unload_ailst_en_seed(apps, schema_editor):
    """Reverse: delete only the rows this seed inserted."""
    AilstItem = apps.get_model('ailst', 'AilstItem')
    AilstItem.objects.filter(
        language='en',
        instrument_version='ning_2025_v1',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ailst', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=load_ailst_en_seed,
            reverse_code=unload_ailst_en_seed,
        ),
    ]
