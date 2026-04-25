"""
tab3_content_m3.py
M3 TAB3 Context — AI Tools for Educators: Understand, Evaluate & Curate
UNESCO Aspect 3: AI Foundations | Level: Acquire

3 Challenges:
  1. Reliability Framework in Action — Try a tool, then evaluate it
  2. Build Your Starter Toolkit — Organise tools by pedagogical purpose
  3. Spot the Category — Classify AI tools as Symbolic / Predictive / Generative
"""


def get_context():
    return {

        # ── Challenge 1 ──────────────────────────────────────────────────────
        # Try a tool, then evaluate using the Reliability Framework
        'c1_starter_tools': [
            {
                'name': 'ChatGPT (free)',
                'url': 'https://chat.openai.com',
                'task': 'Ask it to create 3 discussion questions on a topic you are currently teaching. No account needed for basic use.',
                'category': 'Generative AI',
            },
            {
                'name': 'Gemini (free)',
                'url': 'https://gemini.google.com',
                'task': 'Ask it to explain a concept from your subject to a 12-year-old. Sign in with any Google account.',
                'category': 'Generative AI',
            },
            {
                'name': 'Perplexity AI (free)',
                'url': 'https://www.perplexity.ai',
                'task': 'Search for a factual topic from your subject. Note whether it provides sources. No account needed.',
                'category': 'Generative AI (with search)',
            },
        ],

        'c1_dimensions': [
            {
                'key': 'accuracy',
                'label': 'Accuracy',
                'icon': '🎯',
                'question': 'Did it produce factually correct output for your subject?',
                'hint': 'Ask something you already know the answer to — did it get it right?',
            },
            {
                'key': 'appropriateness',
                'label': 'Appropriateness',
                'icon': '👥',
                'question': 'Is the tone and content level suitable for your students?',
                'hint': 'Would you be comfortable sharing this output directly with your class?',
            },
            {
                'key': 'local_context',
                'label': 'Local Context',
                'icon': '🗺️',
                'question': 'Does it work in your teaching language and understand your curriculum?',
                'hint': 'Test in your teaching language. Ask about your national curriculum or local examples.',
            },
            {
                'key': 'accessibility',
                'label': 'Accessibility',
                'icon': '♿',
                'question': 'Can all your students access it? Does it require accounts, devices, or data?',
                'hint': 'Think about your most disadvantaged students — would they be excluded?',
            },
            {
                'key': 'cost',
                'label': 'Cost & Sustainability',
                'icon': '💰',
                'question': 'Is the free tier sufficient? Is this tool likely to remain available?',
                'hint': 'Check if the features you used are free or paid. Has the tool changed pricing recently?',
            },
        ],

        'c1_ratings': [
            {'value': 'strong', 'label': '✅ Strong', 'color': 'success'},
            {'value': 'acceptable', 'label': '⚠️ Acceptable', 'color': 'warning'},
            {'value': 'weak', 'label': '❌ Weak', 'color': 'error'},
            {'value': 'not_tested', 'label': '— Not tested', 'color': 'ghost'},
        ],

        'c1_decisions': [
            {'value': 'adopt', 'label': '✅ Adopt — suitable for my classroom'},
            {'value': 'caution', 'label': '⚠️ Use with caution — works but needs verification'},
            {'value': 'teacher_only', 'label': '🔒 Teacher use only — not suitable for direct student use'},
            {'value': 'reject', 'label': '❌ Not suitable — for this purpose at this time'},
        ],

        # ── Challenge 2 ──────────────────────────────────────────────────────
        # Build Your Starter Toolkit — organise by pedagogical purpose
        'c2_categories': [
            {
                'key': 'content_creation',
                'label': '✍️ Content Creation',
                'description': 'Lesson plans, worksheets, explanations, presentations',
                'example': 'e.g. ChatGPT, Claude',
            },
            {
                'key': 'assessment',
                'label': '📊 Assessment',
                'description': 'Quiz generation, rubrics, feedback templates',
                'example': 'e.g. Gemini, Diffit',
            },
            {
                'key': 'differentiation',
                'label': '🎯 Differentiation',
                'description': 'Simplified texts, reading levels, accessibility adaptations',
                'example': 'e.g. Diffit, Claude',
            },
            {
                'key': 'feedback',
                'label': '💬 Feedback',
                'description': 'Student comments, parent emails, report drafts',
                'example': 'e.g. Copilot, ChatGPT',
            },
            {
                'key': 'admin',
                'label': '🔧 Admin & Planning',
                'description': 'Meeting summaries, planning templates, research',
                'example': 'e.g. Perplexity, Gemini',
            },
        ],

        # ── Challenge 3 ──────────────────────────────────────────────────────
        # Spot the Category — classify 5 AI tools
        'c3_tools': [
            {
                'id': 'tool_a',
                'name': 'Tool A',
                'description': 'A writing support app that checks your grammar and spelling by applying a set of language rules. It flags errors based on predefined patterns and suggests corrections.',
                'correct': 'symbolic',
                'explanation': 'This is Symbolic AI — it applies explicit, predefined language rules to identify and correct errors. There is no learning from data involved; the rules are fixed.',
            },
            {
                'id': 'tool_b',
                'name': 'Tool B',
                'description': 'A learning platform that tracks each student\'s quiz performance over time and automatically adjusts the difficulty of the next set of practice questions to match their level.',
                'correct': 'predictive',
                'explanation': 'This is Predictive AI — it learns patterns from student performance data and uses those patterns to predict what difficulty level will be most effective next. It adapts based on past behaviour.',
            },
            {
                'id': 'tool_c',
                'name': 'Tool C',
                'description': 'A chatbot assistant that can write a lesson plan, answer questions about your subject, and draft a parent communication — all based on the instructions you provide.',
                'correct': 'generative',
                'explanation': 'This is Generative AI — it produces new, original content (lesson plans, text, answers) based on patterns learned from large amounts of training data. The output is created, not retrieved.',
            },
            {
                'id': 'tool_d',
                'name': 'Tool D',
                'description': 'A classroom behaviour management app that analyses patterns in student engagement data across the school year and flags students who may be at risk of disengaging.',
                'correct': 'predictive',
                'explanation': 'This is Predictive AI — it analyses historical patterns in data to make predictions about future outcomes (at-risk students). It does not create content; it identifies patterns to forecast behaviour.',
            },
            {
                'id': 'tool_e',
                'name': 'Tool E',
                'description': 'A maths practice app where students solve equations step-by-step. The app checks each step against a fixed set of mathematical rules and immediately indicates whether each step is correct or incorrect.',
                'correct': 'symbolic',
                'explanation': 'This is Symbolic AI — it verifies each step against fixed mathematical rules. The system does not learn or adapt; it applies predefined logic to determine correctness.',
            },
        ],

        'c3_categories': [
            {'value': 'symbolic', 'label': '⚙️ Symbolic AI', 'sublabel': 'Rule-based · Predictable'},
            {'value': 'predictive', 'label': '📊 Predictive AI', 'sublabel': 'Pattern-based · Adaptive'},
            {'value': 'generative', 'label': '✨ Generative AI', 'sublabel': 'Creative · Flexible'},
        ],
    }
