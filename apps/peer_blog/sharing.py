"""
Per-module artefact-to-Workshop sharing orchestration.

Tier 3 Step 4 (M9) + Step 5 (M14) wire here. Each module that opts into
the Practice Workshop registers its body-renderer function and field
naming in MODULE_SHARE_CONFIG. The generic ``share_artefact_to_workshop``
function handles persistence (challenge_data updates) + BlogPost creation
inside a single transaction.

M9 sharing pattern (Blocker 3 Option A modified + Hybrid Option C):
    - Opt-in lives on Challenge 3 only (the substantive lesson decisions).
    - User supplies a title (≤100 chars) and summary (≤500 chars).
    - The post body is the Hybrid synthesis: user summary on top, then
      auto-generated context (subject scenario, decisions taken, C1/C2
      module scores). Pattern: peer reads what the author meant AND
      sees the underlying choices that informed it.
"""

import importlib

from django.db import transaction

from .services import create_blog_post


def _render_m9_lesson_body(challenge_data: dict) -> str:
    """
    Render an M9 lesson-design artefact for the Practice Workshop.

    Layout:
        <user summary>
        ---
        Subject focus: <subject_label>
        Lesson scenario: <topic>
        <context paragraph>

        My design decisions:
        1. <question>
           → ✓/○ <chosen option text>
        ...

        Module exercise scores:
        • Backward Design Sorter: X/Y
        • UDL Profile Matcher: X/Y
        • Lesson Design Decisions: X/Y
    """
    cd = challenge_data or {}

    try:
        m9_mod = importlib.import_module('apps.modules.tab3_content_m9')
        scenarios = getattr(m9_mod, 'LESSON_SCENARIOS', {})
    except Exception:
        scenarios = {}

    user_summary = (cd.get('shared_lesson_summary') or '').strip()
    subject = (cd.get('challenge3_subject') or '').strip()
    scenario = scenarios.get(subject, {}) if isinstance(scenarios, dict) else {}

    lines = []

    if user_summary:
        lines.append(user_summary)
        lines.append('')
        lines.append('---')
        lines.append('')

    if subject:
        subject_display = subject.replace('_', ' ').title()
        lines.append(f'Subject focus: {subject_display}')

    if scenario.get('topic'):
        lines.append(f'Lesson scenario: {scenario["topic"]}')
    if scenario.get('context'):
        lines.append(scenario['context'])
    if subject or scenario.get('topic') or scenario.get('context'):
        lines.append('')

    decisions = scenario.get('decisions') or []
    if decisions:
        lines.append('My design decisions:')
        for i, decision in enumerate(decisions, start=1):
            did = decision.get('id', '')
            user_choice = cd.get(f'challenge3_{did}')
            chosen_text = ''
            for opt in decision.get('options', []):
                if opt.get('value') == user_choice:
                    chosen_text = opt.get('text') or ''
                    break
            question = (decision.get('question') or '').strip()
            lines.append(f'{i}. {question}')
            if chosen_text:
                lines.append(f'   → {chosen_text}')

    # Tier 3 design fix: module exercise scores intentionally NOT included.
    # Scores are quiz-mechanic performance signals, not research-grade
    # artefact content; exposing them in a public Workshop post conflicts
    # with the Schön reflective-practice framing. Researchers retain DB
    # access to scores for pilot analysis.

    return '\n'.join(lines).rstrip()


# ────────────────────────────────────────────────────────────────────────
# M14 — Gamified Unit Planner renderer
# ────────────────────────────────────────────────────────────────────────

# Decoration-test labels are long sentences in tab3_content_m14; we rephrase
# for compact body display while preserving the substance/decoration tradeoff.
_M14_DECORATION_SHORT = {
    'yes_valuable': 'Yes — substance survives without the mechanics',
    'partial': 'Partial — mechanics add real engagement value',
    'no_decoration': 'No — without the mechanics the activity loses most of its value',
}


def _strip_after_dash(label: str) -> str:
    """Trim option-label decorations after first '—' or '(' for compact display."""
    import re as _re
    if not label:
        return ''
    return _re.split(r'\s*[—(]', label, maxsplit=1)[0].strip()


