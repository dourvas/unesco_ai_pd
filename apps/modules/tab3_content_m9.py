# tab3_content_m9.py
# M9 — AI-Enhanced Lesson Design
# UNESCO Aspect 4 Deepen
# TAB3: Three challenges — Backward Design Sorter, UDL Profile Matcher,
#        Lesson Design Decisions (subject-specific)

# ── Challenge 1: Backward Design Sorter ────────────────────────────────────
# 10 planning elements to sort into Stage 1 / Stage 2 / Stage 3 / Not part of backward design

C1_ELEMENTS = [
    {
        'id': 'e1',
        'text': 'Define what students should understand and be able to do by the end of the lesson',
        'correct_stage': 'stage1',
        'explanation': 'This is Stage 1 — the desired outcome. Backward design starts here, before any activity or tool is chosen.',
    },
    {
        'id': 'e2',
        'text': 'Design an assessment task that will show whether learning has happened',
        'correct_stage': 'stage2',
        'explanation': 'This is Stage 2 — the evidence of learning. Designing assessment before activities keeps the outcome in view.',
    },
    {
        'id': 'e3',
        'text': 'Choose an AI tool that looks useful for this topic',
        'correct_stage': 'not_bd',
        'explanation': 'Choosing a tool before knowing the outcome is the forward planning trap. AI enters at Stage 3 — after the outcome and evidence are defined.',
    },
    {
        'id': 'e4',
        'text': 'Generate a scaffolded worksheet using AI to support learners during the activity',
        'correct_stage': 'stage3',
        'explanation': 'This is Stage 3 — designing the learning experience. AI scaffold generation belongs here, once you know what the activity needs to achieve.',
    },
    {
        'id': 'e5',
        'text': 'Decide which content is suitable for pre-class video and which needs the teacher present',
        'correct_stage': 'stage3',
        'explanation': 'This is Stage 3 — designing the learning experience. The flipped learning design split is a Stage 3 decision.',
    },
    {
        'id': 'e6',
        'text': 'Identify the learner profiles in the class and the barriers each might face',
        'correct_stage': 'stage3',
        'explanation': 'This is Stage 3 — designing the learning experience. UDL-based differentiation is a Stage 3 design decision, made after the outcome is fixed.',
    },
    {
        'id': 'e7',
        'text': 'Write the learning objective on the board at the start of class',
        'correct_stage': 'not_bd',
        'explanation': 'Writing an objective on the board is a delivery act, not a design stage. Backward design happens before the lesson, not during it.',
    },
    {
        'id': 'e8',
        'text': 'Draft a rubric that will be used to assess the final student product',
        'correct_stage': 'stage2',
        'explanation': 'This is Stage 2 — the evidence of learning. A rubric is an assessment instrument; designing it before activities keeps assessment honest.',
    },
    {
        'id': 'e9',
        'text': 'Review the AI-generated materials for conceptual accuracy before distributing them',
        'correct_stage': 'stage3',
        'explanation': 'This is Stage 3 — reviewing materials is part of implementing the learning experience. It is the human judgment step inside Stage 3.',
    },
    {
        'id': 'e10',
        'text': 'Search for an interesting video on the topic to show at the start of the lesson',
        'correct_stage': 'not_bd',
        'explanation': 'Finding an interesting video without knowing the outcome first is content-led, not design-led. In backward design, resources are chosen to serve a defined outcome — not the other way around.',
    },
]

C1_STAGES = [
    {'id': 'stage1', 'label': 'Stage 1', 'subtitle': 'Desired Outcomes', 'color': 'indigo'},
    {'id': 'stage2', 'label': 'Stage 2', 'subtitle': 'Assessment Evidence', 'color': 'purple'},
    {'id': 'stage3', 'label': 'Stage 3', 'subtitle': 'Learning Experiences', 'color': 'cyan'},
    {'id': 'not_bd', 'label': 'Not part of backward design', 'subtitle': 'Forward planning trap', 'color': 'red'},
]


# ── Challenge 2: UDL Profile Matcher ───────────────────────────────────────
# 5 learner descriptions — match UDL principle + AI support type

C2_PROFILES = [
    {
        'id': 'p1',
        'description': 'A student who understands the concept well when you explain it verbally in class, but cannot complete the written task independently — the words don\'t come, even though the thinking is there.',
        'correct_principle': 'expression',
        'correct_support': 'rubric_alt',
        'explanation': 'The barrier is expression, not comprehension. UDL Principle 3 (Multiple Means of Action and Expression) applies. AI support: a rubric that accepts oral or recorded responses alongside written ones.',
    },
    {
        'id': 'p2',
        'description': 'A recently arrived student who processes the subject content in their first language fluently, but needs extra time with any task that involves reading or writing in the language of instruction.',
        'correct_principle': 'representation',
        'correct_support': 'vocab_scaffold',
        'explanation': 'The barrier is representation — the content encoding creates a language access problem. UDL Principle 2 (Multiple Means of Representation) applies. AI support: a vocabulary glossary with first-language equivalents and simplified sentence structures.',
    },
    {
        'id': 'p3',
        'description': 'A student who finishes every task in the first five minutes and then disengages, often distracting peers. They say the work is "too easy" — and they\'re usually right.',
        'correct_principle': 'engagement',
        'correct_support': 'elevated_complexity',
        'explanation': 'The barrier is engagement — insufficient challenge. UDL Principle 1 (Multiple Means of Engagement) applies. AI support: an elevated complexity version of the task that moves from application to analysis or evaluation.',
    },
    {
        'id': 'p4',
        'description': 'A student diagnosed with dyslexia who has strong verbal reasoning but struggles significantly with multi-step written tasks — they lose track of where they are in a complex process.',
        'correct_principle': 'expression',
        'correct_support': 'chunked_task',
        'explanation': 'The barrier is task format — the multi-step written structure creates a working memory problem. UDL Principle 3 (Multiple Means of Action and Expression) applies. AI support: a chunked version of the task broken into single steps with clear stopping points.',
    },
    {
        'id': 'p5',
        'description': 'A student who switches off during abstract explanations but immediately engages when examples connect to sport, music, or things from their own life. Motivation is clearly there — the entry point is wrong.',
        'correct_principle': 'engagement',
        'correct_support': 'relevant_context',
        'explanation': 'The barrier is engagement — the content entry point doesn\'t connect to what motivates this student. UDL Principle 1 (Multiple Means of Engagement) applies. AI support: topic variations that connect the same concept to different student interests and contexts.',
    },
]

C2_PRINCIPLES = [
    {'value': 'engagement', 'label': '❤️ Principle 1 — Multiple Means of Engagement (the why)'},
    {'value': 'representation', 'label': '🧠 Principle 2 — Multiple Means of Representation (the what)'},
    {'value': 'expression', 'label': '✋ Principle 3 — Multiple Means of Action and Expression (the how)'},
]

