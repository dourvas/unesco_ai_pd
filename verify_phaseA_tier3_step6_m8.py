"""RAG retrieval verification for Tier 3 Step 6 M8 patches."""
import os
import time
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

# Per spec Section 6 + 7: target #1 mod-scoped, sim ≥ 0.78
QUERIES = [
    {
        'label': 'M8_ETHICS — primary',
        'query': 'How can I check my prompts for bias and privacy?',
        'expected_patch': 'm8_ethics_by_design',
        'mod_code': 'M8',
    },
    {
        'label': 'M8_ETHICS — alt 1',
        'query': 'What ethics checks should I apply to my prompts before using them?',
        'expected_patch': 'm8_ethics_by_design',
        'mod_code': 'M8',
    },
    {
        'label': 'M8_ETHICS — alt 2',
        'query': 'How do I make my prompts more inclusive and avoid student PII?',
        'expected_patch': 'm8_ethics_by_design',
        'mod_code': 'M8',
    },
    {
        'label': 'M8_XREF_M3 — primary',
        'query': 'How does M8 relate to M3 on AI techniques?',
        'expected_patch': 'm8_cross_ref_m3',
        'mod_code': 'M8',
    },
    {
        'label': 'M8_XREF_M3 — alt 1',
        'query': 'Where can I learn about symbolic AI versus generative AI?',
        'expected_patch': 'm8_cross_ref_m3',
        'mod_code': 'M8',
    },
    {
        'label': 'M8_XREF_M3 — alt 2',
        'query': 'What is the difference between predictive and generative AI?',
        'expected_patch': 'm8_cross_ref_m3',
        'mod_code': 'M8',
    },
]


def embed_query(text):
    if NEW_GENAI_API:
        r = client.models.embed_content(
            model='models/gemini-embedding-001',
            contents=text,
            config={'output_dimensionality': 768, 'task_type': 'RETRIEVAL_QUERY'},
        )
        if hasattr(r, 'embeddings') and r.embeddings:
            return r.embeddings[0].values
        return r if isinstance(r, list) else r.get('embedding', r)
    return genai.embed_content(
        model='models/text-embedding-004', content=text,
        task_type='retrieval_query',
    )['embedding']


def main():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT id FROM modules_module WHERE code = 'M8';")
    m8_id = cur.fetchone()[0]
    cur.close()

    print('=' * 78)
    print('TIER 3 STEP 6 — M8 PATCHES RAG VERIFICATION')
    print('=' * 78)

    for q in QUERIES:
        print(f"\n--- {q['label']} ---")
        print(f"Q: {q['query']!r}")
        emb = embed_query(q['query'])
        emb_str = '[' + ','.join(repr(float(v)) for v in emb) + ']'

        # Unfiltered top-3
        cur = conn.cursor()
        cur.execute("""
            SELECT dc.id, d.title, d.module_id,
                   1 - (dc.embedding <=> %s::vector) AS sim,
                   dc.metadata->>'patch_id' AS patch_id
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            ORDER BY dc.embedding <=> %s::vector
            LIMIT 3;
        """, (emb_str, emb_str))
        unfiltered = cur.fetchall()
        cur.close()

        # M8-scoped top-3
        cur = conn.cursor()
        cur.execute("""
            SELECT dc.id, d.title, d.module_id,
                   1 - (dc.embedding <=> %s::vector) AS sim,
                   dc.metadata->>'patch_id' AS patch_id
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE d.module_id = %s
            ORDER BY dc.embedding <=> %s::vector
            LIMIT 3;
        """, (emb_str, m8_id, emb_str))
        scoped = cur.fetchall()
        cur.close()

        print('  Unfiltered top-3:')
        for rank, row in enumerate(unfiltered, 1):
            chunk_id, title, mod_id, sim, pid = row
            mark = ' <- TARGET' if pid == q['expected_patch'] else ''
            print(f"    #{rank}  sim={sim:.4f}  chunk={chunk_id}  patch={pid!r}  title={title[:60]!r}{mark}")

        print(f"  M8-scoped top-3:")
        for rank, row in enumerate(scoped, 1):
            chunk_id, title, mod_id, sim, pid = row
            mark = ' <- TARGET' if pid == q['expected_patch'] else ''
            print(f"    #{rank}  sim={sim:.4f}  chunk={chunk_id}  patch={pid!r}  title={title[:60]!r}{mark}")

        # Verdict
        u_top = unfiltered[0]
        s_top = scoped[0]
        u_hit = u_top[4] == q['expected_patch']
        s_hit = s_top[4] == q['expected_patch']
        print(f"  Verdict: unfiltered #1 hit={u_hit} (sim={u_top[3]:.4f})  | M8-scoped #1 hit={s_hit} (sim={s_top[3]:.4f})")
        time.sleep(1.0)

    conn.close()
    print('\n' + '=' * 78)
    print('DONE')
    print('=' * 78)


if __name__ == '__main__':
    main()