def _render_m14_unit_body(challenge_data: dict) -> str:
    """
    Render an M14 Gamified Unit Planner artefact for the Practice Workshop.

    Layout:
        <user summary>
        ---
        Subject focus: <subject_label>
        Learning goal: <user-typed learning_goal>

        Unit design choices:
        • Student role: ...
        • Gamification principle: ...
        • Visible progression: ...
        • Assessment evidence: ...
        • SAMR level: ...
        • Substance test: <decoration_test rephrasing>

    Module exercise scores intentionally excluded (see _render_m9_lesson_body
    note — Schön reflective practice framing, no quiz-style judgment).
    """
    cd = challenge_data or {}

    try:
        m14_mod = importlib.import_module('apps.modules.tab3_content_m14')
        m14_ctx = m14_mod.get_context()
    except Exception:
        m14_ctx = {}

    user_summary = (cd.get('shared_lesson_summary') or '').strip()
    subject_value = (cd.get('challenge3_subject') or '').strip()
    learning_goal = (cd.get('challenge3_learning_goal') or '').strip()

    def _label_for(options_key, value, *, trim=True):
        if value is None or value == '':
            return ''
        # Multi-select fields (e.g., challenge3_assessment) come through as lists.
        if isinstance(value, list):
            parts = [_label_for(options_key, v, trim=trim) for v in value if v]
            return ', '.join(p for p in parts if p)
        if not isinstance(value, str):
            value = str(value)
        for opt in m14_ctx.get(options_key, []) or []:
            if opt.get('value') == value:
                lbl = opt.get('label') or value
                return _strip_after_dash(lbl) if trim else lbl
        return value.replace('_', ' ').strip().title()

    lines = []

    if user_summary:
        lines.append(user_summary)
        lines.append('')
        lines.append('---')
        lines.append('')

    subject_label = _label_for('c3_subject_options', subject_value, trim=False)
    if subject_label:
        lines.append(f'Subject focus: {subject_label}')
    if learning_goal:
        lines.append(f'Learning goal: {learning_goal}')
    if subject_label or learning_goal:
        lines.append('')

    design_lines = []

    role_lbl = _label_for('c3_role_options', cd.get('challenge3_student_role'))
    if role_lbl:
        design_lines.append(f'• Student role: {role_lbl}')

    principle_lbl = _label_for('c3_gamification_principles', cd.get('challenge3_principle'))
    if principle_lbl:
        design_lines.append(f'• Gamification principle: {principle_lbl}')

    progression_lbl = _label_for('c3_progression_options', cd.get('challenge3_progression'), trim=False)
    if progression_lbl:
        design_lines.append(f'• Visible progression: {progression_lbl}')

    assessment_lbl = _label_for('c3_assessment_options', cd.get('challenge3_assessment'), trim=False)
    if assessment_lbl:
        design_lines.append(f'• Assessment evidence: {assessment_lbl}')

    samr_lbl = _label_for('c3_samr_options', cd.get('challenge3_samr'))
    if samr_lbl:
        design_lines.append(f'• SAMR level: {samr_lbl}')

    decoration_value = cd.get('challenge3_decoration_test')
    decoration_short = _M14_DECORATION_SHORT.get(decoration_value)
    if decoration_short:
        design_lines.append(f'• Substance test (would the activity stand without the mechanics?): {decoration_short}')
    elif decoration_value:
        design_lines.append(f'• Substance test: {_label_for("c3_decoration_options", decoration_value)}')

    if design_lines:
        lines.append('Unit design choices:')
        lines.extend(design_lines)

    return '\n'.join(lines).rstrip()


# Per-module sharing configuration. Adding a new module = registering an entry.
# Step 4 wires M9. Step 5 wires M14 (Challenge 3 — Gamified Unit Planner — only).
MODULE_SHARE_CONFIG = {
    'M9': {
        'artefact_type': 'm9_lesson',
        'body_renderer': _render_m9_lesson_body,
        'title_field': 'shared_lesson_title',
        'summary_field': 'shared_lesson_summary',
        'gate_attr': 'challenge3_completed',
        'gate_message': 'Complete Challenge 3 (Lesson Design Decisions) before sharing.',
    },
    'M14': {
        'artefact_type': 'm14_gamified_unit',
        'body_renderer': _render_m14_unit_body,
        'title_field': 'shared_unit_title',
        'summary_field': 'shared_lesson_summary',  # reuse shared_lesson_summary key for consistency
        'gate_attr': 'challenge3_completed',
        'gate_message': 'Complete Challenge 3 (Gamified Unit Planner) before sharing.',
    },
}


def share_artefact_to_workshop(module_code, user, activity, title, summary):
    """
    Persist title+summary to challenge_data, render the body via the
    module's renderer, and create a BlogPost — all in one transaction.

    Returns: BlogPost instance.
    Raises: ValueError if module isn't registered or already shared.
    """
    config = MODULE_SHARE_CONFIG.get(module_code)
    if not config:
        raise ValueError(f"Workshop sharing not configured for {module_code}.")

    cd = dict(activity.challenge_data or {})
    if cd.get('shared_to_blog') and cd.get('blog_post_id'):
        raise ValueError('You have already shared this artefact to the Workshop.')

    cd[config['title_field']] = title
    cd[config['summary_field']] = summary
    cd['shared_to_blog'] = True

    body = config['body_renderer'](cd)
    if not body.strip():
        raise ValueError(
            'Cannot synthesise a Workshop post — the artefact is empty. '
            'Complete the relevant challenges first.'
        )

    with transaction.atomic():
        activity.challenge_data = cd
        activity.save(update_fields=['challenge_data', 'updated_at'])

        post = create_blog_post(
            artefact_type=config['artefact_type'],
            artefact_id=activity.id,
            title=title,
            body=body,
            author_user=user,
        )

        cd['blog_post_id'] = post.id
        activity.challenge_data = cd
        activity.save(update_fields=['challenge_data'])

    return post
