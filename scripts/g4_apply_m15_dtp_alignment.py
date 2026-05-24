"""
Phase G.4 — M15 content alignment with the D.3a dual-signal DTP redefinition.

What this script does
---------------------
Two surgical text replacements on `apps.modules.models.ModuleContent` rows for
M15 (Universal scope):

  - id=925  type=main_content  — replaces:
      Part 2 intro paragraph
      Part 2 "Where you will see your own data" alert
      Part 2 "What the DTP Similarity Score Means" full subsection
      Part 2 "Example: What a Dashboard Looks Like" full subsection
      Part 2 "How to Read Your Development Without Turning It Into a Grade"
      Part 4 Administrative Pragmatism Patch — institutional layer paragraph
      Part 5 closing PROODOS Epilogue alert
      Part 5 Key Takeaways — Epilogue-mention bullet

  - id=958  type=assessment    — replaces:
      Question 4 (the "DTP similarity curve drops at M6" item)
      Question 6 (the "how to read DTP without turning it into a metric" item)

Why
---
The D.3a redefinition (2026-05-18) replaced the single cross-aspect DTP
similarity with two distinct signals — Vertical Continuity Signal (VCS,
same-aspect / one-level-lower) and Temporal Shift Signal (TSS,
consecutive-module). The pilot version is threshold-free, descriptive only,
and presents no three-band continuity label.

The pre-G.4 M15 main_content taught the OLD framing in full (Part 2) and
incidentally still referenced the now-deactivated Aletheia reflective
dialogue (Phase G closure, 2026-05-24). Both alignments land in this one
content edit + RAG re-ingest.

Idempotency
-----------
Each replacement uses str.replace with the exact old block — running twice
no-ops (the second pass finds no match and writes nothing). Each row is
checked for "did any replacement actually happen" before saving; if no
replacement landed, that row is skipped and a warning is printed.

Safety
------
Prerequisite (PI workflow rule): pg_dump backup BEFORE running this script:
    pg_dump unesco_ai_teacher_pd > pre_phaseG_G4_<date>.sql

All edits happen inside a single transaction.atomic() block.

Post-run: re-run ingest_m15_rag.py from project root to refresh embeddings.
"""
import os
import sys

# Bootstrap Django so we can import apps.modules.models from a plain script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from apps.modules.models import ModuleContent  # noqa: E402


# ---------------------------------------------------------------------------
# id=925 main_content — Part 2 intro paragraph
# ---------------------------------------------------------------------------

MC_OLD_PART2_INTRO = '<p>Every time you completed a TAB5 reflection in this platform, something was recorded. Not a grade. Not a score. A semantic trace of your professional thinking at that moment. Fourteen reflections across fourteen modules. Each one compared to the one before it. Each comparison generating a development signal.</p>'

MC_NEW_PART2_INTRO = '<p>Every time you completed a TAB5 reflection in this platform, something was recorded. Not a grade. Not a score. A semantic trace of your professional thinking at that moment. Fourteen reflections across fourteen modules. From M2 onward, each one was positioned in two ways: against the reflection you wrote at the same UNESCO competency aspect one level lower (your <em>vertical</em> development within a competency), and against the immediately preceding module (your <em>focus shift</em> from one module to the next). Two different lenses on the same reflection corpus.</p>'


# ---------------------------------------------------------------------------
# id=925 main_content — "Where you will see your own data" alert
# ---------------------------------------------------------------------------

MC_OLD_WHERE_DATA = '''<div class="alert alert-success mb-6">
    <div>
        <h4 class="font-bold">Where you will see your own data:</h4>
        <p class="text-sm mt-1">The data described in this Part — your DTP similarity curve, your RTM tension trajectories, the themes that defined your reflective writing — is revealed in full in the <strong>PROODOS Epilogue</strong>. The Epilogue is a post-completion dialogic reflection session where Gemini synthesises your entire reflection corpus and opens a three-phase dialogue with you. It is available after M15. Part 5 of this module describes it.</p>
    </div>
</div>'''

