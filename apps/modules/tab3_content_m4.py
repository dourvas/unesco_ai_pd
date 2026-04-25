# apps/modules/tab3_content_m4.py
# M4 — AI Tools for Teaching (Aspect 4 Acquire)
# TAB3: Three challenges — Pedagogical Fit Test · Human Voice Rule · Student-Facing Activity Design

# ─────────────────────────────────────────────
# CHALLENGE 1 — THE PEDAGOGICAL FIT TEST
# ─────────────────────────────────────────────
# Five teaching tasks. For each one the teacher decides:
#   pass_both    → passes Reliability check AND Pedagogical Fit
#   fail_fit     → reliable tool exists, but wrong task for AI
#   not_suitable → AI is not the right tool at all

M4_TASKS = [
    {
        'id': 'task_a',
        'label': 'Task A',
        'text': (
            'You want to generate a first draft of a reading comprehension worksheet '
            'for a mixed-ability class, covering a text you have already selected. '
            'You plan to review and edit all questions before use.'
        ),
        'correct': 'pass_both',
        'explanation': (
            'This task passes both steps. The tool produces draft content — not a final product. '
            'You apply the Reliability check (accuracy, appropriateness) and then the Pedagogical Fit '
            'question: it saves significant preparation time, the task type suits AI generation, '
            'and you can fully review the output before it reaches students.'
        ),
    },
    {
        'id': 'task_b',
        'label': 'Task B',
        'text': (
            'A student has been disengaged for two weeks. You want to decide whether to contact '
            'the family, refer to a school counsellor, or wait and observe. '
            'You are considering using an AI tool to help you choose.'
        ),
        'correct': 'not_suitable',
        'explanation': (
            'AI is not the right tool here. This is a welfare decision that requires '
            'professional judgment, knowledge of the student and family, and ethical accountability. '
            'No AI tool — however reliable — can substitute for that. '
            'Using AI to make or guide this decision would shift accountability away from you.'
        ),
    },
    {
        'id': 'task_c',
        'label': 'Task C',
        'text': (
            'You want to use an AI tool to generate personalised written feedback on a set of '
            'student essays. You plan to send the AI-generated feedback to students without reading it first.'
        ),
        'correct': 'fail_fit',
        'explanation': (
            'A reliable AI tool can generate useful draft feedback — so it passes the Reliability check. '
            'But it fails the Pedagogical Fit question: feedback sent without teacher review '
            'may be generic, miss context, or carry errors. '
            'The generate-then-shape workflow is right here — review before sending.'
        ),
    },
    {
        'id': 'task_d',
        'label': 'Task D',
        'text': (
            'You are preparing a unit on a historical event. You want to use an AI tool '
            'to produce a list of 10 possible discussion questions at different cognitive levels. '
            'You will select 3–4 questions from the list for classroom use.'
        ),
        'correct': 'pass_both',
        'explanation': (
            'This is a strong use case for AI. Generating question options is the kind of '
            'repetitive, time-consuming task where AI adds clear value. '
            'You retain full control: you select, adapt, and decide what gets used. '
            'Both steps pass — the tool is doing the right kind of work, and you are reviewing the output.'
        ),
    },
    {
        'id': 'task_e',
        'label': 'Task E',
        'text': (
            'You want to use an AI tool to generate an end-of-term grade for each student '
            'based on their assignment scores and class participation records. '
            'You plan to submit these grades directly to the school system.'
        ),
        'correct': 'not_suitable',
        'explanation': (
            'Summative grading is a professional and legal responsibility. '
            'AI can support data analysis and highlight patterns, but the grading decision belongs to you. '
            'Submitting AI-generated grades without teacher judgment is a clear accountability failure — '
            'regardless of how reliable the tool is.'
        ),
    },
]

M4_FIT_OPTIONS = [
    {'value': 'pass_both',    'label': '✓ Passes both steps — good use of AI'},
    {'value': 'fail_fit',     'label': '⚠ Reliable tool, but wrong task for AI'},
    {'value': 'not_suitable', 'label': '✗ AI is not the right tool here'},
]


# ─────────────────────────────────────────────
# CHALLENGE 2 — THE HUMAN VOICE RULE
# ─────────────────────────────────────────────
# Three AI-generated feedback samples for fictional students.
# The teacher reads the student context and edits the feedback
# to add human voice: specificity, encouragement, professional tone.

