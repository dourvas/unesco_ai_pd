"""
PHASE A TIER 3 — STEP 6: M8 Type-A patches
==========================================
Two patches to M8 main_content (row 447):

1. M8_ETHICS_BY_DESIGN_PATCH (Section 6 of v3 spec)
   - Inserted BEFORE Part 5 H2 (i.e., at end of Part 4)
   - Indicator: CG3.2.4 PARTIAL → STRONG

2. M8_CROSS_REF_M3_PATCH (Section 7 of v3 spec)
   - Inserted AFTER Part 1 H2 (beginning of Part 1 body)
   - Indicator: CG3.2.1 PARTIAL → STRONG

Usage:
    python phaseA_tier3_step6_apply.py            # apply (COMMIT)
    python phaseA_tier3_step6_apply.py --dry-run  # rollback after verification
"""
import sys, json
import psycopg2

DB = dict(dbname='unesco_ai_teacher_pd', user='postgres', password='Django123!',
          host='localhost', port='5432')

DRY_RUN = '--dry-run' in sys.argv

ROW_ID = 447  # M8 main_content


# ── Section 6: M8 Ethics-by-Design subsection (end of Part 4, BEFORE the
# divider that separates Part 4 from Part 5). Anchor includes both divider
# and Part 5 H2 to keep the composite unique while letting the patch land
# attached to Part 4's visual flow.
P5_ANCHOR = (
    '<div class="divider my-8"></div>\n\n'
    '<h2 class="text-3xl font-bold text-info mb-6">🧭 Part 5: From Library to Live — Orchestrating Your Prompts in Real Time</h2>'
)

ETHICS_PATCH = (
    '<!-- M8_ETHICS_BY_DESIGN_PATCH -->\n'
    '<div class="card bg-base-200 border-l-4 border-warning p-4 my-4"\n'
    '     role="region" aria-label="Hands-on ethics checks for prompts">\n'
    '  <h4 class="font-bold text-warning mb-2">Hands-on Ethics in Your Prompts</h4>\n'
    "  <p>Ethics-by-design isn’t an abstract goal — it’s a daily practice in how you write prompts. Three concrete checks you can apply to any prompt before sending it:</p>\n"
    '\n'
    '  <div class="space-y-3 mt-3">\n'
    '    <div>\n'
    '      <p class="font-semibold">Bias check.</p>\n'
    '      <p>Does your prompt assume student demographics, abilities, or backgrounds? “Write an example for a typical student” carries hidden assumptions. “Write an example accessible to learners with diverse strengths” is more inclusive.</p>\n'
    '    </div>\n'
    '\n'
    '    <div>\n'
    '      <p class="font-semibold">Privacy check.</p>\n'
    '      <p>Does your prompt include real student names, identifiable details, or sensitive information? Replace with anonymised placeholders (“Student A”, “a learner with reading difficulties”).</p>\n'
    '    </div>\n'
    '\n'
    '    <div>\n'
    '      <p class="font-semibold">Inclusivity check.</p>\n'
    "      <p>Does your prompt’s tone or framing exclude any group? Test by reading aloud — if it sounds othering, rewrite.</p>\n"
    '    </div>\n'
    '  </div>\n'
    '\n'
    '  <p class="mt-3">Apply these checks habitually, and your Studio templates will embody ethics-by-design without conscious effort.</p>\n'
    '</div>\n'
    '<!-- /M8_ETHICS_BY_DESIGN_PATCH -->\n\n'
)
ETHICS_REPLACEMENT = ETHICS_PATCH + P5_ANCHOR


# ── Section 7: M8 Cross-ref to M3 (AFTER Part 1 H2) ──────────────────────────
P1_ANCHOR = '<h2 class="text-3xl font-bold text-primary mb-6">🔄 Part 1: From Knowing to Doing</h2>'

XREF_PATCH = (
    '\n\n'
    '<!-- M8_CROSS_REF_M3_PATCH -->\n'
    '<div class="card bg-base-200 border-l-4 border-info p-4 my-4"\n'
    '     role="note" aria-label="Cross-reference to M3 on AI techniques">\n'
    '  <h4 class="font-bold text-info mb-2">A note on AI techniques</h4>\n'
    "  <p>M8 specialises in <strong>generative AI</strong> — the LLM-based prompt engineering you’ll do most often as a teacher. For a broader comparison of AI techniques (symbolic AI, predictive AI, generative AI) and when to use each, refer to <strong>M3 Part 2</strong> (AI Categories and the Reliability Framework). M8 builds on that foundation; here we go deeper on the generative side.</p>\n"
    '</div>\n'
    '<!-- /M8_CROSS_REF_M3_PATCH -->\n'
)
XREF_REPLACEMENT = P1_ANCHOR + XREF_PATCH


PATCHES = [
    {
        'label': 'M8_ETHICS',
        'marker': 'M8_ETHICS_BY_DESIGN_PATCH',
        'anchor': P5_ANCHOR,
        'replacement': ETHICS_REPLACEMENT,
        'patch_id': 'm8_ethics_by_design',
        'indicator': 'CG3.2.4',
    },
    {
        'label': 'M8_XREF_M3',
        'marker': 'M8_CROSS_REF_M3_PATCH',
        'anchor': P1_ANCHOR,
        'replacement': XREF_REPLACEMENT,
        'patch_id': 'm8_cross_ref_m3',
        'indicator': 'CG3.2.1',
    },
]