MC_NEW_WHERE_DATA = '''<div class="alert alert-success mb-6">
    <div>
        <h4 class="font-bold">Where you will see your own data:</h4>
        <p class="text-sm mt-1">The two DTP signals described in this Part are computed at every module from M2 onward and shown in your TAB5 reflection panels as you go. The synthesis view — your development across all fifteen modules as a single picture, alongside your tension positions and the themes that defined your reflective writing — is revealed in the <strong>PROODOS Epilogue</strong>, the Personal Evolution Dashboard that opens after M15.</p>
    </div>
</div>'''


# ---------------------------------------------------------------------------
# id=925 main_content — "What the DTP Similarity Score Means" full subsection
# Old block includes the 3-band table; new block has 2-panel + "continuity is
# not quality" + non-uniformity table.
# ---------------------------------------------------------------------------

MC_OLD_DTP_SECTION = '''<h3 class="text-xl font-bold mt-8 mb-4">What the DTP Similarity Score Means</h3>

<p class="mb-4">The DTP compares each reflection to the one before it using semantic embedding — a measure of how similar the underlying ideas and concerns are, not just the words. Think of it this way: the system doesn't check whether you used the same words, but whether your ideas pointed in the same direction. The result is a similarity score between 0 and 1, grouped into three continuity levels.</p>

<div class="overflow-x-auto mb-6">
    <table class="table table-zebra w-full text-sm">
        <thead>
            <tr><th>Continuity Level</th><th>Score Range</th><th>What it suggests</th></tr>
        </thead>
        <tbody>
            <tr>
                <td class="font-semibold text-blue-700">High Continuity</td>
                <td>0.75 – 1.0</td>
                <td>Your thinking is building steadily on what came before. You are deepening an existing line of inquiry.</td>
            </tr>
            <tr>
                <td class="font-semibold text-amber-700">Moderate Shift</td>
                <td>0.45 – 0.74</td>
                <td>Something has changed. A new concern has emerged, or an old one has receded. Common at level transitions.</td>
            </tr>
            <tr>
                <td class="font-semibold text-red-700">Significant Shift</td>
                <td>0.0 – 0.44</td>
                <td>Your reflective focus has moved substantially. This isn't a problem — it often marks a genuine turning point.</td>
            </tr>
        </tbody>
    </table>
</div>

<p class="mb-4">Neither high continuity nor significant shift is better. A flat line of high similarity scores could mean stable, deepening expertise — or it could mean that your thinking hasn't been challenged. A dip to significant shift could mark confusion — or the moment a genuinely new understanding arrived. The score is a prompt to reflect, not a verdict.</p>'''

