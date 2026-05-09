# ============================================================
# apps/modules/tab3_content_m13.py
# M13 — Multimodal AI Content Creation
# TAB3 Challenges:
#   1. Prompt the Perfect Image (4-element formula + refinement)
#   2. Design a Hybrid Workflow (Workflow Canvas)
#   3. The Disclosure Decision (3 grey-zone scenarios)
# ============================================================

from django.conf import settings


def get_context():
    return {
        # ============================================================
        # PHASE A TIER 2 STEP 4 — Repository Submission CTA (Challenge 2)
        # ============================================================
        'github_workflows_url': getattr(
            settings,
            'GITHUB_WORKFLOWS_URL',
            'https://github.com/dourvas/proodos-eduai-teacher-workflows',
        ),

        # ============================================================
        # CHALLENGE 1: PROMPT THE PERFECT IMAGE
        # Structured form guiding teacher through all 4 elements
        # + a Refinement step where they change one element
        # ============================================================
        'c1_subject_options': [
            {'value': 'a_concept_with_spatial_structure', 'label': 'A concept with spatial structure (e.g. cell, solar system, map)'},
            {'value': 'a_historical_or_cultural_scene',   'label': 'A historical or cultural scene'},
            {'value': 'a_process_or_sequence',            'label': 'A process or sequence (e.g. water cycle, algorithm)'},
            {'value': 'an_abstract_concept',              'label': 'An abstract concept I want to make visual'},
            {'value': 'a_vocabulary_or_language_item',    'label': 'A vocabulary or language item'},
            {'value': 'other',                            'label': 'Something else from my subject'},
        ],

        'c1_how_styles': [
            {'value': 'cartoon style',              'label': 'Cartoon style — bright, simple, engaging (primary/elementary)'},
            {'value': 'storybook illustration',     'label': 'Storybook illustration — whimsical, colourful (primary)'},
            {'value': 'educational diagram',        'label': 'Educational diagram — clear, labelled, precise (secondary)'},
            {'value': 'scientific illustration',    'label': 'Scientific illustration — accurate, technical (secondary)'},
            {'value': 'infographic style',          'label': 'Infographic style — data-driven, modern (all ages)'},
            {'value': 'historical painting style',  'label': 'Historical painting style — for humanities content'},
            {'value': 'watercolour style',          'label': 'Watercolour style — soft, artistic (primary)'},
            {'value': 'flat icon style',            'label': 'Flat icon style — simple, uncluttered (special education / early childhood)'},
        ],

        'c1_quality_checks': [
            {'value': 'age_appropriate',    'label': 'Age appropriate — content and style match my students'},
            {'value': 'accurate',           'label': 'Educationally accurate — I would verify before using'},
            {'value': 'culturally_safe',    'label': 'Culturally sensitive — no stereotyping or misrepresentation'},
            {'value': 'readable',           'label': 'Clear and readable — visible at classroom display size'},
            {'value': 'labels_ok',          'label': 'Labels checked — no gibberish text inside the image'},
            {'value': 'curriculum_aligned', 'label': 'Curriculum aligned — supports a specific learning objective'},
            {'value': 'rights_checked',     'label': 'Rights checked — I know this tool\'s usage licence'},
        ],

        'c1_refinement_elements': [
            {'value': 'who_what', 'label': 'WHO & WHAT — change the subject or action'},
            {'value': 'where',    'label': 'WHERE — change the setting or context'},
            {'value': 'how',      'label': 'HOW — change the visual style'},
            {'value': 'for_whom', 'label': 'FOR WHOM — change the age group or educational level'},
        ],

        # ============================================================
        # CHALLENGE 2: DESIGN A HYBRID WORKFLOW
        # Teacher designs a multimodal project using the Workflow Canvas
        # ============================================================
        'c2_learning_goal_options': [
            {'value': 'explain_concept',        'label': 'Explain a concept students find difficult to visualise'},
            {'value': 'introduce_topic',        'label': 'Introduce a new topic as a lesson hook'},
            {'value': 'revision_resource',      'label': 'Create a revision resource students can use independently'},
            {'value': 'vocabulary_acquisition', 'label': 'Support vocabulary acquisition'},
            {'value': 'historical_immersion',   'label': 'Create historical or cultural immersion'},
            {'value': 'accessible_content',     'label': 'Make content more accessible (language, disability)'},
            {'value': 'student_project',        'label': 'Design a student creation project'},
        ],

        'c2_modality_options': [
            {'value': 'image',    'label': '🖼️ Image — static visual, diagram, or illustration'},
            {'value': 'video',    'label': '🎬 Video — short clip, avatar presentation, or animation'},
            {'value': 'audio',    'label': '🎵 Audio — narration, song, or background music'},
            {'value': 'platform', 'label': '🔧 No-code platform — curated interactive experience'},
        ],

        'c2_tool_category_options': [
            {'value': 'image_generation',   'label': 'Image generation (e.g. text-to-image tool)'},
            {'value': 'avatar_video',       'label': 'Avatar video (e.g. presenter-style video tool)'},
            {'value': 'generative_video',   'label': 'Generative video (e.g. text-to-video tool)'},
            {'value': 'ai_editing',         'label': 'AI-enhanced editing (e.g. script-to-video with stock footage)'},
            {'value': 'voice_synthesis',    'label': 'Voice synthesis (e.g. text-to-speech tool)'},
            {'value': 'music_generation',   'label': 'Music generation (e.g. AI background music tool)'},
            {'value': 'audio_enhancement',  'label': 'Audio enhancement (e.g. noise removal tool)'},
            {'value': 'nocode_platform',    'label': 'No-code platform (e.g. Google Arts & Culture, Europeana)'},
        ],

        'c2_canvas_steps': [
            {'step': 1, 'label': 'Step 1', 'placeholder': 'What do students need to understand or do?', 'hint': 'Your learning goal'},
            {'step': 2, 'label': 'Step 2', 'placeholder': 'Which modality — image, video, audio, or platform?', 'hint': 'Choose the simplest that works'},
            {'step': 3, 'label': 'Step 3', 'placeholder': 'Which tool category will you use?', 'hint': 'Not a brand name — a category'},
            {'step': 4, 'label': 'Step 4', 'placeholder': 'What will you create? Describe the output.', 'hint': 'One sentence describing the finished asset'},
            {'step': 5, 'label': 'Step 5', 'placeholder': 'How will students interact with it?', 'hint': 'In class, independently, as a discussion prompt...'},
        ],

        'c2_prep_time_options': [
            '15 minutes',
            '30 minutes',
            '45 minutes',
            '1 hour',
            'More than 1 hour',
        ],

        # ============================================================
        # CHALLENGE 3: THE DISCLOSURE DECISION
        # 3 grey-zone scenarios — teacher decides: use or not, disclose how
        # ============================================================
        # ============================================================
        # CHALLENGE 3 SCENARIO 1 — Subject-specific variants
        # Template selects via teacher_profile.subject_area
        # ============================================================
        'c3_scenario1_variants': {
            'mathematics': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '📐',
                'situation': (
                    "You generate an AI diagram showing the proof of the Pythagorean theorem — "
                    "a² + b² = c² — with a right triangle and labelled squares on each side. "
                    "The visual is clean and clear. On close inspection, the right-angle marker "
                    "is placed at the wrong vertex, making it technically incorrect. "
                    "Most students would not notice. You plan to use it as a visual aid, "
                    "not as a formal proof."
                ),
                'tension': 'Visual clarity vs. mathematical precision',
            },
            'language_arts': {
                'title': 'The Almost-Accurate Scene',
                'icon': '📖',
                'situation': (
                    "You generate an AI illustration of a scene from a novel your class is studying. "
                    "The image captures the mood well, but one character is depicted wearing clothing "
                    "that does not match the author's description — a minor detail most students "
                    "would miss on a first read. You plan to use it as a discussion starter "
                    "about the scene's atmosphere, not as a literal reference."
                ),
                'tension': 'Atmospheric value vs. fidelity to the text',
            },
            'science': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '🔬',
                'situation': (
                    "You generate an AI cross-section of a volcano for an earth science lesson. "
                    "The image is visually engaging and shows the main features — magma chamber, "
                    "conduit, crater. On close inspection, the relative depths of the layers "
                    "are not geologically accurate. You plan to use it as a concept introduction, "
                    "not as a technical reference."
                ),
                'tension': 'Visual engagement vs. scientific accuracy',
            },
            'physics': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '⚡',
                'situation': (
                    "You generate an AI free-body diagram showing forces on a block on an "
                    "inclined plane. The diagram looks professional. On close inspection, "
                    "the friction arrow is pointing in the wrong direction relative to the "
                    "motion. The error is physically incorrect but subtle. "
                    "You plan to use it as an introduction before students draw their own."
                ),
                'tension': 'Professional appearance vs. physical correctness',
            },
            'chemistry': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '⚗️',
                'situation': (
                    "You generate an AI molecular model of a water molecule. The image is "
                    "colourful and clear. On close inspection, the bond angle shown is "
                    "approximately 90° rather than the correct 104.5°. It is visually appealing "
                    "but chemically imprecise. You plan to use it to introduce the concept "
                    "of molecular geometry, not as a precise reference."
                ),
                'tension': 'Visual accessibility vs. chemical precision',
            },
            'biology': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '🧬',
                'situation': (
                    "You generate an AI diagram of a plant cell. Most organelles are correctly "
                    "placed and labelled. On close inspection, the chloroplasts are shown inside "
                    "the nucleus — a clear biological error. The rest of the diagram is useful "
                    "for your lesson on cell structure. You plan to use it as a labelling "
                    "activity starter."
                ),
                'tension': 'Practical utility vs. biological accuracy',
            },
            'history': {
                'title': 'The Almost-Accurate Scene',
                'icon': '🏛️',
                'situation': (
                    "You generate an AI image of a medieval market scene for a lesson on "
                    "trade and commerce. The image looks convincing and visually engaging. "
                    "On close inspection, one building in the background has architectural "
                    "features from the wrong century — subtle enough that most students "
                    "would not notice. You plan to use it as a discussion starter, "
                    "not as a factual reference."
                ),
                'tension': 'Visual quality vs. historical accuracy',
            },
            'geography': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '🌍',
                'situation': (
                    "You generate an AI aerial diagram of a river delta for a physical geography "
                    "lesson. The image shows branching channels and sediment clearly. "
                    "On close inspection, the scale of the delta relative to surrounding features "
                    "is significantly distorted. You plan to use it to explain the concept of "
                    "delta formation, not as a cartographically accurate reference."
                ),
                'tension': 'Conceptual clarity vs. cartographic accuracy',
            },
            'social_studies': {
                'title': 'The Almost-Accurate Infographic',
                'icon': '📊',
                'situation': (
                    "You generate an AI infographic showing the three branches of government "
                    "and their relationships. The overall structure is correct. On close "
                    "inspection, one arrow showing a checks-and-balances relationship is "
                    "pointing in the wrong direction — a minor but civically incorrect detail. "
                    "You plan to use it as a visual anchor for a class discussion."
                ),
                'tension': 'Visual engagement vs. civic accuracy',
            },
            'foreign_languages': {
                'title': 'The Almost-Accurate Scene',
                'icon': '🗣️',
                'situation': (
                    "You generate an AI image of a family breakfast scene for a vocabulary "
                    "lesson. The image is warm and natural. On close inspection, one food "
                    "item visible on the table is labelled incorrectly in your prompt — "
                    "the image shows bread but you intended to introduce the word for cereal. "
                    "You plan to use it as a conversation prompt, asking students to describe "
                    "what they see."
                ),
                'tension': 'Natural conversation prompt vs. vocabulary precision',
            },
            'computer_science': {
                'title': 'The Almost-Accurate Flowchart',
                'icon': '💻',
                'situation': (
                    "You generate an AI flowchart of a binary search algorithm. The overall "
                    "structure is clear and well-labelled. On close inspection, one decision "
                    "diamond has the true/false branches swapped — the logic would produce "
                    "incorrect results if followed literally. You plan to use it as a "
                    "discussion starter before students trace through the algorithm themselves."
                ),
                'tension': 'Structural clarity vs. logical correctness',
            },
            'physical_education': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '⚽',
                'situation': (
                    "You generate an AI tactical diagram showing player positions for a "
                    "set-play in football. The image is clean and easy to read. On close "
                    "inspection, the movement arrows for two players cross in a way that "
                    "would create a collision in real play. You plan to use it to introduce "
                    "the concept of off-the-ball movement, not as a precise play to execute."
                ),
                'tension': 'Tactical concept illustration vs. practical accuracy',
            },
            'arts': {
                'title': 'The Almost-Accurate Artwork',
                'icon': '🎨',
                'situation': (
                    "You generate an AI image 'in the style of Monet' for a lesson on "
                    "Impressionism. The image captures the soft brushwork and light quality well. "
                    "On close inspection, the colour palette includes deep blacks that Monet "
                    "famously avoided — a stylistic inaccuracy that art historians would notice. "
                    "You plan to use it alongside real Monet works to prompt discussion "
                    "about what defines the style."
                ),
                'tension': 'Impressionistic feel vs. stylistic accuracy',
            },
            'special_education': {
                'title': 'The Almost-Accurate Visual Support',
                'icon': '🌟',
                'situation': (
                    "You generate a series of AI visual schedule cards for a student. "
                    "Most cards are clear and appropriate. One card showing 'wash hands' "
                    "depicts only three steps, missing the soap step that is part of "
                    "the student's specific routine. The card is visually consistent "
                    "with the others. You plan to use the full set as a daily routine support."
                ),
                'tension': 'Visual consistency vs. routine precision',
            },
            'early_childhood': {
                'title': 'The Almost-Accurate Illustration',
                'icon': '🌈',
                'situation': (
                    "You generate an AI storybook illustration of a duck for a colour and "
                    "animal recognition activity. The image is bright and friendly. "
                    "On close inspection, the duck has five legs — a common AI generation "
                    "error. Young children might not notice, but a parent or colleague "
                    "reviewing your materials certainly would. You plan to use it in "
                    "a small group activity."
                ),
                'tension': 'Visual appeal vs. factual accuracy for young learners',
            },
            'other': {
                'title': 'The Almost-Accurate Diagram',
                'icon': '🗺️',
                'situation': (
                    "You generate an AI diagram to illustrate a key concept in your subject area. "
                    "The overall structure is useful and visually clear. On close inspection, "
                    "one detail is incorrect — subtle enough that most students would not notice, "
                    "but wrong enough that a subject specialist would flag it. "
                    "You plan to use it as a discussion starter or visual introduction, "
                    "not as a definitive reference."
                ),
                'tension': 'Practical utility vs. subject accuracy',
            },
        },

        'c3_scenarios': [
            {
                'id': 1,
                'title': 'The Almost-Accurate Diagram',
                'icon': '🗺️',
                'situation': (
                    "You generate an AI image of a historical market scene for a lesson on medieval trade. "
                    "The image looks convincing and visually engaging. On close inspection, one building in the background "
                    "has architectural features from the wrong century — subtle enough that most students would not notice, "
                    "but historically inaccurate. You plan to use it as a discussion starter, not as a factual reference."
                ),
                'tension': 'Visual quality vs. historical accuracy',
                'options': [
                    {'value': 'use_as_is',          'label': 'Use it as-is — the inaccuracy is minor and the image serves its purpose'},
                    {'value': 'use_with_caveat',    'label': 'Use it, but explicitly point out the inaccuracy to students as a teaching moment'},
                    {'value': 'use_and_fix',        'label': 'Use it, regenerate until I get an accurate version first'},
                    {'value': 'do_not_use',         'label': 'Do not use it — accuracy cannot be compromised even for a discussion image'},
                ],
                'disclosure_prompt': 'If you decide to use this image, what would you say to your students?',
                'reflection_prompt': 'What does this scenario reveal about your personal threshold for "good enough" in AI-generated educational content?',
            },
            {
                'id': 2,
                'title': 'The Convincing Voice',
                'icon': '🎙️',
                'situation': (
                    "You want to add an audio element to a science lesson on climate change. "
                    "A colleague shares a tool that can generate a narration in a voice that sounds remarkably like "
                    "a well-known scientist — highly realistic, authoritative, and engaging. "
                    "The script you would use is factually accurate and written entirely by you. "
                    "Students would hear what sounds like an expert speaking directly to them."
                ),
                'tension': 'Engagement and authority vs. authenticity and potential deception',
                'options': [
                    {'value': 'use_as_is',          'label': 'Use it — the content is accurate and the engagement benefit is high'},
                    {'value': 'use_with_disclosure', 'label': 'Use it, but clearly tell students it is an AI-generated voice, not the real scientist'},
                    {'value': 'use_generic_voice',  'label': 'Use AI narration but choose a clearly synthetic voice rather than one mimicking a real person'},
                    {'value': 'do_not_use',         'label': 'Do not use it — voice cloning of real people crosses a line regardless of content accuracy'},
                ],
                'disclosure_prompt': 'If you decide to use this audio, what would you say to your students — and when?',
                'reflection_prompt': 'Where do you draw the line between using AI to enhance engagement and using it in ways that could mislead students?',
            },
            {
                'id': 3,
                'title': 'The Heavily Edited Diagram',
                'icon': '✏️',
                'situation': (
                    "You generate an AI diagram of the water cycle. The initial output has several errors — "
                    "wrong labels, a missing process step, and imprecise arrows. You spend 45 minutes manually correcting "
                    "every label, redrawing two arrows, and adding the missing evaporation step. "
                    "The final diagram is now scientifically accurate and exactly what you wanted. "
                    "Your corrections account for most of the informational content. "
                    "Do you still need to disclose that it started as AI-generated?"
                ),
                'tension': 'Significant human effort and accuracy vs. transparency about origin',
                'options': [
                    {'value': 'no_disclosure',      'label': 'No disclosure needed — I corrected everything; the AI was just a starting point like a blank template'},
                    {'value': 'brief_disclosure',   'label': 'Brief disclosure — mention it casually if asked, but it does not need to be prominent'},
                    {'value': 'full_disclosure',    'label': 'Full disclosure — tell students it started as AI and I edited it extensively, explain why'},
                    {'value': 'attribute_tool',     'label': 'Attribute the tool in writing (e.g. in the image caption) but do not discuss it verbally'},
                ],
                'disclosure_prompt': 'Write the exact words you would use (or not use) to address the origin of this diagram.',
                'reflection_prompt': 'How much human editing is required before AI-assisted content becomes "your own work"? Does your answer change depending on context?',
            },
        ],

    }
