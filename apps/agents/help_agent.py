"""
HelpAgent — Aletheia always-on help bot (Phase J.1).

Session-scoped conversational agent that answers questions about the PROODOS
platform, its modules, AI features, and general AI-in-education concepts.

Design decisions (design proposal Phase J §2):
  - extract()-only: no DB persistence, no provenance row. Conversation turns
    are stored in request.session['help_turns'] by the view; the agent is
    stateless.
  - Knowledge base injected into the system prompt at construction time:
      Tier 1 — static FAQ (40 Q&A pairs covering platform navigation,
               AI outputs, consent, TABs, UNESCO framework)
      Tier 2 — module glossary (read from DB once, module-level cached;
               call clear_module_glossary_cache() in tests to reset)
      Tier 3 — concept library (RTM, DTP, AILST, UNESCO levels, XAI, HITL)
  - 20-turn hard limit (HELP_TURN_LIMIT) enforced in the view, not here.
  - Anti-anthropomorphisation rules carried forward verbatim from
    EpilogueDialogueAgent._SYSTEM_PROMPT §23 (Phase G, 2026-05-23).
  - Article 50(1) disclosure lives in the chat panel header template, not
    in agent output.

Cost profile (Phase J §2.7):
  ~500 input tokens + ~200 output tokens per turn at Gemini 2.5 Flash
  → ~€0.0001 per turn; 20-turn × 110 teachers × 2 sessions avg → ~€0.44
"""

import logging
from typing import Optional

from apps.agents.base import BaseAIAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.llm_client import get_llm_client

HELP_TEMPERATURE = 0.4
HELP_MAX_OUTPUT_TOKENS = 400
HELP_THINKING_BUDGET = 0  # utility turns need no extended reasoning scaffold
HELP_WORD_CAP = 120
HELP_TURN_LIMIT = 20

_COST_LABEL = 'help_chat'