MC_NEW_DTP_SECTION = '''<h3 class="text-xl font-bold mt-8 mb-4">What the Two DTP Signals Show</h3>

<p class="mb-4">The Developmental Trajectory Predictor (DTP) compares the semantic content of your reflections — the underlying ideas and concerns, not the surface words. It produces <strong>two distinct signals</strong>, each answering a different question about your development. Each signal is a cosine similarity between two reflective-text embeddings, presented to you as a short descriptive narrative — not a numeric score.</p>

<div class="grid md:grid-cols-2 gap-4 mb-6">
    <div class="card bg-blue-50 border border-blue-200 p-5">
        <h4 class="font-bold text-blue-900 mb-2">Vertical Continuity Signal (VCS)</h4>
        <p class="text-sm text-blue-900 mb-2"><em>"How has my thinking about <strong>this competency</strong> matured as I moved up a level?"</em></p>
        <p class="text-xs text-blue-800">Compares the current reflection against your reflection at the immediately lower proficiency level in the <strong>same UNESCO aspect</strong>. For example: M8 (Deepen, AI Foundations) compared with M3 (Acquire, AI Foundations). The vertical comparison removes the topic-changes-across-modules noise that would otherwise dominate the comparison.</p>
    </div>
    <div class="card bg-amber-50 border border-amber-200 p-5">
        <h4 class="font-bold text-amber-900 mb-2">Temporal Shift Signal (TSS)</h4>
        <p class="text-sm text-amber-900 mb-2"><em>"How much did my focus move between <strong>this module and the one just before</strong>?"</em></p>
        <p class="text-xs text-amber-800">Compares the current reflection against the reflection at the immediately preceding module (e.g. M8 vs M7). This signal answers "where did my attention shift?" — it is honestly named as a focus-shift measure, not as a developmental measure.</p>
    </div>
</div>

<div class="alert alert-warning mb-6">
    <div>
        <h4 class="font-bold">Continuity is not quality</h4>
        <p class="text-sm mt-1">A high similarity is not "good" and a low similarity is not "bad". A teacher whose Acquire reflection reads "AI generates quizzes" and whose Deepen reflection reads "orchestrating AI within inquiry-based pedagogy" has grown enormously — yet the cosine similarity falls because the vocabulary changed. The DTP <em>describes what shifted</em>; it does not <em>evaluate</em> whether the shift was positive.</p>
    </div>
</div>

<h4 class="font-bold mt-6 mb-3">When each signal is — and isn't — available</h4>

<div class="overflow-x-auto mb-6">
    <table class="table table-zebra w-full text-sm">
        <thead>
            <tr><th>Where you are</th><th>VCS</th><th>TSS</th><th>Why</th></tr>
        </thead>
        <tbody>
            <tr><td class="font-semibold">M1</td><td>—</td><td>—</td><td>No same-aspect lower level; no preceding module.</td></tr>
            <tr><td class="font-semibold">M2–M5 (Acquire)</td><td>—</td><td>shown</td><td>Base of an aspect column: no lower level exists yet. A preceding module exists.</td></tr>
            <tr><td class="font-semibold">M6–M15 (Deepen / Create)</td><td>shown</td><td>shown</td><td>Same-aspect lower level and a preceding module both exist.</td></tr>
        </tbody>
    </table>
</div>

<p class="mb-4 text-sm italic opacity-80">The instrument reports a signal only where the underlying data supports it. Showing a uniform-looking signal everywhere would be more impressive but less honest — and the platform's stance throughout has been to prefer honest evidence over manufactured uniformity.</p>'''


# ---------------------------------------------------------------------------
# id=925 main_content — "Example: What a Dashboard Looks Like" full subsection
# Old block is the SVG curve + reading paragraph; new block is the 2-panel
# illustrative DTP card mockup as described in proposal §4.3.
# ---------------------------------------------------------------------------

