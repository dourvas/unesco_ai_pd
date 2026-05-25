"""
Versioned consent / disclosure copy text for the compliance app.

The text constants defined here are BOTH:
  - rendered in the disclosure modal template (so the user reads them)
  - passed to record_consent() (so they are stored verbatim per row)

This guarantees the row's `consent_text` matches what the user agreed
to (IRB-defensibility).

Versioning workflow:
  1. v1_pre_irb is the draft before IRB review.
  2. After IHU IRB feedback, add a new constant
     AI_DISCLOSURE_TEXT_V2_IRB_REVISED below; do NOT edit v1.
  3. Update settings.AI_DISCLOSURE_CURRENT_VERSION to the new tag.
  4. New acknowledgments use the new version; existing rows preserve
     their version. The compliance/services.record_consent helper handles
     the rest.

A regression test (`test_stored_consent_text_matches_copy_module_exactly`
in apps/compliance/tests.py) asserts that the version-tagged DB rows
contain the exact text from this module. If you change a text constant
without bumping its version tag, the test fails by design.
"""


AI_DISCLOSURE_TEXT_V1_PRE_IRB = """\
Important: AI Use Disclosure

PROODOS uses AI (Google Gemini 2.5 Flash) to provide you with personalised
feedback, reflection prompts, and developmental insights as you progress
through the 15 modules of this professional development programme.

What this means for you:
  - All AI-generated suggestions are advisory, not directive.
  - You remain the final judge of your own teaching practice.
  - Every AI output can be disputed and corrected through the platform.
  - Your data is governed by the EU General Data Protection Regulation
    (Regulation 2016/679, 'GDPR').

Legal framing.
Under our assessment of the EU AI Act (Regulation 2024/1689), PROODOS
is classified as a Limited Risk AI system falling under Article 50
transparency obligations. No automated decisions are made about you,
your teaching, or your professional standing. The AI assists you; it
does not evaluate you administratively.

Your right to withdraw.
You may leave the platform at any time using the Logout option in the
top-right menu. After completing onboarding you will also have access
to a Privacy dashboard where you can review or delete your data.

Your acknowledgment.
By clicking "I acknowledge and continue" you confirm that you have
read this notice and understand that PROODOS uses AI assistance
throughout your interaction with the platform.
"""


# Visual bullets rendered as <ul> in the disclosure template. Wording
# matches the bullet list inside AI_DISCLOSURE_TEXT_V1_PRE_IRB so that
# the user sees the same content the row stores.
AI_DISCLOSURE_HTML_BULLETS_V1_PRE_IRB = (
    "All AI-generated suggestions are advisory, not directive.",
    "You remain the final judge of your own teaching practice.",
    "Every AI output can be disputed and corrected through the platform.",
    "Your data is governed by the EU General Data Protection Regulation "
    "(Regulation 2016/679, 'GDPR').",
)


# ============================================================
# Phase C C.2.2 — Step 3 research consent texts
# ============================================================
# Two independent consents shown on onboarding Step 3. They are
# versioned together (RESEARCH_CONSENT_CURRENT_VERSION) because the
# IRB review is a single combined review.

RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB = """\
Research Participation — PROODOS Doctoral Research

PROODOS is the empirical instrument of a doctoral dissertation at the
International Hellenic University (Διεθνές Πανεπιστήμιο της Ελλάδος, IHU),
Thessaloniki. The principal investigator is John Dourvas, doctoral
researcher, under the supervision of Asst. Prof. Georgios Kokkonis,
Department of Information and Electronic Systems Engineering.

Your platform interactions are research data. This includes:
  - Your responses to module activities and reflection prompts
  - Your AILST questionnaire responses (3 administrations)
  - Your AI dispute submissions when you contest AI feedback
  - Your module progress and completion data
  - The personalization fields you provide in your profile

What participation involves:
  - Completing the AI Literacy Scale for Teachers (AILST) at three
    points: once after onboarding (T0), once after Module 5 (T1), and
    once after Module 15 (T2). Each administration takes approximately
    7 minutes.
  - These three AILST administrations are required parts of the
    programme. You cannot proceed to Module 6 without completing T1,
    or receive a completion certificate without completing T2.
  - Allowing your platform interaction data to be analysed for the
    dissertation and any peer-reviewed publications arising from it.

Your right to withdraw:
  You may withdraw from the research at any time without consequence
  using the Logout option (and, once available, through the Privacy
  dashboard in your account settings). On withdrawal, your platform
  data will be handled per the Privacy Policy and applicable provisions
  of the EU General Data Protection Regulation (Regulation 2016/679,
  'GDPR') and Greek Law 4624/2019.

Contact:
  For questions about the research, contact John Dourvas at
  idourvas@ihu.gr.

Your acknowledgment:
  By checking "I consent to participate in this research" you confirm
  that you have read and understood the above.
"""