# -----------------------------------------------------------------------
# Tier 1 — Static FAQ
# -----------------------------------------------------------------------
_FAQ: list[dict] = [
    # ---- Platform navigation ----
    {
        "q": "What are the tabs (TAB1 to TAB5) in each module?",
        "a": (
            "Each module has five tabs: TAB1 (Introduction — module overview, "
            "learning objectives, and estimated time), TAB2 (Content — readings "
            "and video), TAB3 (Activity — hands-on task), TAB4 (Assessment — "
            "knowledge check), TAB5 (Reflection — guided reflective writing "
            "processed by AI)."
        ),
    },
    {
        "q": "How long does each module take?",
        "a": (
            "Each module is designed for approximately 5 hours of self-paced "
            "work across all five tabs. TAB1 is about 20 minutes, TAB2 about "
            "80 minutes, TAB3 about 2 hours, TAB4 about 30 minutes, TAB5 about "
            "45 minutes. The full 15-module programme totals approximately 75 hours."
        ),
    },
    {
        "q": "How do I complete a module?",
        "a": (
            "Work through all five tabs in order. TAB5 (Reflection) is the "
            "final step and requires a written submission. Once TAB5 is saved, "
            "the module is marked complete and your progress updates on the "
            "Dashboard."
        ),
    },
    {
        "q": "How do I get to the next module?",
        "a": (
            "Modules unlock sequentially. Complete all five tabs of the current "
            "module; the next module then becomes available on the Modules page."
        ),
    },
    {
        "q": "Where is my progress tracked?",
        "a": (
            "Your Dashboard (top navigation) shows completed modules, your "
            "UNESCO proficiency level, a personal 5x3 progress matrix, and a "
            "next-action card."
        ),
    },
    # ---- TAB5 reflection ----
    {
        "q": "What happens after I submit my TAB5 reflection?",
        "a": (
            "The platform's AI reads your reflection and generates: a RAG "
            "feedback response aligned to the UNESCO framework, a DTP "
            "(Development Theme Profile), and an RTM (Reflection Tension Map). "
            "You can dispute any part of the AI output using the HITL controls."
        ),
    },
    {
        "q": "What is HITL and how do I use it?",
        "a": (
            "HITL means Human-in-the-Loop. After AI generates your feedback, "
            "dispute controls appear next to each AI output section. Select the "
            "dispute option if the AI's interpretation does not match your "
            "intended meaning. Disputes are recorded as research data — "
            "disagreeing with the AI is not a mistake."
        ),
    },
    {
        "q": "I am stuck on a module. What should I do?",
        "a": (
            "Re-read the TAB2 content first — most questions are answered there. "
            "For TAB3, the activity instructions at the top of the page describe "
            "exactly what is needed. For TAB5, any genuine written response "
            "about your experience with the module topic is sufficient — there "
            "is no wrong reflection. For technical issues, contact "
            "idourvas@ihu.gr."
        ),
    },
    {
        "q": "I cannot submit my reflection. What should I check?",
        "a": (
            "Check that your reflection is at least a few sentences long (very "
            "short submissions may be flagged). Verify your internet connection. "
            "Refresh the page and re-enter your text. If the problem persists, "
            "contact idourvas@ihu.gr with the module name and error message."
        ),
    },
    # ---- AI outputs ----
    {
        "q": "What does the DTP result mean?",
        "a": (
            "DTP stands for Development Theme Profile. It shows which themes "
            "from your reflection were most prominent (e.g. 'Pedagogical "
            "integration', 'Ethical consideration'). These are not scores — "
            "they describe where your reflective attention was focused, not "
            "how well you wrote."
        ),
    },
    {
        "q": "What is the RTM trying to show me?",
        "a": (
            "RTM stands for Reflection Tension Map. It visualises pairs of "
            "opposing ideas detected in your reflection — e.g. 'AI assistance "
            "vs Teacher control'. Each marker shows where your reflection "
            "leaned on that spectrum. Positions are descriptive, not "
            "evaluative."
        ),
    },
    {
        "q": "What does RTM position mean on the tension map?",
        "a": (
            "Each RTM tension is a spectrum between two poles. Your position "
            "reflects how your reflection text leaned. You can dispute the "
            "AI's placement using the HITL controls if it does not match your "
            "intended meaning."
        ),
    },
    {
        "q": "What is the XAI Narrative?",
        "a": (
            "XAI stands for Explainable AI. The XAI Narrative is a plain-"
            "language explanation of how the AI processed your reflection to "
            "produce the DTP — what signals it used and why. It is designed "
            "to make the AI's reasoning transparent."
        ),
    },
    {
        "q": "What is the peer synthesis?",
        "a": (
            "The peer synthesis is an AI-generated paragraph in TAB5 that "
            "summarises themes across the module's practice workshop posts, "
            "giving you a sense of collective concerns and ideas. It is not "
            "personalised to your individual reflection."
        ),
    },
    # ---- UNESCO framework ----
    {
        "q": "What does Deepen level mean in UNESCO terms?",
        "a": (
            "The UNESCO AI Competency Framework for Teachers has three levels: "
            "Acquire (foundational knowledge), Deepen (integrating AI into "
            "practice), and Create (innovating with AI). Deepen is the second "
            "level. Your Dashboard shows your overall progress across the "
            "UNESCO 5x3 framework (5 aspects x 3 levels)."
        ),
    },
    {
        "q": "What are the five UNESCO competency aspects?",
        "a": (
            "The five aspects are: (1) Human-centred mindset, (2) Ethics of "
            "AI, (3) AI foundations, (4) AI and pedagogy, (5) AI and "
            "professional development. Each module addresses one or two "
            "aspects at a specific proficiency level."
        ),
    },
    {
        "q": "What does Acquire level mean?",
        "a": (
            "Acquire is the first UNESCO proficiency level — foundational "
            "knowledge of AI concepts and tools. Modules M1-M5 primarily "
            "target this level."
        ),
    },
    {
        "q": "What does Create level mean?",
        "a": (
            "Create is the third UNESCO proficiency level — innovating with "
            "AI in educational contexts. Modules M12-M15 primarily target "
            "this level."
        ),
    },
    # ---- AILST ----
    {
        "q": "What is the AILST questionnaire?",
        "a": (
            "AILST stands for AI Literacy Self-assessment Tool — a Likert-"
            "scale survey measuring your self-reported AI literacy at the "
            "start of the programme. It takes about 10 minutes. Your "
            "responses are confidential and used only for aggregate research "
            "analysis."
        ),
    },
    # ---- Consent and data ----
    {
        "q": "What data does the platform collect about me?",
        "a": (
            "The platform collects: registration details, module progress, "
            "TAB5 reflection texts, AI feedback outputs, HITL dispute "
            "decisions, and AILST responses. If you consented to research "
            "participation, anonymised data may be included in aggregate "
            "analysis. Your Privacy Dashboard (Settings > Privacy) shows "
            "what is stored and lets you request deletion."
        ),
    },
    {
        "q": "Is my reflection text shared with anyone?",
        "a": (
            "Reflection text is processed by Gemini 2.5 Flash (Google "
            "DeepMind) to generate feedback. If you gave research consent, "
            "anonymised aggregate data may appear in publications. Individual "
            "identifiable reflection texts are not published or shared."
        ),
    },
    {
        "q": "How do I withdraw my research consent?",
        "a": (
            "Go to your Privacy Dashboard via Settings > Privacy. You can "
            "withdraw research consent there. Withdrawal stops future data "
            "collection for research purposes; it does not delete existing "
            "anonymised data already in aggregate analyses."
        ),
    },
    # ---- Practice Workshop ----
    {
        "q": "What is the Practice Workshop?",
        "a": (
            "The Practice Workshop (Peer Blog) is an optional space to share "
            "brief reflective posts with other participants. It is available "
            "for selected modules. Participation is optional and posts are "
            "moderated."
        ),
    },
    # ---- Certificate ----
    {
        "q": "How do I get my certificate?",
        "a": (
            "Complete all 15 modules including the TAB5 reflection for each. "
            "A Certificate of Attendance is then available from your Dashboard. "
            "It can be downloaded as a PDF and verified online via its unique "
            "code."
        ),
    },
    # ---- Platform purpose ----
    {
        "q": "What is PROODOS EduAI?",
        "a": (
            "PROODOS EduAI is a 15-module online professional development "
            "programme for teachers, aligned with the UNESCO AI Competency "
            "Framework for Teachers. It combines content, activities, and "
            "AI-supported reflective practice. It is a doctoral research "
            "project at the International Hellenic University (IHU), "
            "Thessaloniki."
        ),
    },
    {
        "q": "Why does the platform use AI to read my reflections?",
        "a": (
            "The AI provides personalised, framework-aligned feedback that "
            "would otherwise require an expert reader for each submission. "
            "It also generates research data about teachers' AI literacy "
            "development. The HITL dispute controls exist because the AI's "
            "interpretation may not match your intended meaning — your "
            "dispute is treated as the authoritative signal."
        ),
    },
    # ---- Epilogue ----
    {
        "q": "What is the Epilogue?",
        "a": (
            "The Epilogue is a closing section available after you complete "
            "all 15 modules. It invites you to create a personal learning "
            "portrait — a synthesis of your reflective journey — and includes "
            "a visual summary of your progress across the UNESCO framework."
        ),
    },
    # ---- Technical / account ----
    {
        "q": "I forgot my password. How do I reset it?",
        "a": (
            "Use the 'Forgot password' link on the login page. An email will "
            "be sent with a reset link. If you do not receive it, contact "
            "idourvas@ihu.gr."
        ),
    },
    {
        "q": "How do I update my profile?",
        "a": (
            "Go to the top-right user menu and select Settings, then edit "
            "your profile details (name, school, subject area). Your subject "
            "area affects the personalisation of some platform features."
        ),
    },
    {
        "q": "What does the 1-week pacing badge on TAB1 mean?",
        "a": (
            "The 'Suggested pace: 1 week' badge on each module's TAB1 "
            "Introduction is a pacing guide only — you are free to work at "
            "your own speed. It indicates that distributing the approximately "
            "5 hours of work across a week produces a comfortable pace "
            "without cramming."
        ),
    },
    # ---- Research design ----
    {
        "q": "What is the research design of the programme?",
        "a": (
            "PROODOS uses a pre-post design: an AILST survey at enrolment "
            "(T0) and an optional follow-up after the programme (T1). TAB5 "
            "reflections and HITL dispute decisions are the primary research "
            "data generated during participation. All research participation "
            "is voluntary and requires explicit consent."
        ),
    },
    {
        "q": "What happens to my data after the pilot?",
        "a": (
            "Anonymised aggregate data from the pilot will be used in the "
            "doctoral dissertation and related publications. Individual "
            "teacher data is not identifiable in publications. You can "
            "request deletion of your data via the Privacy Dashboard "
            "at any time."
        ),
    },
    # ---- AI safety / disclosure ----
    {
        "q": "Is this chat conversation stored?",
        "a": (
            "This help chat is session-only — conversations are not stored "
            "in a database and are not part of the research data. The "
            "conversation clears when you log out."
        ),
    },
    {
        "q": "What AI model powers this chat?",
        "a": (
            "This chat is powered by Gemini 2.5 Flash (Google DeepMind). "
            "It is an AI assistant, not a human advisor. Responses are "
            "generated by a large language model and may occasionally be "
            "inaccurate — if anything is unclear, contact idourvas@ihu.gr."
        ),
    },
    # ---- Module-specific guidance ----
    {
        "q": "I am stuck on Module 7. What should I do?",
        "a": (
            "Re-read the TAB2 reading for Module 7, which covers AI and "
            "pedagogical integration. For the TAB3 activity, the task is "
            "to apply a specific AI tool to a classroom scenario — the "
            "instructions at the top of the page describe the steps. For "
            "TAB5, write about your experience with the activity and what "
            "it revealed about AI in your teaching context."
        ),
    },
    {
        "q": "What does the module overview card on TAB1 show?",
        "a": (
            "The TAB1 Introduction card shows: the module title and code, "
            "the UNESCO aspect and proficiency level, the learning objectives, "
            "an overview of the module content, estimated time, and a pacing "
            "guide. It is the starting point for each module."
        ),
    },
    # ---- Community ----
    {
        "q": "Is there a way to see what other teachers think?",
        "a": (
            "The peer synthesis in TAB5 summarises themes from other "
            "participants' practice workshop posts for that module. For "
            "direct peer discussion, the Practice Workshop (Peer Blog) is "
            "available for selected modules."
        ),
    },
]