MC_OLD_EXAMPLE_DASH = '''<h3 class="text-xl font-bold mt-8 mb-4">Example: What a Dashboard Looks Like</h3>

<div class="alert alert-warning mb-4">
    <div>
        <p class="text-sm">The following is a hypothetical example showing the kind of data the dashboard displays. Your actual dashboard in TAB3 will show your own data.</p>
    </div>
</div>

<div class="card bg-base-100 border border-gray-200 p-4 mb-4">
    <p class="text-sm font-semibold text-gray-600 mb-3">DTP Similarity Curve — Example teacher (Mathematics, Secondary)</p>
    <svg viewBox="0 0 620 200" xmlns="http://www.w3.org/2000/svg" class="w-full">
        <rect width="620" height="200" fill="#f8fafc" rx="8"/>
        <line x1="60" y1="20" x2="60" y2="165" stroke="#e2e8f0" stroke-width="1"/>
        <line x1="60" y1="165" x2="590" y2="165" stroke="#e2e8f0" stroke-width="1"/>
        <text x="50" y="30" text-anchor="end" font-family="sans-serif" font-size="9" fill="#94a3b8">1.0</text>
        <text x="50" y="75" text-anchor="end" font-family="sans-serif" font-size="9" fill="#94a3b8">0.75</text>
        <text x="50" y="110" text-anchor="end" font-family="sans-serif" font-size="9" fill="#94a3b8">0.45</text>
        <text x="50" y="165" text-anchor="end" font-family="sans-serif" font-size="9" fill="#94a3b8">0.0</text>
        <rect x="60" y="20" width="530" height="55" fill="#dbeafe" opacity="0.3"/>
        <rect x="60" y="75" width="530" height="35" fill="#fef3c7" opacity="0.4"/>
        <rect x="60" y="110" width="530" height="55" fill="#fee2e2" opacity="0.3"/>
        <text x="65" y="32" font-family="sans-serif" font-size="8" fill="#3b82f6">High Continuity</text>
        <text x="65" y="88" font-family="sans-serif" font-size="8" fill="#d97706">Moderate Shift</text>
        <text x="65" y="122" font-family="sans-serif" font-size="8" fill="#ef4444">Significant Shift</text>
        <polyline points="98,46 136,52 174,62 212,86 250,110 288,60 326,67 364,49 402,58 440,107 478,55 516,50 554,60 592,42" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linejoin="round"/>
        <circle cx="98" cy="46" r="4" fill="#3b82f6"/>
        <circle cx="136" cy="52" r="4" fill="#3b82f6"/>
        <circle cx="174" cy="62" r="4" fill="#3b82f6"/>
        <circle cx="212" cy="86" r="4" fill="#d97706"/>
        <circle cx="250" cy="110" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5"/>
        <circle cx="288" cy="60" r="4" fill="#3b82f6"/>
        <circle cx="326" cy="67" r="4" fill="#3b82f6"/>
        <circle cx="364" cy="49" r="4" fill="#3b82f6"/>
        <circle cx="402" cy="58" r="4" fill="#3b82f6"/>
        <circle cx="440" cy="107" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="1.5"/>
        <circle cx="478" cy="55" r="4" fill="#3b82f6"/>
        <circle cx="516" cy="50" r="4" fill="#3b82f6"/>
        <circle cx="554" cy="60" r="4" fill="#3b82f6"/>
        <circle cx="592" cy="42" r="5" fill="#15803d" stroke="#ffffff" stroke-width="1.5"/>
        <defs><marker id="arr-m15p2a" markerWidth="6" markerHeight="5" refX="6" refY="2.5" orient="auto"><polygon points="0 0, 6 2.5, 0 5" fill="#ef4444"/></marker></defs>
        <line x1="250" y1="110" x2="250" y2="130" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,2"/>
        <text x="250" y="142" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#ef4444">M6</text>
        <text x="250" y="152" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#94a3b8">Accountability shift</text>
        <line x1="440" y1="107" x2="440" y2="130" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,2"/>
        <text x="440" y="142" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#ef4444">M11</text>
        <text x="440" y="152" text-anchor="middle" font-family="sans-serif" font-size="7.5" fill="#94a3b8">Leadership shift</text>
        <text x="592" y="32" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#15803d">M15</text>
        <text x="98" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M2</text>
        <text x="174" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M4</text>
        <text x="250" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M6</text>
        <text x="326" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M8</text>
        <text x="402" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M10</text>
        <text x="478" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M12</text>
        <text x="554" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M14</text>
        <text x="592" y="177" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#64748b">M15</text>
    </svg>
    <div class="bg-blue-50 rounded p-3 mt-3 text-sm text-blue-800">
        <p class="font-semibold mb-1">Reading this curve:</p>
        <p>This teacher shows stable high continuity across most modules. The two significant dips at M6 (accountability) and M11 (leadership) mark genuine turning points — moments where a new professional concern entered their reflective writing and redirected it. The high score at M15 suggests those threads have been integrated into a coherent professional stance.</p>
    </div>
</div>'''

