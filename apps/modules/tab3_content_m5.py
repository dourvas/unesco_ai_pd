# tab3_content_m5.py
# M5 — Prompt Engineering as Reflective Practice
# TAB3: The Iceberg Audit
# UNESCO Aspect 5 Acquire

def get_context():
    return {

        # ── CHALLENGE 1 — Sort the Knowledge ──────────────────────────
        # 8 professional knowledge items to classify as Explicit or Tacit
        'knowledge_items': [
            {
                'id': 'k1',
                'text': 'Knowing the curriculum sequence for your subject across year groups.',
                'correct': 'explicit',
                'explanation': 'Curriculum sequences are written down — in national frameworks, syllabi, and scheme-of-work documents. They are explicit by design.',
            },
            {
                'id': 'k2',
                'text': 'Knowing that this particular student needs to be called on early in the lesson before they mentally check out.',
                'correct': 'tacit',
                'explanation': 'This is relational knowledge built from observation of one student over time. It exists in your practice, not in any document.',
            },
            {
                'id': 'k3',
                'text': 'Knowing the school\'s assessment submission deadlines.',
                'correct': 'explicit',
                'explanation': 'Deadlines are documented in timetables, policy documents, and school calendars. Fully explicit.',
            },
            {
                'id': 'k4',
                'text': 'Knowing when a class discussion is genuinely productive versus when students are just talking to avoid the written task.',
                'correct': 'tacit',
                'explanation': 'This is contextual judgment — reading the room in real time. It can\'t be written into a procedure. It develops through experience.',
            },
            {
                'id': 'k5',
                'text': 'Knowing the grading criteria for a specific assignment.',
                'correct': 'explicit',
                'explanation': 'Grading criteria are defined in rubrics, mark schemes, and assignment briefs. They are made explicit precisely so students and teachers share them.',
            },
            {
                'id': 'k6',
                'text': 'Knowing which analogy will finally make the concept click for students who have been stuck on it for two lessons.',
                'correct': 'tacit',
                'explanation': 'This is pedagogical content knowledge in action — the intuitive match between a specific concept and a specific representation. It lives in your practice, not in the textbook.',
            },
            {
                'id': 'k7',
                'text': 'Knowing the school\'s policy on mobile phone use in class.',
                'correct': 'explicit',
                'explanation': 'School policies are written documents, communicated formally to staff and students. Explicit by definition.',
            },
            {
                'id': 'k8',
                'text': 'Knowing that today\'s lesson needs to slow down because the class\'s energy suggests something happened at break time.',
                'correct': 'tacit',
                'explanation': 'This is real-time contextual reading — an adjustment based on emotional and social signals that no lesson plan could anticipate. Pure tacit expertise.',
            },
        ],

        # ── CHALLENGE 2 — Map the Strategy ────────────────────────────
        # Thin prompt vs Rich prompt — 5 elements to map to S1-S5
        'thin_prompt': "Create a reading comprehension activity for Year 6.",

        'rich_prompt_parts': [
            {
                'id': 'p1',
                'text': 'Act as an experienced primary literacy educator.',
                'strategy': 'S2',
                'strategy_label': 'S2 · Context',
                'explanation': 'Assigning a role gives AI a perspective to reason from. This is part of providing context — specifically, the professional lens through which the output should be shaped.',
            },
            {
                'id': 'p2',
                'text': 'I have a Year 6 class of 28 students. Six are EAL learners at early fluency stage.',
                'strategy': 'S2',
                'strategy_label': 'S2 · Context',
                'explanation': 'Describing the class — size, year group, specific learner profiles — is exactly what Strategy 2 asks for. This transforms "Year 6" from a generic label into a real classroom.',
            },
            {
                'id': 'p3',
                'text': 'The learning objective is that students can identify the author\'s viewpoint and distinguish it from stated facts.',
                'strategy': 'S1',
                'strategy_label': 'S1 · Goals',
                'explanation': 'A specific, measurable learning objective is the core of Strategy 1. "Create a reading activity" tells AI nothing about what learning should result. This does.',
            },
            {
                'id': 'p4',
                'text': 'Target: inference and interpretation — not literal recall.',
                'strategy': 'S4',
                'strategy_label': 'S4 · Bloom Level',
                'explanation': 'Naming the cognitive level explicitly — inference and interpretation versus recall — is Strategy 4. Without this, AI defaults to the easiest cognitive demand.',
            },
            {
                'id': 'p5',
                'text': 'Provide five questions with a clear scaffold for EAL learners. Do not include questions that can be answered by copying a sentence from the text.',
                'strategy': 'S5',
                'strategy_label': 'S5 · Examples & Exclusions',
                'explanation': 'Specifying both a positive requirement (EAL scaffold) and an explicit exclusion (no copy-paste questions) is the core of Strategy 5. Exclusions are often the most powerful part.',
            },
        ],

        # The strategies as options for the mapping activity
        'strategy_options': [
            {'value': 'S1', 'label': 'S1 · Goals — specifies what students should be able to do'},
            {'value': 'S2', 'label': 'S2 · Context — describes the class or learning situation'},
            {'value': 'S3', 'label': 'S3 · Format — defines the structure of the output'},
            {'value': 'S4', 'label': 'S4 · Bloom Level — names the cognitive demand'},
            {'value': 'S5', 'label': 'S5 · Examples & Exclusions — shows what to include or avoid'},
        ],

        # ── CHALLENGE 3 — Recognise the Role ──────────────────────────
        # 3 scenarios — Scaffolder, Designer, or Guardian
        'role_scenarios': [
            {
                'id': 'r1',
                'text': 'Elena is preparing a prompt for AI to generate differentiated vocabulary activities. She starts typing "create vocabulary activities" — then stops. She realises she hasn\'t described her students\' current level, their L1 interference patterns, or which words they\'ve already encountered. She rewrites the prompt from scratch, naming all three. The AI output is completely different — and usable.',
                'correct': 'scaffolder',
                'options': [
                    {'value': 'scaffolder', 'label': '🌿 The Scaffolder — translating knowing-in-action into explicit language'},
                    {'value': 'designer', 'label': '🏗️ The Designer — building a learning experience from a goal backwards'},
                    {'value': 'guardian', 'label': '🛡️ The Guardian — keeping professional judgment in control'},
                ],
                'explanation': 'Elena is doing exactly what the Scaffolder does: converting tacit professional knowledge (what she knows about her students) into explicit language that AI can act on. The transformation from "I know my students" to "here is what I know about my students, written down" is the Scaffolder\'s move.',
            },
            {
                'id': 'r2',
                'text': 'Marcus wants students to analyse a primary source document. Before he thinks about what AI tool to use, he writes down the learning objective: students should be able to identify bias in a historical source and connect it to the author\'s context. He then asks AI to generate three discussion questions that build toward that objective — not three questions about the document in general.',
                'correct': 'designer',
                'options': [
                    {'value': 'scaffolder', 'label': '🌿 The Scaffolder — translating knowing-in-action into explicit language'},
                    {'value': 'designer', 'label': '🏗️ The Designer — building a learning experience from a goal backwards'},
                    {'value': 'guardian', 'label': '🛡️ The Guardian — keeping professional judgment in control'},
                ],
                'explanation': 'Marcus starts from the learning outcome and works backwards — that is backward design, the core of the Designer role. He is not asking AI "what should we do?" He is telling AI "here is where we need to arrive" and using it to build the path.',
            },
            {
                'id': 'r3',
                'text': 'AI generates a set of feedback comments for Priya\'s student essays. The comments are technically accurate and well-structured. Priya reads each one before sending. She edits two of them — one because the tone is too harsh for a student who has been struggling emotionally, and one because it misses the specific learning goal she had set for this assignment. She sends the rest unchanged.',
                'correct': 'guardian',
                'options': [
                    {'value': 'scaffolder', 'label': '🌿 The Scaffolder — translating knowing-in-action into explicit language'},
                    {'value': 'designer', 'label': '🏗️ The Designer — building a learning experience from a goal backwards'},
                    {'value': 'guardian', 'label': '🛡️ The Guardian — keeping professional judgment in control'},
                ],
                'explanation': 'Priya is the Guardian. AI produced technically correct output — but it lacked two things only she could supply: knowledge of this student\'s emotional context, and the specific learning goal she had in mind. Her review is not a formality. It is the professional judgment that makes the output appropriate for these students.',
            },
        ],
    }
