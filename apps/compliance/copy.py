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
