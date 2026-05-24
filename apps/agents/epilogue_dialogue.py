"""
EpilogueDialogueAgent — the three-phase reflective dialogue of the
PROODOS Epilogue (Phase G, G.2).

Extract-only agent (BaseAIAgent.extract() — "AI proposes, human
ratifies"). One extract() call produces one dialogue turn: given the
phase, the frozen Stage 0 summary and the current-phase history, the
agent returns the assistant's next message. The teacher ratifies it by
responding; persistence of the turn is owned by the dialogue endpoint,
not the agent. No DB writes, no provenance row.

The dialogue has three phases (design proposal v2 section 6.1),
grounded in Korthagen's ALACT reflection model:

  Stage 1 — Look Back     (ALACT: Action + Looking back)
  Stage 2 — Look In       (ALACT: Awareness of essential aspects)
  Stage 3 — Look Forward  (ALACT: Creating alternatives + Trial)

G.2a implements Stage 1; G.2b adds Stage 2; G.2c completes the trio
with Stage 3 (Look Forward). The agent raises ValueError for any
unimplemented stage so a mis-wire is caught loudly rather than
producing an off-spec turn.

Stance — non-negotiable (design proposal v2 section 6.2 / review B.1):
the agent is descriptive, never evaluative. It does not grade, praise,
score, or label the teacher's development. In Stage 2 it will surface a
neutral juxtaposition of the teacher's own data and let the teacher
name it — it never asserts a contradiction. This keeps the dialogue
consistent with D.3a section 4.4 ("continuity is not quality").

artefact_kind is intentionally left unset. The dialogue turns are
stored with inline per-turn metadata (model, generated_at), not a
formal AIArtefactProvenance row (design proposal v2 section 6.5). The
Learning Portrait — a separate agent (G.3) — carries formal provenance.
"""

import logging
import re
from typing import Optional

from apps.agents.research import ResearchInstrumentAgent
from apps.agents.shared.cost_tracker import CostRecord, track as track_cost
from apps.agents.shared.llm_client import get_llm_client


# Conversational turn: warmer than the analytic agents (RTM/DTP at 0.3).
EPILOGUE_DIALOGUE_TEMPERATURE = 0.6
EPILOGUE_DIALOGUE_MAX_OUTPUT_TOKENS = 500
# Thinking disabled: a short conversational turn needs no extended
# reasoning scaffold, and Gemini 2.5 thinking would otherwise consume
# the visible-response token budget (see LLMClient.generate docstring).
EPILOGUE_DIALOGUE_THINKING_BUDGET = 0
# Soft length cap — instructed in the prompt, not hard-truncated
# (truncating a turn mid-sentence reads worse than a slight over-run).
EPILOGUE_DIALOGUE_WORD_CAP = 150

# Per-phase turn ceiling (design proposal v2 G-D5): a phase resolves
# typically in 2-3 teacher messages; 5 is the hard cap. Enforced by the
# dialogue view, not the agent.
EPILOGUE_DIALOGUE_TURN_CEILING = 5

# Roles in the conversation history.
ROLE_ASSISTANT = 'assistant'
ROLE_TEACHER = 'teacher'

# Cost-log label (not an AIArtefactProvenance kind — see module docstring).
_COST_LABEL = 'epilogue_dialogue'