M4_FEEDBACK_SAMPLES = [
    {
        'id': 'student_1',
        'student_name': 'Sofia',
        'student_context': (
            'Sofia is a Year 8 student who has been struggling with confidence after switching schools '
            'mid-year. She worked very hard on this assignment and submitted it on time — '
            'which is significant given her recent difficulties. She responds well to specific praise.'
        ),
        'ai_feedback': (
            'Good effort on this assignment. You have demonstrated an understanding of the main concepts. '
            'Your writing is generally clear, though some sections could benefit from more detail. '
            'Consider developing your arguments further in future work. Overall a solid piece of work.'
        ),
        'edit_prompt': (
            'Edit this feedback so it reflects what you know about Sofia. '
            'Make it specific, personal, and genuinely encouraging — without changing the core assessment.'
        ),
    },
    {
        'id': 'student_2',
        'student_name': 'Marcus',
        'student_context': (
            'Marcus is a high-achieving Year 10 student who submitted a technically strong piece '
            'but clearly rushed the conclusion. He has a tendency to stop engaging once he '
            'feels he has "done enough". He needs to be challenged, not reassured.'
        ),
        'ai_feedback': (
            'This is a strong piece of work overall. Your analysis of the main themes is detailed '
            'and shows good critical thinking. The conclusion is brief but covers the main points. '
            'Well done on a high-quality submission.'
        ),
        'edit_prompt': (
            'Edit this feedback to name the specific gap in Marcus\'s conclusion and set '
            'a clear expectation for his next submission. Keep the tone professional but direct.'
        ),
    },
    {
        'id': 'student_3',
        'student_name': 'Aisha',
        'student_context': (
            'Aisha is a Year 6 student with strong verbal skills but difficulty organising '
            'written work. This assignment shows a real improvement in paragraph structure — '
            'a goal you set together at the start of the term. This progress should be named explicitly.'
        ),
        'ai_feedback': (
            'You have written a good response to the task. Your ideas are interesting and relevant. '
            'The organisation of your work is improving. Keep working on developing your paragraphs. '
            'A promising piece of writing.'
        ),
        'edit_prompt': (
            'Edit this feedback to acknowledge the specific progress Aisha has made on paragraph structure. '
            'Connect it to the goal you set together. Keep it age-appropriate and warm.'
        ),
    },
]

M4_VOICE_CHECKLIST = [
    {'value': 'named_student',    'label': 'I addressed the student by name or with a personal reference'},
    {'value': 'specific_detail',  'label': 'I added at least one specific detail not in the AI draft'},
    {'value': 'right_tone',       'label': 'The tone matches what this student needs'},
    {'value': 'my_judgment',      'label': 'The feedback reflects my professional judgment, not just AI output'},
]


# ─────────────────────────────────────────────
# CHALLENGE 3 — STUDENT-FACING ACTIVITY DESIGN
# ─────────────────────────────────────────────
# The teacher designs one teacher-controlled student-facing activity
# using one of the four activity types from M4 TAB2 Part 4.

M4_ACTIVITY_TYPES = [
    {
        'value': 'interview',
        'label': 'Interview',
        'description': 'Students question an AI playing a role (historical figure, character, expert). Teacher controls the AI setup and all prompts.',
    },
    {
        'value': 'debate',
        'label': 'Debate',
        'description': 'AI presents one side of an argument; students develop and defend the other. Teacher designs the question and monitors the exchange.',
    },
    {
        'value': 'game',
        'label': 'Game / Quiz',
        'description': 'AI-powered quiz or challenge activity. Teacher sets the topic, difficulty, and reviews all AI-generated questions before use.',
    },
    {
        'value': 'co_writing',
        'label': 'Co-writing',
        'description': 'Students and AI write together on a structured task. Teacher defines the task, the AI\'s role, and the review step.',
    },
]

M4_CONTROL_OPTIONS = [
    {'value': 'pre_set_prompts',   'label': 'I will pre-set all AI prompts — students only see the output'},
    {'value': 'structured_inputs', 'label': 'Students submit structured inputs I have designed — no free prompting'},
    {'value': 'guided_turn',       'label': 'Students interact turn by turn but I review each AI response first'},
    {'value': 'other',             'label': 'Other — I will describe my control approach in the box below'},
]

M4_ASSESSMENT_OPTIONS = [
    {'value': 'product',    'label': 'I assess the final product (written, spoken, or created output)'},
    {'value': 'process',    'label': 'I assess the process — how students engaged, questioned, and reasoned'},
    {'value': 'discussion', 'label': 'I follow up with a class discussion where students explain their thinking'},
    {'value': 'mixed',      'label': 'A combination of the above'},
]


def get_context():
    return {
        'm4_tasks':            M4_TASKS,
        'm4_fit_options':      M4_FIT_OPTIONS,
        'm4_feedback_samples': M4_FEEDBACK_SAMPLES,
        'm4_voice_checklist':  M4_VOICE_CHECKLIST,
        'm4_activity_types':   M4_ACTIVITY_TYPES,
        'm4_control_options':  M4_CONTROL_OPTIONS,
        'm4_assessment_options': M4_ASSESSMENT_OPTIONS,
    }