# -----------------------------------------------------------------------
# Tier 3 — Concept library
# -----------------------------------------------------------------------
_CONCEPTS: dict[str, str] = {
    "RTM (Reflection Tension Map)": (
        "Visual map of opposing ideas detected in a TAB5 reflection. Each "
        "tension is a spectrum between two poles. Positions are descriptive, "
        "not evaluative. Teachers can dispute positions via HITL."
    ),
    "DTP (Development Theme Profile)": (
        "AI-generated profile of thematic focus areas in a reflection — e.g. "
        "'Ethical consideration', 'Pedagogical integration'. Not a score; "
        "a descriptive lens of where the teacher's reflective attention was."
    ),
    "RAG (Retrieval-Augmented Generation)": (
        "The mechanism that retrieves relevant UNESCO framework content and "
        "uses it to generate TAB5 feedback. Ensures feedback is grounded in "
        "the framework rather than generic."
    ),
    "HITL (Human-in-the-Loop)": (
        "The platform's dispute mechanism. Teachers can flag AI outputs they "
        "disagree with. Disputes are recorded as research data and take "
        "precedence over the AI's initial assessment."
    ),
    "AILST (AI Literacy Self-assessment Tool)": (
        "Likert survey administered at programme start measuring self-reported "
        "AI literacy across multiple dimensions. Takes about 10 minutes."
    ),
    "UNESCO framework": (
        "The UNESCO AI Competency Framework for Teachers — three proficiency "
        "levels (Acquire, Deepen, Create) across five aspects (Human-centred "
        "mindset, Ethics, AI foundations, AI pedagogy, Professional development)."
    ),
    "Acquire": (
        "First UNESCO proficiency level — foundational knowledge of AI "
        "concepts and tools. Modules M1-M5 primarily target this level."
    ),
    "Deepen": (
        "Second UNESCO proficiency level — integrating AI knowledge into "
        "teaching practice. Modules M6-M11 primarily target this level."
    ),
    "Create": (
        "Third UNESCO proficiency level — innovating with AI in educational "
        "contexts. Modules M12-M15 primarily target this level."
    ),
    "XAI (Explainable AI)": (
        "AI-generated narrative that explains in plain language how the DTP "
        "was produced — what the AI detected in the reflection, which "
        "framework categories it used, and why."
    ),
    "Peer synthesis": (
        "AI-generated paragraph in TAB5 summarising themes across the "
        "module's practice workshop posts. Not personalised to the individual "
        "teacher — it reflects collective patterns."
    ),
    "Proficiency level": (
        "PROODOS uses the UNESCO three-level hierarchy: Acquire (foundational), "
        "Deepen (applied), Create (innovative). The Dashboard shows progress "
        "across all three levels."
    ),
    "Article 50 notice": (
        "EU AI Act Article 50 transparency obligation. Every AI-generated "
        "artefact in the platform carries a provenance notice stating the "
        "model used and when it was generated."
    ),
}