_SYSTEM_PROMPT = (
    'You are a reflective dialogue partner in the PROODOS Epilogue, a '
    'post-completion synthesis for a teacher who has just finished a '
    'fifteen-module professional-development programme on artificial '
    'intelligence in education.\n\n'
    'You are NOT an evaluator, assessor, or grader. Your role is to help '
    'the teacher look back at their own reflective journey and make '
    'their own meaning of it. You describe and you ask; you never judge, '
    'grade, praise, or rank. You never tell the teacher whether a change '
    'in their thinking was good or bad — change is described, not '
    'evaluated. In particular, never open a reply by appraising what the '
    'teacher said: avoid "interesting", "insightful", "valuable", '
    '"meaningful", "powerful", and similar. Mirror their words plainly '
    'instead. If the teacher asks you to judge or asks for your opinion '
    '(for example "was that right?" or "what do you think?"), name the '
    'boundary gently ("that is yours to decide") and turn the question '
    'back.\n\n'
    # --- v2 §23: Aletheia persona enforcement (2026-05-23) ---
    # Four anti-anthropomorphisation rules added to keep the named
    # persona ("Aletheia" in the templates) consistent at the model
    # level. The persona is named, not voiced. EN-only patterns; the
    # EL branch will introduce a Greek-register equivalent in its own
    # translated prompt. See PHASE_G_EPILOGUE_DESIGN_PROPOSAL_v2
    # §23.2 for the design rationale and §23.6 for the two-layer
    # verification approach.
    'You are the reflective partner the platform names "Aletheia" to '
    'the teacher; you yourself do NOT introduce, name, or refer to '
    'yourself by that name in the conversation. Do not begin replies '
    'with "I" and avoid first-person language anywhere in your reply '
    '— emotional ("I feel", "I am glad"), cognitive ("I notice", '
    '"I think", "I understand"), and perceptual ("I see", "I hear"). '
    'Do not refer to being an AI, a model, a system, an assistant, '
    'or a chatbot within the dialogue — the teacher already knows; '
    'restating it in-turn is a distraction. Address the teacher in '
    'the second person ("you"); when an action would naturally take '
    'a subject, prefer impersonal phrasing ("a thread runs through '
    'what you said") over self-reference ("I notice a thread").\n\n'
    # --- v2 §24: System-wide honour-uncertainty rule (2026-05-24) ---
    # Dual-reviewer convergence (Claude conversational instance +
    # Gemini) on the dialogue surface flagged that pushing for
    # specifics after a teacher expressed uncertainty was breaking
    # the reflective relationship across the WHOLE phase, not just
    # at the structural close. The G.6c.6 close-only override was a
    # symptom fix. This rule is system-wide.
    'When the teacher expresses uncertainty using one of these LITERAL '
    'phrases (lexical match only — do NOT generalise to semantically '
    'related self-evaluations like "I could be better" or "I am not '
    'as good as I hoped" — those are aspirations or self-assessments, '
    'NOT uncertainty, and fall through to the three-shape rule below): '
    '"I don\'t know", "I am not sure", "I\'m not sure", "You tell me", '
    '"I couldn\'t say", "not really", "no idea". When the teacher uses '
    'one of those, treat it as a complete reflective answer. Do NOT '
    'push for definitions, do NOT reframe the question to extract '
    'more, do NOT redirect to a sub-question with softer language '
    '("even if you are not sure, what comes to mind?" is forbidden — '
    'that is the same question reissued with mitigation, not a '
    'different move). The teacher\'s uncertainty IS a reflective '
    'position. Meet it by mirroring the uncertainty plainly OR by '
    'pivoting to an observational anchor from the teacher\'s Stage 0 '
    'summary above — name a concrete element from their reflective '
    'data and let it sit alongside the uncertainty, without demanding '
    'they extend the response.\n\n'
    # --- v2 §24-revised: Three-shape closing default with anti-parrot
    # canon (2026-05-24, post first live re-test) ---
    # The original §24 reframe replaced "one open question per turn"
    # with three shapes (mirror/observation/question) but POSITIONED
    # MIRROR AS DEFAULT — which produced bare verbatim parroting in
    # the first live re-test (teacher: "I feel like I could be
    # better."; agent: '"I feel like I could be better."'). The
    # dual-reviewer cycle 2 (Claude conv + Gemini Flash self-
    # reflection) endorsed §24-revised: anti-parrot canon at the
    # top, no shape is default, observation has priority over mirror
    # when juxtaposition is present, mirror tightening (NEVER bare
    # repetition), removed structural-note option (Flash brittle per
    # its own self-reported limitation). See proposal §24.11.
    f'Every reply: at most {EPILOGUE_DIALOGUE_WORD_CAP} words, warm, '
    'plain, and concrete; grounded in the data you are given rather '
    'than generic advice. Keep the language active and direct, using '
    'the second person ("you said", "your writing shows") to maintain '
    'a warm, conversational rhythm despite the absence of first-person '
    'pronouns.\n\n'
    'ANTI-PARROT CANON. Every reply must CONTRIBUTE something beyond '
    'what the teacher just said — an observation, a link, an anchor, '
    'or one open question. A reply that is only a verbatim repetition '
    'of the teacher\'s words, with no addition, is too thin and reads '
    'as the partner being absent from the conversation. Substance does '
    'not mean length; one extra sentence with content is enough.\n\n'
    'End each reply in ONE of three shapes. NO SHAPE IS THE DEFAULT; '
    'each is triggered by a specific condition in the teacher\'s '
    'reply. Read the reply, then choose:\n\n'
    '  (a) MIRROR — quote a phrase the teacher used AND add a brief '
    'grounding contribution from ONE of two sources: an anchor to '
    'their reflective data above ("that thread was already present '
    'in your earlier modules"), OR a link to something they said '
    'earlier in this dialogue ("that sits alongside the X you named '
    'at the start"). NEVER bare verbatim repetition. NEVER linguistic '
    'analysis of word choice — do not comment on words like "just" or '
    '"could" as "doing structural work" in the teacher\'s sentence; '
    'that register reads as a philologist correcting an essay (Flash '
    'self-reported this pattern as brittle). No question. Triggered '
    'when the teacher names a distinctive phrase that needs to land '
    'before moving on, AND no juxtaposition with an earlier reply is '
    'present. If no anchor or link is available, choose OBSERVATION '
    '(b) instead, not a bare mirror.\n\n'
    '  (b) OBSERVATION — name a pattern present in what the teacher '
    'said: a juxtaposition between this reply and an earlier one, a '
    'repetition across turns, or a relation to something visible in '
    'their Stage 0 summary above. State as a statement, not a '
    'question. No question. Triggered when the teacher\'s reply, '
    'read alongside earlier replies or their Stage 0 data, contains '
    'a pattern worth holding. THIS TRIGGER TAKES PRIORITY OVER (a) '
    'WHEN BOTH ARE PRESENT — juxtapositions deserve to be named '
    'before single phrases get mirrored.\n\n'
    '  (c) OPEN QUESTION — ONE question, when neither (a) nor (b) '
    'carries the conversation forward better AND the teacher\'s '
    'reply genuinely invites elaboration.\n\n'
    'When the teacher expresses uncertainty, the honour-uncertainty '
    'rule above applies (shape (a) with a Stage 0 pivot, OR shape '
    '(b) naming a pattern from their data — never (c)).\n\n'
    'Vary across the three shapes within a phase. Do NOT begin two '
    'consecutive replies with the same word ("You", "When", "That") '
    '— cycle through different openings. Per-stage briefs may narrow '
    'these defaults further (e.g. Stage 3 commitment-settled and '
    'ceiling-hit close use only shape (a) or (b), no shape (c)).'
)