# ============================================================
# Phase C C.1 — EU AI Act Article 50 transparency document
# ============================================================
# This is the participant-facing AI Impact Assessment. Public; reachable
# from the AI Disclosure modal "Learn more" link. Distinct from the
# consent texts above: those are what the user *agreed to*; this is the
# *transparency notice* explaining what the AI does and how risks are
# handled, per EU AI Act Article 50(1).
#
# Structured as a list of (heading, body) sections so the template loop
# can render each section with consistent typography. Body text follows
# the same paragraph + bullet conventions handled by the existing
# consent_format template filter (blank lines for paragraph breaks,
# "  - " for bullet items).
#
# Version-pinned. After IHU IRB feedback, add a V2_IRB_REVISED list
# below; do not edit V1 in place (mirrors the AI_DISCLOSURE_TEXT
# pattern). The active version is exposed via
# settings.AI_IMPACT_ASSESSMENT_CURRENT_VERSION.

AI_IMPACT_ASSESSMENT_VERSION = 'v1_pre_irb'

AI_IMPACT_ASSESSMENT_V1_PRE_IRB = [
    {
        'heading': '1. What PROODOS is',
        'body': (
            "PROODOS EduAI is a doctoral research platform developed at the "
            "International Hellenic University (IHU), Thessaloniki, for the "
            "professional development of K-12 teachers in artificial "
            "intelligence literacy. The platform is structured around 15 "
            "UNESCO-aligned modules followed by a synthesis Epilogue, and "
            "uses AI-generated feedback as a core pedagogical mechanism.\n"
            "\n"
            "PROODOS is the empirical instrument of John Dourvas's doctoral "
            "dissertation, under the supervision of Asst. Prof. Georgios "
            "Kokkonis, Department of Information and Electronic Systems "
            "Engineering."
        ),
    },
    {
        'heading': '2. AI components in PROODOS',
        'body': (
            "Four AI-driven features are active during a participant's "
            "journey:\n"
            "\n"
            "  - RAG-based reflection feedback: after each module's "
            "reflection submission, a retrieval-augmented generation "
            "pipeline (Google Gemini 2.5 Flash) produces a personalised "
            "feedback narrative grounded in pedagogy literature.\n"
            "  - Reflective Tension Mapper (RTM): from the participant's "
            "reflection text, the system extracts up to three pedagogical "
            "tensions and asks the participant to self-position on a "
            "5-point scale between two contrasting poles.\n"
            "  - Developmental Trajectory Predictor (DTP): a narrative "
            "summary of the participant's reflection trajectory across "
            "modules. Available from Module 2 onwards.\n"
            "  - Peer synthesis: drawing on pseudonymised peer "
            "reflections, this produces a comparative view of how other "
            "participants engaged with the same content.\n"
            "\n"
            "After the pilot, the PROODOS Epilogue will add a Personal "
            "Evolution Dashboard, a three-stage Gemini dialogue, and a "
            "Learning Portrait PDF. These are currently scaffolded but not "
            "yet implemented for participants."
        ),
    },
    {
        'heading': '3. Risk classification under the EU AI Act',
        'body': (
            "Under our assessment of Regulation 2024/1689 (the EU AI Act), "
            "PROODOS is classified as a Limited Risk AI system falling "
            "under Article 50 transparency obligations.\n"
            "\n"
            "The platform:\n"
            "\n"
            "  - Does not produce automated decisions about participants' "
            "professional, academic, or employment standing.\n"
            "  - Does not perform biometric identification, social "
            "scoring, or any practice listed as Prohibited (Article 5) or "
            "as High-Risk (Annex III).\n"
            "  - Generates content that the user reviews and may dispute "
            "(see Section 4).\n"
            "\n"
            "The AI's role is assistive and pedagogical: it surfaces "
            "patterns, asks reflective questions, and offers commentary. "
            "Authority over interpretation remains with the educator."
        ),
    },
    {
        'heading': '4. Mitigation and human oversight',
        'body': (
            "Per Article 50 and the spirit of Article 14 (human oversight) "
            "of the EU AI Act:\n"
            "\n"
            "  - Explicit consent: use of AI assistance is disclosed "
            "before account creation and is revocable at any time from "
            "the Privacy dashboard.\n"
            "  - Output dispute: every AI-generated artefact (RAG, RTM, "
            "DTP) carries a dispute submission button. Flagged outputs "
            "feed back into the research dataset for AI-alignment "
            "analysis.\n"
            "  - No automated decision-making: AILST self-assessment "
            "scores are computed deterministically from the participant's "
            "own responses; no AI inference is involved in score "
            "calculation, gating, or certification.\n"
            "  - Pedagogical framing: AI feedback is presented as one "
            "voice among many, not as authoritative pronouncement. Module "
            "copy reinforces this stance throughout the programme.\n"
            "  - Continuous evaluation: AI dispute submissions, RAG "
            "telemetry, and AILST trajectory data are part of an ongoing "
            "research programme to refine the AI's pedagogical alignment."
        ),
    },
    {
        'heading': '5. Data handling and retention',
        'body': (
            "Lawful basis under the EU General Data Protection Regulation "
            "(GDPR, Regulation 2016/679) and Greek Law 4624/2019:\n"
            "\n"
            "  - Primary basis: Article 6(1)(a) — explicit informed "
            "consent, captured at onboarding Step 3.\n"
            "  - Special category basis: Article 9(2)(j) — processing "
            "for scientific research with appropriate safeguards.\n"
            "\n"
            "Retention and identifiers:\n"
            "\n"
            "  - Research data is retained for seven years following "
            "programme completion (IRB audit window). Participants can "
            "request earlier removal of identifying information via the "
            "Privacy dashboard's account anonymisation action.\n"
            "  - All analysed data is pseudonymised before analytics "
            "processing. Free-text fields that may contain identifiers "
            "are cleared on participant-initiated erasure.\n"
            "  - IP addresses are captured at consent time only, "
            "automatically redacted after 30 days, and immediately "
            "cleared on erasure.\n"
            "\n"
            "Optional data sharing for secondary research: a separate "
            "consent allows pseudonymised data to be used in further "
            "analyses approved separately by the IHU Research Ethics "
            "Committee. Optional and revocable independently of primary "
            "research consent."
        ),
    },
    {
        'heading': '6. Your rights as a participant',
        'body': (
            "Guaranteed by GDPR Articles 7, 15, 17, and 21 and "
            "operationalised in the Privacy dashboard at "
            "/profile/privacy/:\n"
            "\n"
            "  - Withdraw any consent at any time (Article 7(3)): three "
            "independent revoke endpoints, one per consent type.\n"
            "  - Download a full copy of your personal data in JSON "
            "format (Article 15).\n"
            "  - Anonymise your account permanently (Article 17): "
            "identifying information is removed; pseudonymised research "
            "data remains attached to an anonymous account and is "
            "excluded from future analyses through the opt-out flag set "
            "at the same time.\n"
            "  - Object to processing or contact the research team for "
            "questions about your data (Article 21)."
        ),
    },
    {
        'heading': '7. Contact',
        'body': (
            "For questions about this platform's AI use or your data:\n"
            "\n"
            "  - Principal Investigator: John Dourvas, doctoral "
            "researcher - idourvas@ihu.gr.\n"
            "  - Academic Supervisor: Asst. Prof. Georgios Kokkonis - "
            "IHU, Department of Information and Electronic Systems "
            "Engineering.\n"
            "  - Institution: International Hellenic University (IHU, "
            "Διεθνές Πανεπιστήμιο της Ελλάδος), Thessaloniki.\n"
            "\n"
            "This document is version v1_pre_irb (May 2026). It will be "
            "revised after IHU IRB review."
        ),
    },
]