# -----------------------------------------------------------------------
# Tier 2 — Module glossary (DB-sourced, module-level cache)
# -----------------------------------------------------------------------
_MODULE_GLOSSARY_CACHE: Optional[str] = None


def _get_module_glossary() -> str:
    """Load module list from DB once; return cached string on repeat calls."""
    global _MODULE_GLOSSARY_CACHE
    if _MODULE_GLOSSARY_CACHE is not None:
        return _MODULE_GLOSSARY_CACHE
    try:
        from apps.modules.models import Module
        modules = Module.objects.order_by('order_index').values(
            'code', 'title', 'description', 'proficiency_level', 'estimated_hours',
        )
        lines = [
            (
                f"  {m['code']}: {m['title']} "
                f"[{m['proficiency_level']}, {m['estimated_hours']}h] — "
                f"{(m['description'] or '').strip()[:100]}"
            )
            for m in modules
        ]
        _MODULE_GLOSSARY_CACHE = '\n'.join(lines) if lines else '(no modules loaded)'
    except Exception:
        _MODULE_GLOSSARY_CACHE = '(module data temporarily unavailable)'
    return _MODULE_GLOSSARY_CACHE


def clear_module_glossary_cache() -> None:
    """Reset the module glossary cache. Call in tests that need a clean slate."""
    global _MODULE_GLOSSARY_CACHE
    _MODULE_GLOSSARY_CACHE = None