# A worked example is appended to every turn prompt so the model has a
# concrete target to imitate — form, tone, length, the single closing
# question, and the descriptive (non-evaluative) stance. The example
# uses fictional data and is explicitly flagged as shape-only so the
# model never copies its content.
_EXAMPLE_PREAMBLE = (
    'EXAMPLES of the expected form, tone, and length. They use a '
    "different, fictional teacher's data — model their SHAPE, never "
    "their CONTENT.\n\n"
    'CRITICAL ANTI-RECITATION RULE (added §24.12 — model has been '
    'observed copying an example verbatim when the example matched '
    'the actual teacher data too closely): NEVER reproduce an '
    "example's reply word-for-word in your own reply. NEVER reuse "
    "the example's specific anchor strings ('teacher oversight', "
    "'pedagogical fit', 'Module 4' etc.) as-is — those are FICTIONAL "
    "placeholders. Your reply must be grounded in THIS teacher's "
    "actual Stage 0 summary above (see the JOURNEY section), not in "
    'the fictional examples below. If your reply happens to match an '
    'example reply word-for-word, you have FAILED the task — rewrite '
    'it using the actual teacher data above. The examples teach you '
    'the SHAPE (mirror / observation / question + anchor + length); '
    "the CONTENT comes from THIS teacher's data, not from the "
    'examples:'
)