MC_NEW_EXAMPLE_DASH = '''<h3 class="text-xl font-bold mt-8 mb-4">Example: What a DTP Card Looks Like</h3>

<div class="alert alert-warning mb-4">
    <div>
        <p class="text-sm">The following is a hypothetical example showing how a DTP card appears in TAB5 once a reflection is submitted. Your own cards will use your own reflections.</p>
    </div>
</div>

<div class="card bg-base-100 border border-gray-200 p-5 mb-4">
    <p class="text-sm font-semibold text-gray-700 mb-3">Example: a teacher submits the TAB5 reflection at M8 (AI Foundations, Deepen).</p>

    <div class="grid md:grid-cols-2 gap-4 mb-4">
        <div class="bg-blue-50 border border-blue-200 rounded p-4">
            <p class="text-xs font-bold text-blue-900 uppercase tracking-wide mb-2">Vertical Continuity Signal — M8 vs M3</p>
            <p class="text-xs text-blue-800 italic mb-2">Same competency aspect (AI Foundations), one level lower (Acquire).</p>
            <ul class="text-xs text-blue-900 space-y-1 list-disc list-inside">
                <li>Vocabulary shift: from "tool selection" to "orchestration"</li>
                <li>New focus on prompt iteration as professional craft</li>
                <li>Earlier emphasis on output evaluation has receded</li>
            </ul>
        </div>
        <div class="bg-amber-50 border border-amber-200 rounded p-4">
            <p class="text-xs font-bold text-amber-900 uppercase tracking-wide mb-2">Temporal Shift Signal — M8 vs M7</p>
            <p class="text-xs text-amber-800 italic mb-2">The immediately preceding module (Ethics: Dilemmas in practice).</p>
            <ul class="text-xs text-amber-900 space-y-1 list-disc list-inside">
                <li>Reflective focus has moved from ethical dilemmas to technical craft</li>
                <li>Ethics framing persists in the background but is no longer the centre</li>
            </ul>
        </div>
    </div>

    <div class="bg-gray-50 border border-gray-200 rounded p-4">
        <p class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Narrative synthesis</p>
        <p class="text-sm text-gray-800 italic">"Between M3 and M8 your engagement with AI Foundations has matured from selecting tools to orchestrating them within a planned pedagogical flow. Compared to the immediately preceding ethics module (M7), your focus this week has shifted toward technical craft, with ethical framing in the background. Both shifts describe where your attention is moving — they do not evaluate whether the direction is right."</p>
    </div>
</div>

<p class="mb-4 text-sm opacity-80">During the pilot, no numeric scores or band labels are displayed. The two panels each surface the thematic shifts identified between the compared reflections; the narrative synthesises both signals. After the pilot, calibrated thresholds will allow the researcher to bucket signals into labels for the dissertation analysis — but the teacher-facing presentation will continue to favour descriptive over evaluative language.</p>'''


# ---------------------------------------------------------------------------
# id=925 main_content — "How to Read Your Development Without Turning It Into
# a Grade" subsection
# ---------------------------------------------------------------------------

MC_OLD_HOW_TO_READ = '''<h3 class="text-xl font-bold mt-8 mb-4">How to Read Your Development Without Turning It Into a Grade</h3>

<p class="mb-4">There is a temptation, when confronted with data about yourself, to immediately ask: "Is this good?" The DTP is designed to resist that question.</p>

<p class="mb-4">A low similarity score isn't a failure. A tension that didn't move isn't stubbornness. The data is descriptive, not evaluative. What matters is what <em>you</em> make of it.</p>

<div class="alert alert-warning my-6">
    <div>
        <h4 class="font-bold">Three questions to bring to the PROODOS Epilogue:</h4>
        <ol class="list-decimal ml-4 mt-2 text-sm space-y-1">
            <li>Where did my thinking shift most? What was happening in that module?</li>
            <li>Which tension has stayed with me across the whole journey — and what does that reveal?</li>
            <li>What theme has grown stronger in my reflective writing over time?</li>
        </ol>
    </div>
</div>'''

