"""
JSON repair for Gemini outputs that aren't strictly valid JSON.

Lifted verbatim from rag_query_system.clean_json_response and shared between
RTM (extract_tensions) and DTP (extract_development_themes). Kept here so
Phase E commit 9 can delete the monolith copy without touching the agents.
"""

import re


def clean_json_response(text: str) -> str:
    """Best-effort cleanup of a Gemini JSON-ish response.

    - Strips markdown code fences (```json ... ``` or generic ``` ... ```)
    - Trims to outermost { ... } boundaries
    - Normalises Unicode smart quotes to escaped ASCII
    - Replaces unescaped inner double quotes inside string values with
      single quotes so json.loads can parse the result

    Returns the cleaned string. Caller is responsible for json.loads and
    any error handling.
    """
    text = text.strip()
    if '```json' in text:
        text = text.split('```json')[-1].split('```')[0].strip()
    elif text.startswith('```'):
        text = text[3:].split('```')[0].strip()

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end + 1]

    text = text.replace('“', '\\"').replace('”', '\\"')
    text = text.replace('‘', "\\'").replace('’', "\\'")

    text = re.sub(
        r':\s*"(.*?)"(?=\s*[,}\]])',
        lambda m: ': "' + m.group(1).replace('"', "'") + '"',
        text,
        flags=re.DOTALL,
    )

    return text