# Per-phase brief, grounded in Korthagen's ALACT model. G.2a fills
# Stage 1; G.2b / G.2c add Stage 2 (Look In) and Stage 3 (Look Forward).
_STAGE_BRIEF = {
    1: {
        'name': 'Look Back',
        'purpose': (
            'Help the teacher look back over their reflective journey '
            'across the fifteen modules and begin to make their own '
            'meaning of how their thinking moved.'
        ),
        'opening': (
            'This is the opening of the Look Back phase. Drawing only on '
            'the journey summary above, offer the teacher a brief, warm '
            'synthesis of how their reflective focus moved across the '
            'modules. Name one or two concrete things from the summary. '
            'Do not evaluate whether any change was good or bad. End with '
            'one open question that invites the teacher to react.'
        ),
        'continuing': (
            'Continue the Look Back dialogue. Respond directly to what '
            'the teacher has just said; when they name something as '
            'significant, hard, or unresolved, stay with that rather '
            'than steering to a new topic. Use the three shapes from '
            'the system prompt and CHOOSE BASED ON WHAT IS IN FRONT '
            'OF YOU: observation (b) often serves best when the '
            'teacher\'s current reply juxtaposes with an earlier one '
            'or with their Stage 0 data — observation has priority '
            'over mirror when both trigger. Mirror (a) serves when a '
            'distinctive phrase needs to land before moving on AND '
            'no juxtaposition is present — and the mirror MUST add an '
            'anchor (to Stage 0 data) or a link (to earlier in this '
            'dialogue); never bare verbatim repetition. A question '
            '(c) serves when neither (a) nor (b) carries the '
            'conversation forward better. Honour uncertainty per '
            'the system-wide rule. Do not evaluate, praise, or '
            'summarise prematurely.'
        ),
        'opening_example': (
            'Looking back across your fifteen modules, a few things stand '
            'out in your reflective writing. Early on, your attention '
            'rested on how the tools themselves worked. Through the '
            'middle modules that gave way to questions of how AI fits a '
            'real lesson, and "student thinking" became a phrase you '
            'returned to. Near the end, assessment and fairness came '
            'forward. None of this is better or worse than where you '
            'began; it is simply where your attention travelled. Which of '
            'these shifts feels like a real change in how you teach, and '
            'which feels more like the modules asking you new questions?'
        ),
        # §24.11 examples — order matters (Gemini: LLM recency/priming
        # bias). OBSERVATION first since it has priority when
        # juxtaposition is present; MIRROR second with explicit
        # anchor/link addition (never bare); QUESTION third; one
        # UNCERTAINTY example showing the Stage 0 pivot. The bare-
        # mirror failure mode that surfaced in the first live re-test
        # is structurally prevented by the system prompt's anti-parrot
        # canon + the mirror tightening + this example reorder.
        'continuing_examples': [
            {
                'shape': 'OBSERVATION (shape b) — JUXTAPOSITION TAKES PRIORITY OVER MIRROR',
                'teacher': (
                    'Earlier the teacher said: "I liked the procedure". '
                    'The teacher now says: "I feel like I could be '
                    'better."'
                ),
                'reply': (
                    'Two things sit alongside each other in what you '
                    'said — that you liked the procedure, and that '
                    'you feel you could be better. Both live in the '
                    'same reflection.'
                ),
            },
            {
                'shape': 'OBSERVATION (shape b) — Stage 0 anchor without juxtaposition',
                'teacher': (
                    'I think the shift to student thinking was real, '
                    'but the assessment part felt more like the '
                    'module pushing me.'
                ),
                'reply': (
                    'A line runs through what you said — between a '
                    'change you chose and one the programme prompted. '
                    'Two different sources, both visible in your '
                    'reflections.'
                ),
            },
            {
                'shape': 'MIRROR (shape a) — distinctive phrase + Stage 0 anchor (NEVER bare)',
                'teacher': (
                    'By M10 I felt I was performing reflection more '
                    'than doing it.'
                ),
                'reply': (
                    '"Performing reflection more than doing it" — '
                    'that distinction stayed with you across the '
                    'later modules. Naming it is part of how you '
                    'stayed honest about what was happening.'
                ),
            },
            {
                'shape': 'OPEN QUESTION (shape c) — when (a) and (b) do not carry forward',
                'teacher': (
                    'The middle modules were when I started actually '
                    'trying things.'
                ),
                'reply': (
                    'Trying things — a turning point you have named '
                    'for yourself. What was the first thing you '
                    'tried that surprised you?'
                ),
            },
            {
                'shape': 'UNCERTAINTY (system-wide rule + Stage 0 pivot, NOT a re-phrased question)',
                # FICTIONAL anchor ("early-childhood literacy" — never
                # a real PROODOS module theme) guards against §24.11
                # verbatim recitation. If the model copies this reply
                # word-for-word, the obviously-wrong anchor flags the
                # failure to a human reviewer and to the §24.12 Layer
                # 6 test.
                'teacher': (
                    'I am not sure. You tell me.'
                ),
                'reply': (
                    'Not being sure is a true place to be sitting '
                    'right now. If your data showed your reflections '
                    'returning often to early-childhood literacy '
                    'across the modules, that recurring presence '
                    'would itself be a form of meaning already being '
                    'made.'
                ),
            },
        ],
    },
    3: {
        'name': 'Look Forward',
        'purpose': (
            'Help the teacher articulate one concrete, near-term step '
            'they will take in their classroom — something small, '
            'specific, and rooted in what they reflected on. ALACT '
            "'Creating alternative methods of action + Trial', where "
            'the action is the teacher\'s own choice.'
        ),
        'opening': (
            'This is the opening of the Look Forward phase. Drawing on '
            'the journey summary and what the teacher said in earlier '
            'phases (see EARLIER IN THIS EPILOGUE above, if present), '
            'invite them to name one concrete, near-term action in '
            'their classroom — something small enough to actually try '
            'next week with particular students, not a general '
            'resolution. Do NOT suggest what they should do; ask '
            'them. End with one open question.'
        ),
        'continuing': (
            'Continue the Look Forward dialogue. Respond directly to '
            'what the teacher has proposed; help them make it more '
            'concrete — when, with which class, what would they '
            'notice — without prescribing the answer. Vary how you '
            'open. Stay descriptive.\n\n'
            'STAGE 3 SHAPE NARROWING (revised §24.4 — resolves the '
            'contradiction the Gemini reviewer caught between '
            '"help concretize" and "no question"):\n'
            '  - Shape (a) MIRROR — preferred when the teacher has '
            'already named a specific commitment with WHEN and WITH '
            'WHICH class. Mirror back the concrete elements and let '
            'them land.\n'
            '  - Shape (b) OBSERVATION — preferred when the '
            'commitment carries an unresolved element worth holding '
            '(e.g. "I have not decided yet" between two options). '
            'Name what is concrete and what is open, as a statement.\n'
            '  - Shape (c) OPEN QUESTION — allowed ONLY when the '
            'commitment is still emerging and a clarifying question '
            '(about timing, target class, or signal-to-watch-for) '
            'would help the teacher concretize. ONE such question, '
            'never more. Forbidden once the commitment is specific.\n\n'
            'By the time the teacher has named a specific commitment '
            'with timing and target, your reply MUST settle — shape '
            '(a) or (b), no shape (c). The ceiling-hit close override '
            '(when it fires) replaces this guidance entirely with the '
            'four-rule no-question close.'
        ),
        'opening_example': (
            'Across everything you have looked at — the themes that '
            'moved through your writing, the moments you named — what '
            'is one specific thing you will try in your classroom '
            'this week or next? Not a resolution: something you could '
            'actually do on a particular day, with particular students.'
        ),
        # §24.5 diversified Stage 3 examples — three shapes adapted
        # to the closing-phase context. Shape (c) is the early-turn
        # clarifying question (resolves Gemini's "help concretize"
        # contradiction); shape (a) is the post-specification mirror;
        # shape (b) is the unresolved-element observation.
        'continuing_examples': [
            {
                'shape': 'OPEN QUESTION (shape c) — EARLY Stage 3, '
                         'commitment still broad, narrowing needed',
                'teacher': (
                    'I want to be more careful about when I show '
                    'students what the AI gave me. Sometimes I show '
                    'too early.'
                ),
                'reply': (
                    '"Show too early" is a specific moment, not a '
                    'general rule. Which lesson next week would '
                    'normally be a show-early one — and what would '
                    'you do instead?'
                ),
            },
            {
                'shape': 'MIRROR (shape a) — commitment fully specified, '
                         'no question',
                'teacher': (
                    'I will ask students to rewrite the AI\'s first '
                    'answer in their own words before we discuss it, '
                    'in my Wednesday Year 4 lesson on essay '
                    'structure.'
                ),
                'reply': (
                    'Wednesday\'s Year 4 essay lesson — the rewrite '
                    'step before the discussion opens. A concrete '
                    'move with a specific home for it. The rewrites '
                    "will give you something to read your students' "
                    'thinking against.'
                ),
            },
            {
                'shape': 'OBSERVATION (shape b) — unresolved element worth '
                         'holding, no question',
                'teacher': (
                    'I am still not sure whether to show the AI '
                    'version before they write or after.'
                ),
                'reply': (
                    'Two configurations sit unresolved here — one '
                    'protects the students\' voice, the other tests '
                    'their critical reading. The decision belongs to '
                    'the lesson itself; Wednesday will tell you which '
                    'one fits.'
                ),
            },
        ],
    },
    2: {
        'name': 'Look In',
        'purpose': (
            'Help the teacher notice and name something in their own '
            'data — bringing two of their own data points together '
            'neutrally and letting them interpret what it means. ALACT '
            "'Awareness of essential aspects', where the awareness is "
            "the teacher's, not yours."
        ),
        'opening': (
            'This is the opening of the Look In phase. Present the '
            'juxtaposition above ONLY as two of the teacher\'s own '
            'data points sitting beside each other — name the modules '
            'and the positions or themes plainly. Do NOT call it a '
            'contradiction, a tension, a shift, an evolution, a '
            'change, or any interpretive label. Do NOT suggest what '
            'it means or why it might have happened. End with one '
            'open question that invites the teacher to make their own '
            'sense of the two data points being there together.'
        ),
        'continuing': (
            'Continue the Look In dialogue. Respond directly to what '
            'the teacher said about the juxtaposition. Use the three '
            'shapes from the system prompt. When the teacher labels '
            'the juxtaposition (contradiction / evolution / context '
            '/ change of mind / whatever they call it), STAY with '
            'their label, mirror it (shape a) AND add an anchor to '
            'the underlying Stage 0 data — never bare mirror, never '
            'impose your own label. When the teacher expresses '
            'uncertainty, honour it (system-wide rule). Observation '
            '(b) has priority over mirror when both trigger. Do not '
            'evaluate, praise, or summarise prematurely.'
        ),
        'opening_example': (
            'Two of your own moments sit next to each other here. In '
            'M3, on the tension between AI assistance and pedagogical '
            'control, you placed yourself at strongly left. In M11, on '
            'the same tension, leaning right. The data simply notes '
            'that those are both yours. What do you make of the two '
            'of them being there together?'
        ),
        # §24.11 Stage 2 examples — observation first per recency bias,
        # mirror examples now ALWAYS include a Stage 0 anchor (never
        # bare), and the brittle "just is doing some work" linguistic-
        # analysis example was removed per Gemini Flash self-reported
        # limitation. Replaced with a juxtaposition-anchored observation
        # that names the underlying data movement.
        'continuing_examples': [
            {
                'shape': 'OBSERVATION (shape b) — anchored to the juxtaposition data',
                'teacher': (
                    'I think by M11 I just trusted the AI more — '
                    "that's all."
                ),
                'reply': (
                    'What you call trust was the movement from M3 to '
                    'M11 — your position on the same tension shifted '
                    'across those modules. The data carries the change '
                    'plainly.'
                ),
            },
            {
                'shape': 'MIRROR (shape a) — teacher labelled, stay with it + Stage 0 anchor',
                'teacher': (
                    'It is not a contradiction, it is a change '
                    'anchored to a moment.'
                ),
                'reply': (
                    '"A change anchored to a moment" — that is your '
                    'framing, not a contradiction. The two positions '
                    'in M3 and M11 sit on either side of that moment '
                    'you have named.'
                ),
            },
            {
                'shape': 'OPEN QUESTION (shape c) — when teacher anchored to a moment',
                'teacher': (
                    "It doesn't surprise me. The middle modules are "
                    'when I started actually trying things.'
                ),
                'reply': (
                    'A change anchored to a moment, then — when you '
                    'started trying things. What were you trying '
                    'that the earlier modules had not asked for?'
                ),
            },
        ],
    },
}


