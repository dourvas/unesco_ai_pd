def get_context():
    return {

        # ── CHALLENGE 1 — SAMR Audit ────────────────────────────────
        'c1_scenarios': [
            {
                'id': 'sc1',
                'label': 'Scenario A',
                'text': (
                    'A teacher creates a Kahoot quiz that covers the same '
                    'multiple-choice questions they previously gave on paper. '
                    'Students answer on their phones and see their score on a '
                    'leaderboard at the end of the lesson.'
                ),
            },
            {
                'id': 'sc2',
                'label': 'Scenario B',
                'text': (
                    'A teacher builds a branching narrative using an AI tool. '
                    'Students play the role of a city planner deciding how to '
                    'respond to a flood risk. Each decision leads to a different '
                    'consequence, and students must justify their final choice '
                    'in a short debrief discussion.'
                ),
            },
            {
                'id': 'sc3',
                'label': 'Scenario C',
                'text': (
                    'Students work in small groups to design a quiz game about '
                    'the topic they just studied — intended for a younger year '
                    'group. They use an AI tool to generate the game structure, '
                    'then review and edit the questions for accuracy and '
                    'appropriate difficulty.'
                ),
            },
        ],

        'c1_samr_options': [
            {'value': 'substitution', 'label': 'Substitution — same task, digital format'},
            {'value': 'augmentation', 'label': 'Augmentation — same task, new function added'},
            {'value': 'modification', 'label': 'Modification — task redesigned around new possibilities'},
            {'value': 'redefinition', 'label': 'Redefinition — task impossible without AI'},
        ],

        'c1_decoration_options': [
            {'value': 'decoration', 'label': 'Decoration — remove the mechanics and nothing valuable remains'},
            {'value': 'transformation', 'label': 'Transformation — the learning activity stands on its own'},
        ],

        # ── CHALLENGE 2 — Five Roles Matcher ────────────────────────
        'c2_situations': [
            {
                'id': 'sit1',
                'text': (
                    'A student asks AI to summarise a chapter they have not read, '
                    'copies the summary into their notes, and moves on.'
                ),
            },
            {
                'id': 'sit2',
                'text': (
                    'A student writes their own answer to an essay question, '
                    'then asks AI for an answer to the same question. They compare '
                    'the two and highlight where they disagree — and why.'
                ),
            },
            {
                'id': 'sit3',
                'text': (
                    'A student asks AI to explain a scientific claim from the '
                    'textbook, then checks each point the AI makes against the '
                    'textbook and their class notes.'
                ),
            },
            {
                'id': 'sit4',
                'text': (
                    'A student drafts an essay introduction, shares it with AI, '
                    'receives feedback, and then decides which suggestions to '
                    'accept — based on whether they improve what they were '
                    'trying to say.'
                ),
            },
            {
                'id': 'sit5',
                'text': (
                    'A student uses AI as a discussion partner to develop their '
                    'position on a controversial topic. They push back when AI '
                    'gives a vague answer, ask follow-up questions, and finish '
                    'with a position they can fully explain themselves.'
                ),
            },
            {
                'id': 'sit6',
                'text': (
                    'A student writes a detailed brief specifying exactly what '
                    'they want AI to produce — the format, the audience, the '
                    'constraints. They review the output against their brief and '
                    'revise the specification where the output misses the mark.'
                ),
            },
        ],

        'c2_roles': [
            {'value': 'critic',       'label': '🧠 Critic — own work first, then evaluates AI'},
            {'value': 'verifier',     'label': '🧠 Verifier — tests AI claims against sources'},
            {'value': 'interlocutor', 'label': '🧠 Interlocutor — uses AI to develop thinking'},
            {'value': 'editor',       'label': '🧠 Editor — AI responds to student work'},
            {'value': 'architect',    'label': '🏗️ Architect — directs AI via specification'},
            {'value': 'none',         'label': '✗ None of the above — student is outsourcing'},
        ],

        'c2_priority_roles': [
            {'value': 'critic',       'label': 'Critic'},
            {'value': 'verifier',     'label': 'Verifier'},
            {'value': 'interlocutor', 'label': 'Interlocutor'},
            {'value': 'editor',       'label': 'Editor'},
            {'value': 'architect',    'label': 'Architect'},
        ],

        # ── CHALLENGE 3 — Gamified Unit Planner ─────────────────────
        'c3_subject_options': [
            {'value': 'mathematics',       'label': 'Mathematics'},
            {'value': 'language_arts',     'label': 'Language Arts'},
            {'value': 'science',           'label': 'Science'},
            {'value': 'physics',           'label': 'Physics'},
            {'value': 'chemistry',         'label': 'Chemistry'},
            {'value': 'biology',           'label': 'Biology'},
            {'value': 'history',           'label': 'History'},
            {'value': 'geography',         'label': 'Geography'},
            {'value': 'social_studies',    'label': 'Social Studies'},
            {'value': 'foreign_languages', 'label': 'Foreign Languages'},
            {'value': 'computer_science',  'label': 'Computer Science'},
            {'value': 'physical_education','label': 'Physical Education'},
            {'value': 'arts',              'label': 'Arts'},
            {'value': 'special_education', 'label': 'Special Education'},
            {'value': 'early_childhood',   'label': 'Early Childhood'},
            {'value': 'other',             'label': 'Other'},
        ],

        'c3_role_options': [
            {'value': 'critic',       'label': 'Critic — students produce first, then evaluate AI'},
            {'value': 'verifier',     'label': 'Verifier — students check AI claims against sources'},
            {'value': 'interlocutor', 'label': 'Interlocutor — students use AI to develop thinking'},
            {'value': 'editor',       'label': 'Editor — students use AI feedback on their own work'},
            {'value': 'architect',    'label': 'Architect — students direct AI via specification'},
        ],

        'c3_gamification_principles': [
            {'value': 'challenge_calibration', 'label': 'Challenge Calibration — difficulty adjusts to the learner'},
            {'value': 'immediate_feedback',    'label': 'Immediate Feedback — students know instantly if they succeeded'},
            {'value': 'visible_progression',   'label': 'Visible Progression — students can see where they are'},
            {'value': 'meaningful_choice',     'label': 'Meaningful Choice — students choose their own path'},
        ],

        'c3_progression_options': [
            {'value': 'levels',      'label': 'Levels or stages students move through'},
            {'value': 'progress_bar','label': 'A visible progress bar or completion tracker'},
            {'value': 'milestones',  'label': 'Milestone markers at key points'},
            {'value': 'score',       'label': 'A score or point total that updates in real time'},
            {'value': 'none',        'label': 'No visible progression in this activity'},
        ],

        'c3_assessment_options': [
            {'value': 'product',     'label': 'A student-produced artefact (written, visual, built)'},
            {'value': 'explanation', 'label': 'A verbal or written explanation of a decision made'},
            {'value': 'comparison',  'label': 'A comparison between student thinking and AI output'},
            {'value': 'reflection',  'label': 'A short reflection on what changed in their thinking'},
            {'value': 'peer',        'label': 'Peer evaluation of the activity or game they designed'},
        ],

        'c3_decoration_options': [
            {
                'value': 'yes_valuable',
                'label': 'Yes — if I remove all the points and mechanics, a valuable learning activity remains',
            },
            {
                'value': 'partial',
                'label': 'Partially — the activity works, but the mechanics add real engagement value',
            },
            {
                'value': 'no_decoration',
                'label': 'No — without the mechanics the activity loses most of its value',
            },
        ],

        'c3_samr_options': [
            {'value': 'substitution',  'label': 'Substitution'},
            {'value': 'augmentation',  'label': 'Augmentation'},
            {'value': 'modification',  'label': 'Modification'},
            {'value': 'redefinition',  'label': 'Redefinition'},
        ],
    }
