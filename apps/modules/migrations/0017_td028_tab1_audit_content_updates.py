"""
Phase H TD-028 — TAB1 audit content updates.

Updates per the audit comparing live DB Module rows against
proodos_files/CONTENT_VALIDATION_MATRIX.md:

- All 15 modules: estimated_hours unified to 5 (post-TD-028 decision,
  anchored to PROODOS_PROGRAMME_DURATION_METHODOLOGY v1.2 §4).
- Title corrections (4 modules): M2 → "Ethics of AI in Education";
  M7 → "Navigating Ethical Dilemmas in Practice"; M8 → "Advanced
  Prompt Engineering with EduPrompt Studio"; M12 subtitle added.
- LO + module_overview expansion for 6 modules whose existing content
  was thin or generic relative to the matrix: M2, M4, M7, M8, M9, M12.
- M6, M14: minor LO/overview enhancements naming key concepts the
  matrix highlights (M6 5-part structure; M14 Decoration Test + 4
  Game Design Principles).
- Modules whose existing content already matched the matrix
  comprehensively are left untouched: M1, M3, M5, M10, M11, M13, M15.

Reversible: the migration records the prior values inline so the
reverse function can restore them. Both directions encoded as
RunPython.

Reference:
  - proodos_files/CONTENT_VALIDATION_MATRIX.md (per-module rationale)
  - proodos_files/PROODOS_PROGRAMME_DURATION_METHODOLOGY_v1_20260526.md
    §4 (5h decomposition)
  - proodos_files/TECH_DEBT_LOG.md TD-028 (audit findings)
"""

from django.db import migrations


# ----------------------------------------------------------------------
# Content updates per module — keyed by Module.code
# ----------------------------------------------------------------------
# Each entry: {code: {field: new_value, ...}}. Only fields that change
# appear; untouched fields preserve their current DB value. The
# `_prior` companion dict records the pre-migration values for the
# reverse path so the migration is cleanly reversible.

