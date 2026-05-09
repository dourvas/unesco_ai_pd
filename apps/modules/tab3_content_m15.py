"""
M15 TAB3 Content — Professional Transformation & Research Leadership
UNESCO: Aspect 5 Professional Development | Level: Create

Three mouse-only synthesis challenges:
  Challenge 1 — Turning Points Mapper
  Challenge 2 — Portfolio Builder
  Challenge 3 — Leadership Stance Selector
"""


def get_context():
    return {

        # ── CHALLENGE 1 — TURNING POINTS MAPPER ─────────────────────────
        # The teacher selects 5 moments from a list of 15 that feel
        # most true for their own journey. Mouse-only — no free text.

        'turning_points': [
            {
                'value': 'tp_01',
                'label': 'I realised AI output needed my judgment before reaching students — not just my approval.'
            },
            {
                'value': 'tp_02',
                'label': 'I caught AI making a subject-specific error I would not have noticed a year ago.'
            },
            {
                'value': 'tp_03',
                'label': 'I explained to a parent why I use AI — and I actually knew what to say.'
            },
            {
                'value': 'tp_04',
                'label': 'I wrote a reflection that surprised me — I didn\'t expect to think that way about AI.'
            },
            {
                'value': 'tp_05',
                'label': 'I chose NOT to use AI for something, and I could articulate exactly why.'
            },
            {
                'value': 'tp_06',
                'label': 'I shared something about my AI practice with a colleague — and they found it useful.'
            },
            {
                'value': 'tp_07',
                'label': 'I felt genuinely uncertain about an ethical dimension of AI — and sat with that uncertainty rather than dismissing it.'
            },
            {
                'value': 'tp_08',
                'label': 'I designed a lesson where AI played a specific, purposeful role I could explain to a student.'
            },
            {
                'value': 'tp_09',
                'label': 'I noticed that a prompt I wrote six months ago wouldn\'t satisfy me now.'
            },
            {
                'value': 'tp_10',
                'label': 'I had a professional conversation about AI — with a colleague, a leader, or a parent — that I initiated.'
            },
            {
                'value': 'tp_11',
                'label': 'I documented something about my AI practice — even briefly — so someone else could learn from it.'
            },
            {
                'value': 'tp_12',
                'label': 'I overrode an AI suggestion because my knowledge of a specific student made the AI output wrong.'
            },
            {
                'value': 'tp_13',
                'label': 'I recognised a recurring professional tension in my reflections — and named it rather than resolving it.'
            },
            {
                'value': 'tp_14',
                'label': 'I thought about what AI means for my subject specifically — not just for "education" in general.'
            },
            {
                'value': 'tp_15',
                'label': 'I started to think of my reflection corpus as evidence of something — not just as completed tasks.'
            },
        ],

        # ── CHALLENGE 2 — PORTFOLIO BUILDER ─────────────────────────────
        # The teacher assigns artefact cards to the correct portfolio
        # column. One card per column must be marked as strongest evidence.
        # Mouse-only — radio buttons and select.

        'portfolio_columns': [
            {
                'key': 'prompt_library',
                'title': 'Prompt Library',
                'colour': 'blue',
                'description': 'Prompts that show disciplinary judgment — annotated with what they were designed to do.',
                'icon': '💬',
            },
            {
                'key': 'reflections',
                'title': 'Annotated Reflections',
                'colour': 'purple',
                'description': 'Three reflections showing development over time — each with a note on what changed.',
                'icon': '📝',
            },
            {
                'key': 'lesson_cycle',
                'title': 'Lesson Cycle',
                'colour': 'teal',
                'description': 'One documented lesson where AI played a purposeful role — what worked and what didn\'t.',
                'icon': '🎓',
            },
            {
                'key': 'contribution',
                'title': 'Community Contribution',
                'colour': 'green',
                'description': 'A moment where your practice became visible to others — shared, posted, or proposed.',
                'icon': '🌐',
            },
        ],

        'portfolio_cards': [
            {
                'value': 'card_a',
                'text': 'A prompt I wrote to generate misconception-based diagnostic questions — annotated with what I was trying to avoid.',
                'hint': 'Shows disciplinary judgment in prompt design.',
            },
            {
                'value': 'card_b',
                'text': 'My M3 reflection and my M12 reflection, read side by side — with a note on what shifted between them.',
                'hint': 'Shows development over time.',
            },
            {
                'value': 'card_c',
                'text': 'A lesson plan where AI generated the first-draft feedback and I documented where I overrode it and why.',
                'hint': 'Shows AI as purposeful tool with teacher judgment primary.',
            },
            {
                'value': 'card_d',
                'text': 'A post I shared in a subject network — a prompt with annotation — that three colleagues responded to.',
                'hint': 'Shows practice made visible to others.',
            },
            {
                'value': 'card_e',
                'text': 'Three prompts from M5, M8, and M14 — showing how my prompting approach evolved across levels.',
                'hint': 'Shows development in practice.',
            },
            {
                'value': 'card_f',
                'text': 'A one-page note I wrote for my department on what AI got wrong in our subject — with examples.',
                'hint': 'Documents practice as professional knowledge.',
            },
            {
                'value': 'card_g',
                'text': 'My TAB5 reflection from M7 — the one where I was most uncertain — annotated with what I understand now that I didn\'t then.',
                'hint': 'Captures genuine professional thinking in motion.',
            },
            {
                'value': 'card_h',
                'text': 'A proposal I made to my department for how AI should be used in one specific assessment task.',
                'hint': 'Shows leadership in practice.',
            },
        ],

        # ── CHALLENGE 3 — LEADERSHIP STANCE SELECTOR ────────────────────
        # A scenario + three levels of response (colleague / school /
        # policy). Radio buttons only — mouse-only throughout.

        'leadership_scenario': {
            'text': (
                'A colleague approaches you after a staff meeting. She teaches the same year group as you. '
                'She says: "I\'ve started using AI to mark first drafts. It saves me two hours a week. '
                'But I\'m not sure I\'m supposed to — and honestly, I\'m not sure the feedback is actually good. '
                'What do you think I should do?" '
                'You have been working through PROODOS for fifteen modules. You have thought carefully about '
                'exactly this kind of situation. What do you do?'
            ),
            'tags': ['Colleague support', 'AI assessment', 'Professional accountability', 'Systemic change'],
        },

        'leadership_responses': {
            'colleague': {
                'level': 'Your response to your colleague',
                'colour': 'blue',
                'icon': '👩‍🏫',
                'options': [
                    {
                        'value': 'col_a',
                        'label': 'Share your own experience',
                        'note': 'Tell her honestly what you have noticed about AI feedback in your own marking — the good and the gaps. Let her draw her own conclusions.',
                    },
                    {
                        'value': 'col_b',
                        'label': 'Ask her a clarifying question',
                        'note': 'Ask: "What does the feedback actually look like? Can you show me an example?" Surface the tacit knowledge before advising.',
                    },
                    {
                        'value': 'col_c',
                        'label': 'Give her a direct recommendation',
                        'note': 'Tell her clearly what you think she should do — and why — based on your professional judgment.',
                    },
                    {
                        'value': 'col_d',
                        'label': 'Invite her to document what she notices',
                        'note': 'Suggest she keeps a simple record — two weeks, what the AI got right and what it missed. Then you can look at it together.',
                    },
                ],
            },
            'school': {
                'level': 'Your response at school level',
                'colour': 'amber',
                'icon': '🏫',
                'options': [
                    {
                        'value': 'sch_a',
                        'label': 'Raise it informally with your department',
                        'note': 'Mention the conversation at your next team meeting — frame it as a shared question, not a problem to report.',
                    },
                    {
                        'value': 'sch_b',
                        'label': 'Propose a department discussion on AI and assessment',
                        'note': 'Suggest a structured 30-minute conversation — bring one documented example and ask colleagues to bring theirs.',
                    },
                    {
                        'value': 'sch_c',
                        'label': 'Suggest a clear policy is needed',
                        'note': 'Bring the gap to school leadership: teachers are making individual decisions because there is no shared guidance. Propose that guidance is developed.',
                    },
                    {
                        'value': 'sch_d',
                        'label': 'Do nothing at school level yet',
                        'note': 'The conversation was private. Support your colleague first — a school-level move can come later if the issue is wider.',
                    },
                ],
            },
            'system': {
                'level': 'Your response at systemic level',
                'colour': 'green',
                'icon': '🌐',
                'options': [
                    {
                        'value': 'sys_a',
                        'label': 'Document your own practice as evidence',
                        'note': 'Write up what you have learned about AI and assessment in your subject. Three paragraphs. That is the foundation of any systemic argument.',
                    },
                    {
                        'value': 'sys_b',
                        'label': 'Connect the conversation to a wider professional community',
                        'note': 'Share the question — anonymised — in a subject network or CoP. Find out whether others are navigating the same thing.',
                    },
                    {
                        'value': 'sys_c',
                        'label': 'Contribute to a policy conversation',
                        'note': 'If your school or district is developing AI guidance, ask to be involved. Practitioner knowledge belongs in policy discussions.',
                    },
                    {
                        'value': 'sys_d',
                        'label': 'Wait for systemic clarity before acting',
                        'note': 'Systemic change takes time. Focus on your own classroom and your colleague — the system will follow when enough practitioners have done this work.',
                    },
                ],
            },
        },

        # ── COMPLETED STATE DISPLAY LABELS ──────────────────────────────
        'portfolio_column_labels': {
            'prompt_library': 'Prompt Library',
            'reflections': 'Annotated Reflections',
            'lesson_cycle': 'Lesson Cycle',
            'training_module': 'Training Module',
            'contribution': 'Community Contribution',
        },

        # ============================================================
        # PHASE A TIER 2 STEP 5 — Tier 5 Training Module (CA5.3.2)
        # JSONB approach (Decision 5) — no migration; optional 5th column
        # gated by yes/no question. Soft-mandatory textarea (200 chars)
        # for teachers who design PD training for colleagues.
        # ============================================================
        'tier5_training_module': {
            'key': 'training_module',
            'icon': '🎓',
            'title': 'Training Module',
            'colour': 'amber',
            'description': (
                'For teachers who want to design PD training for colleagues. '
                'Include: training programme outline (5+ sessions), scaffolded '
                'activities, accessibility considerations, evaluation rubric. '
                'Validated by your school PD lead or a master trainer in your network.'
            ),
            'selection_criterion': (
                'Have you designed (or do you plan to design) PD training for '
                'other teachers in AI integration?'
            ),
            'input_label': (
                'Briefly describe the audience and goals of your training programme '
                '(200 characters)'
            ),
            'input_placeholder': 'Who will attend, and what should they be able to do after?',
            'input_max_length': 200,
            'soft_mandatory_message': (
                'Your training tier is strongest when you can articulate audience '
                'and goals. Continue without describing them?'
            ),
            # 2 dedicated cards added below in portfolio_cards extension
            'card_values': ['card_i', 'card_j'],
        },

        # 2 NEW training-related cards (extend portfolio_cards via the
        # tier5_training_module-specific column rendering, kept here for
        # discoverability)
        'tier5_training_cards': [
            {
                'value': 'card_i',
                'text': 'A training session outline I designed for colleagues — sequence, activities, reflection moments — with a note on what I would adjust after one round.',
                'hint': 'Shows PD design intent + iteration awareness.',
            },
            {
                'value': 'card_j',
                'text': 'A 5-session AI integration programme outline I delivered (or plan to deliver) — with accessibility considerations and an evaluation rubric.',
                'hint': 'Shows training-programme-level design and validation thinking.',
            },
        ],
    }