MC_NEW_HOW_TO_READ = '''<h3 class="text-xl font-bold mt-8 mb-4">How to Read Your Development Without Turning It Into a Grade</h3>

<p class="mb-4">There is a temptation, when confronted with data about yourself, to immediately ask: "Is this good?" The DTP is designed to resist that question. Both signals describe <em>what</em> shifted, never <em>whether</em> the shift was an improvement.</p>

<p class="mb-4">A low similarity at the Vertical Continuity Signal isn't a failure — it can mean your thinking about a competency has moved to a fundamentally different vocabulary as it matured. A tension that didn't move isn't stubbornness. The data is descriptive, not evaluative. What matters is what <em>you</em> make of it.</p>

<div class="alert alert-warning my-6">
    <div>
        <h4 class="font-bold">Three questions to bring to the PROODOS Epilogue:</h4>
        <ol class="list-decimal ml-4 mt-2 text-sm space-y-1">
            <li>At which module did the Vertical Continuity Signal report the largest vocabulary shift — and what was happening in your professional reading of that aspect at that level?</li>
            <li>Which tension has stayed with you across the whole journey — and what does that reveal?</li>
            <li>What theme has grown stronger in your reflective writing over time?</li>
        </ol>
    </div>
</div>'''


# ---------------------------------------------------------------------------
# id=925 main_content — Part 4 Administrative Pragmatism Patch institutional
# layer paragraph
# ---------------------------------------------------------------------------

MC_OLD_ADMIN_INST = '<p class="text-sm mb-3"><strong>The institutional layer.</strong> This module\'s own design dashboards (Part 2: Developmental Trajectory Predictor and Reflective Tension Mapper) and the closing Epilogue dialogue are themselves administrative AI streamlining — for the CPD pathway you are completing right now. PROODOS demonstrates at programme level what these three classroom examples demonstrate at teacher level: AI handles structured, repeatable work; humans retain judgement on what matters.</p>'

MC_NEW_ADMIN_INST = '<p class="text-sm mb-3"><strong>The institutional layer.</strong> This module\'s own design dashboards (Part 2: the two-signal Developmental Trajectory display and the Reflective Tension Mapper) and the closing PROODOS Epilogue synthesis are themselves administrative AI streamlining — for the CPD pathway you are completing right now. PROODOS demonstrates at programme level what these three classroom examples demonstrate at teacher level: AI handles structured, repeatable work; humans retain judgement on what matters.</p>'


# ---------------------------------------------------------------------------
# id=925 main_content — Part 5 closing PROODOS Epilogue alert
# ---------------------------------------------------------------------------

MC_OLD_EPILOGUE_ALERT = '''<div class="alert alert-success my-6">
    <div>
        <h4 class="font-bold">↓ PROODOS Epilogue — optional, after M15</h4>
        <p class="text-sm mt-1">After completing M15, you have the option to engage in the PROODOS Epilogue — a dialogic reflection session where Gemini synthesises your entire learning journey across all fifteen modules. The Epilogue is a three-phase Socratic dialogue — Look Back, Look In, Look Forward — that ends with a personalised Learning Portrait generated from your reflection corpus. It is not part of the assessed programme. It is an invitation to go one step further.</p>
    </div>
</div>'''

MC_NEW_EPILOGUE_ALERT = '''<div class="alert alert-success my-6">
    <div>
        <h4 class="font-bold">↓ PROODOS Epilogue — after M15</h4>
        <p class="text-sm mt-1">After completing M15, you reach the PROODOS Epilogue — a Personal Evolution Dashboard that brings together the trajectory of your reflective writing, the developmental signals from your DTP cards across all modules, and the tension positions you held throughout the journey. It is a synthesis surface, not a new assessment. From there you continue to the closing AILST measurement.</p>
    </div>
</div>'''


# ---------------------------------------------------------------------------
# id=925 main_content — Part 5 Key Takeaway bullet that mentions Epilogue
# dialogue
# ---------------------------------------------------------------------------

MC_OLD_KEY_TAKEAWAY = '<li>The PROODOS Epilogue will show you what fifteen modules of reflection look like as data — and open a dialogue about what it means</li>'

MC_NEW_KEY_TAKEAWAY = '<li>The PROODOS Epilogue presents what fifteen modules of reflection look like as data — your Personal Evolution Dashboard</li>'


# ---------------------------------------------------------------------------
# id=958 assessment — Question 4 (old DTP curve / 0.44 drop / three-band)
# ---------------------------------------------------------------------------

