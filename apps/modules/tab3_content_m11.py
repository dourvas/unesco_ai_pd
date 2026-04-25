"""
M11 -- Your Voice in the AI School
UNESCO Aspect 1: Human-Centred Mindset | Level: Create

TAB3 context data for the 3-challenge activity sequence:
  Challenge 1: Stakeholder Conversation -- map approach, draft response
  Challenge 2: AI Literacy Teaching Move -- design one concrete classroom move
  Challenge 3: The Proposal -- AI Stance Canvas first step
"""


def get_context():
    return {

        # -- CHALLENGE 1: STAKEHOLDER CONVERSATION --------------------------
        # Scenario: difficult conversation requiring professional stance
        'conversation_scenario': {
            'title': 'The Staff Meeting Moment',
            'text': (
                'Your school principal has just announced at a staff meeting that the school '
                'will adopt a new AI platform across all year groups from next term. '
                'The platform will automatically generate weekly progress reports for parents '
                'based on student activity data. Teachers were not consulted before the decision.\n\n'
                'A colleague looks at you across the table. You have been vocal about AI '
                'accountability before. The principal asks: "Any questions before we move forward?"\n\n'
                'Three other teachers are watching. Two parents on the school council are present. '
                'You have about thirty seconds.'
            ),
            'tags': ['Leadership without authority', 'Stakeholder communication', 'Create level'],
        },

        # Challenge 1 Step 1: Who is in the room and what do they need?
        'stakeholders': [
            {'value': 'principal',
             'label': 'Principal -- needs risk reduction and easy approval'},
            {'value': 'colleagues',
             'label': 'Colleagues -- need reassurance and no extra workload'},
            {'value': 'parent_council',
             'label': 'Parent council -- need transparency and to feel consulted'},
            {'value': 'sceptical_colleague',
             'label': 'Sceptical colleague -- needs professional validation'},
            {'value': 'all_of_above',
             'label': 'All of the above -- this is a public moment'},
        ],

        # Challenge 1 Step 2: What is your goal right now?
        'conversation_goals': [
            {
                'value': 'block_decision',
                'label': 'Block the decision -- this should not proceed',
                'note': 'You want to stop the adoption entirely at this meeting.',
            },
            {
                'value': 'slow_down',
                'label': 'Slow it down -- ask for a teacher review before rollout',
                'note': 'You are not opposed in principle, but the process needs a step.',
            },
            {
                'value': 'raise_specific',
                'label': 'Raise one specific concern -- the auto-sent parent reports',
                'note': 'You can live with the platform, but one element needs changing.',
            },
            {
                'value': 'build_allies',
                'label': 'Plant a seed -- make others in the room think, act later',
                'note': 'This is not the right moment for a full challenge; you lay groundwork.',
            },
        ],

        # Challenge 1 Step 3: Draft your question/response
        'response_prompts': [
            'What is the one thing you most need to say in 30 seconds?',
            'How do you frame your concern as professional interest -- not opposition?',
            'Which stakeholder in the room are you really speaking to?',
        ],

        # Challenge 1 completed -- perspectives
        'conversation_perspectives': [
            {
                'title': 'Why "slow it down" is usually the strongest position',
                'text': (
                    'Blocking a decision in public often creates defensiveness and positions '
                    'you as an obstacle. Asking for a review step -- "Could we trial this with '
                    'one year group first, and have teachers report back before full rollout?" -- '
                    'achieves most of what a block achieves, without triggering resistance. '
                    'It signals competence, not opposition. Principals who hear this often agree.'
                ),
            },
            {
                'title': 'The question that does most work in the room',
                'text': (
                    '"Who will teachers contact if a parent questions a report they did not '
                    'write?" This question is specific, practical, and unanswerable without '
                    'the policy work that has not yet been done. It raises the accountability '
                    'gap without framing you as anti-AI. Parent council members will hear it '
                    'and ask themselves the same question.'
                ),
            },
            {
                'title': 'The allies you did not know you had',
                'text': (
                    'The colleague who looked at you across the table is probably thinking '
                    'what you are thinking. So, likely, is one of the parent council members. '
                    'A public moment where you speak clearly creates private conversations '
                    'afterwards. Leadership without authority often works this way: you say '
                    'the thing, and others come to you.'
                ),
            },
        ],

        # -- CHALLENGE 2: AI LITERACY TEACHING MOVE -------------------------
        # Design one concrete classroom move from the 5 in Part 3
        'teaching_moves': [
            {
                'value': 'make_visible',
                'label': 'Make AI visible -- not invisible',
                'description': (
                    'When you use AI to prepare materials, say so explicitly. '
                    'Students cannot develop critical judgment about something '
                    'they do not know is there.'
                ),
                'example': '"I used AI to generate these practice questions. Before we start, '
                           'let us look at question 3 together -- does anything seem off to you?"',
            },
            {
                'value': 'who_built_this',
                'label': 'Ask "who built this -- and for whom?"',
                'description': (
                    'Every AI tool was built by someone, trained on specific data, '
                    'and designed for a purpose. Teaching students to ask this question '
                    'is teaching them to think like citizens.'
                ),
                'example': '"This translation tool was built by a large tech company. '
                           'What do you think their main goal was?"',
            },
            {
                'value': 'celebrate_override',
                'label': 'Celebrate the override',
                'description': (
                    'When a student spots an AI error, questions a suggestion, or '
                    'chooses not to use AI -- make it visible as exactly the right move.'
                ),
                'example': '"Maya just pointed out that the AI got this wrong. '
                           'That is exactly the skill I want every one of you to develop."',
            },
            {
                'value': 'require_human',
                'label': 'Design tasks that require the human',
                'description': (
                    'Tasks requiring personal experience, local knowledge, genuine '
                    'opinion, or creative risk resist AI misuse -- and make human '
                    'thinking feel valuable again.'
                ),
                'example': '"Interview someone in your family about how things have changed, '
                           'then write about what AI cannot know about this topic."',
            },
            {
                'value': 'social_dimension',
                'label': 'Talk about AI\'s social dimension',
                'description': (
                    'Students who will vote, work, and participate in society need to '
                    'understand that AI decisions affect real people -- and that they '
                    'have a right to question them.'
                ),
                'example': '"This hiring algorithm rejected candidates based on their postcode. '
                           'Who does that affect most? Who decided to build it this way?"',
            },
        ],

        # Age groups for move adaptation
        'age_groups': [
            {'value': 'early_years', 'label': 'Early years (3-6)'},
            {'value': 'primary', 'label': 'Primary (6-11)'},
            {'value': 'lower_secondary', 'label': 'Lower secondary (11-14)'},
            {'value': 'upper_secondary', 'label': 'Upper secondary (14-18)'},
        ],

        # -- CHALLENGE 3: THE PROPOSAL (AI STANCE CANVAS) ------------------
        # Teachers complete a simplified version of the Stance Canvas
        'canvas_sections': [
            {
                'id': 'position',
                'label': 'My position',
                'prompt': 'Complete this: "I believe AI in my classroom should..."',
                'placeholder': 'I believe AI in my classroom should...',
                'hint': 'Not what you think you should believe -- what you actually believe '
                       'based on your experience across M1, M6, and M11.',
                'min_length': 30,
            },
            {
                'id': 'non_negotiable',
                'label': 'My one non-negotiable',
                'prompt': 'One thing you will not do regardless of what your school adopts:',
                'placeholder': 'I will never...',
                'hint': 'Ground this in what you learned about accountability in M6. '
                       'Make it specific enough to be actionable.',
                'min_length': 20,
            },
            {
                'id': 'first_step',
                'label': 'My first small step',
                'prompt': 'The one change I want to start -- and my first concrete action:',
                'placeholder': 'The change I want to make is... My first step is...',
                'hint': 'One change, one step. Small and specific beats ambitious and vague. '
                       'What could you do this week?',
                'min_length': 30,
            },
            {
                'id': 'first_ally',
                'label': 'My first conversation',
                'prompt': 'Who will you talk to, and what is the one thing you will say?',
                'placeholder': 'I will talk to [name/role]... I will say...',
                'hint': 'Name a specific person -- not "a colleague". The more specific, '
                       'the more likely it will actually happen.',
                'min_length': 20,
            },
        ],

        'canvas_completed_prompts': [
            'Reading your position statement back -- does it sound like you?',
            'Is your non-negotiable something you could defend to a parent or principal?',
            'Could you take your first step this week -- or is it still too abstract?',
            'Have you told the person you named that you want to talk to them?',
        ],
    }
