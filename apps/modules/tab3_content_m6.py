"""
M6 -- Human Accountability in AI
UNESCO Aspect 1: Human-Centred Mindset | Level: Deepen

TAB3 context data for the 3-challenge activity sequence:
  Challenge 1: AI Audit -- read vendor claims, identify what is missing
  Challenge 2: Evaluation Card in Action -- apply the 5-question framework
  Challenge 3: The Override Decision -- accept, adjust, or reject AI output
"""


def get_context():
    return {

        # -- CHALLENGE 1: AI AUDIT -------------------------------------------
        # Scenario: vendor promotional material with missing critical information
        'scenario': {
            'text': (
                'An EdTech company has released an AI-powered writing feedback tool '
                'for secondary students. The promotional material states:\n\n'
                '"Our model was trained on over 2 million student essays and achieves '
                '92% accuracy in identifying grammatical errors and 87% accuracy in '
                'assessing argumentative quality. Teachers in our pilot school rated '
                'student improvement at 4.3 out of 5."\n\n'
                'Your school\'s purchasing committee is meeting in 30 minutes '
                'to approve a 3-year contract. You have time to raise two or three questions.'
            ),
            'tags': ['Algorithmic transparency', 'Vendor claims', 'Black box', 'Deepen'],
        },

        # Challenge 1 Step 1: Which critical questions are most urgent?
        'principles': [
            {'value': 'demographic_breakdown',
             'label': 'Accuracy across different student groups?'},
            {'value': 'training_data_origin',
             'label': 'Where did the 2 million essays come from?'},
            {'value': 'explainability',
             'label': 'Can the tool explain its scores?'},
            {'value': 'gdpr_approval',
             'label': 'Has GDPR compliance been verified?'},
            {'value': 'pilot_independence',
             'label': 'Was the pilot independently evaluated?'},
            {'value': 'override_possible',
             'label': 'Can teachers review and override outputs?'},
            {'value': 'contract_exit',
             'label': 'Is there an exit clause if the tool underperforms?'},
            {'value': 'eal_performance',
             'label': 'How does it perform for EAL/D learners?'},
        ],

        # Challenge 1 Step 2: Where is the core transparency gap?
        'tensions': [
            {
                'value': 'accuracy_for_whom',
                'label': '"92% accurate" -- but for which students?',
                'note': (
                    'Accuracy averaged across a population can mask very poor performance '
                    'for specific subgroups: EAL/D learners, students with disabilities, '
                    'or students whose writing style differs from the training set.'
                ),
            },
            {
                'value': 'pilot_bias',
                'label': 'Teacher satisfaction does not equal student improvement',
                'note': (
                    'A 4.3/5 teacher rating from a self-selected pilot is evidence of '
                    'teacher satisfaction -- not independent evidence that students learned more. '
                    'Selection bias and social desirability effects are significant here.'
                ),
            },
            {
                'value': 'lock_in_risk',
                'label': '3-year contract for an unaudited system',
                'note': (
                    'A long-term contract removes the ability to exit if bias or harm is '
                    'discovered later. Vendors who are confident in their tool '
                    'typically welcome short pilots with exit clauses.'
                ),
            },
            {
                'value': 'no_explanation',
                'label': 'Scores without reasoning -- a legal accountability gap',
                'note': (
                    'If the tool cannot explain why a student received a particular score, '
                    'the teacher cannot justify that score to the student or their family. '
                    'This may be a legal problem under GDPR and the EU AI Act.'
                ),
            },
        ],

        # Challenge 1 Step 3: Professional recommendation
        'decisions': [
            {
                'value': 'pause_and_audit',
                'label': 'Pause -- request an independent audit before signing',
                'note': (
                    'Ask for bias testing across student demographics, GDPR compliance '
                    'documentation, and an independent accuracy review. Worth a delay.'
                ),
            },
            {
                'value': 'pilot_first',
                'label': 'Pilot -- approve a 6-month trial with a defined exit clause',
                'note': (
                    'Limit to two classes, appoint a teacher review lead, and establish '
                    'clear criteria before full rollout. Preserves the option to exit.'
                ),
            },
            {
                'value': 'conditional_approve',
                'label': 'Conditionally approve -- with mandatory override protocols',
                'note': (
                    'Proceed, but require teachers to document any AI assessment they '
                    'override, prohibit use for final grades, and review at 6 months.'
                ),
            },
            {
                'value': 'reject',
                'label': 'Reject -- the evidence provided is insufficient',
                'note': (
                    'No demographic breakdown, no independent verification, no GDPR '
                    'documentation, no explanation capability, and a 3-year lock-in. '
                    'The transparency gap is too large for a high-stakes educational tool.'
                ),
            },
        ],

        # Challenge 1 completed state -- perspectives
        'perspectives': [
            {
                'title': 'The demographic breakdown question',
                'text': (
                    'Experienced educators ask: "accurate for which students?" '
                    'A model trained on native-speaker essays from well-resourced schools '
                    'may perform significantly worse for EAL/D learners or students from '
                    'under-represented backgrounds. Accuracy claims without demographic '
                    'breakdowns are incomplete information, not evidence of fairness.'
                ),
            },
            {
                'title': 'The 4.3/5 teacher rating problem',
                'text': (
                    'Pilot ratings from self-selected participants are subject to '
                    'selection bias and social desirability effects. Teachers who found the '
                    'tool useful are more likely to participate and rate it highly. '
                    'This is evidence of satisfaction in a non-representative sample -- '
                    'not independent evidence of student improvement.'
                ),
            },
            {
                'title': 'The EU AI Act dimension',
                'text': (
                    'An AI tool that assesses student writing quality may qualify as a '
                    'high-risk AI system under the EU AI Act -- which requires '
                    'transparency, human oversight, and the right to explanation. '
                    'A vendor who cannot provide these assurances may not meet legal '
                    'requirements for use in EU educational institutions from 2026.'
                ),
            },
        ],

        # -- CHALLENGE 2: EVALUATION CARD IN ACTION -------------------------
        # Apply the 5-question Critical AI Evaluation Card to a tool scenario
        'eval_tool': {
            'name': 'SmartLearn Adaptive Quiz',
            'description': (
                'Your school has received free access to SmartLearn Adaptive Quiz: '
                'an AI tool that generates personalised quiz questions, adjusts difficulty '
                'based on performance, and produces a weekly "mastery report" per student '
                'that is sent automatically to parents. '
                'A colleague wants to start using it next week. '
                'You remember the Critical AI Evaluation Card from this module.'
            ),
        },

        # Five Card questions with multiple-choice answers
        'card_questions': [
            {
                'id': 'q1',
                'question': '1. Who made this tool -- and for what purpose?',
                'options': [
                    {
                        'value': 'a',
                        'label': 'The vendor says: built for US middle schools, optimised for Common Core standards.',
                        'correct': True,
                        'implication': (
                            'A tool built for US Common Core may not align with your curriculum. '
                            'Its question bank and difficulty calibration may not match your students. '
                            'This warrants careful piloting before full adoption.'
                        ),
                    },
                    {
                        'value': 'b',
                        'label': 'Built by a European university research team for multilingual classroom contexts.',
                        'correct': False,
                        'implication': '',
                    },
                    {
                        'value': 'c',
                        'label': 'The vendor provides no information about training context or original purpose.',
                        'correct': False,
                        'implication': '',
                    },
                ],
            },
            {
                'id': 'q2',
                'question': '2. What data does it use -- and whose?',
                'options': [
                    {
                        'value': 'a',
                        'label': 'Student quiz responses are stored on the vendor\'s US-based servers. No GDPR documentation provided.',
                        'correct': True,
                        'implication': (
                            'Storing student data on servers outside the EU without confirmed GDPR '
                            'compliance is a significant data protection risk. Your school\'s DPO '
                            'must review this before any student data is processed. '
                            'This alone may prevent use of the tool.'
                        ),
                    },
                    {
                        'value': 'b',
                        'label': 'All processing is on-device. No student data leaves the school network.',
                        'correct': False,
                        'implication': '',
                    },
                    {
                        'value': 'c',
                        'label': 'Student data is anonymised before processing. GDPR compliance is certified.',
                        'correct': False,
                        'implication': '',
                    },
                ],
            },
            {
                'id': 'q3',
                'question': '3. Can it explain its outputs?',
                'options': [
                    {
                        'value': 'a',
                        'label': 'The mastery report shows percentage scores only. No explanation of how mastery is calculated.',
                        'correct': True,
                        'implication': (
                            'A mastery report sent to parents that cannot explain how '
                            'mastery was determined is problematic. If a parent questions the '
                            'report, you cannot explain it. Unexplained outputs should not be '
                            'sent to parents without teacher review and contextualisation.'
                        ),
                    },
                    {
                        'value': 'b',
                        'label': 'Each mastery level includes a breakdown of which question types were answered correctly.',
                        'correct': False,
                        'implication': '',
                    },
                    {
                        'value': 'c',
                        'label': 'The tool provides a natural language explanation for each mastery assessment.',
                        'correct': False,
                        'implication': '',
                    },
                ],
            },
            {
                'id': 'q4',
                'question': '4. What are the stakes of this decision?',
                'options': [
                    {
                        'value': 'a',
                        'label': 'High -- mastery reports are sent directly to parents and shape their view of their child\'s progress.',
                        'correct': True,
                        'implication': (
                            'Automated reports sent directly to parents without teacher review '
                            'are high-stakes: they shape parental perceptions of student ability, '
                            'may cause anxiety, and remove your opportunity to contextualise or '
                            'correct before the information reaches the family.'
                        ),
                    },
                    {
                        'value': 'b',
                        'label': 'Low -- the quizzes are purely for practice, with no reports or records kept.',
                        'correct': False,
                        'implication': '',
                    },
                    {
                        'value': 'c',
                        'label': 'Medium -- teachers see reports but decide whether to share them with parents.',
                        'correct': False,
                        'implication': '',
                    },
                ],
            },
            {
                'id': 'q5',
                'question': '5. Can I review, adjust, and override the output?',
                'options': [
                    {
                        'value': 'a',
                        'label': 'No -- reports are auto-generated and sent to parents automatically at end of each week.',
                        'correct': True,
                        'implication': (
                            'Auto-sending high-stakes reports without teacher review is a direct '
                            'accountability gap. If the report is inaccurate, a teacher is left '
                            'managing consequences of a communication they never approved. '
                            'This conflicts with the EU AI Act\'s requirement for meaningful '
                            'human oversight in high-stakes educational decisions.'
                        ),
                    },
                    {
                        'value': 'b',
                        'label': 'Yes -- reports are drafted and held for teacher approval before sending.',
                        'correct': False,
                        'implication': '',
                    },
                    {
                        'value': 'c',
                        'label': 'Partially -- teachers can delay sending but cannot edit the report content.',
                        'correct': False,
                        'implication': '',
                    },
                ],
            },
        ],

        # -- CHALLENGE 3: THE OVERRIDE DECISION -----------------------------
        # High-stakes scenario where the AI flag conflicts with teacher knowledge
        'override_scenario': {
            'tool': 'AI Early Warning System',
            'ai_output': 'RED -- Intervention required. Risk score: 8.4/10. Recommend immediate family contact.',
            'text': (
                'Your school has introduced an AI Early Warning System. Every Monday it '
                'analyses last week\'s attendance, assignment completion, and platform '
                'engagement data, then flags students as GREEN (on track), AMBER (monitor), '
                'or RED (intervention needed).\n\n'
                'This Monday, the system flags Eleni -- a student you know well -- as RED. '
                'Her attendance last week was 60% because she had a family emergency '
                'that you know about. Her work quality when present was excellent. '
                'The system has no access to this context.\n\n'
                'The RED flag is visible to your Head of Year and will trigger a formal '
                'school intervention process if not reviewed within 24 hours.'
            ),
        },

        'override_options': [
            {
                'value': 'accept',
                'label': 'Accept -- allow the formal intervention process to proceed as flagged',
                'note': 'Follow the system recommendation without modification.',
            },
            {
                'value': 'adjust',
                'label': 'Adjust -- add context so your Head of Year has the full picture',
                'note': 'Override the automated framing with your professional knowledge of the student.',
            },
            {
                'value': 'override',
                'label': 'Override -- clear the flag and document your reasoning',
                'note': 'Exercise your professional judgment that no formal intervention is needed here.',
            },
            {
                'value': 'escalate',
                'label': 'Escalate -- raise the system design as a concern with leadership',
                'note': 'The individual flag is manageable, but a system that cannot incorporate teacher knowledge is a structural problem.',
            },
        ],

        'override_analysis_prompts': [
            'What information does the AI have that you do not?',
            'What information do you have that the AI does not?',
            'What are the consequences for Eleni if the flag is accepted without context?',
            'What does your professional accountability require you to do here?',
        ],
    }