ASS_OLD_Q4 = '''  {
    "id": 4,
    "text": "A teacher's DTP similarity curve shows a significant drop (score below 0.44) at M6. What is the most accurate interpretation?",
    "options": {
      "A": "The teacher failed to engage meaningfully — low similarity at any point is a reliable indicator that the reflection did not meet the expected standard for that module level in the programme",
      "B": "The quality of the teacher's written reflection declined, suggesting fatigue or disengagement at that stage",
      "C": "A technical error in the embedding calculation produced an artificially low similarity score for that particular module",
      "D": "The teacher's reflective focus shifted — a likely turning point"
    },
    "correct": "D",
    "explanation": "Options A and B both interpret low similarity as failure or decline. Option C attributes it to technical error. All three read the data evaluatively — they treat low scores as bad. The module is explicit: the DTP is descriptive, not evaluative. A significant shift below 0.44 means the reflective content moved substantially from the previous reflection — new concerns entered, old concerns receded, or a genuinely new understanding arrived. M6, which introduces the accountability dimension of AI, is exactly the kind of module where professional thinking shifts. A dip here is pedagogically meaningful — it is evidence that something changed, not evidence of failure."
  }'''

ASS_NEW_Q4 = '''  {
    "id": 4,
    "text": "At M8, a teacher's Vertical Continuity Signal panel reports very different vocabulary between M3 and M8 — the two reflections look semantically distant. What is the most accurate interpretation?",
    "options": {
      "A": "The teacher's M8 reflection failed to build on what they had written at M3 and the gap indicates weak engagement with the same UNESCO competency aspect",
      "B": "A technical error in the embedding calculation produced an artificially low similarity for that comparison and the result should be discarded",
      "C": "The teacher's vocabulary about this competency has shifted — possibly because their thinking has matured into a different conceptual register as they moved from Acquire to Deepen",
      "D": "The teacher should revisit M3 and rewrite their reflection there to better match what they wrote at M8 so that the curve regains continuity"
    },
    "correct": "C",
    "explanation": "Options A and D treat low semantic similarity as a defect — something the teacher should fix. Option B attributes it to technical error. All three read the data evaluatively. The redefined DTP is explicit: the Vertical Continuity Signal describes how the teacher's thinking about the same UNESCO competency aspect has shifted as they moved up a level, and a low similarity is just as likely to mark genuine maturation as it is to mark anything else. A teacher whose Acquire reflection reads 'AI generates quizzes' and whose Deepen reflection reads 'orchestrating AI within inquiry-based pedagogy' has grown enormously — yet the cosine similarity falls because the vocabulary changed. Continuity is not quality."
  }'''


# ---------------------------------------------------------------------------
# id=958 assessment — Question 6 (old DTP performance-metric question)
# ---------------------------------------------------------------------------

ASS_OLD_Q6 = '''  {
    "id": 6,
    "text": "Which of the following best describes how to read DTP data without turning it into a performance metric?",
    "options": {
      "A": "Ignore low scores and focus on the overall upward trend across all modules",
      "B": "Compare scores to the cohort average to check whether development is typical of the group",
      "C": "Treat high continuity as strong learning and significant shift as evidence of weak module engagement throughout the sequence from M1 to M15 of the professional development programme",
      "D": "Use the data as a prompt for reflection — asking where shifts occurred and what they reveal"
    },
    "correct": "D",
    "explanation": "Options A, B, and C all treat the DTP as a performance signal in different ways — ignoring low scores, comparing to averages, or mapping continuity levels onto quality judgments. The module explicitly resists all of these moves. Neither high continuity nor significant shift is better. A flat line of high similarity could mean deepening expertise or a thinking that hasn't been challenged. A dip could mark confusion or a genuine turning point. The data becomes valuable when it is used as a reflective prompt — 'where did my thinking shift most, and what was happening at that point?' — not as a score to be maximised or defended."
  }'''

