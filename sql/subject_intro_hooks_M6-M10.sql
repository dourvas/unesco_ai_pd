-- ============================================================================
-- SUBJECT INTRO HOOKS — M6 to M10 (Deepen Level)
-- ============================================================================
-- Phase 4b of Subject Intro Hooks rollout
-- Records inserted: 85 (5 modules × 17 entries: 16 subjects + Universal)
-- Source: RESISTANCE_MATRIX_M6-M10.md (Phase 3 deliverable)
-- Spec: SUBJECT_INTRO_HOOKS_PATCH_APR2026.md
-- ============================================================================
-- Run order: M1-M5 FIRST, then THIS file, then M11-M15
-- Run via pgAdmin Query Tool against the PROODOS database
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- Idempotency: clear any existing subject_intro records for M6-M10
-- ----------------------------------------------------------------------------
DELETE FROM modules_modulecontent
WHERE content_type = 'subject_intro'
  AND module_id IN (SELECT id FROM modules_module WHERE code IN ('M6','M7','M8','M9','M10'));


-- ============================================================================
-- M6 — Human-Centred AI: Identity and Values
-- ============================================================================

-- M6 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Identity questions are for humanities people. Mathematics is content-driven.</p>
    <p class="text-sm mb-2">Mathematics teaching is full of identity work: who's "a maths person", who isn't, who gets called intuitive vs procedural. AI surfaces these labels in new ways, through recommendation systems, automated grading, and learning analytics.</p>
    <p class="text-sm">You'll get a frame for noticing where AI tools are quietly making identity judgements about your students. Before those judgements harden into tracking decisions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI threatens what you do. Talking about identity won't change the threat.</p>
    <p class="text-sm mb-2">The threat is real, and the identity question is exactly what helps you respond. What part of writing instruction is irreducibly yours? Once you can name it, you can defend it from automation.</p>
    <p class="text-sm">You'll find language to articulate what you bring that AI doesn't. Useful for parent meetings, department conversations, and your own confidence on hard days.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science teaching is about evidence and method. Identity is sociology.</p>
    <p class="text-sm mb-2">Method is identity, in disguise. The scientist's stance — sceptical, evidence-based, transparent about uncertainty — is what separates a science teacher from an AI delivering science facts.</p>
    <p class="text-sm">You'll find a way to teach the scientific stance, not just the scientific content. AI works as a useful contrast that makes the stance visible.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics is the same whether a human or AI explains it. Identity isn't part of the equation.</p>
    <p class="text-sm mb-2">It is, in two places: how you choose what to teach (curriculum is values), and how you teach failure productively (AI confidently fails physics, you don't). Both are deeply human moves.</p>
    <p class="text-sm">You'll come away with recognition of where physics teaching depends on you specifically. Your selection, your handling of uncertainty. That remains irreducibly human.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry is dangerous when wrong. Identity questions feel like distraction.</p>
    <p class="text-sm mb-2">Safety culture is identity. The teacher who builds careful chemistry practice in students is teaching a way of being, not just a list of rules. AI doesn't transmit ethos; it transmits content.</p>
    <p class="text-sm">You'll get a frame for understanding chemistry teaching as ethos transmission. That protects what you do from being seen as content-delivery that AI could replace.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Identity is psychology, not biology. You teach the biology of organisms, not professional self-reflection.</p>
    <p class="text-sm mb-2">Biology teachers shape how students view their own bodies, their place in nature, their species' future. Identity is unavoidable in biology classrooms; AI just pushes the question into the open.</p>
    <p class="text-sm">You'll get tools for handling identity-laden topics in biology — body image, gender, race in genetics, environmental ethics — alongside AI's increasing presence in those discussions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Historians teach about identity all the time. Probably old territory for you.</p>
    <p class="text-sm mb-2">Likely true for student identity in historical context. Less covered: your own identity as a teacher in the AI moment. Are you a curator? An interpreter? A guide through contested narratives? AI forces the question.</p>
    <p class="text-sm">You'll get direct engagement with your own identity as a history teacher in the AI era. Useful for departmental conversations and for your own choice of stance.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography is about places and people, not professional self-image.</p>
    <p class="text-sm mb-2">Geography teachers regularly help students locate themselves: in a city, a region, a global system. The same skills apply to locating yourself as a teacher in the AI ecosystem. What's local, what's global, what's automated, what's irreplaceable.</p>
    <p class="text-sm">You'll get a geographically inflected identity exercise, drawing on your existing skill of helping students situate themselves spatially and culturally.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Translation tools keep getting better. Your identity as a language teacher feels under siege.</p>
    <p class="text-sm mb-2">Under siege is exactly the right description, which is why this module exists. The path through is articulating what you do that translation tools don't: relationship, motivation, error-as-learning, cultural transmission. None of that is automated.</p>
    <p class="text-sm">You'll find a defended position on your professional value, drawn from explicit features of language teaching that AI doesn't replicate. Useful for your own resilience.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Identity is core to your curriculum. This module sounds like content you already deliver.</p>
    <p class="text-sm mb-2">You deliver student identity work skilfully. Less likely is that you've systematically considered your own — as a social studies teacher whose subject is being reshaped by AI surveillance, AI bias, AI-generated political content. Your students will need your stance.</p>
    <p class="text-sm">You'll get time to articulate your own positioning on AI in your subject area. Before students push the question and you respond from improvisation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">As a CS teacher, your professional identity is closer to the AI than to humanities teachers. This module isn't really for you.</p>
    <p class="text-sm mb-2">It is, with a twist. CS teachers are increasingly asked to be the ethical voice in their school's AI conversations — a role most weren't prepared for. Identity-as-CS-teacher needs renegotiation as the field shifts.</p>
    <p class="text-sm">You'll get a framework for handling the new ethical-spokesperson role that CS teachers find themselves in. Distinct from the technical role.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE is bodies, sport, presence. Identity in AI era? Hard to see the connection.</p>
    <p class="text-sm mb-2">PE is one of the few subjects where AI struggles to replace anything central. Movement coaching, team dynamics, body confidence — all human. That position is rare and worth understanding.</p>
    <p class="text-sm">You'll come to recognise PE's particular AI-resilience. Useful for your own confidence and for advocating for the subject's value when curriculum decisions get made.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Art is about human expression. AI's encroachment is exactly what you're trying to resist.</p>
    <p class="text-sm mb-2">Resistance is one stance; the module helps you articulate it as a defended position, not a default reaction. What about your art teaching is irreducibly human, and how do you communicate that to students who'll be told otherwise online?</p>
    <p class="text-sm">You'll get a clear, articulable position on human creativity in your classroom. Robust to the inevitable "but ChatGPT can do that" challenge.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Your identity as an SEN teacher is already clear: advocate, individualiser, careful presence. You don't need a module on it.</p>
    <p class="text-sm mb-2">Probably not. But AI tools will increasingly be sold as solutions for your students. Your identity as the irreplaceable individualiser is exactly what protects students from over-automated provision.</p>
    <p class="text-sm">You'll get reinforcement of professional ground you already stand on. Vocabulary for resisting automation pressure that will only grow.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years is human-centred by definition. This module is preaching to the choir.</p>
    <p class="text-sm mb-2">Possibly, but worth checking. Even in early years, AI products are expanding: voice assistants in classrooms, automated literacy tracking, "personalised" learning apps for three-year-olds. Your human-centred identity gets tested in concrete decisions.</p>
    <p class="text-sm">You'll get concrete criteria for testing AI-product proposals against your human-centred stance. Rather than relying on instinct alone.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're the relationship adult for 25 children all day. Your identity isn't in question; your time is.</p>
    <p class="text-sm mb-2">Your identity is exactly what's at stake when AI tools are pitched as efficiency aids that "free time for relationship building." What if the time saved by AI is the time of relationship building, in disguise?</p>
    <p class="text-sm">You'll get a clear-eyed look at AI efficiency claims in primary settings. Attention to whether the "saved" time is in fact relational time being relocated, not freed.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';

-- M6 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Identity work feels like a soft module without practical output.</p>
    <p class="text-sm mb-2">This module's output is your stance: what you defend, what you concede, what you delegate. Without a stance, AI integration decisions get made by inertia and vendor pressure.</p>
    <p class="text-sm">You'll come away with a defended stance on your role in AI-augmented teaching. Useful for any decision involving AI in your classroom from now on.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M6';


-- ============================================================================
-- M7 — Applied AI Ethics in Classroom Practice
-- ============================================================================

-- M7 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Maths is unaffected by ethics in daily lessons. Where do you apply this?</p>
    <p class="text-sm mb-2">Daily applications: deciding whether to allow AI for homework, handling the student who used it without saying, choosing whether to use AI-generated problem sets you can't fully verify. All concrete, all this week.</p>
    <p class="text-sm">You'll get classroom decision rules for the specific AI ethics moments that arise in maths teaching. Ready for use without further translation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">This module will be all about AI-written essays. You've heard it.</p>
    <p class="text-sm mb-2">The essay question is in here, but it's one of many. Also covered: AI as a feedback partner, voice authenticity in AI-assisted drafts, student peer review when some peers use AI, parents asking why you "can't just check with ChatGPT."</p>
    <p class="text-sm">You'll get a wider repertoire of classroom ethics decisions in writing instruction. Beyond the single essay-detection conversation that dominates the field.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science ethics is in the curriculum. This module risks being repetitive.</p>
    <p class="text-sm mb-2">Curriculum ethics is general (animal testing, climate). Classroom ethics is specific (which AI claims do you check, how do you handle a student who AI-generated a lab report). Different territory.</p>
    <p class="text-sm">You'll get classroom-specific ethical decisions in science teaching. Distinct from the curricular ethics already covered.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics has unambiguous answers. Ethics needs ambiguous problems. Strange fit.</p>
    <p class="text-sm mb-2">Classroom physics has plenty of ambiguity: which student work to trust, how to handle a confident-but-wrong AI explanation a student presents, when to allow AI for problem-checking. Operational, not theoretical.</p>
    <p class="text-sm">You'll get decision rules for the operational ethics moments in physics teaching, where the answer isn't predetermined.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You worry about students using AI to generate dangerous-knowledge essays. What's the protocol?</p>
    <p class="text-sm mb-2">Exactly the kind of case the module covers, alongside related concerns: AI giving wrong safety information, students fact-checking your safety teaching against ChatGPT, how to handle "but AI says it's fine" moments.</p>
    <p class="text-sm">You'll get a protocol for the chemistry-specific AI safety moments that the general module wouldn't anticipate.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You want concrete classroom rules, not more principle-talk.</p>
    <p class="text-sm mb-2">This module is rules. When to allow, when to forbid, what to do when a student crosses the line, how to handle the student who only crossed because they didn't understand the line.</p>
    <p class="text-sm">You'll get classroom rules for AI in biology learning, drafted as actual rules and not as ethical considerations.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">History ethics is rich and old. New AI cases will fit existing frameworks.</p>
    <p class="text-sm mb-2">Mostly true. The specifically new cases: AI-generated primary sources presented as real, students using AI to "interview" historical figures, AI-fabricated quotes in essays. Worth handling explicitly.</p>
    <p class="text-sm">You'll get history-specific cases that don't quite fit existing frameworks. Proposed handling drawn from your existing ethical literacy.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geographic ethics is mostly about field ethics and respect for places. Less obvious AI angle.</p>
    <p class="text-sm mb-2">AI angle: location data privacy in fieldwork, AI-generated maps presented as accurate, automated demographic analysis that reproduces stereotypes. All operational classroom issues.</p>
    <p class="text-sm">You'll get classroom rules for geographic AI work. Focused on fieldwork prep, mapping projects, and analysis using AI tools.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">"Translation cheating" will dominate this module. You've already settled your position.</p>
    <p class="text-sm mb-2">Cheating is one cell. Other cells: AI as a pronunciation coach (when it's accurate, when it isn't), AI's cultural-flattening tendency in language production, students using AI to "check" your corrections.</p>
    <p class="text-sm">You'll come across wider ground beyond the cheating debate. Including useful AI uses you may not yet have policy for.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Social studies has the strongest ethical curriculum. This module risks duplicating.</p>
    <p class="text-sm mb-2">Curricular ethics covers what students study. Teacher ethics covers what you do — your AI use, your tool selection, your data sharing with vendors. Different layer.</p>
    <p class="text-sm">You'll get teacher-side ethical practice in your subject. Complementary to (not replacing) the strong curricular ethics you already deliver.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You teach AI ethics. You might be teaching this module's content already.</p>
    <p class="text-sm mb-2">Possibly. The module's specific contribution is the teacher-as-decision-maker frame: when you decide to deploy AI in your CS classroom, what factors weigh?</p>
    <p class="text-sm">You'll get a teacher-decision framework distinct from the developer-decision framework you likely already teach. Useful for your own pedagogical AI choices.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE rarely has classroom AI ethics moments. You're outside, mostly moving.</p>
    <p class="text-sm mb-2">AI is moving outside too: fitness apps logging student data, video analysis tools, body composition scanners. Each is an ethics decision before it's a pedagogical one.</p>
    <p class="text-sm">You'll get decision rules for the AI products that vendors increasingly target at PE departments. Before your school adopts them by default.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Image-generation ethics is the obvious topic. Will the module say anything new?</p>
    <p class="text-sm mb-2">Image generation is one cell among several. Others: AI critique of student work (whose values?), AI-generated reference images masquerading as real artists, students "improving" peer work with AI between feedback rounds.</p>
    <p class="text-sm">You'll get a wider ethics map for art classroom AI. Beyond the well-trodden image-generation debate.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">SEN students are most affected by AI ethics failures. You want practice tools, not principles.</p>
    <p class="text-sm mb-2">Tools are what's here: how to evaluate AI accessibility tools before adopting, how to handle data-collection consent for students with limited capacity to consent, what to do when an AI tool works for most students but fails for one.</p>
    <p class="text-sm">You'll get operational practice tools for the AI ethics situations specific to special education, where the stakes are higher than the general module conveys.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Ethics in early years is foundational and constant. Adding AI is unnecessary complication.</p>
    <p class="text-sm mb-2">AI products targeting under-fives are a fast-growing market. Your ethics work is already foundational, but it needs new vocabulary to evaluate these products specifically.</p>
    <p class="text-sm">You'll get early-years-specific evaluation tools for AI products marketed to your setting. Building on your existing ethics practice.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You make 50 small ethics decisions every day across five subjects. You can't add an AI ethics layer to every one.</p>
    <p class="text-sm mb-2">You won't. The module gives you a small set of cross-subject decision rules that apply to AI ethics. So the layer is one rule applied many times, not many rules.</p>
    <p class="text-sm">You'll get a short, reusable set of AI ethics decision rules for primary classrooms. Designed to integrate into your existing ethics-handling rather than parallel it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';

-- M7 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Applied ethics modules tend to be case studies that don't quite match your situation.</p>
    <p class="text-sm mb-2">Cases here are categorised by decision type, not by surface details, so the underlying logic transfers across contexts.</p>
    <p class="text-sm">You'll get decision rules organised by type. Reusable across the specific ethics situations you'll face that this module won't have predicted.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M7';


-- ============================================================================
-- M8 — Reflective Prompt Engineering: Deepening Practice
-- ============================================================================

-- M8 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You've prompted AI for maths help. It gets things wrong, sometimes confidently. Deeper practice won't fix the underlying problem.</p>
    <p class="text-sm mb-2">Right; deeper prompting doesn't make AI a mathematician. It makes you a better diagnostician of when the AI's mathematical output is useful and when it's not. It lets you produce reliable maths-classroom material consistently.</p>
    <p class="text-sm">You'll get a diagnostic eye for AI maths output. Plus a workflow for producing reliable problem variations and explanations through controlled prompting.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">As a writer, you should be good at prompting. If your prompts aren't producing what you want, the tool's at fault.</p>
    <p class="text-sm mb-2">Sometimes. More often, prompting is a different genre with conventions you haven't yet learned — closer to drafting a brief for a difficult intern than to writing prose. The seven strategies make those conventions explicit.</p>
    <p class="text-sm">You'll get genre-specific writing skills for prompts. Drawing on your existing writing strength but adding the AI-specific moves you may have been missing.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Effective prompting must be experimental. You don't have time for systematic experiments on every lesson prep task.</p>
    <p class="text-sm mb-2">Hands-on prompting in this module isn't open-ended experimentation; it's structured iteration with feedback at each step. Closer to a focused inquiry than to research design.</p>
    <p class="text-sm">You'll get a small, structured iteration workflow that produces working prompts in minutes. Not the open-ended experiments you reasonably want to avoid.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You tried complex prompts. The AI lost the thread halfway through. Deeper prompting probably hits the same wall.</p>
    <p class="text-sm mb-2">It does, and the module names the wall: context windows, attention attenuation, drift over long generations. Deeper prompting is partly about not building prompts that the wall will defeat.</p>
    <p class="text-sm">You'll come away with awareness of where the AI's limits actually live. So you build prompts that work within them rather than struggling against them.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You want repeatable prompts. AI's variability defeats reuse.</p>
    <p class="text-sm mb-2">Variability is reduced by tighter context-setting (one of the seven strategies) and by lower temperature settings where the tool allows. Both covered hands-on.</p>
    <p class="text-sm">You'll get specific moves to reduce AI variability where it matters in chemistry teaching. The trade-offs (less creative output) made explicit.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Detailed biology prompts produce confident wrong answers. The pattern is consistent.</p>
    <p class="text-sm mb-2">Consistent with what AI is built for: producing plausible-sounding text. The module's deeper practice teaches you to constrain the output to verification-friendly forms (cite-or-decline, structured) rather than free generation.</p>
    <p class="text-sm">You'll get output constraints that route AI toward forms you can verify quickly. Reducing the confident-wrong-answer problem in your prep work.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI hallucinates dates, names, sources. No prompting strategy fixes that.</p>
    <p class="text-sm mb-2">True for content generation. The module's history applications focus on prompts that work on text you provide (analysis, comparison, differentiation) rather than prompts that ask AI to recall.</p>
    <p class="text-sm">You'll get a division of prompt types — generation vs analysis-on-source — with classroom uses in each. Grounded in what AI can actually do reliably.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography prompts hit AI's localism gap fast. Hard to make them useful.</p>
    <p class="text-sm mb-2">Localism is one limit; others matter too. The module's deeper practice teaches you to prompt for transferable structures (e.g., "ways to approach studying any river system") rather than local content.</p>
    <p class="text-sm">You'll get geographic prompting that works across locations because it asks for analytical structures, not local facts AI may not know.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multilingual prompting introduces extra failure modes. Probably more frustration than payoff.</p>
    <p class="text-sm mb-2">Multilingual prompting is genuinely harder. The module addresses it: prompting in the target language vs prompting about the target language, when each works, and how to handle the unreliability gracefully.</p>
    <p class="text-sm">You'll get specific moves for prompting in multilingual contexts. Realistic expectations about which use cases pay off and which don't.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompting's appearance of neutrality hides political choices. Deepening the practice deepens that problem.</p>
    <p class="text-sm mb-2">Right, and the module engages with it. The seven strategies' framing as reflective practice surfaces value-laden choices (audience, format, framing) rather than hiding them.</p>
    <p class="text-sm">You'll get awareness of which prompting moves carry political weight. Useful for your subject and for your own resistance to seemingly neutral AI workflows.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You know prompting techniques. EduPrompt Studio looks like a wrapper.</p>
    <p class="text-sm mb-2">It's a wrapper, but with a specific function: enforcing the seven strategies as a habit-formation tool for non-CS teachers. Worth looking at as a teaching artefact, regardless of whether you'd use it personally.</p>
    <p class="text-sm">You'll get a view of EduPrompt Studio as a pedagogy-of-prompting tool. Useful when you're asked to support colleagues' AI work in your school.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Hands-on prompting practice is desk-bound. PE is the wrong context.</p>
    <p class="text-sm mb-2">Prep is desk-bound. The deeper practice produces better warm-up variations, drill rotations, parent communications about sport injuries. Quick-payback at the desk.</p>
    <p class="text-sm">You'll get specific PE-prep prompting recipes that pay off in saved time at the desk. Leaving more time for the field.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Image generation prompting must dominate this. You'd rather not.</p>
    <p class="text-sm mb-2">This module is text-prompting. Image generation is M13. Text-prompting for art teaching: writing critique scaffolds, drafting artist research questions, generating gallery-tour discussion prompts.</p>
    <p class="text-sm">You'll get text-only prompting practice for art classrooms. Leaving the image-generation question entirely separate.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Generic prompt examples don't translate to your students. Deepening practice probably means deeper generic.</p>
    <p class="text-sm mb-2">The module's deepen practice includes constraint-heavy prompting — exactly what SEN-specific work needs. You define audience precisely, set cognitive load constraints, specify accessibility requirements explicitly.</p>
    <p class="text-sm">You'll get constraint-heavy prompting techniques tuned to specific SEN needs. Replacing the generic outputs of casual prompting.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompts produce text designed for older audiences. Adapting it for under-fives is more work than writing from scratch.</p>
    <p class="text-sm mb-2">Adapting for under-fives is exactly what the audience-specification strategy makes possible. With explicit audience constraints — language a 4-year-old uses, no abstract nouns, no metaphor — the output becomes useable.</p>
    <p class="text-sm">You'll get a small set of early-years-specific prompt templates that produce content at the right developmental level. Instead of needing rewrite from scratch.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You tried prompting. Half the time the output needed more editing than writing from scratch would have. You're done.</p>
    <p class="text-sm mb-2">"More editing than writing" is usually a sign of weak context-setting in the prompt. The deeper practice fixes this. By front-loading subject, age, and purpose, the output lands closer to usable on first attempt.</p>
    <p class="text-sm">You'll find prompting moves that reduce edit time below write-time. The only standard that matters for a teacher with five subjects to plan.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';

-- M8 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompting practice modules tend to be theoretical or to cover only easy cases.</p>
    <p class="text-sm mb-2">This module is hands-on with hard cases. EduPrompt Studio enforces the seven strategies, surfacing what your prompts are missing.</p>
    <p class="text-sm">You'll get hands-on practice with structured feedback. Producing prompts you can keep and adapt for your subject.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M8';


-- ============================================================================
-- M9 — AI-Augmented Lesson Design
-- ============================================================================

-- M9 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Maths lesson design is structured. AI integration risks introducing chaos.</p>
    <p class="text-sm mb-2">AI placement in maths lessons is narrow and predictable: warm-up problem variation, worked-example generation for differentiation, exit-ticket distractor production. Three or four well-placed roles, not pervasive integration.</p>
    <p class="text-sm">You'll get a small set of evidence-based AI placements in maths lessons. Explicit guidance on where AI doesn't help (concept introduction, worked-example modelling).</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson design with AI either makes AI central or treats it as ornament. Neither matches your practice.</p>
    <p class="text-sm mb-2">A third option: AI as a contrast tool. Student-AI versus student-only writing, used to surface what voice means. Not central, not ornament — pedagogical.</p>
    <p class="text-sm">You'll get a specific lesson pattern (AI-as-contrast) for writing instruction. Designed for the 50-minute class rather than the unit-long project.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science lessons follow predict-observe-explain cycles. AI doesn't fit cleanly.</p>
    <p class="text-sm mb-2">AI fits at the predict step (generating diverse student-style predictions for class compare), at the differentiation of the explain step, and at the formative-check stage. Not at the observe step, which stays purely empirical.</p>
    <p class="text-sm">You'll get three specific placement points where AI strengthens predict-observe-explain cycles. The empirical heart of science teaching protected.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics lessons depend on careful conceptual sequencing. AI won't get the order right.</p>
    <p class="text-sm mb-2">AI doesn't choose order; you do. AI generates the variations you've decided to need (e.g., context variations for the same concept). Order stays in your hands.</p>
    <p class="text-sm">You'll get a workflow where AI handles the surface variation that you've designed for. Your conceptual sequence intact.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson design including AI feels like adding a dependency. What if the tool changes?</p>
    <p class="text-sm mb-2">Design the lesson to work without the AI, with AI as a quality-of-life add. Then if the tool changes, the lesson still works at the level it would have without AI.</p>
    <p class="text-sm">You'll get a design principle (AI-as-add, not AI-as-dependency) that protects your lessons against tool churn. While still benefiting from current AI.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology has detail-rich lessons. AI introduces detail-error risk.</p>
    <p class="text-sm mb-2">AI placement that avoids detail-generation: differentiating reading levels of texts you've vetted, drafting student-friendly explanations of figures you've made, generating quiz distractors from your own taught misconceptions.</p>
    <p class="text-sm">You'll get biology-specific AI placements that route around the detail-error risk. By working on your verified content rather than generating biology.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">History lessons depend on source selection and interpretive framing. AI doesn't do either well.</p>
    <p class="text-sm mb-2">Source selection and framing remain yours. AI handles: differentiated reading-level versions of selected sources, comparison-grid generation, debate-prompt drafting. Mechanical work, not interpretive work.</p>
    <p class="text-sm">You'll get a clear separation of mechanical from interpretive work in history lesson design. AI assigned only the mechanical.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography lessons increasingly depend on current data. AI's training data is old.</p>
    <p class="text-sm mb-2">Don't use AI for current data. Use it for: generating fieldwork-prep questions, drafting differentiated atlas-reading scaffolds, producing case-study comparison frameworks. All non-temporal work.</p>
    <p class="text-sm">You'll get geography lesson designs that quarantine AI to the non-temporal scaffolding work. Current data left to your usual sources.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Language lessons have communicative goals. AI integration risks turning lessons into translation exercises.</p>
    <p class="text-sm mb-2">Right, and the module addresses it. Communicative-goal lessons use AI as a conversation partner (with caveats), as a comprehensible-input generator, as a pronunciation-mirror. Not as a translation oracle.</p>
    <p class="text-sm">You'll find lesson design moves that preserve communicative aims while using AI strategically. Instead of letting AI flatten lessons into translation drills.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Social studies lessons need careful framing. AI may introduce inappropriate framings.</p>
    <p class="text-sm mb-2">Likely. The module's social studies guidance includes prompt-design moves that constrain AI outputs to be evidence-based, multi-perspectival, and framing-light. Not bias-free, but workably bounded.</p>
    <p class="text-sm">You'll get specific prompt-design moves for social studies lesson preparation that reduce (not eliminate) AI's framing-injection risk.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI-augmented lesson design in CS is well-trodden territory. Will this say anything new?</p>
    <p class="text-sm mb-2">Probably not on technical placement. The contribution is the teacher-as-pedagogical-designer framing: not "where can AI go" but "what design move does AI replace, and is that worth the trade?"</p>
    <p class="text-sm">You'll get a pedagogical-design lens that goes beyond "AI is good for X" to "AI replaces design move Y, and the trade-off is Z." Useful even for CS teachers familiar with the technical side.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson design for movement-based lessons doesn't involve AI in the room.</p>
    <p class="text-sm mb-2">AI in PE lesson design lives in the prep stage: drafting differentiated rule explanations, producing risk assessments, generating pre-lesson video summaries. Class-time stays AI-free if you choose.</p>
    <p class="text-sm">You'll get prep-stage AI integration in PE that respects your class-time AI-free choice. With concrete prep-stage time savings.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Art lessons need to protect creative space. AI lesson design risks reducing that space.</p>
    <p class="text-sm mb-2">Reducing or expanding, depending on placement. Module guidance protects making-time as AI-free; AI sits at preparation, criticism, or contrast — never at the making moment itself.</p>
    <p class="text-sm">You'll get art lesson design rules that explicitly protect making-time from AI intrusion. AI placed where it doesn't compete with student creation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson design for SEN students is highly individualised. Generic AI integration won't work.</p>
    <p class="text-sm mb-2">Individualisation is exactly where AI helps most: producing differentiated versions of materials you've designed, generating visual schedule variants, drafting communication adapted to specific student needs.</p>
    <p class="text-sm">You'll get AI integration tuned to individualisation. The AI multiplies your personalisation work rather than averaging it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years lesson design follows children's interests. AI prep is a poor match for emergent practice.</p>
    <p class="text-sm mb-2">AI prep for emergent practice is light and reactive: morning-after drafting of learning stories from observation notes, follow-up activity ideas based on observed interest, parent-communication drafting from your bullet points.</p>
    <p class="text-sm">You'll get light, reactive AI prep that supports emergent practice. Without imposing pre-planned structure on it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You plan a week of lessons across five subjects in one prep block. AI integration in each lesson would multiply complexity, not reduce it.</p>
    <p class="text-sm mb-2">AI integration done once, across all five subjects, reduces complexity. The same prompt-pattern produces spelling-list variations, maths-problem variations, science-vocabulary supports, art-discussion prompts, and PE-rule simplifications.</p>
    <p class="text-sm">You'll get a single AI workflow for primary-generalist planning that scales across the week's five subjects. Instead of needing separate workflows per subject.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';

-- M9 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson design modules tend to assume single-subject specialists with planning time and small classes.</p>
    <p class="text-sm mb-2">This module's guidance is designed to scale: from single-lesson placement decisions to multi-subject planning patterns, depending on your context.</p>
    <p class="text-sm">You'll get lesson design moves that work in different teaching contexts. With explicit attention to where each pattern's assumptions might not match yours.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M9';


-- ============================================================================
-- M10 — Building Your AI-Pedagogical Practice
-- ============================================================================

-- M10 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Reflective practice is humanities territory. Maths is concrete.</p>
    <p class="text-sm mb-2">Maths teaching has reflective traditions: lesson study, error analysis, problem-solving observation. The module's practice cultivation can plug into these existing forms.</p>
    <p class="text-sm">You'll get a reflective-practice frame that uses maths-teaching traditions you already know. For AI-related observation specifically.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You keep a teaching journal. Adding AI reflection feels like assigning yourself homework.</p>
    <p class="text-sm mb-2">Plug-in approach, not parallel approach. Add an AI question to existing journal entries: "where did AI appear today, and what did I notice?" One sentence, no new artefact.</p>
    <p class="text-sm">You'll get a minimal addition to your existing reflective practice that captures AI noticing. Without creating new workload.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Practice cultivation sounds vague. Science teachers want operational definitions.</p>
    <p class="text-sm mb-2">Operational here means: a brief, periodic observation routine, with explicit questions, captured in a chosen format. Not vague. Short, specified, reusable.</p>
    <p class="text-sm">You'll get an operational reflective-practice routine for AI-noticing in science teaching. With the structure you'd want from any well-defined intervention.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Habits modules are mostly self-help. Physics teachers don't operate on inspirational language.</p>
    <p class="text-sm mb-2">Module language is operational, not inspirational. Habits get specific triggers, specific durations, and specific outputs. No vibes.</p>
    <p class="text-sm">You'll get a reflective-practice habit specified with the kind of precision a physics teacher would want before adopting it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You have a chemistry-teaching practice. Adding an AI layer feels like a separate thing.</p>
    <p class="text-sm mb-2">It's a layer, not a separate thing. The same lesson observations include "what AI showed up, and how did I handle it" as one of several existing reflection prompts.</p>
    <p class="text-sm">You'll get a small additional question for your existing reflective practice. Integrated rather than parallel.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You cultivate practice through colleague conversations and lesson study, not through formal modules.</p>
    <p class="text-sm mb-2">Module guidance can feed into colleague conversations: structured questions to bring to a department meeting, observation prompts for peer visits, journal templates that match lesson-study traditions.</p>
    <p class="text-sm">You'll get inputs to your existing practice-cultivation methods (colleague conversations, lesson study). In the form of AI-specific structured questions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Reflective practice is well-established. Adding AI dimensions risks faddishness.</p>
    <p class="text-sm mb-2">AI is the most likely current candidate for reflective attention because it's reshaping the very texts and tools your subject works with. Worth one focused practice cycle, even if you decide it's not worth more.</p>
    <p class="text-sm">You'll get a focused practice cycle on AI's effects in history teaching. A clear endpoint where you decide whether continued attention is warranted.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Practice cultivation tends to assume long-term planning horizons. Your department changes rapidly.</p>
    <p class="text-sm mb-2">The module's practice cycles are brief — weekly questions, half-termly reviews, yearly pattern-spotting. Designed for change, not stability.</p>
    <p class="text-sm">You'll get a practice cultivation rhythm tuned to short cycles. Suitable for departments and contexts that don't reward long planning horizons.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Reflective practice in language teaching is well-developed. AI dimensions feel bolted on.</p>
    <p class="text-sm mb-2">They are, until they're integrated. The module shows what integration looks like: AI questions woven into existing reflective categories (lesson aims, student response, communicative success), not a new column.</p>
    <p class="text-sm">You'll get integration moves for adding AI to your existing reflective categories. Without creating a parallel system.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You reflect on power, framing, and pedagogy already. AI is one more strand.</p>
    <p class="text-sm mb-2">Worth treating as its own strand initially because of pace of change. Once the patterns stabilise (probably in two years), it folds into general reflective practice.</p>
    <p class="text-sm">You'll get a justified separate-strand approach for AI reflection now. With an exit plan to fold it into your general practice when AI stops being a moving target.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Practice cultivation modules from outside CS rarely match the field's pace.</p>
    <p class="text-sm mb-2">Module rhythm is short-cycle, not long-cycle, which fits CS pace better than most teacher-PD reflective practices.</p>
    <p class="text-sm">You'll get a reflective rhythm fast enough to keep up with CS-teaching change. Distinct from the year-long cycles common in general teacher PD.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Reflective practice that isn't body-based misses what PE actually is.</p>
    <p class="text-sm mb-2">Reflective practice can include body-based observation: how students moved, what they tried, what AI tools said about their movement (if any). Body-aware reflection is possible.</p>
    <p class="text-sm">You'll get reflective-practice prompts attentive to embodied teaching. Not only desk-based work. Suitable for PE-specific observation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Studio practice cultivation is built into art teaching. Why a parallel AI version?</p>
    <p class="text-sm mb-2">Not parallel — woven in. AI-noticing as one observation thread among the many you already track in studio teaching: who used what, when, how it shaped the making, whether the making suffered or grew.</p>
    <p class="text-sm">You'll find a way to extend studio reflective practice to include AI. Without forcing a separate journal or process.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Reflective practice in SEN is constant and intensive. Adding AI strands feels like cognitive overload.</p>
    <p class="text-sm mb-2">AI in SEN reflection is targeted: did the AI accommodation help this specific student, or did it fail in a way I should record for next time? Single-question, single-incident.</p>
    <p class="text-sm">You'll get single-incident AI reflection prompts that fit into your existing SEN reflection. Without expanding it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years reflective practice is rich and embodied. AI reflection is a desk activity.</p>
    <p class="text-sm mb-2">Desk reflection on AI use isn't different from desk reflection on resource use. Same form, new content. The embodied reflection on children stays as it is.</p>
    <p class="text-sm">You'll get adult-side AI reflection at the desk, distinct from child-side embodied reflection. Neither displacing the other.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You have no reflective time. Five subjects, 25 children, marking, parent communication. Practice cultivation is a fantasy.</p>
    <p class="text-sm mb-2">The module accepts that and offers minimum-viable practice: one observation question per week, one half-page review per half-term. Not a fantasy — a deliberate floor.</p>
    <p class="text-sm">You'll get a minimum-viable AI reflective practice for primary generalists. Tested against the reality of zero-prep-time teaching.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';

-- M10 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Practice cultivation modules tend to assume teachers with energy for self-development.</p>
    <p class="text-sm mb-2">This module assumes teachers without that energy and works backward. Practices are minimum-viable, integrative with existing reflection, and have explicit exit conditions.</p>
    <p class="text-sm">You'll get a practice-cultivation approach tuned for tired teachers. Floor-not-ceiling expectations and explicit permission to keep it small.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M10';


-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Expected: 17 records per module (M6, M7, M8, M9, M10)
-- Total: 85 records
-- ============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM modules_modulecontent mc
    JOIN modules_module m ON mc.module_id = m.id
    WHERE mc.content_type = 'subject_intro'
      AND m.code IN ('M6','M7','M8','M9','M10');

    RAISE NOTICE 'Total subject_intro records for M6-M10: %', v_count;

    IF v_count != 85 THEN
        RAISE EXCEPTION 'Expected 85 records, found %. Rolling back.', v_count;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- POST-COMMIT VERIFICATION QUERY (run separately if desired)
-- ============================================================================
-- SELECT m.code, COUNT(*) AS hooks, COUNT(DISTINCT mc.subject_area) AS distinct_subjects
-- FROM modules_modulecontent mc
-- JOIN modules_module m ON mc.module_id = m.id
-- WHERE mc.content_type = 'subject_intro'
--   AND m.code IN ('M6','M7','M8','M9','M10')
-- GROUP BY m.code
-- ORDER BY m.code;
--
-- Expected: 5 rows, each with hooks=17 and distinct_subjects=17
-- ============================================================================