MODULE_UPDATES = {
    # ===== Unified 5h for all 15 modules (TD-028) =====
    'M1':  {'estimated_hours': 5},
    'M2':  {
        'estimated_hours': 5,
        'title': 'Ethics of AI in Education',
        'learning_objectives': [
            'Explain the five core ethical principles for AI in education '
            '(Fairness, Transparency, Accountability, Privacy, Critical thinking)',
            'Analyse controversies in AI deployment from human-agency, '
            'security, and privacy perspectives',
            'Apply equity and inclusion principles to classroom AI decisions',
            'Practise ethical decision-making through four realistic '
            'classroom scenarios (Fact Finder, Inspiration Seeker, Peer '
            'Editor, Translator)',
            'Develop a personal ethical framework supported by the M2 '
            'Toolbox of disclosure, classroom-statement, and reflection '
            'resources',
        ],
        'module_overview': (
            'M2 establishes the ethical foundation for all subsequent '
            'AI work in PROODOS. Across five parts and a six-resource '
            'Toolbox, you explore the five core ethical principles for '
            'AI in K-12 education — Fairness, Transparency, '
            'Accountability, Privacy, and Critical Thinking — through '
            'five practical challenges and four realistic classroom '
            'scenarios. You build the analytical vocabulary needed for '
            'the deeper ethical dilemmas of M7 and the institutional '
            'policy work of M12.'
        ),
    },
    'M3':  {'estimated_hours': 5},
    'M4':  {
        'estimated_hours': 5,
        'learning_objectives': [
            'Identify teaching tasks where AI support is pedagogically '
            'appropriate using the Pedagogical Fit Test',
            'Apply the Two-Step Selection process (Reliability + '
            'Pedagogical Fit) to choose AI tools for a specific '
            'teaching context',
            'Use AI for lesson preparation, differentiation, feedback, '
            'and assessment design across the four teaching domains',
            'Implement the Human Voice Rule when AI drafts '
            'student-facing communications',
            'Navigate the 5-Question Decision Sequence for principled '
            'student-facing AI use',
        ],
        'module_overview': (
            'M4 moves you from understanding AI tools (M3) to using '
            'them in actual teaching. You explore the four teaching '
            'domains where AI delivers real value — Lesson Preparation, '
            'Differentiation, Feedback Generation, and Assessment '
            'Design — and learn the Pedagogical Fit Test. The module '
            'distinguishes what AI drafts (which you edit) from what '
            'AI cannot do (give feedback in your voice), introducing '
            'the Human Voice Rule and a structured 5-Question Decision '
            'Sequence for principled student-facing AI use.'
        ),
    },
    'M5':  {'estimated_hours': 5},
    'M6':  {
        'estimated_hours': 5,
        'module_overview': (
            'M6 builds directly on M1 foundations. You already know '
            'how AI works — now you learn how to evaluate it critically '
            'across five parts: the Black Box Problem and three '
            'classroom scenarios, the Human-AI Decision Loop with a '
            'proportional-stakes table, the EU AI Act with four risk '
            'classifications, your four Rights as a professional, and '
            'the Critical AI Evaluation Card as a daily tool. You '
            'assert your rights as a professional in the age of AI.'
        ),
    },
    'M7':  {
        'estimated_hours': 5,
        'title': 'Navigating Ethical Dilemmas in Practice',
        'learning_objectives': [
            'Recognise the four reasons ethics becomes difficult in AI '
            'use (conflicting principles, context dependence, power '
            'dynamics, no institutional guidance)',
            'Apply four pedagogical strategies — process documentation, '
            'authentic tasks, disclosure literacy, dialogue before '
            'judgement — to classroom integrity work',
            'Analyse multi-modality academic integrity across text, '
            'image, video, code, and data analysis',
            'Reason through complex scenarios including the AI Detector '
            'Problem, deepfake harassment, and AI-amplified bullying',
            'Apply the Assessment Reliability Pyramid (Live Performance '
            '→ Process Evidence → Final Output) to redesign tasks '
            'rather than police tools',
        ],
        'module_overview': (
            'M7 takes you beyond foundational ethical principles into '
            'the genuinely difficult territory of competing values. '
            'Across nine parts including three complex classroom '
            'scenarios, three dramatised audio dilemmas, and a '
            'nine-resource Toolbox, you develop the professional '
            'judgement needed when two valid principles conflict. The '
            'module reframes ethics as a design challenge — redesign '
            'the task rather than police the tool — and equips you '
            'with the Assessment Reliability Pyramid for '
            'context-dependent decisions.'
        ),
    },
    'M8':  {
        'estimated_hours': 5,
        'title': 'Advanced Prompt Engineering with EduPrompt Studio',
        'learning_objectives': [
            'Map RPE Framework Strategies 1–5 onto the EduPrompt '
            'Studio interface fields',
            'Operate the Studio to produce subject-specific structured '
            'prompts ready for live classroom use',
            'Apply the "Invisible Theory" principle whereby Studio '
            'embeds Bloom, UDL, TPACK, and Constructivism into your '
            'daily prompting workflow',
            'Build a personal subject-specific prompt library using '
            'fully RPE-annotated templates, exemplified by the Math '
            'Starter Library',
            'Implement the four Orchestrator advanced moves (live '
            're-prompting, differentiation reservoir, strategic '
            'prompt withholding, in-moment audit)',
            'Evaluate prompt quality using the 5-criterion Prompt '
            'Audit Template combined with the ethics-by-design '
            '3-check pattern (Bias / Privacy / Inclusivity)',
        ],
        'module_overview': (
            'M8 operationalises the RPE Framework introduced in M5 '
            'through EduPrompt Studio — a structured prompting '
            'environment that embeds educational theory (Bloom, UDL, '
            'TPACK) automatically while you provide subject knowledge. '
            'Across six parts the module walks you from Studio '
            'interface mapping to the Math Starter Library (four '
            'fully annotated prompts), through live classroom '
            'Orchestrator moves, to the 5-criterion Prompt Audit '
            'Template with integrated ethics-by-design 3-check '
            'pattern. The "Invisible Theory" principle reframes the '
            'division of labour: the teacher provides four things; '
            'the tool handles four things.'
        ),
    },
    'M9':  {
        'estimated_hours': 5,
        'learning_objectives': [
            "Design a complete lesson using Wiggins & McTighe's "
            'Backward Design 3-stage model, with AI entering only at '
            'Stage 3',
            'Apply UDL 3 Principles (Engagement, Representation, '
            'Expression) for proactive inclusive design rather than '
            'reactive intervention',
            'Differentiate learning experiences for three Learner '
            'Profiles (ESL/EAL, SEN, Advanced) using AI as a '
            'deliberate design tool',
            'Apply the 4-Step Planning Cycle (Identify needs → UDL '
            'principle → AI support → Review for bias)',
            'Use the Human Signature concept and Productive Friction '
            'principle to redesign tasks that AI alone could complete',
        ],
        'module_overview': (
            'M9 moves from using AI for individual teaching tasks to '
            'designing complete learning experiences with AI built in '
            'from the start. Through Backward Design, UDL, and three '
            'differentiated Learner Profiles, you treat AI as a '
            'deliberate design choice rather than an add-on. The '
            "module's centrepiece is the Human Signature concept — if "
            'an assessment can be completed without student voice or '
            'classroom-specific context, AI can complete it too, '
            'which is the signal to redesign — alongside the 4-Step '
            'Planning Cycle and Productive Friction principle.'
        ),
    },
    'M10': {'estimated_hours': 5},
    'M11': {'estimated_hours': 5},
    'M12': {
        'estimated_hours': 5,
        'title': 'Ethics Integration Across Curriculum (School AI Policy Co-Creation)',
        'learning_objectives': [
            'Apply the seven Elements of Effective School AI Policy '
            '(Definitions, Differentiated Expectations, Transparency '
            '& Disclosure, Equity & Access, Data Privacy & Tool '
            'Approval, Integrity Procedures, Review Cycle)',
            'Lead a 5-Step Participatory Process — Audit, Consult, '
            'Draft, Pilot, Communicate — for institutional AI policy',
            'Adapt policy across seven Subject Areas and three '
            'Special Circumstances (IEPs/504 learning differences, '
            'Emergency situations, High-Stakes Standardised '
            'Assessment)',
            "Use the Designer's Cycle 5-step iterative framework to "
            'maintain school AI policy as an evolving artefact rather '
            'than a one-off document',
            'Apply the AI Tool Evaluation Checklist and Model Policy '
            'Guidelines (positive criteria + warning signs) to '
            'systemic AI decisions',
        ],
        'module_overview': (
            'M12 moves you from individual ethical decisions to '
            'institutional policy co-creation. Through seven Elements '
            'of effective policy and a 5-Step Participatory Process '
            '(Audit → Consult → Draft → Pilot → Communicate), you '
            'learn to lead school-level frameworks that embed ethics '
            'across subjects and student profiles. The six-resource '
            "Toolbox includes a Policy Template, AI Tool Evaluation "
            "Checklist, Model Policy Guidelines, and Designer's Cycle "
            '— explicitly designed for return-and-revise iterations '
            'rather than file-and-forget completion.'
        ),
    },
    'M13': {'estimated_hours': 5},
    'M14': {
        'estimated_hours': 5,
        'learning_objectives': [
            'Design a gamified learning experience grounded in the '
            'four Game Design Principles (Challenge Calibration via '
            "Vygotsky's ZPD, Immediate Feedback, Visible Progression, "
            'Meaningful Choice via Self-Determination Theory)',
            'Apply the Five Roles Framework (Director, Researcher, '
            'Critic, Editor, Audience) to build student AI literacy '
            'through classroom design',
            "Use the SAMR transformation lens to design experiences "
            'that target Redefinition rather than Substitution',
            'Apply the Decoration Test — if you remove all '
            'gamification mechanics, is there still a valuable '
            'learning activity underneath? — to evaluate whether '
            'gamification serves a learning goal',
            'Create learning experiences that represent genuine '
            'pedagogical transformation rather than AI-flavoured '
            'adaptation',
        ],
    },
    'M15': {'estimated_hours': 5},
}


