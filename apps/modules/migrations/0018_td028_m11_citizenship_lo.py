"""
Phase H TD-028 follow-up — M11 5th learning objective.

Recognises the three Tier 1 patches that closed M11's pre-audit
PARTIAL flags but were not reflected in the post-TD-028 LO array:

  - citizenship_apr2026 (Part 4) — Teacher as Citizen with 3 Rights
    + 3 Obligations; closed CG1.3.3 / LO1.3.3.
  - commercial_apr2026 (Part 1) — "When AI Becomes a Product" + AI
    Sycophancy named mechanism; closed CG1.3.1.
  - accessibility_bridge_apr2026 (Part 3) — AI as Accessibility
    Bridge SVG with equity framework.

The post-TD-028 audit re-read (TD-028 final consolidated pass)
flagged this as a medium-priority enhancement: the existing 4 LOs
cover Parts 2-5 of the matrix but do not surface the three Tier 1
substantive closures. A single 5th LO bundles all three under the
"AI citizenship + commercial-AI critique + accessibility bridge"
framing so the LO array matches the module's actual taught content.

Reversible: the prior 4-item array is recorded inline.

Reference:
  - proodos_files/CONTENT_VALIDATION_MATRIX.md (M11 section)
  - migration 0017 (TD-028 main TAB1 audit content updates)
"""

from django.db import migrations


M11_LO_BEFORE = [
    'Communicate a clear, credible professional position on AI to parents and community',
    'Apply subject-specific strategies for building AI-literate students',
    'Map stakeholders and design a low-stakes proposal for school-level AI change',
    'Complete a personal AI Stance Canvas as a leadership tool',
]

M11_LO_AFTER = [
    'Communicate a clear, credible professional position on AI to parents and community',
    'Apply subject-specific strategies for building AI-literate students',
    'Map stakeholders and design a low-stakes proposal for school-level AI change',
    'Complete a personal AI Stance Canvas as a leadership tool',
    'Engage with teacher AI citizenship — three Rights and three '
    'Obligations — alongside critical awareness of commercial AI '
    'mechanisms (the sycophancy economy) and AI as an accessibility '
    'bridge for inclusive practice',
]


def apply_m11_lo(apps, schema_editor):
    Module = apps.get_model('modules', 'Module')
    try:
        m = Module.objects.get(code='M11')
    except Module.DoesNotExist:
        return
    m.learning_objectives = M11_LO_AFTER
    m.save()


def revert_m11_lo(apps, schema_editor):
    Module = apps.get_model('modules', 'Module')
    try:
        m = Module.objects.get(code='M11')
    except Module.DoesNotExist:
        return
    m.learning_objectives = M11_LO_BEFORE
    m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0017_td028_tab1_audit_content_updates'),
    ]

    operations = [
        migrations.RunPython(apply_m11_lo, revert_m11_lo),
    ]
