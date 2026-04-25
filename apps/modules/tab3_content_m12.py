"""
M12 TAB3 Context — Designing Ethical AI Systems for Education
UNESCO Aspect 2: Ethics | Level: Create
Deploy to: apps/modules/tab3_content_m12.py
"""


def get_context():
    return {

        # ── CHALLENGE 1 — Policy Audit ──────────────────────────────────────
        'sample_policy': {
            'title': 'Riverside School AI Use Policy (Draft)',
            'date': 'September 2024',
            'clauses': [
                {
                    'id': 'c1',
                    'label': 'Clause 1 — General Rule',
                    'text': 'Students may not use AI tools to complete assignments. Any work suspected of being AI-generated will receive a grade of zero.',
                },
                {
                    'id': 'c2',
                    'label': 'Clause 2 — Teacher Use',
                    'text': 'Teachers may use AI tools to support lesson preparation at their own discretion.',
                },
                {
                    'id': 'c3',
                    'label': 'Clause 3 — Detection',
                    'text': 'The school will use AI detection software to identify policy violations. Detection tool results are considered conclusive.',
                },
                {
                    'id': 'c4',
                    'label': 'Clause 4 — Special Cases',
                    'text': 'Students with special educational needs should speak to their class teacher.',
                },
                {
                    'id': 'c5',
                    'label': 'Clause 5 — Data',
                    'text': 'Student work may be processed by AI tools for educational purposes.',
                },
                {
                    'id': 'c6',
                    'label': 'Clause 6 — Review',
                    'text': 'This policy will be reviewed as needed.',
                },
            ],
        },

        'seven_elements': [
            'Clear Definitions',
            'Differentiated Expectations by Context',
            'Transparency and Disclosure Procedures',
            'Equity and Access Provisions',
            'Data Privacy and Tool Approval Process',
            'Integrity Procedures and Due Process',
            'Review and Update Cycle',
        ],

        'audit_ratings': [
            {'value': 'strong', 'label': '✅ Strong'},
            {'value': 'partial', 'label': '⚠️ Partial'},
            {'value': 'missing', 'label': '❌ Missing'},
        ],

        # ── CHALLENGE 2 — Designer's Cycle ──────────────────────────────────
        'designers_cycle_steps': [
            {
                'number': 1,
                'color': 'indigo',
                'title': 'Identify',
                'question': 'What is irreplaceable in my subject?',
                'hint': 'Name 2–3 learning experiences that AI cannot replicate: direct observation, personal voice, live performance, original argument, authentic creation.',
                'placeholder': 'e.g. In my subject, the irreplaceable experiences are...',
            },
            {
                'number': 2,
                'color': 'amber',
                'title': 'Map',
                'question': 'Where does AI help and where does it undermine learning?',
                'hint': 'Think of 3 specific tasks in your curriculum. For each: does AI support the learning goal, bypass it, or make no difference?',
                'placeholder': 'Task 1: [name] → AI [supports / bypasses / neutral] because...\nTask 2: ...\nTask 3: ...',
            },
            {
                'number': 3,
                'color': 'emerald',
                'title': 'Define',
                'question': 'What are the clear rules, task by task?',
                'hint': 'Write 3 specific task-level rules. Not general principles — specific guidance: "For [this task], AI use is [permitted / not permitted / requires disclosure] because..."',
                'placeholder': 'Rule 1: For [task], AI use is...\nRule 2: For [task], AI use is...\nRule 3: For [task], AI use is...',
            },
            {
                'number': 4,
                'color': 'teal',
                'title': 'Communicate',
                'question': 'How will I explain this to students and parents?',
                'hint': 'Write 2–3 sentences you would actually say to students at the start of a unit. Focus on the reasoning behind the rules, not just the rules.',
                'placeholder': 'To my students, I would explain: ...',
            },
            {
                'number': 5,
                'color': 'rose',
                'title': 'Review',
                'question': 'When will I evaluate whether my policy is working?',
                'hint': 'Set a specific review date and 2 questions you will ask yourself: What is working? What needs to change?',
                'placeholder': 'I will review this policy on [date]. I will ask myself: ...',
            },
        ],

        # ── CHALLENGE 3 — Edge Case Resolution ──────────────────────────────
        'edge_cases': [
            {
                'id': 'ec1',
                'title': 'The Emergency Claim',
                'icon': '🚨',
                'scenario': (
                    'A Year 11 student submits an essay that you suspect was AI-generated. '
                    'When you speak to her privately, she explains that her mother was hospitalised '
                    'the night before the deadline and she "had no choice." She has no documentation yet '
                    'but says she can get a letter from the hospital. '
                    'Two other students in your class also had extensions for minor reasons this term.'
                ),
                'guiding_questions': [
                    'How do you handle the wellbeing concern separately from the integrity concern?',
                    'What evidence standard do you apply before drawing any conclusion?',
                    'What alternative would you offer that is fair to this student and to peers?',
                ],
                'placeholder': 'My policy-level response to this situation would be:\n\n1. Regarding the student\'s wellbeing: ...\n2. Regarding the integrity concern: ...\n3. The policy clause I would draft from this case: ...',
                'model_response': {
                    'title': 'Policy-Level Approach',
                    'points': [
                        'Separate the two issues immediately: address the emergency first, the integrity concern second and only after the student\'s situation is stabilised.',
                        'Apply the same evidence standard as any other case — AI detection alone is never conclusive. Offer an oral discussion of the work.',
                        'Offer an alternative assessment pathway (extension + oral defence or fresh submission) documented consistently so similar situations receive similar treatment.',
                        'Draft a clause: "When a student claims personal emergency, welfare response takes priority. Integrity concerns are addressed through standard procedure after the emergency is resolved, with the same evidence threshold as any other case."',
                    ],
                },
            },
            {
                'id': 'ec2',
                'title': 'The Equity Complaint',
                'icon': '⚖️',
                'scenario': (
                    'You have allowed a student with a documented reading difficulty to use an AI grammar '
                    'and text-organisation tool throughout the term — this is specified in her learning plan. '
                    'Three other students come to you and say this is unfair: "She gets to use AI and we don\'t." '
                    'One parent has emailed the head teacher to complain that your class has inconsistent rules.'
                ),
                'guiding_questions': [
                    'How do you explain the distinction between accessibility support and general AI use?',
                    'What can you say to the class without disclosing the student\'s confidential information?',
                    'What policy clause would prevent this misunderstanding in future?',
                ],
                'placeholder': 'My policy-level response to this situation would be:\n\n1. What I would say to the class: ...\n2. What I would communicate to the parent/head teacher: ...\n3. The policy clause I would draft from this case: ...',
                'model_response': {
                    'title': 'Policy-Level Approach',
                    'points': [
                        'Explain to the class without disclosing specific needs: different students have different support requirements — as with reading glasses, calculators, or extra time. The goal is always the learning, not equal restriction.',
                        'Communicate to the head teacher: the accommodation is documented in the student\'s individual learning plan and is consistent with the school\'s inclusion principles and GDPR-compliant.',
                        'Draft a clause: "AI tools used as documented accessibility accommodations are not subject to general AI use restrictions. These uses are specified in individual student plans and are consistent with the school\'s inclusion policy."',
                        'Proactively share this clause with all students and parents at the start of the year to prevent future complaints.',
                    ],
                },
            },
            {
                'id': 'ec3',
                'title': 'The Outdated Policy',
                'icon': '📋',
                'scenario': (
                    'Your school\'s AI policy was written in 2022 — before ChatGPT existed. '
                    'It bans "automated writing tools" but makes no mention of large language models, '
                    'image generation, or AI-assisted coding. A student argues that since ChatGPT is '
                    'not an "automated writing tool" (it is a "conversational AI"), their use of it '
                    'on a graded essay is technically permitted. The head of department agrees the '
                    'policy is ambiguous.'
                ),
                'guiding_questions': [
                    'How do you respond to this student\'s argument in the short term?',
                    'What is the first step in updating the policy?',
                    'What definition clause would resolve this ambiguity?',
                ],
                'placeholder': 'My policy-level response to this situation would be:\n\n1. My immediate response to the student: ...\n2. The update process I would initiate: ...\n3. The definition clause I would draft: ...',
                'model_response': {
                    'title': 'Policy-Level Approach',
                    'points': [
                        'Respond to the student: the spirit of the policy is clear even if the letter is ambiguous — using any AI system to generate text submitted as your own work is not permitted. Apply this interpretation consistently while the policy is updated.',
                        'Initiate an urgent policy review: use the AI Tool Evaluation Checklist to audit tools currently in use, then convene a small working group to update definitions.',
                        'Draft a definition clause: "\'AI use\' means any use of systems that generate, rephrase, translate, or substantially edit text, images, code, or other content — including but not limited to large language models, conversational AI, image generation tools, grammar assistants, and code completion tools."',
                        'Note: broad definitions prevent loophole arguments; they should be paired with differentiated guidance about which uses are and are not permitted by task type.',
                    ],
                },
            },
            {
                'id': 'ec4',
                'title': 'The High-Stakes Disconnect',
                'icon': '📝',
                'scenario': (
                    'Your Year 12 students have been using AI tools freely throughout the year '
                    'for drafting, feedback, and research — as your classroom policy permits with disclosure. '
                    'Two months before their national examinations, you realise that several students '
                    'cannot write a coherent argument independently. They have become dependent on AI '
                    'to organise their thinking. The exam is closed-book with no AI access.'
                ),
                'guiding_questions': [
                    'What does this situation reveal about the policy you implemented?',
                    'What is the immediate pedagogical response?',
                    'What policy clause would prevent this in future?',
                ],
                'placeholder': 'My policy-level response to this situation would be:\n\n1. What this reveals about my policy design: ...\n2. My immediate response for these students: ...\n3. The policy clause I would add for future cohorts: ...',
                'model_response': {
                    'title': 'Policy-Level Approach',
                    'points': [
                        'This reveals a gap in the policy: permitting AI for all drafting without building in regular AI-free practice created dependency rather than supported learning.',
                        'Immediate response: intensive practice at independent writing tasks before the exam, framed honestly — "we need to make sure you can do this without support."',
                        'Draft a clause: "Classroom AI integration must include regular practice at tasks completed without AI assistance. At least [X]% of graded work each term must be completed under conditions that match high-stakes assessment — no AI, no external tools."',
                        'This is the Module 12 principle: classroom policy must prepare students for all contexts, including those where AI is not permitted.',
                    ],
                },
            },
            {
                'id': 'ec5',
                'title': 'The Cross-Subject Inconsistency',
                'icon': '🏫',
                'scenario': (
                    'A student points out — correctly — that her science teacher allows AI for lab report '
                    'write-ups, her history teacher bans it entirely, her English teacher requires disclosure '
                    'but permits it, and your class (mathematics) has never mentioned AI at all. '
                    '"How am I supposed to know what\'s allowed?" she asks. '
                    'You realise there is no coordination across the department.'
                ),
                'guiding_questions': [
                    'Is the inconsistency across subjects a problem, or is it appropriate?',
                    'What is the teacher\'s individual responsibility vs. the institution\'s responsibility here?',
                    'What process would you initiate to address this?',
                ],
                'placeholder': 'My policy-level response to this situation would be:\n\n1. My view on subject-level variation vs. school-wide consistency: ...\n2. What I will do in my own classroom immediately: ...\n3. The institutional process I would initiate: ...',
                'model_response': {
                    'title': 'Policy-Level Approach',
                    'points': [
                        'Subject-level variation is appropriate — AI use looks different across disciplines. But students need a coherent framework to navigate variation. The problem is not inconsistency per se, but invisible inconsistency.',
                        'Individual responsibility: clarify your own classroom policy in writing immediately. Do not wait for institutional action.',
                        'Institutional process: bring the student\'s question to a department or staff meeting as a system problem. Propose: each teacher writes their own subject policy using a shared template; these are compiled into a school-wide document students can consult.',
                        'Draft a meta-clause: "Each subject area maintains its own AI use guidelines, available to students in writing. All subject policies operate within the school\'s shared framework of principles."',
                    ],
                },
            },
        ],

        # Which 2 edge cases are shown by default (indices into edge_cases list)
        'active_edge_cases': [0, 1],
    }
