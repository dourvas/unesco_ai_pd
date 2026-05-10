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