def apply_updates(apps, schema_editor):
    Module = apps.get_model('modules', 'Module')
    for code, updates in MODULE_UPDATES.items():
        try:
            m = Module.objects.get(code=code)
        except Module.DoesNotExist:
            continue
        for field, value in updates.items():
            setattr(m, field, value)
        m.save()


def revert_updates(apps, schema_editor):
    """Restore the pre-TD-028 values inline.

    The original values are recorded here verbatim so the reverse
    path is fully deterministic (no need to read backup files).
    """
    Module = apps.get_model('modules', 'Module')
    PRIOR = {
        'M1':  {'estimated_hours': 4},
        'M2':  {
            'estimated_hours': 4,
            'title': 'Ethical Foundations in AI Use',
            'learning_objectives': [
                'Understand the five core principles of ethical AI use in education',
                'Apply fairness, transparency, accountability, privacy, and critical thinking principles to classroom practice',
                'Develop a personal ethical framework for AI integration',
            ],
            'module_overview': (
                'This module explores the five core ethical principles for AI use in '
                'educational contexts. Teachers will examine real classroom scenarios, '
                'develop their own ethical frameworks, and build practical strategies for '
                'guiding students toward responsible AI use.'
            ),
        },
        'M3':  {'estimated_hours': 3},
        'M4':  {
            'estimated_hours': 3,
            'learning_objectives': [
                'Identify teaching tasks where AI support is appropriate',
                'Apply a pedagogical fit test to AI tool selection',
                'Use AI for lesson preparation, feedback, and assessment design',
                'Make principled decisions about student-facing AI use',
            ],
            'module_overview': (
                'In this module you will explore the four teaching domains where AI '
                'delivers real value, learn how to apply a pedagogical fit test to any '
                'tool, and develop a principled approach to student-facing AI use.'
            ),
        },
        'M5':  {'estimated_hours': 4},
        'M6':  {
            'estimated_hours': 5,
            'module_overview': (
                'Module 6 builds directly on M1 foundations. You already know how AI '
                'works — now you learn how to evaluate it critically, understand who '
                'carries responsibility when AI is involved in educational decisions, and '
                'assert your rights as a professional in the age of AI.'
            ),
        },
        'M7':  {
            'estimated_hours': 4,
            'title': 'Navigating Ethical Dilemmas in AI Use',
            'learning_objectives': [
                'Navigate complex ethical dilemmas arising from AI use in education',
                'Apply structured ethical reasoning frameworks to ambiguous classroom situations',
                'Support students in developing their own ethical decision-making capacities',
            ],
            'module_overview': (
                'This module guides teachers through complex real-world ethical dilemmas '
                'in AI use, developing their capacity to navigate ambiguous situations '
                'with confidence, apply structured ethical reasoning, and support '
                'students in doing the same.'
            ),
        },
        'M8':  {
            'estimated_hours': 2,
            'title': 'Advanced Prompt Engineering',
            'learning_objectives': [
                'Apply the RPE Framework using EduPrompt Studio',
                'Build a subject-specific prompt library',
                'Evaluate prompt quality using the Prompt Audit Template',
            ],
            'module_overview': (
                'This module moves from understanding prompt engineering as reflective '
                'practice to applying it systematically — using EduPrompt Studio to '
                'create, refine, and curate prompts for your teaching context.'
            ),
        },
        'M9':  {
            'estimated_hours': 4,
            'learning_objectives': [
                'Design a complete lesson using backward design principles with AI as a support tool',
                'Apply UDL principles to create inclusive learning experiences with AI',
                'Select and justify AI integration strategies for different learner needs',
                'Use AI to design formative assessment loops',
            ],
            'module_overview': (
                'M9 moves from using AI for teaching tasks to designing complete learning '
                'experiences with AI. You will apply backward design, Universal Design '
                'for Learning, and differentiation strategies — with AI as a deliberate '
                'design tool, not an add-on.'
            ),
        },
        'M10': {'estimated_hours': 4},
        'M11': {'estimated_hours': 5},
        'M12': {
            'estimated_hours': 4,
            'title': 'Ethics Integration Across Curriculum',
            'learning_objectives': [
                'Design curriculum-wide ethical AI frameworks and policies',
                'Lead school-level ethical AI integration initiatives',
                'Create learning experiences that embed ethical AI reasoning across subjects',
            ],
            'module_overview': (
                'This module empowers teachers to move beyond individual ethical '
                'decisions and design systemic, curriculum-wide approaches to ethical AI '
                'integration — creating policies, frameworks, and learning experiences '
                'that embed ethics into every subject and level.'
            ),
        },
        'M13': {'estimated_hours': 4},
        'M14': {
            'estimated_hours': 4,
            'learning_objectives': [
                'Design a gamified learning experience grounded in pedagogical principles',
                'Apply the Five Roles Framework to build student AI literacy',
                'Critically evaluate whether gamification serves a learning goal',
                'Create learning experiences that represent genuine pedagogical transformation',
            ],
        },
        'M15': {'estimated_hours': 4},
    }
    for code, prior in PRIOR.items():
        try:
            m = Module.objects.get(code=code)
        except Module.DoesNotExist:
            continue
        for field, value in prior.items():
            setattr(m, field, value)
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0016_td028_estimated_hours_default_5'),
    ]

    operations = [
        migrations.RunPython(apply_updates, revert_updates),
    ]
