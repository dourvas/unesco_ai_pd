def get_context():
    return {

        # ── CHALLENGE 1 ─────────────────────────────────────────────
        # Four group vignettes. One is a genuine CoP, three are not.
        # Players identify which is which and why.

        'c1_vignettes': [
            {
                'id': 'vignette_a',
                'label': 'Group A — The AI Updates Channel',
                'text': (
                    "Every Monday, the school's IT coordinator sends a short email "
                    "to all staff with two or three AI tools worth trying that week. "
                    "Teachers read it, occasionally try a tool, and sometimes reply "
                    "with a thumbs up. The coordinator collects positive replies and "
                    "shares them in a termly summary. Participation is voluntary and "
                    "most teachers find it useful."
                ),
                'is_cop': False,
                'verdict': 'Not a CoP',
                'feedback': (
                    "This is an information broadcast, not a community. There is no "
                    "mutual engagement — teachers receive content but don't examine each "
                    "other's practice. There is no joint enterprise — the coordinator "
                    "defines the agenda unilaterally. There is no shared repertoire being "
                    "built — the termly summary is a record of tool popularity, not "
                    "professional knowledge."
                ),
            },
            {
                'id': 'vignette_b',
                'label': 'Group B — The AI Integration Working Group',
                'text': (
                    "The headteacher formed a six-person working group to produce an "
                    "AI use policy for the school by the end of term. Members were "
                    "assigned by the headteacher. They meet fortnightly, divide tasks, "
                    "and report progress. When the policy is finished, the group will "
                    "be dissolved. Members describe the work as useful but time-pressured."
                ),
                'is_cop': False,
                'verdict': 'Not a CoP',
                'feedback': (
                    "This is a task force — a group assembled to produce a specific "
                    "deliverable and then disband. It has mutual engagement and a joint "
                    "enterprise, but the enterprise is assigned from above and has a "
                    "fixed endpoint. A CoP's joint enterprise is negotiated by members "
                    "and evolves over time. When the policy is done, the group dissolves "
                    "— which means no shared repertoire persists."
                ),
            },
            {
                'id': 'vignette_c',
                'label': 'Group C — The Thursday Prompt Group',
                'text': (
                    "Eight teachers across four departments meet every other Thursday "
                    "at lunch. One teacher brings an annotated AI interaction — a prompt "
                    "they used, what surprised them, what they rejected and why. The group "
                    "examines the reasoning together, asks questions, and suggests "
                    "alternatives. Notes are kept in a shared folder. The group has been "
                    "running for two terms and has built a small annotated prompt library "
                    "that members refer to regularly."
                ),
                'is_cop': True,
                'verdict': 'A genuine CoP',
                'feedback': (
                    "All three Wenger dimensions are present. Mutual engagement: members "
                    "examine each other's practice regularly and genuinely. Joint "
                    "enterprise: the group has negotiated its own purpose — examining AI "
                    "reasoning, not just sharing tools — and sustains it across time. "
                    "Shared repertoire: the annotated prompt library is exactly the kind "
                    "of collective knowledge artefact that defines a functioning CoP. "
                    "The knowledge persists beyond any single session."
                ),
            },
            {
                'id': 'vignette_d',
                'label': 'Group D — The CPD Session Cohort',
                'text': (
                    "Twelve teachers attended a two-day AI in Education CPD course "
                    "together last autumn. They still have a WhatsApp group where they "
                    "occasionally share links to AI news articles and remind each other "
                    "of things covered on the course. Two members have met for coffee "
                    "once to discuss a specific challenge. The group chat has been quiet "
                    "for about six weeks."
                ),
                'is_cop': False,
                'verdict': 'Not a CoP',
                'feedback': (
                    "This started with a shared experience but hasn't developed into a "
                    "community. The WhatsApp group has low mutual engagement — links and "
                    "reminders, not examination of practice. There is no joint enterprise "
                    "the group is actively pursuing. No shared repertoire is being built. "
                    "A common history is a starting condition for a CoP, not a CoP itself."
                ),
            },
        ],

        'c1_cop_id': 'vignette_c',  # correct answer

        # ── CHALLENGE 2 ─────────────────────────────────────────────
        # Slot labels passed to template for rendering the three assignment slots
        'c2_slots': [
            ('why',       '📌 Why — what pedagogical problem was this prompt solving?',       'indigo'),
            ('surprise',  '💡 Surprise — what did the AI reveal that the teacher didn\'t expect?', 'amber'),
            ('rejection', '✗ Rejection — what output was discarded, and why?',               'red'),
        ],
        # A prompt is shown without annotations.
        # Six annotation fragments are presented.
        # Three belong to Why / Surprise / Rejection.
        # Three are distractors (plausible but wrong).

        'c2_prompt': (
            "You are a geography teacher who grounds abstract concepts in specific places. "
            "Explain population distribution in Greece for Year 8 students who understand "
            "the concept abstractly but cannot apply it to real places they can locate. "
            "This explanation will be used as a reading text before students annotate a map. "
            "Use Athens, Thessaloniki, and rural Epirus as specific examples. Connect each "
            "location to a physical geography feature. Do not use generic phrases like "
            "'rural areas' or 'urban centres' — name the places. Format: three paragraphs, "
            "one per location, each ending with a map annotation prompt."
        ),

        'c2_fragments': [
            {
                'id': 'frag_1',
                'text': (
                    "The AI knew Athens and Thessaloniki well but produced generic "
                    "statements about 'rural areas.' Specifying Epirus by name produced "
                    "much richer geographical detail — place specificity unlocked AI "
                    "knowledge I hadn't expected."
                ),
                'correct_slot': 'surprise',
            },
            {
                'id': 'frag_2',
                'text': (
                    "I rejected an explanation attributing rural depopulation entirely "
                    "to economic factors without mentioning terrain. Geographically "
                    "incomplete — and it would have reinforced the idea that geography "
                    "is just economics with maps."
                ),
                'correct_slot': 'rejection',
            },
            {
                'id': 'frag_3',
                'text': (
                    "The methodology link — reading text before map annotation — was "
                    "the key decision. A generic explanation can precede any task. "
                    "A map annotation task requires named, locatable places."
                ),
                'correct_slot': 'why',
            },
            {
                'id': 'frag_4',
                'text': (
                    "I was pleased with the output length — three paragraphs was exactly "
                    "right for my class and the reading time fitted the lesson slot well."
                ),
                'correct_slot': None,  # distractor
            },
            {
                'id': 'frag_5',
                'text': (
                    "I decided to use Greece because my students had just finished a "
                    "unit on European geography and I wanted to build on their existing "
                    "map knowledge."
                ),
                'correct_slot': None,  # distractor
            },
            {
                'id': 'frag_6',
                'text': (
                    "The AI produced good paragraphs overall. The format was consistent "
                    "and the language level was appropriate for Year 8."
                ),
                'correct_slot': None,  # distractor
            },
        ],

        # ── CHALLENGE 3 ─────────────────────────────────────────────
        # A CoP session vignette with 3 failure modes embedded.
        # Players identify which failure modes are present and
        # select a facilitator response for each.

        'c3_vignette': (
            "The Thursday Prompt Group is in its fifth session. Maya brings a prompt "
            "she used to generate a reading comprehension exercise. Before anyone looks "
            "at the annotations, David says 'Oh, I've been using a much better tool for "
            "reading tasks — let me show everyone how it works.' He shares his screen and "
            "spends eight minutes demonstrating the tool's features. Several teachers take "
            "notes. When the group returns to Maya's prompt, there are twelve minutes left. "
            "Maya reads out her Why annotation, but before she finishes, two teachers begin "
            "discussing a similar activity they both tried last week. The session ends "
            "without anyone documenting what was learned. Next week's artefact hasn't "
            "been confirmed."
        ),

        'c3_failure_modes': [
            {
                'id': 'fm_tool_tutorial',
                'label': 'The session became a tool tutorial',
                'present': True,
                'explanation': (
                    "David's eight-minute tool demonstration is exactly the failure mode "
                    "the no-tool-tutorial rule exists to prevent. The group lost a third "
                    "of its time to a product showcase rather than an examination of "
                    "reasoning. The facilitator should have redirected immediately: "
                    "'That sounds useful — let's stay with Maya's reasoning for now "
                    "and you can share that separately.'"
                ),
                'redirect': (
                    "Redirect immediately when tool demonstrations begin: "
                    "'Let's stay with the reasoning — tool exploration can happen outside the session.'"
                ),
            },
            {
                'id': 'fm_no_documentation',
                'label': 'Nothing was documented',
                'present': True,
                'explanation': (
                    "The session ended without any record of what was learned. "
                    "Documentation is not optional — it is the mechanism by which "
                    "individual session learning becomes institutional memory. "
                    "A facilitator who doesn't protect the closing documentation "
                    "step is letting the session's value evaporate."
                ),
                'redirect': (
                    "Reserve the last five minutes for documentation regardless of what else is happening: "
                    "'Before we finish — one sentence each: what did this annotation reveal?'"
                ),
            },
            {
                'id': 'fm_no_artefact',
                'label': 'No shared artefact confirmed for next session',
                'present': True,
                'explanation': (
                    "A session without a confirmed next artefact has no continuity. "
                    "The group will arrive next week without a shared anchor, and the "
                    "session will drift. Confirming the next artefact before closing "
                    "is a basic facilitator responsibility — it takes ninety seconds "
                    "and prevents the most common failure mode of the following session."
                ),
                'redirect': (
                    "Always confirm the next artefact before closing: "
                    "'Who is bringing something next time — and what is it?'"
                ),
            },
            {
                'id': 'fm_wrong_group_size',
                'label': 'The group is too large for genuine dialogue',
                'present': False,
                'explanation': (
                    "Group size isn't mentioned as a problem in this vignette. "
                    "The Thursday Prompt Group has eight members — a workable size "
                    "for a CoP session. The failures here are about session management, "
                    "not group composition."
                ),
                'redirect': None,
            },
            {
                'id': 'fm_wrong_topic',
                'label': "The shared artefact wasn't connected to a real teaching challenge",
                'present': False,
                'explanation': (
                    "There is no evidence of this in the vignette. Maya brought a "
                    "prompt from a real task — a reading comprehension exercise. "
                    "The problem wasn't the artefact, it was the session management "
                    "around it."
                ),
                'redirect': None,
            },
        ],

    }