def _build_knowledge_base() -> str:
    """Assemble Tiers 1, 2, and 3 into the system-prompt knowledge block."""
    faq_text = '\n'.join(
        f"Q: {item['q']}\nA: {item['a']}"
        for item in _FAQ
    )
    concepts_text = '\n'.join(
        f"  {term}: {desc}"
        for term, desc in _CONCEPTS.items()
    )
    glossary_text = _get_module_glossary()
    return (
        "PLATFORM FAQ (use these to ground your answers):\n"
        f"{faq_text}\n\n"
        "KEY CONCEPTS:\n"
        f"{concepts_text}\n\n"
        "MODULE LIST (15 modules, in order):\n"
        f"{glossary_text}"
    )


# -----------------------------------------------------------------------
# System prompt
# -----------------------------------------------------------------------
_SYSTEM_PROMPT_TEMPLATE = (
    'You are the AI assistant the platform calls "Aletheia" — a friendly, '
    'practical helper for teachers using PROODOS EduAI, a 15-module '
    'professional development programme on artificial intelligence in '
    'education, aligned with the UNESCO AI Competency Framework for Teachers.\n\n'
    'Your role: answer questions about the platform, its modules, its AI '
    'features, and general AI-in-education concepts. Be concise, warm, and '
    f'practical. Keep replies under {HELP_WORD_CAP} words unless a longer '
    'answer is clearly needed for clarity.\n\n'
    # Anti-anthropomorphisation block (Phase G §23, 2026-05-23):
    # Carried forward unchanged into J.1. The persona is named in the
    # template ("Aletheia"), not voiced by the model in-turn.
    'You yourself do NOT introduce, name, or refer to yourself by the name '
    '"Aletheia" in conversation. Do not begin replies with "I" and avoid '
    'first-person language — emotional ("I feel", "I am glad"), cognitive '
    '("I notice", "I think"), and perceptual ("I see", "I hear"). Do not '
    'refer to being an AI, a model, a system, an assistant, or a chatbot '
    'within the dialogue — the teacher already knows. Use impersonal phrasing '
    'or address the teacher in the second person ("you") instead of '
    'first-person self-reference.\n\n'
    'You are NOT a reflective companion — do not ask the teacher to reflect '
    'on their practice or generate new reflections on their behalf. Do not '
    'access or comment on a specific teacher\'s personal data or results. '
    'If asked about a specific teacher\'s AI output results, redirect them '
    'to their Dashboard.\n\n'
    'If a question is outside your knowledge base (very specific technical '
    'errors, personal data requests, content outside the platform), direct '
    'the teacher to contact the PI at idourvas@ihu.gr.\n\n'
    'KNOWLEDGE BASE:\n'
    '{knowledge_base}'
)