def main():
    print('=' * 78)
    print(f"PHASE A TIER 3 STEP 6 — M8 patches  ({'DRY-RUN' if DRY_RUN else 'APPLY'})")
    print('=' * 78)

    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Pre-snapshot ────────────────────────────────────────────────────────
    cur.execute("""
        SELECT mc.id, m.code, length(mc.content_data),
               jsonb_array_length(COALESCE(mc.metadata->'patches', '[]'::jsonb))
        FROM modules_modulecontent mc JOIN modules_module m ON mc.module_id = m.id
        WHERE mc.id = %s
        FOR UPDATE;
    """, (ROW_ID,))
    row = cur.fetchone()
    pre_id, pre_code, pre_len, pre_n_patches = row
    print(f"\nPRE-SNAPSHOT  row={pre_id}  module={pre_code}  len={pre_len}  patches[]={pre_n_patches}")

    # ── Anchor + idempotency check ──────────────────────────────────────────
    cur.execute("SELECT content_data FROM modules_modulecontent WHERE id = %s;", (ROW_ID,))
    blob = cur.fetchone()[0]

    print(f"\nANCHOR + MARKER PRE-CHECK")
    print('-' * 60)
    all_ok = True
    for p in PATCHES:
        a_count = blob.count(p['anchor'])
        m_count = blob.count(p['marker'])
        ok = (a_count == 1 and m_count == 0)
        all_ok = all_ok and ok
        flag = '✓' if ok else '✗'
        print(f"  {flag} {p['label']:>12s}  anchor_count={a_count}  marker_pre={m_count}  patch_id={p['patch_id']!r}")

    if not all_ok:
        print("\n[ABORT] anchor or idempotency check failed — rolling back.")
        conn.rollback(); cur.close(); conn.close()
        sys.exit(1)

    # ── Show seam preview ───────────────────────────────────────────────────
    print(f"\nSEAM PREVIEW (200 chars before + after each anchor)")
    print('-' * 60)
    for p in PATCHES:
        idx = blob.find(p['anchor'])
        before = blob[max(0, idx - 200):idx]
        after = blob[idx + len(p['anchor']):idx + len(p['anchor']) + 200]
        print(f"\n--- {p['label']} ---")
        print('BEFORE:')
        print('  ' + before.replace('\n', '\n  '))
        print('  >>>>> [ANCHOR] ' + p['anchor'][:100] + ('...' if len(p['anchor']) > 100 else ''))
        print('AFTER:')
        print('  ' + after.replace('\n', '\n  '))

    # ── Apply ───────────────────────────────────────────────────────────────
    print(f"\nAPPLYING {len(PATCHES)} PATCH(ES)  (will {'ROLLBACK' if DRY_RUN else 'COMMIT'})")
    print('-' * 60)
    for p in PATCHES:
        entry = json.dumps([{
            'id': p['patch_id'],
            'phase': 'A_tier3_step6',
            'indicator': p['indicator'],
            'applied_at': '2026-05-03',
        }])
        cur.execute("""
            UPDATE modules_modulecontent
            SET content_data = REPLACE(content_data, %s, %s),
                metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{patches}',
                    COALESCE(metadata->'patches', '[]'::jsonb) || %s::jsonb
                ),
                updated_at = NOW()
            WHERE id = %s;
        """, (p['anchor'], p['replacement'], entry, ROW_ID))
        rc = cur.rowcount
        print(f"  {p['label']:>12s}  rowcount={rc}")

    # ── Post-state verify ───────────────────────────────────────────────────
    cur.execute("""
        SELECT length(content_data),
               jsonb_array_length(COALESCE(metadata->'patches', '[]'::jsonb)),
               jsonb_pretty(metadata->'patches')
        FROM modules_modulecontent WHERE id = %s;
    """, (ROW_ID,))
    post_len, post_n_patches, patches_json = cur.fetchone()
    delta = post_len - pre_len

    cur.execute("SELECT content_data FROM modules_modulecontent WHERE id = %s;", (ROW_ID,))
    post_blob = cur.fetchone()[0]

    print(f"\nPOST-STATE  len={post_len}  Δ={delta:+d}  patches[]={post_n_patches}")
    # Each patch contains its marker in BOTH open <!-- MARKER --> and close
    # <!-- /MARKER --> tags, so .count() of just the marker substring = 2.
    for p in PATCHES:
        m_count = post_blob.count(p['marker'])
        flag = '✓' if m_count == 2 else '✗'
        print(f"  {flag} {p['label']:>12s}  marker_post={m_count}  (expect 2 = open+close)")

    print(f"\nMETADATA.PATCHES (post-state):")
    print(patches_json)

    # ── Commit or rollback ──────────────────────────────────────────────────
    if DRY_RUN:
        conn.rollback()
        print("\n[ROLLBACK OK] dry-run only — no changes persisted.")
    else:
        conn.commit()
        print("\n[COMMIT OK] Step 6 patches applied to row 447.")

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