# ============================================================
# Phase H H.6 — Research participation V2 (follow-up bundled)
# ============================================================
# 2026-05-25 redesign (PI decision): rather than collecting a third,
# separate "followup_recruitment" consent at onboarding Step 3, the
# follow-up-contact provision is bundled into the existing
# RESEARCH_PARTICIPATION consent as one additional bullet under
# "What participation involves:". The teacher gives a single broad
# research consent that covers (a) platform data analysis,
# (b) AILST administrations, and (c) email retention for possible
# future follow-up invitation.
#
# Ethical framing: the bundled bullet permits the INVITATION only.
# If a follow-up study is launched, it will carry its own IRB
# protocol + its own study-specific information sheet + its own
# consent form at the time of invitation, which the teacher remains
# free to decline. The pool consent is a "right to invite", not
# "participation in an unknown future study".
#
# Trade-off vs the earlier separate-consent design: loses the
# statistical filtering ("X% of consenters opted into the pool" —
# everyone in the pool now) but gains clarity for the teacher
# (one decision, all uses listed) and for the IRB (one consent
# packet, no granularity layers).
#
# V1 retained byte-identical above per the versioning workflow.

RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED = """\
Research Participation — PROODOS Doctoral Research

PROODOS is the empirical instrument of a doctoral dissertation at the
International Hellenic University (Διεθνές Πανεπιστήμιο της Ελλάδος, IHU),
Thessaloniki. The principal investigator is John Dourvas, doctoral
researcher, under the supervision of Asst. Prof. Georgios Kokkonis,
Department of Information and Electronic Systems Engineering.

Your platform interactions are research data. This includes:
  - Your responses to module activities and reflection prompts
  - Your AILST questionnaire responses (3 administrations)
  - Your AI dispute submissions when you contest AI feedback
  - Your module progress and completion data
  - The personalization fields you provide in your profile

What participation involves:
  - Completing the AI Literacy Scale for Teachers (AILST) at three
    points: once after onboarding (T0), once after Module 5 (T1), and
    once after Module 15 (T2). Each administration takes approximately
    7 minutes.
  - These three AILST administrations are required parts of the
    programme. You cannot proceed to Module 6 without completing T1,
    or receive a completion certificate without completing T2.
  - Allowing your platform interaction data to be analysed for the
    dissertation and any peer-reviewed publications arising from it.
  - Allowing the research team to retain your contact email address
    for possible invitation to a follow-up study approximately 4-6
    weeks after programme completion. This consent permits the
    invitation only; if a follow-up study is launched, it will carry
    its own separate information sheet and consent form at the time
    of invitation, which you remain free to decline.

Your right to withdraw:
  You may withdraw from the research at any time without consequence
  using the Logout option (and, once available, through the Privacy
  dashboard in your account settings). On withdrawal, your platform
  data will be handled per the Privacy Policy and applicable provisions
  of the EU General Data Protection Regulation (Regulation 2016/679,
  'GDPR') and Greek Law 4624/2019. Your email address is removed from
  the follow-up invitation pool as part of the same withdrawal.

Contact:
  For questions about the research, contact John Dourvas at
  idourvas@ihu.gr.

Your acknowledgment:
  By checking "I consent to participate in this research" you confirm
  that you have read and understood the above.
"""