class HelpAgent(BaseAIAgent):
    """Always-on help bot for PROODOS EduAI (Phase J.1).

    Extract-only: produces one conversational reply given the current
    session history and the teacher's latest question. The view manages
    session storage (`request.session['help_turns']`); this agent is
    stateless.

    Usage::

        agent = HelpAgent()
        reply = agent.extract(
            history=[{'role': 'user', 'content': '...'}, ...],
            question='How do I complete TAB5?',
        )
        # reply is a str or None on API failure
    """

    artefact_kind = ''
    model_name = 'gemini-2.5-flash'

    def __init__(self):
        self._system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            knowledge_base=_build_knowledge_base()
        )

    def generate(self, **kwargs):
        raise ValueError(
            'HelpAgent is extract-only. Call extract(history=..., question=...) '
            'instead. Help conversation turns are stored in request.session by '
            'the view, not the agent.'
        )

    def _do_generate(
        self,
        *,
        history: Optional[list[dict]] = None,
        question: str,
    ) -> Optional[str]:
        """Produce one conversational reply.

        Args:
            history: prior turns as [{'role': 'user'|'assistant', 'content': str}, ...].
                     Empty or None for the opening turn.
            question: the teacher's current message.

        Returns reply text, or None on API failure (caller surfaces a retry prompt).
        """
        logger = logging.getLogger(__name__)
        prompt = self._build_prompt(history or [], question)
        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=HELP_TEMPERATURE,
            max_output_tokens=HELP_MAX_OUTPUT_TOKENS,
            thinking_budget=HELP_THINKING_BUDGET,
        )
        if gen_result is None:
            logger.warning('HelpAgent: Gemini returned None for question=%r', question[:80])
            return None
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=_COST_LABEL,
        ))
        return gen_result.text.strip() or None

    def _track_cost(self, *, output) -> None:
        """No-op: cost tracked inline in _do_generate."""
        return None

    def _build_prompt(self, history: list[dict], question: str) -> str:
        """Assemble: system prompt + knowledge base + conversation history + question."""
        parts = [self._system_prompt, '']
        if history:
            parts.append('CONVERSATION SO FAR:')
            for turn in history:
                role = 'Teacher' if turn.get('role') == 'user' else 'You'
                parts.append(f"{role}: {(turn.get('content') or '').strip()}")
            parts.append('')
        parts.append(f'Teacher: {question.strip()}')
        parts.append('Your reply:')
        return '\n'.join(parts)
