# apps/modules/tab3_content_m7.py
# M7 TAB3 Context — Navigating Ethical Dilemmas in Practice
# UNESCO Aspect 2: Ethics | Level: Deepen


def get_context():
    return {

        # ── Challenge 1: Dilemma Mapping ──────────────────────────────────
        'scenario': {
            'text': (
                "Amara is a 16-year-old student who recently moved to your school from another country. "
                "Her written Greek is still developing, but her understanding of the subject matter — as evidenced "
                "in class discussions — is clearly strong. She submits an essay that is noticeably more fluent and "
                "polished than her previous written work. When asked privately, she admits she used an AI tool to "
                "rephrase her ideas into better Greek, but insists the thinking and argument are entirely her own.\n\n"
                "Two of your colleagues have opposite reactions: one says this is a clear integrity violation and "
                "the work should not be accepted. The other says refusing Amara's essay while accepting native "
                "speakers' work — which also gets informal help — is discriminatory."
            ),
            'tags': ['fairness', 'academic integrity', 'language equity', 'transparency', 'accountability'],
        },

        'principles': [
            {'value': 'fairness',         'label': 'Fairness'},
            {'value': 'accountability',   'label': 'Accountability'},
            {'value': 'transparency',     'label': 'Transparency'},
            {'value': 'human_oversight',  'label': 'Human Oversight'},
            {'value': 'privacy',          'label': 'Privacy'},
            {'value': 'non_discrimination', 'label': 'Non-discrimination'},
        ],

        'tensions': [
            {
                'value': 'equity_vs_standards',
                'label': 'Equity vs. Standards',
                'note': (
                    'Treating Amara fairly as a language learner may mean applying different standards — '
                    'but different standards can undermine the integrity of shared assessments.'
                ),
            },
            {
                'value': 'intent_vs_output',
                'label': 'Intent vs. Output',
                'note': (
                    'The thinking is genuinely Amara\'s, but the submitted text is AI-assisted. '
                    'Should assessment measure original thought or original expression?'
                ),
            },
            {
                'value': 'disclosure_vs_penalty',
                'label': 'Disclosure vs. Penalty',
                'note': (
                    'Amara was honest when asked. If honesty leads to penalty, it creates a perverse '
                    'incentive for future students to hide AI use rather than disclose it.'
                ),
            },
            {
                'value': 'consistency_vs_context',
                'label': 'Consistency vs. Context',
                'note': (
                    'Applying the same rule to every student seems fair — but identical rules applied '
                    'to students with very different circumstances can produce unfair outcomes.'
                ),
            },
        ],

        'decisions': [
            {
                'value': 'accept_with_note',
                'label': 'Accept the essay with a disclosure note',
                'note': (
                    'Accept the essay as submitted, adding a brief note that AI was used for language '
                    'support, and treat this as the appropriate model going forward.'
                ),
            },
            {
                'value': 'oral_follow_up',
                'label': 'Accept the essay, but add an oral follow-up',
                'note': (
                    'Ask Amara to explain her argument in a brief conversation. '
                    'If she demonstrates genuine understanding, this confirms the work reflects her thinking.'
                ),
            },
            {
                'value': 'resubmit',
                'label': 'Ask for a resubmission in her own words',
                'note': (
                    'Return the essay and ask Amara to rewrite it in her own Greek, even if imperfect. '
                    'Assess the thinking, not the language quality.'
                ),
            },
            {
                'value': 'escalate_policy',
                'label': 'Escalate to create a school-wide policy',
                'note': (
                    'This is too important to decide alone. Bring the case — anonymised — to a colleague '
                    'or leadership team as the basis for a shared protocol.'
                ),
            },
        ],

        'perspectives': [
            {
                'title': 'The Equity Lens: AI as a Language Scaffold',
                'text': (
                    'Many educators argue that language is not the learning objective in most subjects — '
                    'subject understanding is. For a student whose first language is not the language of '
                    'instruction, AI-assisted phrasing may be equivalent to the informal support native '
                    'speakers receive from family members, tutors, or more fluent peers. The question becomes: '
                    'are we assessing language proficiency, or are we assessing understanding of the subject? '
                    'If the answer is the latter, then AI for language support does not compromise the '
                    'assessment\'s validity — it restores it.'
                ),
            },
            {
                'title': 'The Integrity Lens: The Transparency Dividend',
                'text': (
                    'Amara disclosed her AI use when asked directly. This is precisely the behaviour we want '
                    'to cultivate. Penalising disclosure — even indirectly — creates a clear incentive for '
                    'future students to hide AI involvement rather than acknowledge it. Many educators recommend '
                    'treating transparent AI use very differently from concealed AI use: the former is a sign '
                    'of ethical maturity and should be recognised as such, even if conditions are set on its use.'
                ),
            },
            {
                'title': 'The Assessment Lens: Redesign Rather Than Police',
                'text': (
                    'A third perspective steps back from the immediate case and asks: what does this scenario '
                    'reveal about the assessment design? If a student can meet the assessment\'s requirements '
                    'with AI language support, the assessment may not be adequately measuring what it intends '
                    'to measure. Rather than enforcing rules on this submission, some educators see cases like '
                    'Amara\'s as an opportunity to add a process component — an oral explanation, a revision '
                    'trace, a brief reflection — that makes genuine understanding visible regardless of the '
                    'final product\'s language quality.'
                ),
            },
        ],

        # ── Challenge 2: Action Plan Builder ─────────────────────────────
        'strategy_options': {
            '1': {
                'title': 'Focus on Process, Not Just Product',
                'hint': 'Capturing the learning journey makes AI shortcuts less rewarding and genuine engagement more visible.',
                'options': [
                    {
                        'value': 's1a',
                        'text': "Add a 'process note' requirement to my next major assignment — students answer: what did you struggle with, and what decisions did you make?",
                    },
                    {
                        'value': 's1b',
                        'text': "Ask students to submit a draft alongside their final work for at least one assignment this term.",
                    },
                    {
                        'value': 's1c',
                        'text': "Introduce a short oral check-in on one written assignment — asking each student to explain one key decision they made.",
                    },
                ],
            },
            '2': {
                'title': 'Design Authentic Tasks',
                'hint': 'Tasks rooted in local context and personal experience are significantly harder to outsource to AI.',
                'options': [
                    {
                        'value': 's2a',
                        'text': "Redesign one upcoming assignment to require reference to our specific classroom discussions, local events, or students' own experiences.",
                    },
                    {
                        'value': 's2b',
                        'text': "Replace a general essay prompt with a task requiring students to take and defend a personal position based on their own observations.",
                    },
                    {
                        'value': 's2c',
                        'text': "Add a 'connection to our community' requirement to an existing assignment, making it impossible to complete with generic AI output.",
                    },
                ],
            },
            '3': {
                'title': 'Build Disclosure Literacy',
                'hint': 'A culture of transparency is more sustainable and more educational than a culture of surveillance.',
                'options': [
                    {
                        'value': 's3a',
                        'text': "Introduce an AI use disclosure field as a standard part of at least one assignment this term, and model how to fill it in.",
                    },
                    {
                        'value': 's3b',
                        'text': "Have an explicit classroom conversation about the difference between using AI as a tool and submitting AI work as your own — before the next major assignment.",
                    },
                    {
                        'value': 's3c',
                        'text': "Share my own AI use with students — demonstrating when I use AI tools in my own work and how I disclose or acknowledge that use.",
                    },
                ],
            },
            '4': {
                'title': 'Dialogue Before Judgment',
                'hint': 'When something feels wrong about a student\'s work, conversation is almost always more productive — and more fair — than accusation.',
                'options': [
                    {
                        'value': 's4a',
                        'text': "Commit to a private conversation with any student whose work raises concerns before taking any formal action — asking them to walk me through their process.",
                    },
                    {
                        'value': 's4b',
                        'text': "Prepare a short list of neutral process questions I can use in these conversations — questions that reveal genuine understanding without feeling accusatory.",
                    },
                    {
                        'value': 's4c',
                        'text': "Discuss with a colleague how we would handle a suspected AI misuse case together — so I am not making consequential decisions alone.",
                    },
                ],
            },
        },

        # ── Challenge 3: AI Detector Reality Check ────────────────────────
        # Writing samples are hardcoded in the template (no dynamic data needed)
        # The reveal is also hardcoded — it's the same for everyone
    }
