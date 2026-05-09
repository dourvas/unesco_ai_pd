"""Atomic-chunk RAG ingest for Tier 3 Step 6 M8 patches (ethics + cross-ref)."""
import os, re, json, time
from datetime import datetime
import psycopg2
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))

NEW_GENAI_API = False
try:
    from google import genai as genai_client
    NEW_GENAI_API = True
    client = genai_client.Client(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

DB = dict(dbname='unesco_ai_teacher_pd', user='postgres', password='Django123!',
          host='localhost', port='5432')

PATCHES = [
    {
        'label': 'M8_ETHICS',
        'row_id': 447,
        'module_code': 'M8',
        'module_title': 'Advanced Prompt Engineering',
        'doc_title': 'M8: Hands-on Ethics in Your Prompts (Phase A T3 Step 6)',
        'topic_short': (
            'Ethics-by-design as a daily prompt-writing practice — three concrete '
            'pre-send checks: bias check (assumptions about student demographics, '
            'abilities, backgrounds), privacy check (real student names, identifiable '
            'details, sensitive information; replace with anonymised placeholders), '
            'inclusivity check (othering tone or framing; read aloud test). Studio '
            'templates embody ethics-by-design without conscious effort'
        ),
        'patch_id': 'm8_ethics_by_design',
        'indicator': 'CG3.2.4',
        'open': '<!-- M8_ETHICS_BY_DESIGN_PATCH -->',
        'close': '<!-- /M8_ETHICS_BY_DESIGN_PATCH -->',
    },
    {
        'label': 'M8_XREF_M3',
        'row_id': 447,
        'module_code': 'M8',
        'module_title': 'Advanced Prompt Engineering',
        'doc_title': 'M8: A Note on AI Techniques — Cross-Reference to M3 (Phase A T3 Step 6)',
        'topic_short': (
            'M8 specialises in generative AI — LLM-based prompt engineering. For a '
            'broader comparison of AI techniques (symbolic AI, predictive AI, '
            'generative AI) and when to use each, see M3 Part 2 (AI Categories and '
            'the Reliability Framework). M8 builds on that foundation; here we go '
            'deeper on the generative side'
        ),
        'patch_id': 'm8_cross_ref_m3',
        'indicator': 'CG3.2.1',
        'open': '<!-- M8_CROSS_REF_M3_PATCH -->',
        'close': '<!-- /M8_CROSS_REF_M3_PATCH -->',
    },
]


def clean(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    return text.strip()


def embed(text, retry=3):
    for a in range(retry):
        try:
            if NEW_GENAI_API:
                r = client.models.embed_content(
                    model='models/gemini-embedding-001',
                    contents=text,
                    config={'output_dimensionality': 768},
                )
                if hasattr(r, 'embeddings') and r.embeddings:
                    return r.embeddings[0].values
                return r if isinstance(r, list) else r.get('embedding', r)
            return genai.embed_content(
                model='models/text-embedding-004',
                content=text,
                task_type='retrieval_document',
            )['embedding']
        except Exception:
            if a < retry - 1:
                time.sleep((a + 1) * 2)
            else:
                raise


def main():
    print(f"\nTier 3 Step 6 M8 patches — atomic ingest ({len(PATCHES)} patches)")
    print(f"Start: {datetime.now()}\n")
    conn = psycopg2.connect(**DB)
    summary = []
    for i, p in enumerate(PATCHES, 1):
        print(f"--- [{i}/{len(PATCHES)}] {p['label']} ---")
        cur = conn.cursor()
        cur.execute('SELECT id FROM documents WHERE title = %s;', (p['doc_title'],))
        if cur.fetchone():
            print("  [SKIP] document with this title already exists")
            cur.close()
            continue
        cur.execute('SELECT id FROM modules_module WHERE code = %s;', (p['module_code'],))
        mod_id = cur.fetchone()[0]
        cur.execute('SELECT content_data FROM modules_modulecontent WHERE id = %s;', (p['row_id'],))
        blob = cur.fetchone()[0]
        cur.close()
        i0 = blob.find(p['open'])
        j0 = blob.find(p['close'])
        if i0 < 0 or j0 < 0:
            print(f"  [ERROR] could not locate patch markers in row {p['row_id']}")
            continue
        raw = blob[i0:j0 + len(p['close'])]
        cleaned = clean(raw)
        print(f"  raw={len(raw)}  cleaned={len(cleaned)}")
        chunk_text = (
            f"Module: {p['module_code']} — {p['module_title']}\n"
            f"Subject: Universal\n"
            f"Type: {p['topic_short']}\n"
            f"UNESCO Indicator: {p['indicator']}\n"
            f"Phase: A_tier3_step6  Patch: {p['patch_id']}\n"
            f"{cleaned}"
        )
        print(f"  chunk_text={len(chunk_text)}")
        emb = embed(chunk_text)
        emb_str = '[' + ','.join(repr(float(v)) for v in emb) + ']'
        time.sleep(5.0)

        doc_meta = {
            'source': 'modules_modulecontent',
            'module': p['module_code'],
            'type': p['patch_id'] + '_patch',
            'phase': 'A_tier3_step6',
            'patch_id': p['patch_id'],
            'unesco_indicators': [p['indicator']],
            'topic_short': p['topic_short'],
        }
        chunk_meta = {
            'patch_date': '2026-05-03',
            'phase': 'A_tier3_step6',
            'patch_id': p['patch_id'],
            'unesco_indicators': [p['indicator']],
            'atomic': True,
        }
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (title, document_type, module_id, file_path, "
            "metadata, created_at, updated_at) "
            "VALUES (%s, 'module_content', %s, 'database', %s::jsonb, NOW(), NOW()) "
            "RETURNING id;",
            (p['doc_title'], mod_id, json.dumps(doc_meta)),
        )
        doc_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO document_chunks (document_id, chunk_text, chunk_index, "
            "embedding, metadata, created_at) "
            "VALUES (%s, %s, 0, %s::vector, %s::jsonb, NOW()) RETURNING id;",
            (doc_id, chunk_text, emb_str, json.dumps(chunk_meta)),
        )
        chunk_id = cur.fetchone()[0]
        cur.execute(
            "UPDATE documents SET total_chunks = 1, updated_at = NOW() WHERE id = %s;",
            (doc_id,),
        )
        conn.commit()
        cur.close()
        print(f"  [OK] doc={doc_id} chunk={chunk_id}")
        summary.append({'label': p['label'], 'doc': doc_id, 'chunk': chunk_id})

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM document_chunks;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"\n[OK] Added {len(summary)}/{len(PATCHES)} chunks.  Total corpus: {total}")
    for s in summary:
        print(f"  {s}")


if __name__ == '__main__':
    main()