DATA_SHARING_TEXT_V1_PRE_IRB = """\
Data Sharing for Secondary Research

Optional. Separately from your participation in this research, this
consent allows your anonymised platform data to be used in secondary
research analyses approved separately by the IHU Research Ethics
Committee.

What "anonymised" means here:
  - Direct identifiers are removed: your name, email address, and any
    free-text content you wrote that could identify you.
  - Technical identifiers are removed: IP address, device identifiers.
  - Research variables are kept: subject area, grade level, years of
    teaching experience, AILST responses, and module completion data.
    These are the variables of scientific interest.

Your right to withdraw:
  You may revoke this consent independently of your research
  participation at any time. Revocation prevents any future sharing of
  your data. Data already shared in fully anonymised form is, by
  definition, no longer linked to you and cannot be retroactively
  identified.

Optional consent:
  This consent is OPTIONAL. Declining it does NOT affect your
  participation in the research, your access to the platform, or your
  programme certificate.

Your acknowledgment:
  By checking "I consent to data sharing" you confirm that you have
  read and understood the above.
"""


# ============================================================
# Phase H — AI Impact Assessment V2 (Phase G closure cleanup)
# ============================================================
# V1's section §2 promised "the PROODOS Epilogue will add a Personal
# Evolution Dashboard, a three-stage Gemini dialogue, and a Learning
# Portrait PDF. These are currently scaffolded but not yet
# implemented for participants."
#
# After Phase G closure (2026-05-24,
# PHASE_G_DIALOGUE_DEPRECATION_20260524.md), the three-stage dialogue
# and the Learning Portrait were deactivated. V2 brings §2 in line
# with what the platform actually ships post-G-closure: the Personal
# Evolution Dashboard (Stage 0) is the sole Epilogue surface.
#
# All other sections (§1, §3-§7) are kept byte-identical to V1. V1
# is preserved verbatim above for existing-row IRB-defensibility,
# per the versioning workflow at the top of this module.

