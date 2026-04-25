# ============================================================
# tab3_content_m2.py — TAB3 context data for M2
# Place in: apps/modules/tab3_content_m2.py
# ============================================================

M2_SCENARIO = {
    "text": (
        "A teacher at a secondary school uses an AI writing assistant to help draft "
        "individual progress reports for all 28 of her students. She edits each report "
        "carefully before sending it to parents, personalising the language and adding "
        "specific observations from her own notes. She does not mention to parents or "
        "school leadership that AI was involved in the initial drafts. A colleague who "
        "finds out asks her: 'Shouldn't you tell them?'"
    ),
    "tags": ["Transparency", "Accountability", "Teacher AI Use", "Parent Communication"],
    "options": [
        {
            "value": "disclose_fully",
            "label": "Disclose fully — inform parents and school leadership proactively",
            "note": "Even though the reports were carefully edited, transparency builds trust."
        },
        {
            "value": "disclose_on_request",
            "label": "Disclose on request — be honest if anyone asks, but don't volunteer it",
            "note": "The final content is the teacher's responsibility; AI was just a drafting tool."
        },
        {
            "value": "internal_policy",
            "label": "Raise it with school leadership — this needs a shared policy, not an individual decision",
            "note": "This is an institutional question, not just a personal ethics choice."
        },
        {
            "value": "no_disclosure",
            "label": "No disclosure needed — the teacher reviewed and personalised everything",
            "note": "The content is accurate and personalised; the method of drafting is irrelevant."
        },
    ],
    "perspectives": [
        {
            "title": "The transparency argument",
            "text": (
                "Parents trust that reports reflect the teacher's direct professional judgment. "
                "When AI is involved — even in drafting — this changes the nature of that judgment "
                "in ways parents may care about. Proactive disclosure, even brief, maintains the "
                "integrity of the teacher-parent relationship. It also models the transparency we "
                "expect from students."
            )
        },
        {
            "title": "The accountability argument",
            "text": (
                "The teacher reviewed, edited, and took full responsibility for every report. "
                "Many professional writers, doctors, and administrators use drafting assistance. "
                "What matters is that the final content is accurate, personalised, and the "
                "teacher's own judgment — which it is. Disclosure of every tool used in "
                "professional work is not standard practice."
            )
        },
        {
            "title": "The institutional argument",
            "text": (
                "Individual teachers should not be making these decisions alone. This scenario "
                "reveals a policy gap: most schools have no guidance on teachers' own AI use. "
                "Raising it with leadership is both the professionally responsible and "
                "self-protective choice — and it contributes to building the institutional "
                "frameworks that everyone needs."
            )
        },
    ]
}

M2_PRINCIPLES = [
    {"value": "fairness",       "label": "⚖️ Fairness"},
    {"value": "transparency",   "label": "🔍 Transparency"},
    {"value": "privacy",        "label": "🔒 Privacy"},
    {"value": "accountability", "label": "🎯 Accountability"},
    {"value": "inclusion",      "label": "🤝 Inclusion"},
]

M2_AUDIT_TOOLS = [
    {"value": "ChatGPT",    "label": "ChatGPT"},
    {"value": "Gemini",     "label": "Gemini"},
    {"value": "Claude",     "label": "Claude"},
    {"value": "Copilot",    "label": "Microsoft Copilot"},
    {"value": "Canva AI",   "label": "Canva AI"},
    {"value": "Grammarly",  "label": "Grammarly"},
    {"value": "Quizlet AI", "label": "Quizlet AI"},
    {"value": "Khanmigo",   "label": "Khanmigo"},
    {"value": "Perplexity", "label": "Perplexity"},
]

M2_AUDIT_QUESTIONS = [
    {
        "text": "Do you know what data this tool collects from students who use it?",
        "hint": "Check the tool's privacy policy or data protection page — look for what is logged, stored, or used for training."
    },
    {
        "text": "Does this tool comply with GDPR (or your national equivalent) for use with minors?",
        "hint": "Many consumer AI tools are not approved for under-18 use. Look for an 'Education' version or a DPA (Data Processing Agreement)."
    },
    {
        "text": "Have you (or your school) informed students and parents that this tool is used in your classroom?",
        "hint": "Transparency with students and parents about AI tool use is both an ethical and a legal obligation in most jurisdictions."
    },
    {
        "text": "Could a student without home internet access participate equally in tasks that use this tool?",
        "hint": "If the tool is used for homework or assessed tasks, consider whether all students have equal access."
    },
    {
        "text": "Do you feel confident that the tool's outputs are accurate enough to use in your teaching without systematic verification?",
        "hint": "AI tools can produce plausible but incorrect information. If you're not confident in verifying outputs, this is a concern."
    },
]


def get_context():
    """Return M2-specific TAB3 context. Called automatically by views.py."""
    return {
        'scenario': M2_SCENARIO,
        'principles': M2_PRINCIPLES,
        'audit_tools': M2_AUDIT_TOOLS,
        'audit_questions': M2_AUDIT_QUESTIONS,
    }
