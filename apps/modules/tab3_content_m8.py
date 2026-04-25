"""
tab3_content_m8.py
M8 TAB3 Context — Advanced Prompt Engineering
UNESCO Aspect 3: AI Foundations | Level: Deepen

TAB3 Flow:
  Phase 1 — Build: EduPrompt Studio iframe, one excellent prompt
  Phase 2 — Execute: paste prompt → Gemini runs it → output shown (locked after first use)
  Phase 3 — Evaluate: structured form (radio/checkbox + 1 short text)
  Phase 4 — AI Feedback: optional button → RPE prompt assessment + output assessment
"""


def get_context():
    return {
        'studio_url': 'https://eduprompt-studio.up.railway.app/',

        'phase1_intro': (
            'Your goal is to build one excellent prompt. '
            'Use EduPrompt Studio to design a prompt for a real teaching need. '
            'Apply the RPE Framework: fill in every field carefully, use Enhanced Mode, '
            'and use the Improvement feature before you are satisfied. '
            'When your prompt is ready, copy it and paste it in Phase 2 below.'
        ),

        'phase2_intro': (
            'Paste your completed prompt below. '
            'The platform will run it through Gemini 2.5 Flash and show you the output. '
            'This is a one-time execution — after you see the result, '
            'further testing should be done directly in ChatGPT, Gemini, or Claude.'
        ),

        'phase3_intro': (
            'Evaluate what you received. '
            'These structured questions take two minutes '
            'and will inform your TAB5 reflection.'
        ),

        'evaluation_questions': {
            'usability': {
                'label': 'Would you use this output in your classroom?',
                'options': [
                    {'value': 'yes_as_is', 'label': '✅ Yes, as is'},
                    {'value': 'yes_with_edits', 'label': '✏️ Yes, with minor edits'},
                    {'value': 'needs_rework', 'label': '⚠️ No — needs significant rework'},
                    {'value': 'not_suitable', 'label': '❌ No — not suitable for my context'},
                ]
            },
            'rpe_visible': {
                'label': 'Which RPE strategies are clearly reflected in the output?',
                'options': [
                    {'value': 's1_goals', 'label': 'S1 — Goals: the output targets a clear learning outcome'},
                    {'value': 's2_context', 'label': 'S2 — Context: the output feels tailored to my students'},
                    {'value': 's3_format', 'label': 'S3 — Format: the output has the structure I asked for'},
                    {'value': 's4_cognitive', 'label': 'S4 — Cognitive Level: the output demands the right level of thinking'},
                    {'value': 's5_examples', 'label': 'S5 — Examples/Avoid: the output respects my include/avoid instructions'},
                ]
            },
            'cognitive_match': {
                'label': 'Does the output match the cognitive level you intended?',
                'options': [
                    {'value': 'yes_exactly', 'label': '✅ Yes, exactly'},
                    {'value': 'too_low', 'label': '⬇️ Too low — not demanding enough'},
                    {'value': 'too_high', 'label': '⬆️ Too high — too complex for this purpose'},
                    {'value': 'not_sure', 'label': '🤔 Not sure'},
                ]
            },
        },

        'phase4_intro': (
            'Get AI feedback on your prompt and output. '
            'The system will assess how well your prompt applies the RPE Framework '
            'and how pedagogically useful the output is. '
            'This is optional — but useful before your TAB5 reflection.'
        ),

        'completion_message': (
            'You have built, executed, and evaluated one high-quality prompt. '
            'The evaluation data and AI feedback will inform your TAB5 reflection. '
            'For further testing, open EduPrompt Studio in a new tab '
            'and run prompts directly in ChatGPT, Gemini, or Claude. '
            'In Module 10, you will share selected prompts with colleagues '
            'and explore how they function as boundary objects for professional learning.'
        ),
    }