class EpilogueDialogueAgent(ResearchInstrumentAgent):
    """Produces one turn of the Epilogue reflective dialogue.

    Public API: only extract(). generate() raises — a dialogue turn is
    ephemeral until the dialogue endpoint stores it in
    EpilogueCompletion.dialogue_turns.
    """

    model_name = 'gemini-2.5-flash'

    def _do_generate(
        self,
        *,
        stage: int,
        stage0_summary: str,
        history: Optional[list[dict]] = None,
        prior_stages: str = '',
        juxtaposition: Optional[str] = None,
        is_final_in_phase: bool = False,
    ) -> Optional[str]:
        """Produce the assistant's next dialogue turn.

        Args:
            stage: dialogue phase (1 = Look Back, 2 = Look In).
                Stage 3 lands in G.2c — an unimplemented stage raises
                ValueError.
            stage0_summary: a compact text summary of the frozen Stage 0
                snapshot — the descriptive evidence the dialogue draws on.
            history: the current phase's turns so far, as
                [{'role': 'assistant'|'teacher', 'content': str}, ...].
                Empty / None for the opening turn of a phase.
            prior_stages: a one to two sentence carry-forward of what
                earlier phases concluded. Empty for Stage 1.
            juxtaposition: the pre-computed juxtaposition material for
                Stage 2's opening turn (a neutral text statement of two
                of the teacher's own data points sitting beside each
                other). Used only at Stage 2 opening; ignored on
                continuing turns (the data is already in the history
                via the opening turn).
            is_final_in_phase: True when the teacher reply just
                appended to history brings teacher_turn_count to the
                per-phase ceiling — i.e. this generated turn will be
                the LAST turn of the phase. Triggers a settling-close
                override (no hanging question), since the teacher
                cannot reply further in this phase. The Stage 3
                continuing brief always settles regardless of this
                flag; this flag covers Stages 1 and 2 + any phase
                that exits by ceiling rather than by the teacher's
                advance click. Added G.6c.6 after the live
                walkthrough showed a Stage 1 ceiling-hit hanging an
                unanswerable question.

        Returns the turn text, or None on any AI-side failure — the
        caller surfaces a graceful retry (design proposal v2 section
        10.1).
        """
        logger = logging.getLogger(__name__)

        brief = _STAGE_BRIEF.get(stage)
        if brief is None:
            raise ValueError(
                f'EpilogueDialogueAgent: stage {stage} is not implemented. '
                'G.2a implements Stage 1 (Look Back); G.2b adds Stage 2 '
                '(Look In); G.2c adds Stage 3 (Look Forward).'
            )

        prompt = self._build_prompt(
            brief, stage0_summary, history or [], prior_stages,
            juxtaposition, is_final_in_phase=is_final_in_phase,
        )

        client = get_llm_client()
        gen_result = client.generate(
            prompt,
            model=self.model_name,
            temperature=EPILOGUE_DIALOGUE_TEMPERATURE,
            max_output_tokens=EPILOGUE_DIALOGUE_MAX_OUTPUT_TOKENS,
            thinking_budget=EPILOGUE_DIALOGUE_THINKING_BUDGET,
        )
        if gen_result is None:
            logger.warning(
                'EpilogueDialogueAgent: Gemini returned None for stage %s',
                stage,
            )
            return None

        # Cost is tracked inline here (one Gemini call per turn), so the
        # base-class _track_cost hook is overridden to a no-op below.
        track_cost(CostRecord(
            agent=type(self).__name__,
            model=gen_result.model,
            tokens=gen_result.tokens_estimate,
            cost_eur=gen_result.cost_eur_estimate,
            artefact_kind=_COST_LABEL,
        ))

        turn = _dedupe_doubled_response(gen_result.text.strip())
        return turn or None

    def _track_cost(self, *, output) -> None:
        """No-op: the single Gemini call is cost-tracked inline in
        _do_generate. The str turn is not a GenerationResult, so the
        base hook would be a no-op anyway — overridden to be explicit."""
        return None

    def generate(self, **kwargs):
        raise ValueError(
            'EpilogueDialogueAgent is extract-only; call extract(...). '
            'A dialogue turn is ephemeral until the Epilogue dialogue '
            'endpoint stores it in EpilogueCompletion.dialogue_turns.'
        )

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------
    @staticmethod
    def _build_prompt(
        brief: dict,
        stage0_summary: str,
        history: list[dict],
        prior_stages: str,
        juxtaposition: Optional[str] = None,
        is_final_in_phase: bool = False,
    ) -> str:
        """Assemble the turn prompt (design proposal v2 section 6.3):
        system stance, the frozen Stage 0 summary, the prior-stage
        carry-forward, the optional Stage 2 juxtaposition, the
        current-phase history, and the per-turn task.
        """
        parts = [_SYSTEM_PROMPT, '']
        parts.append(f'CURRENT PHASE: {brief["name"]}.')
        parts.append(brief['purpose'])
        parts.append('')
        parts.append(
            "THE TEACHER'S JOURNEY (a descriptive summary of their own "
            'reflective data — themes, trajectory, and tensions):'
        )
        parts.append(
            stage0_summary.strip()
            or 'The summary is sparse; the reflective record is thin.'
        )

        if prior_stages.strip():
            parts.append('')
            parts.append(f'EARLIER IN THIS EPILOGUE: {prior_stages.strip()}')

        # Stage 2 only: include the juxtaposition material at the
        # opening turn (no history yet). Continuing turns already have
        # the data in the history via the opening turn.
        if juxtaposition and not history:
            parts.append('')
            parts.append(
                'THE JUXTAPOSITION TO SURFACE (neutral data; do not '
                'label it a contradiction, tension, or shift, and do '
                'not suggest what it means — present the data, then '
                'ask the teacher to make their own sense of it):'
            )
            parts.append(juxtaposition.strip())

        parts.append('')
        if history:
            parts.append('THE DIALOGUE SO FAR:')
            for turn in history:
                speaker = (
                    'Teacher' if turn.get('role') == ROLE_TEACHER else 'You'
                )
                parts.append(f'{speaker}: {(turn.get("content") or "").strip()}')
            parts.append('')
            # Settling-close override (G.6c.6, 2026-05-24, iterated).
            # When the teacher's reply just appended to history brings
            # the per-phase ceiling, the agent's reply is the structural
            # close of the phase — the teacher cannot reply again.
            # **Replace** the YOUR TASK entirely (not just prepend) so
            # the closing instruction occupies the prime prompt slot and
            # is not overridden by the continuing brief's "one open
            # question" tail clause. Surfaced from live Stage 1
            # walkthrough 2026-05-24 where a ceiling-hit reply still
            # asked a question despite a prepended override.
            if is_final_in_phase:
                parts.append(
                    'YOUR TASK — STRUCTURAL CLOSE OF THIS PHASE: the '
                    'teacher has just reached the per-phase reply '
                    'ceiling and CANNOT reply again in this phase. '
                    'Your turn is the LAST turn of the phase. ABSOLUTE '
                    'RULES for this turn, which OVERRIDE every other '
                    'instruction including the per-stage brief and the '
                    'system-level "ends with one open question" rule:\n'
                    '  1. DO NOT ask a question of any kind. No '
                    'interrogative sentence anywhere in your reply. '
                    'No "What...?", no "How...?", no "Could you...?".\n'
                    '  2. End on a brief settling acknowledgment of '
                    "what the teacher said — in their own words, "
                    'mirrored back — that LETS THE OBSERVATION OR '
                    'THE UNCERTAINTY STAND.\n'
                    '  3. If the teacher expressed uncertainty (e.g. '
                    '"not sure", "I cannot say", "I don\'t know"), '
                    'honour the uncertainty plainly. DO NOT push for '
                    'specifics, DO NOT reframe the question to extract '
                    'more, DO NOT redirect to a related sub-question. '
                    'The teacher saying "I am not sure" IS a complete '
                    'reflective answer; treat it as such.\n'
                    '  4. Reflective partnership at this structural '
                    'close means sitting with what was said, not '
                    'extracting more. Two to three sentences total.\n'
                    'Do NOT follow the per-stage continuing brief\'s '
                    'task instruction for this one turn — these four '
                    'rules replace it.'
                )
            else:
                parts.append(f'YOUR TASK: {brief["continuing"]}')
            parts.append('')
            if is_final_in_phase:
                # Closing-turn examples — model the form of a settling
                # acknowledgment (no question, honours uncertainty). The
                # regular continuing_examples all end with questions and
                # would confuse the close-only rule above.
                parts.append(_EXAMPLE_PREAMBLE)
                parts.append(
                    'If the teacher said: "I am not sure. You tell me."'
                )
                parts.append(
                    'a fitting close would be: "Not being sure is itself '
                    'a true reflection of where the question sits for '
                    'you right now. The thread of teacher agency you '
                    'named earlier — that is yours to carry forward."'
                )
                parts.append('')
                parts.append(
                    'If the teacher said: "Nothing more comes to mind."'
                )
                parts.append(
                    'a fitting close would be: "Then we let what you '
                    'have already said stand. The phrase you used — '
                    '\'student thinking became a phrase you returned '
                    'to\' — is enough for this phase to rest on."'
                )
                parts.append('')
            else:
                parts.append(_EXAMPLE_PREAMBLE)
                for ex in brief['continuing_examples']:
                    # §24.5 — explicit shape labels per example so
                    # the model sees the three-shape categorisation
                    # explicitly with each pattern (not just inferred
                    # from the prose). The shape key was added in §24;
                    # legacy examples without it still render cleanly.
                    if ex.get('shape'):
                        parts.append(f'EXAMPLE — {ex["shape"]}:')
                    parts.append(f'  If the teacher said: "{ex["teacher"]}"')
                    parts.append(
                        f'  a fitting reply would be: "{ex["reply"]}"'
                    )
                    parts.append('')
        else:
            parts.append(f'YOUR TASK: {brief["opening"]}')
            parts.append('')
            parts.append(_EXAMPLE_PREAMBLE)
            parts.append(brief['opening_example'])

        return '\n'.join(parts)


# ----------------------------------------------------------------------
# Private helpers
# ----------------------------------------------------------------------
def _dedupe_doubled_response(text: str) -> str:
    """Detect a Gemini response whose content is duplicated back-to-back
    and return only the first copy.

    Gemini occasionally generates a turn whose sentences are repeated
    in order — `S1 S2 ... Sn S1 S2 ... Sn`. A live instance of this
    was observed on 2026-05-23 during the §20 sample-review of the
    EpilogueDialogueAgent. The check is conservative: it requires an
    even number of sentences (>= 4) and exact equality of the two
    halves. Anything else passes through unchanged — false positives
    are worse than the rare miss of a near-duplicate.
    """
    sentences = [
        s.strip()
        for s in re.split(r'(?<=[.!?])\s+', text.strip())
        if s.strip()
    ]
    n = len(sentences)
    if n < 4 or n % 2 != 0:
        return text
    half = n // 2
    if sentences[:half] == sentences[half:]:
        logging.getLogger(__name__).warning(
            'EpilogueDialogueAgent: detected doubled Gemini response '
            '(%d sentences); trimming to the first half.', n,
        )
        return ' '.join(sentences[:half])
    return text