C2_SUPPORTS = [
    {'value': 'vocab_scaffold', 'label': 'Vocabulary glossary with first-language equivalents'},
    {'value': 'rubric_alt', 'label': 'Rubric accepting oral, visual, or recorded responses'},
    {'value': 'chunked_task', 'label': 'Task broken into single steps with stopping points'},
    {'value': 'elevated_complexity', 'label': 'Elevated complexity version (analysis / evaluation level)'},
    {'value': 'relevant_context', 'label': 'Topic variation connected to student interests'},
    {'value': 'sentence_frames', 'label': 'Sentence frames and structural scaffolds for written output'},
]


# ── Challenge 3: Lesson Design Decisions (subject-specific) ────────────────
# Each subject has a lesson scenario + 5 design decisions (radio buttons)
# AI feedback is generated from the pattern of choices

LESSON_SCENARIOS = {
    'mathematics': {
        'topic': 'Introducing simultaneous equations — Year 9',
        'context': 'Your class of 28 has a wide range: six students with strong algebraic fluency, a cluster who struggle with any multi-step procedure, and three EAL learners. You have one 50-minute period.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — Where does this lesson sit in backward design?',
                'options': [
                    {'value': 'A', 'text': 'Define the outcome first: students can set up and solve a simultaneous equation by substitution'},
                    {'value': 'B', 'text': 'Find a good worked-example video and build the lesson around it'},
                    {'value': 'C', 'text': 'Ask AI to generate 10 practice problems and use them to structure the lesson'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome comes first — Stage 1 before any resource or tool choice. Options B and C start from a resource or tool, which is forward planning.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What goes in the pre-class video for a flipped approach?',
                'options': [
                    {'value': 'A', 'text': 'A full explanation of both substitution and elimination methods'},
                    {'value': 'B', 'text': 'A short worked example of substitution with one embedded check question: can you identify the first step?'},
                    {'value': 'C', 'text': 'A practice problem set students complete before class'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Pre-class video should be short, single-method, with one low-stakes check. Option A is too dense for independent processing. Option C turns home time into assessment, which creates equity issues.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — Which scaffold does the EAL learner need most for this topic?',
                'options': [
                    {'value': 'A', 'text': 'A simplified version of the problem with smaller numbers'},
                    {'value': 'B', 'text': 'A vocabulary card with terms like "coefficient," "substitute," and "solve" in plain language and their first-language equivalents'},
                    {'value': 'C', 'text': 'A separate, easier set of equations to work through first'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The EAL barrier is language, not mathematics. A vocabulary scaffold removes the linguistic barrier without reducing the mathematical demand. Options A and C reduce the mathematical challenge, which isn\'t the problem.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'More simultaneous equations of the same type to practice'},
                    {'value': 'B', 'text': 'An early introduction to Year 10 content on quadratic equations'},
                    {'value': 'C', 'text': 'A task asking: "Is there always exactly one solution? Construct a pair of equations that has no solution and explain why"'},
                ],
                'correct': 'C',
                'feedback': 'Correct. Extension deepens engagement with the same concept — here, reasoning about solution types. Option A is repetition, not extension. Option B introduces new content rather than deepening the current one.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — When does AI enter the design process?',
                'options': [
                    {'value': 'A', 'text': 'At the start — choose the AI tool first, then design the lesson around what it can produce'},
                    {'value': 'B', 'text': 'At Stage 3 — once the outcome and assessment are defined, use AI to generate scaffolds, check questions, and differentiated versions'},
                    {'value': 'C', 'text': 'Only if you have spare time — AI is a bonus, not part of the design'},
                ],
                'correct': 'B',
                'feedback': 'Correct. AI is a Stage 3 design material — it helps build the learning experiences after the outcome and evidence are fixed. Option A is the forward planning trap. Option C undersells AI\'s genuine utility as a production tool.',
            },
        ],
    },

    'language_arts': {
        'topic': 'Analysing persuasive techniques in a speech — Year 8',
        'context': 'Your class includes strong readers who finish quickly, several students who find extended texts overwhelming, and two students whose written expression is significantly weaker than their verbal understanding.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome for this lesson?',
                'options': [
                    {'value': 'A', 'text': 'Students watch an engaging speech and discuss their reactions'},
                    {'value': 'B', 'text': 'Students can identify and explain the effect of at least two persuasive techniques in an unseen text'},
                    {'value': 'C', 'text': 'Students complete an AI-generated quiz on persuasive language'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The outcome specifies what students can DO and at what level — identifying and explaining technique effects. Option A describes an activity, not an outcome. Option C starts from an AI product, not a learning goal.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — How do you address the expression barrier for students with weak written output?',
                'options': [
                    {'value': 'A', 'text': 'Give them a shorter or simpler text to analyse'},
                    {'value': 'B', 'text': 'Allow them to record a spoken analysis instead of writing, using the same analytical framework'},
                    {'value': 'C', 'text': 'Pair them with a stronger writer to complete the task together'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The barrier is expression format, not analytical ability. A rubric that accepts oral responses preserves the learning outcome while removing the expression barrier. Option A reduces the text difficulty, which isn\'t the problem. Option C outsources the work.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What pre-class task supports the flipped approach for this lesson?',
                'options': [
                    {'value': 'A', 'text': 'Students read the speech at home and answer: name one technique you noticed and describe its effect in one sentence'},
                    {'value': 'B', 'text': 'Students read the speech and write a full paragraph of analysis'},
                    {'value': 'C', 'text': 'Students find their own example of a persuasive speech to bring to class'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The pre-class task should be low-stakes, single-step, and aligned to the outcome. Option B is high-demand — it belongs in class with teacher support. Option C is open-ended and creates equity issues if students lack home resources.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Analyse more speeches of the same type'},
                    {'value': 'B', 'text': 'Compare this speech to a second text from a different context and evaluate whether the same technique has the same effect'},
                    {'value': 'C', 'text': 'Research the historical background of the speaker'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Comparative analysis at a higher cognitive level — evaluating whether technique effects transfer across context — extends the same analytical thinking. Option A is repetition. Option C is research, not literary analysis.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated scaffold for students with text barriers look like?',
                'options': [
                    {'value': 'A', 'text': 'A full summary of the speech that replaces reading the original'},
                    {'value': 'B', 'text': 'A plain-language version with difficult vocabulary glossed, preserving all the persuasive techniques intact'},
                    {'value': 'C', 'text': 'A list of the techniques used in the speech, so students just need to find examples'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The scaffold reduces the reading barrier while keeping the analytical task intact. Option A removes the source — there is nothing left to analyse. Option C removes the analytical work itself, which is the learning goal.',
            },
        ],
    },

    'science': {
        'topic': 'Diffusion and osmosis — Year 8',
        'context': 'You have a practical lesson coming up. Several students have not engaged with prior written explanations of the particle model. Two EAL learners find scientific vocabulary a significant barrier. The practical itself is straightforward.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students complete the osmosis practical successfully'},
                    {'value': 'B', 'text': 'Students can explain why osmosis occurs in terms of particle concentration and movement across a membrane'},
                    {'value': 'C', 'text': 'Students watch an AI-generated animation of osmosis'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The outcome specifies conceptual understanding — explanation using particle model language. Option A describes an activity completion. Option C starts from a resource, not a learning goal.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What goes in the pre-class video for a flipped practical?',
                'options': [
                    {'value': 'A', 'text': 'A full explanation of diffusion, osmosis, and active transport'},
                    {'value': 'B', 'text': 'A short explanation of the mechanism of osmosis with one embedded prediction question: what do you expect to observe when the potato is placed in salt water?'},
                    {'value': 'C', 'text': 'A video of someone else doing the practical, so students know what to expect'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Pre-class content should focus on the concept behind the practical and include a prediction that activates prior thinking. Option A covers too much. Option C shows procedure without building conceptual understanding.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold does the EAL learner need before the practical?',
                'options': [
                    {'value': 'A', 'text': 'A simpler version of the experiment with fewer variables'},
                    {'value': 'B', 'text': 'A vocabulary card with terms like "concentration," "membrane," and "diffusion" in plain language with first-language equivalents'},
                    {'value': 'C', 'text': 'A partner who will explain the experiment to them in their first language'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The barrier is vocabulary, not scientific understanding. A pre-lesson vocabulary card ensures the student arrives at the practical with the language already in place. Option A reduces the science. Option C is a workaround, not a scaffold.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need after the practical?',
                'options': [
                    {'value': 'A', 'text': 'More osmosis problems to calculate percentage change in mass'},
                    {'value': 'B', 'text': 'A design challenge: propose an alternative experimental method to test the same hypothesis and identify one variable you would need to control that the standard method doesn\'t address'},
                    {'value': 'C', 'text': 'Early access to the active transport content from Year 9'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Experimental design requires the student to apply scientific method reasoning — same concept, higher cognitive demand. Option A is calculation practice, not conceptual extension. Option C accelerates through content rather than deepening understanding.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated scaffold for the lab report look like?',
                'options': [
                    {'value': 'A', 'text': 'A completed example report the student can use as a model'},
                    {'value': 'B', 'text': 'A structured template with labelled sections, one sentence starter per section, and a checklist of what each section must include'},
                    {'value': 'C', 'text': 'A simplified report with only two sections: what happened and why'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A structured template reduces the organisational demand without removing the scientific writing task. Option A removes the writing entirely. Option C removes sections that are part of the learning outcome.',
            },
        ],
    },

    'history': {
        'topic': 'Causes of the First World War — Year 9',
        'context': 'A challenging topic with dense source material, multiple causal factors, and high argumentative demand. Your class includes students who struggle with source analysis and some who find the period remote and unengaging.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can identify and rank the causes of WWI with supporting evidence, and justify their ranking'},
                    {'value': 'B', 'text': 'Students learn about the assassination of Franz Ferdinand and the alliance system'},
                    {'value': 'C', 'text': 'Students complete an AI-generated timeline of events leading to war'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies historical thinking — ranking, evidence, and justification — not content coverage. Option B describes content, not outcome. Option C starts from an AI product.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What pre-class task supports the flipped approach?',
                'options': [
                    {'value': 'A', 'text': 'Students watch a short video on the alliance system and answer: which cause do you think was most important, and give one piece of evidence'},
                    {'value': 'B', 'text': 'Students read a chapter of the textbook and take notes'},
                    {'value': 'C', 'text': 'Students research WWI independently and find their own sources'},
                ],
                'correct': 'A',
                'feedback': 'Correct. A short focused video with a pre-commitment question activates thinking before class. Option B is passive and may not be completed. Option C is open-ended, inequitable, and produces unmanageable variation.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — How does AI reduce the source analysis barrier without removing it?',
                'options': [
                    {'value': 'A', 'text': 'AI generates a summary of the source so students don\'t need to read it'},
                    {'value': 'B', 'text': 'AI generates a plain-language companion to the source — a paraphrase, a glossary of period-specific terms, and an explanation of the cultural reference required to understand the source\'s significance'},
                    {'value': 'C', 'text': 'AI identifies the persuasive techniques in the source so students can list them'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A source companion reduces the language barrier while preserving the analytical task — students still need to evaluate the source, just with better access to it. Option A removes the source. Option C removes the analysis.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Analyse more sources on the same topic'},
                    {'value': 'B', 'text': 'Compare the arguments of two historians who disagree about whether militarism or nationalism was the primary cause, and evaluate which interpretation is better supported by the sources'},
                    {'value': 'C', 'text': 'Research the aftermath of WWI and connect it to WWII'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Historiographical comparison requires engagement with the nature of historical argument, not just the facts. Option A is more of the same. Option C moves to new content rather than deepening understanding of causation.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated scaffold for the disengaged student look like?',
                'options': [
                    {'value': 'A', 'text': 'A modern parallel: a scenario showing how similar alliance dynamics created conflict in a recent context the student knows'},
                    {'value': 'B', 'text': 'A simplified summary of the causes with key facts highlighted'},
                    {'value': 'C', 'text': 'A graphic novel version of the events'},
                ],
                'correct': 'A',
                'feedback': 'Correct. A contemporary parallel creates personal relevance and engagement — the historical thinking still applies. Check any AI-generated parallel for accuracy and cultural sensitivity. Option B reduces engagement further. Option C changes format without building the connection.',
            },
        ],
    },

    'physics': {
        'topic': 'Newton\'s laws of motion — Year 10',
        'context': 'Students have seen Newton\'s First and Second Laws in Year 9. This lesson deepens understanding through problem-solving. Several students can manipulate F=ma algebraically but lack physical intuition. Two have significant working memory challenges.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can apply Newton\'s Second Law to solve problems and explain the physical meaning of the result — not just the algebra'},
                    {'value': 'B', 'text': 'Students practise F=ma calculations'},
                    {'value': 'C', 'text': 'Students watch a simulation of forces acting on objects'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies both procedural and conceptual understanding. Option B describes an activity. Option C describes a resource.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What scaffold supports students with physical intuition barriers?',
                'options': [
                    {'value': 'A', 'text': 'Reduce the algebraic complexity — use simpler numbers'},
                    {'value': 'B', 'text': 'Generate a version of each problem that separates the physical question from the algebraic one — first ask what physically must happen, then ask for the calculation'},
                    {'value': 'C', 'text': 'Provide the answers so students can work backwards'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Decoupling physical reasoning from algebraic manipulation allows each to be assessed separately and removes the interference. Option A reduces the mathematics without addressing the intuition gap. Option C removes the reasoning entirely.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports the student with working memory challenges on multi-step problems?',
                'options': [
                    {'value': 'A', 'text': 'A shorter problem with fewer steps'},
                    {'value': 'B', 'text': 'A chunked problem card: Step 1 — write down what you know. Step 2 — identify the equation. Step 3 — substitute. Step 4 — solve. Step 5 — explain the physical meaning'},
                    {'value': 'C', 'text': 'A worked example of the same problem type to copy'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Chunking distributes the working memory demand across explicit steps without reducing the physics. Option A reduces the problem. Option C removes the reasoning — the student copies rather than thinks.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'More F=ma problems with larger numbers'},
                    {'value': 'B', 'text': 'A limiting case question: what happens to the acceleration as the mass approaches infinity? As the force approaches zero? Explain the physical meaning of each limit'},
                    {'value': 'C', 'text': 'An introduction to Newton\'s Third Law'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Limiting case reasoning reveals deep conceptual understanding — the student must think about what the equation means, not just apply it. Option A is repetition. Option C introduces new content rather than deepening the current concept.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — At what point does AI enter this lesson design?',
                'options': [
                    {'value': 'A', 'text': 'Before the outcome is set — to generate interesting problems that shape what gets taught'},
                    {'value': 'B', 'text': 'After the outcome and assessment are defined — to generate chunked scaffolds, decoupled versions, and limiting case extensions'},
                    {'value': 'C', 'text': 'During delivery — to explain concepts to students directly'},
                ],
                'correct': 'B',
                'feedback': 'Correct. AI is a Stage 3 production tool. Option A puts AI before the outcome — the forward planning trap. Option C hands teaching to AI and removes the teacher\'s role in responding to student thinking.',
            },
        ],
    },

    'chemistry': {
        'topic': 'Ionic bonding — Year 9',
        'context': 'Students consistently struggle to connect the three representation levels: what they observe, what happens at the particle level, and what the equation shows. Two EAL learners. One student with high verbal ability and dyslexia.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can explain ionic bond formation at the particle level and connect it to the observable properties of ionic compounds'},
                    {'value': 'B', 'text': 'Students draw dot-and-cross diagrams for ionic compounds'},
                    {'value': 'C', 'text': 'Students complete an AI-generated matching task on bonding types'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies conceptual understanding across representation levels. Option B describes a procedural task. Option C starts from an AI product.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — Which scaffold helps students connect the three representation levels?',
                'options': [
                    {'value': 'A', 'text': 'Teach each level separately in sequence over three lessons'},
                    {'value': 'B', 'text': 'An AI-generated three-column guide: what you observe → what the particles do → what the equation shows — for the specific compound being studied'},
                    {'value': 'C', 'text': 'A simplified version using only the observable level'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A parallel representation guide for the specific compound makes the connections explicit rather than implicit. Option A delays the connection rather than building it. Option C removes two of the three levels.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports the student with dyslexia and high verbal ability?',
                'options': [
                    {'value': 'A', 'text': 'A simplified written explanation with shorter sentences'},
                    {'value': 'B', 'text': 'A rubric that accepts an oral explanation of the bonding process instead of a written answer, assessed against the same criteria'},
                    {'value': 'C', 'text': 'Extra time for written tasks'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The barrier is written production, not understanding. An oral response option removes the expression barrier while keeping the conceptual demand. Option A reduces the language complexity but keeps the written barrier. Option C is an accommodation, not a scaffold.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'More ionic compounds to draw dot-and-cross diagrams for'},
                    {'value': 'B', 'text': 'A novel substrate task: here is an element you haven\'t studied — predict whether it will form an ionic compound with chlorine, and justify your prediction using the bonding principles from this lesson'},
                    {'value': 'C', 'text': 'An introduction to covalent bonding'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Transfer to a novel substrate requires applying principles rather than recalling procedures. Option A is repetition. Option C introduces new content.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated vocabulary scaffold for EAL learners include?',
                'options': [
                    {'value': 'A', 'text': 'A translation of the full lesson into the student\'s first language'},
                    {'value': 'B', 'text': 'A bilingual term card: each key term (ion, lattice, electrostatic attraction) with a plain-language definition, what it means physically, and a first-language equivalent — with a note to verify translation accuracy'},
                    {'value': 'C', 'text': 'A simpler version of the lesson that avoids technical terms'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A targeted bilingual term card separates the vocabulary barrier from the chemistry. Always verify AI translations — quality varies by language pair. Option A over-scaffolds and creates dependency. Option C removes the scientific register that is part of the learning goal.',
            },
        ],
    },

    'biology': {
        'topic': 'Natural selection and evolution — Year 10',
        'context': 'A conceptually demanding topic where students often confuse mechanism and outcome. Some hold strong prior beliefs that conflict with evolutionary theory. One student with ADHD who struggles with long multi-part questions.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can explain the mechanism of natural selection using the four key conditions and apply it to an unfamiliar species scenario'},
                    {'value': 'B', 'text': 'Students understand that evolution happens over long time periods'},
                    {'value': 'C', 'text': 'Students complete an AI-generated quiz on Darwin\'s finches'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies mechanistic understanding and transfer to novel scenarios. Option B is a vague belief statement, not a learning outcome. Option C starts from an AI product.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — How do you approach students whose prior beliefs conflict with evolutionary theory?',
                'options': [
                    {'value': 'A', 'text': 'Avoid the conflict — focus only on the mechanism without discussing origins'},
                    {'value': 'B', 'text': 'Design for engagement: connect the mechanism to a personally relevant context (antibiotic resistance, dog breeding) before addressing the broader theory'},
                    {'value': 'C', 'text': 'Present the scientific consensus and ask students to accept it'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Starting with a personally relevant, non-controversial application of natural selection builds understanding of the mechanism before the broader theory becomes a barrier. Option A avoids the outcome. Option C triggers resistance without building understanding first.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports the student with ADHD on a multi-part question?',
                'options': [
                    {'value': 'A', 'text': 'A shorter question with fewer parts'},
                    {'value': 'B', 'text': 'The same question broken into four single-step cards: Condition 1 → Condition 2 → Condition 3 → How they combine. Each card has one instruction and a stopping point'},
                    {'value': 'C', 'text': 'Extra time and a quieter environment'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Chunking the question into sequential single-step cards reduces the working memory and attention demand without reducing the biological content. Option A reduces the content. Option C is an accommodation, not a scaffold.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Describe natural selection in more detail with additional examples'},
                    {'value': 'B', 'text': 'A failure mode challenge: describe a scenario where one of the four conditions of natural selection is absent — what happens to the population, and why does evolution stop?'},
                    {'value': 'C', 'text': 'Research the history of evolutionary theory from Lamarck to Darwin'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Reasoning about failure modes requires deep understanding of the mechanism — the student must know what each condition does in order to predict what happens when it\'s missing. Option A is repetition. Option C is research, not mechanistic understanding.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated cultural analogy check involve?',
                'options': [
                    {'value': 'A', 'text': 'Nothing — AI analogies are always accurate and culturally neutral'},
                    {'value': 'B', 'text': 'A review of any AI-generated cultural example for stereotypes and accuracy — relevant means genuinely familiar to this student, not associated with their background by assumption'},
                    {'value': 'C', 'text': 'Replacing all cultural analogies with generic examples'},
                ],
                'correct': 'B',
                'feedback': 'Correct. AI cultural analogies can default to stereotypes. A quick teacher review before use ensures the analogy is genuinely relevant. Option A ignores a real risk. Option C removes cultural relevance, which is the point of the analogy.',
            },
        ],
    },

    'geography': {
        'topic': 'Urban growth and its challenges — Year 9',
        'context': 'A case-study-heavy topic requiring integration of physical and human factors. Some students struggle with data interpretation. Others find the global examples remote from their own experience.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can analyse the causes and consequences of rapid urban growth using data and a case study, and evaluate which factor is most significant'},
                    {'value': 'B', 'text': 'Students learn about megacities and population growth'},
                    {'value': 'C', 'text': 'Students complete an AI-generated data table on global urbanisation'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies analytical skills — cause-consequence reasoning, data use, and evaluation of significance. Option B describes content. Option C starts from a tool.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What pre-class task works for this topic?',
                'options': [
                    {'value': 'A', 'text': 'Watch a short video on the case study with one embedded question: name two factors driving growth and predict which you think is most significant — write one sentence'},
                    {'value': 'B', 'text': 'Read the textbook section and take notes on all the factors'},
                    {'value': 'C', 'text': 'Find a news article about a megacity and summarise it'},
                ],
                'correct': 'A',
                'feedback': 'Correct. A short video with a focused prediction activates prior thinking and creates a commitment to test against data in class. Option B is passive reading. Option C is open-ended and inequitable.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports students who struggle with data interpretation?',
                'options': [
                    {'value': 'A', 'text': 'Remove the data task and use only case study text'},
                    {'value': 'B', 'text': 'An AI-generated data literacy scaffold: "This graph shows X on the y-axis and Y on the x-axis. The trend between [date] and [date] is..." — one sentence starter per data feature being interpreted'},
                    {'value': 'C', 'text': 'Provide the interpretation for students to copy'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A sentence-starter scaffold for each data feature supports the interpretation process without removing it. Option A removes the data task entirely. Option C removes the reasoning.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Study an additional case study with the same structure'},
                    {'value': 'B', 'text': 'A contrasting case: apply the same analytical framework to a city in a different context — does the same factor drive growth, or does a different one dominate? Why?'},
                    {'value': 'C', 'text': 'Research the future of urbanisation in 2050'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Comparative case analysis at a higher level — evaluating whether causal factors differ by context — extends the geographical thinking rather than repeating it. Option A is repetition. Option C changes topic.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — How does AI help with the engagement barrier for students who find global examples remote?',
                'options': [
                    {'value': 'A', 'text': 'Generate a simplified version of the case study with easier vocabulary'},
                    {'value': 'B', 'text': 'Generate a local-to-global connection: identify a feature of urban growth (traffic, housing density, green space) visible in the students\' own town and use it as the entry point to the global case study'},
                    {'value': 'C', 'text': 'Replace the global case study with a local one'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A local entry point creates relevance and then extends to the global case — both are studied. Option A reduces language, not the distance of the example. Option C removes the global perspective which is central to the learning goal.',
            },
        ],
    },

    'foreign_languages': {
        'topic': 'Expressing opinions and giving reasons — Year 9 (EFL/target language)',
        'context': 'A mixed-ability class with wide variation in fluency. Several students are strong readers but reluctant speakers. Two have recently joined the class and are significantly behind the group\'s level.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can express and justify an opinion in the target language using at least two structure types — in both written and spoken form'},
                    {'value': 'B', 'text': 'Students learn opinion phrases'},
                    {'value': 'C', 'text': 'Students complete an AI-generated gap-fill exercise on opinion language'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies production in both modes and at a level of complexity (two structure types). Option B describes vocabulary knowledge. Option C starts from a task.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What pre-class task supports the flipped approach?',
                'options': [
                    {'value': 'A', 'text': 'Watch a short video introducing two opinion structures with one embedded question: write two sentences using Structure 1 on a topic you care about — however imperfectly'},
                    {'value': 'B', 'text': 'Learn all the opinion vocabulary from the unit list'},
                    {'value': 'C', 'text': 'Record yourself speaking for one minute about your opinion on a topic'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The pre-class task introduces structure in context and requires a first production attempt. Option B is memorisation without production. Option C is high-demand oral production — it belongs in class with teacher support.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports the two students who are significantly behind the group\'s level?',
                'options': [
                    {'value': 'A', 'text': 'A separate simpler task focused only on one opinion structure'},
                    {'value': 'B', 'text': 'Sentence frames at a lower complexity level — the same communicative task, but with more structural support provided — with a plan to reduce the frames over future lessons'},
                    {'value': 'C', 'text': 'Pair them with stronger students who model the target structures'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Scaffolded sentence frames for the same task maintain the communicative goal while reducing the production barrier. Plan for fading the scaffold as fluency develops. Option A reduces the task. Option C outsources the production.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Write a longer opinion piece using all the structures from the lesson'},
                    {'value': 'B', 'text': 'A register task: write the same opinion as a formal written argument, an informal spoken response to a friend, and a social media post — demonstrating awareness of register and audience'},
                    {'value': 'C', 'text': 'Read an authentic text and translate a section'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Register awareness — adjusting language for audience and purpose — is the higher-order skill that extends beyond structural accuracy. Option A is more of the same. Option C is a different skill entirely.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI scaffold for reluctant speakers look like?',
                'options': [
                    {'value': 'A', 'text': 'Written alternatives that allow them to avoid speaking tasks entirely'},
                    {'value': 'B', 'text': 'A structured preparation scaffold before speaking: vocabulary bank, sentence frames, and a question-answer template to practice from — reducing anxiety without removing the speaking requirement'},
                    {'value': 'C', 'text': 'Grading them only on written production'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Preparation scaffolds reduce performance anxiety while maintaining the communicative task. The speaking requirement is preserved — only the unprepared production demand is reduced. Option A removes the speaking goal. Option C changes the assessment.',
            },
        ],
    },

    'social_studies': {
        'topic': 'How taxation and public services work — Year 8',
        'context': 'An abstract topic that students find remote from their own lives. Dense policy language in sources. Some students struggle with argument construction. Two EAL learners.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can explain the relationship between taxation and public services and evaluate one argument for and one against a specific tax policy'},
                    {'value': 'B', 'text': 'Students learn about different types of taxes'},
                    {'value': 'C', 'text': 'Students complete an AI-generated diagram of the tax system'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies conceptual understanding and evaluative argument — civic reasoning skills. Option B describes content coverage. Option C starts from a tool output.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — How do you make this topic personally relevant to engage students who find it remote?',
                'options': [
                    {'value': 'A', 'text': 'Tell students it will be on the exam'},
                    {'value': 'B', 'text': 'Start with a concrete local example — a public service students use daily (school, bus, park) — and ask: where does the money for this come from? Then connect to the broader tax system'},
                    {'value': 'C', 'text': 'Show a video about taxes in another country'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A familiar local example creates immediate relevance and a concrete entry point to the abstract concept. Option A is external motivation without engagement. Option C adds distance rather than reducing it.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports argument construction for students who struggle with it?',
                'options': [
                    {'value': 'A', 'text': 'A shorter argument task with only one point required'},
                    {'value': 'B', 'text': 'An AI-generated graphic organiser: a position box, two evidence slots, one counter-argument slot, and a conclusion prompt — the student fills in the organiser before writing'},
                    {'value': 'C', 'text': 'A model argument they can follow as a template'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The organiser separates the reasoning decisions from the writing, reducing the simultaneous cognitive load. Option A reduces the argument complexity. Option C risks copying rather than constructing.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Research more types of tax policies'},
                    {'value': 'B', 'text': 'A perspective-switch task: construct the strongest possible counter-argument to the position you just argued — then evaluate which argument is better supported by evidence'},
                    {'value': 'C', 'text': 'Write a longer essay about taxation'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Perspective-switching and comparative evaluation require genuine understanding of both positions — this is the civic reasoning that is the actual learning goal. Option A changes topic. Option C increases length without increasing depth.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What scaffold do EAL learners need for policy language sources?',
                'options': [
                    {'value': 'A', 'text': 'Replace the policy source with a simpler text'},
                    {'value': 'B', 'text': 'An AI-generated source companion: plain-language paraphrase, glossary of policy terms, and explanation of any cultural reference needed to understand the source\'s significance — read alongside the original'},
                    {'value': 'C', 'text': 'A translation of the source into the student\'s first language'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The companion gives access to the source without replacing it — students still engage with the original for language development. Option A removes the source. Option C may create first-language dependency for what is a target-language task.',
            },
        ],
    },

    'computer_science': {
        'topic': 'Introducing recursion — Year 10',
        'context': 'A challenging concept where students either grasp it quickly or completely lose the thread. Several students can follow a worked example but cannot write their own recursive function. One student with strong mathematical reasoning gets it immediately.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can trace through a recursive function by hand and write a simple recursive function for a new problem'},
                    {'value': 'B', 'text': 'Students know what recursion is'},
                    {'value': 'C', 'text': 'Students run an AI-generated recursive code example'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies two skills: tracing (understanding) and writing (application). Option B is vague declarative knowledge. Option C starts from a tool output.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What pre-class task supports this topic?',
                'options': [
                    {'value': 'A', 'text': 'Watch a video on recursion and answer: trace through this function by hand and write down each step — then identify what would happen if there was no base case'},
                    {'value': 'B', 'text': 'Read the textbook chapter on recursion and make notes'},
                    {'value': 'C', 'text': 'Try to write a recursive function on their own before the lesson'},
                ],
                'correct': 'A',
                'feedback': 'Correct. Tracing is the right pre-class task — it can be done independently with pause and rewind. The base case question activates conceptual thinking. Option B is passive. Option C is high-demand independent production before understanding is established.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports students who can follow examples but can\'t write their own?',
                'options': [
                    {'value': 'A', 'text': 'Give them more worked examples to study'},
                    {'value': 'B', 'text': 'A structured debugging guide for the specific error type they make: "Step 1 — what should the function return at this call? Step 2 — what is it actually returning? Step 3 — what is the difference?" Then a writing scaffold: function skeleton with the base case and recursive call labelled but blank'},
                    {'value': 'C', 'text': 'Allow them to use AI to generate the function and then explain it'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A combination of debugging structure and a function skeleton with explicit placeholders supports the transition from following to writing. Option A extends the gap rather than closing it. Option C bypasses the writing task entirely.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'More recursive functions to write'},
                    {'value': 'B', 'text': 'An efficiency challenge: here is a working recursive solution — rewrite it iteratively, then compare the two approaches: which is more readable? Which is more memory-efficient? When would you choose each?'},
                    {'value': 'C', 'text': 'An introduction to dynamic programming'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Comparing recursive and iterative approaches and reasoning about trade-offs is the kind of thinking that distinguishes a programmer from a coder. Option A is repetition. Option C is new content rather than deeper understanding of the current concept.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — When does AI enter the design of this lesson?',
                'options': [
                    {'value': 'A', 'text': 'At the start — find interesting recursive algorithms online and build the lesson around them'},
                    {'value': 'B', 'text': 'After the outcome is set — to generate the function skeleton scaffold, the debugging guide, and the efficiency challenge for the advanced learner'},
                    {'value': 'C', 'text': 'During class — to explain recursion to students who are confused'},
                ],
                'correct': 'B',
                'feedback': 'Correct. AI is a Stage 3 production tool for generating differentiated materials. Option A is resource-led design. Option C removes the teacher\'s diagnostic role — knowing why a student is confused is a professional judgment that AI cannot make in your classroom.',
            },
        ],
    },

    'physical_education': {
        'topic': 'Defensive positioning in small-sided basketball — Year 8',
        'context': 'A skills and tactics lesson. Some students are highly competitive and dominate. Others disengage quickly when the activity becomes competitive. One student uses a wheelchair.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can identify and apply correct defensive positioning in a small-sided game, adjusting their position in response to offensive movement'},
                    {'value': 'B', 'text': 'Students play a basketball game'},
                    {'value': 'C', 'text': 'Students watch an AI-generated tactical diagram of basketball defence'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies tactical understanding and physical application — identify, apply, and adjust. Option B describes an activity. Option C starts from a resource.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What pre-class task supports this flipped lesson?',
                'options': [
                    {'value': 'A', 'text': 'Watch a short video on defensive positioning with one embedded question: look at this diagram — where is the defensive player making an error, and what should they do instead?'},
                    {'value': 'B', 'text': 'Research basketball rules and defensive strategies online'},
                    {'value': 'C', 'text': 'Watch a full professional game and note defensive patterns'},
                ],
                'correct': 'A',
                'feedback': 'Correct. A focused error-identification task on a diagram activates tactical thinking before physical practice. Option B is open-ended research. Option C is passive viewing with no structured thinking task.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — How do you maintain inclusion for the student who uses a wheelchair?',
                'options': [
                    {'value': 'A', 'text': 'Ask them to score and time the game instead of playing'},
                    {'value': 'B', 'text': 'Adapt the activity to preserve the core tactical learning goal — defensive positioning and response to movement — in a wheelchair-accessible format, with the same tactical analysis task as all students'},
                    {'value': 'C', 'text': 'Seat them with a group to discuss tactics while others play'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The learning goal is tactical, not locomotor. An adapted format that preserves the tactical demand maintains inclusion without reducing the learning objective. Option A removes participation. Option C removes the physical component entirely.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension does the advanced learner need?',
                'options': [
                    {'value': 'A', 'text': 'Play in a more competitive game with stronger opponents'},
                    {'value': 'B', 'text': 'A tactical analysis task: watch a 2-minute clip of the class playing and identify two defensive errors — explain what the correct positioning was and why it matters'},
                    {'value': 'C', 'text': 'Learn advanced offensive moves to use in the next lesson'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Tactical analysis — observing, diagnosing errors, and explaining correct positioning — extends thinking beyond execution. Option A increases competitive intensity without increasing understanding. Option C changes the topic to offence.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What does the AI-generated instruction card for EAL learners in PE include?',
                'options': [
                    {'value': 'A', 'text': 'A full translation of the lesson plan into the student\'s first language'},
                    {'value': 'B', 'text': 'Key rules and tactical concepts in simplified language with a diagram of the playing area and defensive positions labelled — a reference card the student can consult during activity'},
                    {'value': 'C', 'text': 'A separate simpler activity without tactical requirements'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A visual reference card with simplified language and labelled diagrams supports participation without disrupting the flow of the lesson. Option A is over-scaffolded for a mainly physical task. Option C removes the tactical learning goal.',
            },
        ],
    },

    'arts': {
        'topic': 'Layering and texture in mixed media — Year 8',
        'context': 'A studio lesson. Several students avoid starting because they fear making mistakes. One student has significant fine motor difficulties. Two students are highly technically skilled but produce predictable work.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can use layering to create visual texture and articulate the effect their choices create'},
                    {'value': 'B', 'text': 'Students make a mixed media artwork'},
                    {'value': 'C', 'text': 'Students watch an AI-generated slideshow of mixed media artworks'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies both making (layering to create texture) and articulating (explaining effect) — two distinct learning goals. Option B describes an activity. Option C starts from a resource.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What scaffold helps students who avoid starting because they fear mistakes?',
                'options': [
                    {'value': 'A', 'text': 'Reassure them that mistakes are part of the creative process'},
                    {'value': 'B', 'text': 'An AI-generated starting constraint: "Use only three materials. Begin with the largest shape. Add one texture using a different material." The constraint reduces the decision space and provides a clear first action'},
                    {'value': 'C', 'text': 'Provide a step-by-step template showing exactly what the finished artwork should look like'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A creative constraint reduces the paralysis of infinite choice without removing creative agency. Once the student has started, the constraint can be relaxed. Option A is reassurance without action. Option C removes creativity entirely.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — How do you adapt the task for the student with fine motor difficulties?',
                'options': [
                    {'value': 'A', 'text': 'Excuse them from the making task and ask them to write about mixed media instead'},
                    {'value': 'B', 'text': 'Identify which materials and tools are accessible for this student and ensure the task allows those — the layering and texture goal remains; the material selection adapts to what can be controlled'},
                    {'value': 'C', 'text': 'Have a teaching assistant complete the physical parts for them'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The learning goal is layering and texture — not the use of specific fine motor tools. Material adaptation preserves the artistic goal while removing the physical barrier. Option A removes making entirely. Option C outsources the task.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension do the technically skilled but predictable students need?',
                'options': [
                    {'value': 'A', 'text': 'More technically demanding layering work'},
                    {'value': 'B', 'text': 'A critical dialogue task: here is an artwork by an established artist using mixed media — how does your work respond to, extend, or challenge this piece? What conversation is your work having with theirs?'},
                    {'value': 'C', 'text': 'Early access to the next technique in the scheme of work'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Contextualising their own work within a broader artistic conversation pushes technically skilled students toward the artistic development that is the actual goal. Option A increases technical demand without developing artistic thinking. Option C accelerates through content.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What vocabulary scaffold supports students writing about their work?',
                'options': [
                    {'value': 'A', 'text': 'Allow them to describe their work in everyday language without technical vocabulary'},
                    {'value': 'B', 'text': 'An AI-generated vocabulary scaffold for the specific reflective task: evaluative terms (evokes, conveys, juxtaposes) with plain-language definitions and sentence frame examples aligned to what students actually made'},
                    {'value': 'C', 'text': 'Provide a model artist statement they can adapt'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Subject-specific evaluative language is part of the arts learning goal. A targeted vocabulary scaffold helps students express their genuine aesthetic response in the register required. Option A removes the language goal. Option C risks close copying rather than genuine expression.',
            },
        ],
    },

    'special_education': {
        'topic': 'Understanding fractions as parts of a whole — mixed-age SEN group',
        'context': 'A small group with varied profiles: one student with high verbal ability and dyslexia, one with dyscalculia, one with ASD and strong visual processing, one EAL student with SEN. All have formal support plans.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Students can identify a fraction as a part of a whole and explain what the numerator and denominator each represent — using a format matched to their individual profile'},
                    {'value': 'B', 'text': 'Students complete a fractions worksheet'},
                    {'value': 'C', 'text': 'Students use an AI maths tool to generate fraction problems'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies conceptual understanding and explicitly allows for format variation — the concept is fixed, the expression route is flexible. Option B describes an activity. Option C starts from a tool.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — What AI scaffold targets the student with dyscalculia specifically?',
                'options': [
                    {'value': 'A', 'text': 'Remove numerical work and use only visual representations'},
                    {'value': 'B', 'text': 'A step-by-step card specific to today\'s problem type: each step has one instruction and one visual anchor — the concept is preserved, the working memory demand is distributed across the card'},
                    {'value': 'C', 'text': 'Pair with the student who has strong verbal ability to work together'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A highly specific step-by-step card with visual anchors reduces working memory demand without removing the mathematical concept. Option A reduces the goal. Option C outsources the thinking.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports the student with ASD who has strong visual processing?',
                'options': [
                    {'value': 'A', 'text': 'Provide a detailed written explanation of fractions'},
                    {'value': 'B', 'text': 'An AI-generated visual organiser using the student\'s specific strength: fraction bars, area models, and visual sequences that show the part-whole relationship without relying on verbal explanation'},
                    {'value': 'C', 'text': 'Reduce the task to matching activities only'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Matching the scaffold to the student\'s processing strength is good UDL practice. Visual representations of the fraction concept use the strength while building the mathematical understanding. Option A works against the processing strength. Option C reduces the conceptual demand.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What does the scaffold for the student with dyslexia and high verbal ability look like?',
                'options': [
                    {'value': 'A', 'text': 'A simplified written version of the task with easier vocabulary'},
                    {'value': 'B', 'text': 'An oral response option — the student explains what the fraction means and why, with the teacher or TA recording the response — assessed against the same conceptual criteria'},
                    {'value': 'C', 'text': 'Extended time for the written version'},
                ],
                'correct': 'B',
                'feedback': 'Correct. The barrier is written production, not mathematical understanding. An oral response option that preserves the conceptual demand is the right scaffold for this profile. Option A reduces language complexity but keeps the written barrier. Option C is an accommodation, not a scaffold.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What is the key principle when generating AI scaffolds for SEN students?',
                'options': [
                    {'value': 'A', 'text': 'Generate the most supportive scaffold possible — maximum support is always best'},
                    {'value': 'B', 'text': 'Target the specific barrier for each student\'s profile, preserve the conceptual demand, and plan from the start when you will begin fading the scaffold as the student develops confidence'},
                    {'value': 'C', 'text': 'Use the same scaffold for all students to ensure fairness'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Specificity, conceptual preservation, and fading are the three principles. Maximum support risks creating dependency. Generic scaffolds don\'t address individual barriers. A scaffold that never comes down becomes a ceiling.',
            },
        ],
    },

    'early_childhood': {
        'topic': 'Counting and grouping — Age 4-5',
        'context': 'A play-based learning session. Children have varied number sense: some count confidently to 20, others are still establishing one-to-one correspondence. Two children are EAL. One child has sensory sensitivities.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'Children can count a group of objects by pointing to each one, and say how many there are in total — using one-to-one correspondence'},
                    {'value': 'B', 'text': 'Children play a counting game'},
                    {'value': 'C', 'text': 'Children use an AI counting app'},
                ],
                'correct': 'A',
                'feedback': 'Correct. The outcome specifies the mathematical behaviour — one-to-one correspondence with a cardinal count. Option B describes an activity. Option C starts from a tool.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — How does a familiar story support engagement and learning?',
                'options': [
                    {'value': 'A', 'text': 'It entertains children before the real learning starts'},
                    {'value': 'B', 'text': 'It provides a narrative context that makes the mathematical concept personally meaningful — children count objects inside the story, then connect the same counting behaviour to physical objects in the activity'},
                    {'value': 'C', 'text': 'It fills time while the teacher prepares the materials'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Narrative context connects the mathematical behaviour to meaning — children are not counting abstractly but counting within a story they understand. Option A treats the story as entertainment rather than learning context. Option C treats it as filler.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — What scaffold supports EAL children in a counting activity?',
                'options': [
                    {'value': 'A', 'text': 'Conduct the activity in the child\'s first language'},
                    {'value': 'B', 'text': 'Use visual and physical supports — pointing gestures, touching each object, and number symbols alongside spoken number words — so the mathematical behaviour can be demonstrated without depending on language comprehension'},
                    {'value': 'C', 'text': 'Simplify the activity to fewer objects so there is less to count and say'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Visual and physical redundancy supports participation without depending on language. The mathematical goal — one-to-one correspondence — is accessible through gesture and physical action. Option A may not be possible and is language-dependent. Option C reduces the mathematical demand.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What extension supports a child who counts confidently to 20?',
                'options': [
                    {'value': 'A', 'text': 'Count to a larger number'},
                    {'value': 'B', 'text': 'Open-ended deepening questions: "How do you know there are six? Can you show me another way to check? What if we put two groups together — how many now?"'},
                    {'value': 'C', 'text': 'Introduce simple addition using worksheets'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Deepening questions extend conceptual engagement with the current skill — verification strategies and combining groups. Option A extends the range without deepening understanding. Option C introduces abstract notation before the concept is fully consolidated.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — How does AI support early childhood session planning?',
                'options': [
                    {'value': 'A', 'text': 'AI generates a digital counting game that replaces the physical activity'},
                    {'value': 'B', 'text': 'AI generates activity variations, story connections, and extension questions — the teacher selects and adapts. Physical manipulation and teacher-child interaction remain the primary learning mode'},
                    {'value': 'C', 'text': 'AI designs the full session plan and the teacher follows it'},
                ],
                'correct': 'B',
                'feedback': 'Correct. AI supports the design and production of materials — the teacher\'s professional judgment about what this group of children needs, and the physical and relational quality of the session, cannot be generated by AI. Option A replaces physical learning. Option C removes professional judgment.',
            },
        ],
    },

    'other': {
        'topic': 'Designing an AI-enhanced lesson in your subject',
        'context': 'You are planning a lesson that integrates AI support. Your class has a mix of learner profiles and you want to apply backward design, UDL, and flipped learning principles.',
        'decisions': [
            {
                'id': 'd1',
                'question': 'Step 1 — What is the Stage 1 outcome?',
                'options': [
                    {'value': 'A', 'text': 'A clear statement of what students will be able to DO and at what level by the end of the lesson — before any activity or tool is chosen'},
                    {'value': 'B', 'text': 'A topic to cover, selected from the curriculum'},
                    {'value': 'C', 'text': 'An AI tool that looks useful for this topic'},
                ],
                'correct': 'A',
                'feedback': 'Correct. Backward design always starts with the outcome — what students can do, not what topic is covered or what tool is available. Option B is content-led. Option C is tool-led.',
            },
            {
                'id': 'd2',
                'question': 'Step 2 — When does AI enter your design process?',
                'options': [
                    {'value': 'A', 'text': 'At Stage 3 — after the outcome and assessment are defined, AI generates scaffolds, differentiated versions, and pre-class check questions'},
                    {'value': 'B', 'text': 'At the start — choose the AI tool first, then design around its capabilities'},
                    {'value': 'C', 'text': 'Only if you have time left after planning everything else'},
                ],
                'correct': 'A',
                'feedback': 'Correct. AI is a Stage 3 design material. Options B and C both misplace AI in the design sequence — one too early, one too late.',
            },
            {
                'id': 'd3',
                'question': 'Step 3 — Which learner profile needs a representation scaffold?',
                'options': [
                    {'value': 'A', 'text': 'A student who finishes everything quickly and disengages'},
                    {'value': 'B', 'text': 'A student who understands the concept verbally but cannot process it from the written source format'},
                    {'value': 'C', 'text': 'A student who understands everything but struggles to write their response'},
                ],
                'correct': 'B',
                'feedback': 'Correct. UDL Principle 2 (Multiple Means of Representation) addresses how content is encoded — it applies when the format of the input creates the barrier. Option A needs an engagement scaffold. Option C needs an expression scaffold.',
            },
            {
                'id': 'd4',
                'question': 'Step 4 — What does a faded scaffold look like over time?',
                'options': [
                    {'value': 'A', 'text': 'The scaffold stays the same — consistency is important for students who need support'},
                    {'value': 'B', 'text': 'Week 1: full scaffold. Week 3: partial scaffold with gaps the student completes. Week 5: no scaffold — student applies the skill independently'},
                    {'value': 'C', 'text': 'Remove the scaffold immediately once the student produces correct work once'},
                ],
                'correct': 'B',
                'feedback': 'Correct. Fading is gradual — the scaffold is reduced progressively as confidence builds. Option A creates dependency. Option C removes support too suddenly before the skill is consolidated.',
            },
            {
                'id': 'd5',
                'question': 'Step 5 — What is the "human signature" check before assessment goes to students?',
                'options': [
                    {'value': 'A', 'text': 'The teacher\'s name is on the document'},
                    {'value': 'B', 'text': 'The assessment requires something a student must produce themselves — a personal reflection, a reference to a classroom discussion, a local context — that AI cannot replicate without knowing this student, this class, and this moment'},
                    {'value': 'C', 'text': 'The assessment was not generated by AI'},
                ],
                'correct': 'B',
                'feedback': 'Correct. A human signature means the task requires something personally situated — experience, context, or in-class knowledge — that AI alone cannot produce. If AI can complete the entire assessment, the task needs redesign.',
            },
        ],
    },
}


def get_context(subject=None):
    """
    Returns all TAB3 context for M9.
    subject is passed by views.py from teacher_profile.subject_area.
    Falls back to 'other' if subject not found.
    """
    scenario = LESSON_SCENARIOS.get(subject, LESSON_SCENARIOS['other'])

    return {
        'c1_elements': C1_ELEMENTS,
        'c1_stages': C1_STAGES,
        'c2_profiles': C2_PROFILES,
        'c2_principles': C2_PRINCIPLES,
        'c2_supports': C2_SUPPORTS,
        'c3_scenario': scenario,
    }
