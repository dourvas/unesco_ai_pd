import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from google.genai import types as genai_types
from rag_query_system import client

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Return a JSON object with exactly 2 tensions. Each tension has label, left_pole, right_pole, grounding_quote fields. Make each field about 20 words long.',
    config=genai_types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=2500
    )
)
print('LENGTH:', len(response.text))
print('TEXT:', repr(response.text))