AI_IMPACT_ASSESSMENT_VERSION_V2 = 'v2_post_g_closure'

AI_IMPACT_ASSESSMENT_V2_POST_G_CLOSURE = [
    AI_IMPACT_ASSESSMENT_V1_PRE_IRB[0],  # §1 unchanged
    {
        'heading': '2. AI components in PROODOS',
        'body': (
            "Four AI-driven features are active during a participant's "
            "journey:\n"
            "\n"
            "  - RAG-based reflection feedback: after each module's "
            "reflection submission, a retrieval-augmented generation "
            "pipeline (Google Gemini 2.5 Flash) produces a personalised "
            "feedback narrative grounded in pedagogy literature.\n"
            "  - Reflective Tension Mapper (RTM): from the participant's "
            "reflection text, the system extracts up to three pedagogical "
            "tensions and asks the participant to self-position on a "
            "5-point scale between two contrasting poles.\n"
            "  - Developmental Trajectory Predictor (DTP): a narrative "
            "summary of the participant's reflection trajectory across "
            "modules. Available from Module 2 onwards.\n"
            "  - Peer synthesis: drawing on pseudonymised peer "
            "reflections, this produces a comparative view of how other "
            "participants engaged with the same content.\n"
            "\n"
            "After Module 15, the PROODOS Epilogue presents a Personal "
            "Evolution Dashboard synthesising the participant's "
            "developmental trajectory across the 15 modules. The "
            "Epilogue is a non-AI synthesis surface: it aggregates "
            "existing AI outputs (DTP themes, RTM tension trajectories) "
            "and existing platform telemetry into a single read-only "
            "view; no new AI inference runs during the Epilogue itself."
        ),
    },
    AI_IMPACT_ASSESSMENT_V1_PRE_IRB[2],  # §3 unchanged
    AI_IMPACT_ASSESSMENT_V1_PRE_IRB[3],  # §4 unchanged
    AI_IMPACT_ASSESSMENT_V1_PRE_IRB[4],  # §5 unchanged
    AI_IMPACT_ASSESSMENT_V1_PRE_IRB[5],  # §6 unchanged
    {
        'heading': '7. Contact',
        'body': (
            "For questions about this platform's AI use or your data:\n"
            "\n"
            "  - Principal Investigator: John Dourvas, doctoral "
            "researcher - idourvas@ihu.gr.\n"
            "  - Academic Supervisor: Asst. Prof. Georgios Kokkonis - "
            "IHU, Department of Information and Electronic Systems "
            "Engineering.\n"
            "  - Institution: International Hellenic University (IHU, "
            "Διεθνές Πανεπιστήμιο της Ελλάδος), Thessaloniki.\n"
            "\n"
            "This document is version v2_post_g_closure (May 2026). "
            "Section 2 was updated to reflect the Phase G closure "
            "(2026-05-24) which removed the planned three-stage "
            "Gemini dialogue and Learning Portrait PDF from the "
            "Epilogue. It will be revised again after IHU IRB review."
        ),
    },
]