ASS_NEW_Q6 = '''  {
    "id": 6,
    "text": "Which of the following best describes how to read the two DTP signals during the PROODOS pilot?",
    "options": {
      "A": "Add the two similarity values together to get an overall development score per module so that progress can be tracked numerically across the sequence",
      "B": "Treat the Vertical Continuity Signal as the primary signal and ignore the Temporal Shift Signal because it is just a relabelling of the original cross-aspect DTP comparison",
      "C": "Read each signal as a separate descriptive lens — the VCS for within-competency development, the TSS for focus shift between consecutive modules — and resist any move that turns either into a numeric grade",
      "D": "Compare your own signals to a cohort average reported by the platform to check whether your trajectory is typical for teachers at your subject and grade level"
    },
    "correct": "C",
    "explanation": "Options A, B, and D all reduce the dual-signal design to a single score in different ways — by summing, by privileging one, or by ranking against a cohort. The redefinition was made precisely to avoid all three moves. The two signals answer different questions ('how has my thinking about this competency matured?' vs 'how much did my focus shift since the last module?') and are different research variables. Reading them together — each as descriptive evidence in its own register — is what the pilot version supports. The pilot deliberately shows no three-band continuity labels and no numeric scores; calibrated thresholds will be derived from pilot data and only used in the post-pilot research analysis."
  }'''


# ---------------------------------------------------------------------------
# Edit recipes
# ---------------------------------------------------------------------------

MAIN_CONTENT_EDITS = [
    ('Part 2 intro paragraph', MC_OLD_PART2_INTRO, MC_NEW_PART2_INTRO),
    ('Part 2 "Where you will see your own data" alert', MC_OLD_WHERE_DATA, MC_NEW_WHERE_DATA),
    ('Part 2 "What the DTP Similarity Score Means" -> dual-signal section', MC_OLD_DTP_SECTION, MC_NEW_DTP_SECTION),
    ('Part 2 SVG dashboard example -> 2-panel DTP card mockup', MC_OLD_EXAMPLE_DASH, MC_NEW_EXAMPLE_DASH),
    ('Part 2 "How to Read Your Development" subsection', MC_OLD_HOW_TO_READ, MC_NEW_HOW_TO_READ),
    ('Part 4 Administrative Pragmatism institutional-layer paragraph', MC_OLD_ADMIN_INST, MC_NEW_ADMIN_INST),
    ('Part 5 closing PROODOS Epilogue alert', MC_OLD_EPILOGUE_ALERT, MC_NEW_EPILOGUE_ALERT),
    ('Part 5 Key Takeaway bullet (Epilogue dialogue)', MC_OLD_KEY_TAKEAWAY, MC_NEW_KEY_TAKEAWAY),
]

ASSESSMENT_EDITS = [
    ('Question 4 — DTP curve drop -> VCS vocabulary shift', ASS_OLD_Q4, ASS_NEW_Q4),
    ('Question 6 — DTP performance metric -> two-signal pilot reading', ASS_OLD_Q6, ASS_NEW_Q6),
]


def apply_edits(row_id: int, label: str, edits: list[tuple[str, str, str]]) -> bool:
    row = ModuleContent.objects.get(pk=row_id)
    text = row.content_data
    applied = []
    not_found = []
    for name, old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append(name)
        else:
            not_found.append(name)
    if not_found:
        print(f'[{label}] WARNING — not found in current content (idempotent skip likely):')
        for n in not_found:
            print(f'  - {n}')
    if not applied:
        print(f'[{label}] No edits applied (already at new state?); row unchanged.')
        return False
    print(f'[{label}] {len(applied)} edit(s) applied:')
    for n in applied:
        print(f'  + {n}')
    print(f'[{label}] length: {len(row.content_data)} -> {len(text)} chars')
    row.content_data = text
    row.save(update_fields=['content_data', 'updated_at'])
    return True


def main():
    with transaction.atomic():
        print('=== id=925 main_content ===')
        apply_edits(925, 'main_content', MAIN_CONTENT_EDITS)
        print()
        print('=== id=958 assessment ===')
        apply_edits(958, 'assessment', ASSESSMENT_EDITS)
        print()
        print('All edits committed inside one transaction.')


if __name__ == '__main__':
    main()
