-- ============================================================================
-- SUBJECT INTRO HOOKS — M1 to M5 (Acquire Level)
-- ============================================================================
-- Phase 4a of Subject Intro Hooks rollout
-- Records inserted: 85 (5 modules × 17 entries: 16 subjects + Universal)
-- Source: RESISTANCE_MATRIX_M1-M5.md (Phase 3 deliverable)
-- Spec: SUBJECT_INTRO_HOOKS_PATCH_APR2026.md
-- ============================================================================
-- Run order: this file FIRST, then M6-M10, then M11-M15
-- Run via pgAdmin Query Tool against the PROODOS database
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 0. Cleanup: remove Phase 2 test seeds before inserting real content
-- ----------------------------------------------------------------------------
DELETE FROM modules_modulecontent
WHERE content_type = 'subject_intro'
  AND content_data LIKE '%PHASE-2-TEST-SEED%';

-- ----------------------------------------------------------------------------
-- Idempotency: clear any existing subject_intro records for M1-M5
-- ----------------------------------------------------------------------------
DELETE FROM modules_modulecontent
WHERE content_type = 'subject_intro'
  AND module_id IN (SELECT id FROM modules_module WHERE code IN ('M1','M2','M3','M4','M5'));


-- ============================================================================
-- M1 — Understanding AI in Education
-- ============================================================================

-- M1 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You might think AI is just clever statistics. You already teach statistics. So what's new here?</p>
    <p class="text-sm mb-2">Mathematics teachers see the structure underneath AI more clearly than anyone. You can be the colleague who explains it accurately to others, instead of repeating tech-press hype.</p>
    <p class="text-sm">This module gives you vocabulary and frame to talk about AI with mathematical accuracy. You can answer the inevitable student questions without overclaiming or dismissing.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI writes. That threatens what you teach. Why would you want to learn more about it?</p>
    <p class="text-sm mb-2">Language teachers spend their careers helping students find their own voice. AI mimicry is the new contrast that makes voice teachable in fresh ways.</p>
    <p class="text-sm">You'll come away with a clear sense of what AI can and can't do with language. You stop arguing about whether it understands, and start using its limits as teaching material.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Another tech wave to add to coding, robotics, and STEM days. When does it stop?</p>
    <p class="text-sm mb-2">Science teachers have absorbed every tech wave for decades. You know what survives the hype and what doesn't, often better than the ed-tech vendors selling it.</p>
    <p class="text-sm">This module gives you criteria to decide whether AI deserves a place in your science classroom. Your judgement, not someone else's enthusiasm.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics is governed by laws. AI is governed by training data. They live in different worlds.</p>
    <p class="text-sm mb-2">Physics teachers already train students to interrogate models and ask "where does this break?" That's exactly the question AI literacy needs.</p>
    <p class="text-sm">You'll find a way to position AI as a model to be tested, not a magic answer machine. Useful in any classroom that values falsifiability.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You teach about reactions and mechanisms. AI feels like one more black box on top of black boxes.</p>
    <p class="text-sm mb-2">Chemistry teachers explain the mechanisms behind apparent magic. AI is the next mechanism worth explaining, and your students will trust your version more than YouTube's.</p>
    <p class="text-sm">You'll get enough understanding to decode AI's role in modern chemistry, including molecular generation, lab automation, and drug discovery. Useful when students ask about it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI in biology sounds like biotech and bioinformatics. It isn't really classroom material.</p>
    <p class="text-sm mb-2">Biology already deals with emergent behaviour, complex systems, and neural networks (the real ones). AI is built on biological metaphors that students recognise from your lessons.</p>
    <p class="text-sm">You'll gain confidence to make the brain to neural-network bridge for students, accurately. Most teachers do it badly. You can do it well.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI is a current event. You teach long-arc patterns. They don't connect.</p>
    <p class="text-sm mb-2">Every technology that reshaped knowledge — print, radio, internet — went through the same hype cycle. Historians spot it faster than anyone.</p>
    <p class="text-sm">You'll get a frame for placing AI in the long history of educational technology. When colleagues panic or evangelise, you have the perspective to steady the conversation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography is grounded in real places, real people, real maps. AI is abstract and online.</p>
    <p class="text-sm mb-2">Geography teachers already use AI: it powers Google Maps, satellite analysis, climate models, traffic predictions. Most teachers don't know the AI is there.</p>
    <p class="text-sm">You'll come to recognise where AI already sits in your subject's tools, so you can name it for students instead of treating it as invisible infrastructure.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Translation tools are getting too good. AI is taking over your subject. You'd rather not look.</p>
    <p class="text-sm mb-2">Translation has always been about more than word-substitution: register, idiom, cultural framing, intent. That's still entirely yours, and now more visible because AI makes the easy part trivial.</p>
    <p class="text-sm">You'll come away with a clear separation between what AI does well in language and where you remain irreplaceable. Teach with confidence rather than defensiveness.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI raises issues of bias, surveillance, power. Important, but not quite your curriculum.</p>
    <p class="text-sm mb-2">Social studies already covers technology and society. The industrial revolution, mass media, globalisation. AI is the current chapter of that exact story.</p>
    <p class="text-sm">You'll work out a position on AI's social role that's yours. When students ask "is this good or bad?" you can frame the question properly instead of dodging it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You teach this already. What can a generic teacher PD module add for you?</p>
    <p class="text-sm mb-2">Computer science teachers know the technology, but rarely the pedagogy of the technology. How non-CS colleagues should think about it, what assumptions they bring, where the analogies break.</p>
    <p class="text-sm">You'll pick up tools to be the AI explainer-in-residence at your school. Support colleagues without dumbing down or losing them in jargon.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI and PE? You teach kids to move. There isn't much overlap.</p>
    <p class="text-sm mb-2">AI is already coaching elite athletes through video analysis, biomechanics, and training-load monitoring. The same tools are starting to reach schools.</p>
    <p class="text-sm">You'll come away with awareness of how AI is entering sport and movement, so you can decide what to bring into your gym and what to keep human.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI generates images, music, writing. It threatens art-making itself. You'd rather not teach that.</p>
    <p class="text-sm mb-2">Art teachers have seen camera, photoshop, and digital art each "end" art and not end it. Each tool became raw material in time.</p>
    <p class="text-sm">You'll build a framework for thinking about AI as an art-making material, not as a competitor. Decide on your own terms how it enters your studio.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI tools are designed for typical learners. They never quite fit your students.</p>
    <p class="text-sm mb-2">Some of the most promising AI applications are accessibility tools: speech-to-text for students with motor challenges, image description for visual impairment, simplification for cognitive load.</p>
    <p class="text-sm">You'll get a scan of where AI genuinely helps in special education, separated from the generic AI hype that ignores your students.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Young children need humans, songs, hands, dirt, books. AI doesn't belong in early years.</p>
    <p class="text-sm mb-2">AI literacy has to start somewhere, and what begins in early childhood — language, pattern recognition, story — is what AI mirrors. Children don't need to use AI to start understanding it.</p>
    <p class="text-sm">You'll work out a position on AI in early years that's yours. When parents ask "should my four-year-old use ChatGPT?" you can answer with clarity.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You teach maths, language, science, art, social studies, and PE to one class of children. AI tools are designed for secondary specialists with one subject. There's no time to learn five different AI workflows.</p>
    <p class="text-sm mb-2">Primary generalists actually have an advantage with AI literacy. You see the same students all day across all subjects. You can build cross-curricular AI awareness in ways no specialist can.</p>
    <p class="text-sm">You'll get a primary-school-shaped understanding of AI that respects your reality: limited time, broad curriculum, young children, and the obligation to model healthy tech relationships.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';

-- M1 × Universal (fallback)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Whatever you teach, this looks like a tech module aimed at someone else.</p>
    <p class="text-sm mb-2">AI in education isn't a subject add-on. It's a shift in how knowledge is produced, consumed, and assessed across all subjects.</p>
    <p class="text-sm">You'll get a starting frame for your own thinking about AI in your classroom, before anyone else's framing locks in.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M1';


-- ============================================================================
-- M2 — AI Ethics for Educators
-- ============================================================================

-- M2 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Ethics belongs to philosophers and lawyers. You work with proofs.</p>
    <p class="text-sm mb-2">Mathematics is full of value-laden choices: what counts as elegant, which problems matter, who gets called "good at maths". The same ethical attention applies to AI.</p>
    <p class="text-sm">Ethics moves from abstract principles to concrete questions you can pose in a maths classroom. About fairness in grading algorithms, about who gets recommended for advanced classes.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI ethics is about plagiarism. You already deal with that.</p>
    <p class="text-sm mb-2">Beyond plagiarism: voice ownership, training-data origins, who gets erased when AI rewrites, whose dialect is treated as standard. All literary territory.</p>
    <p class="text-sm">You'll come away with a wider ethical map of AI in writing classrooms. Plagiarism becomes one issue among many rather than the whole conversation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science values evidence and replicability. You're objective. Ethics is for other subjects.</p>
    <p class="text-sm mb-2">Scientific objectivity is itself an ethical stance. AI's claim to objectivity hides specific value choices, and science teachers are best placed to teach students to interrogate that claim.</p>
    <p class="text-sm">Ethics becomes part of scientific literacy, not a separate module bolted on. Useful in your existing curriculum, not an add-on.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics doesn't do values. AI ethics is sociology dressed up.</p>
    <p class="text-sm mb-2">Physics teaches measurement uncertainty and observer effects. AI ethics asks the same questions: what is being measured, by whom, with what error, affecting whom.</p>
    <p class="text-sm">You'll find a way to bring AI ethics into physics through measurement and modelling decisions, without abandoning what makes physics rigorous.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Your ethics framework is lab safety and academic integrity. That's enough.</p>
    <p class="text-sm mb-2">Chemistry has long ethics practice: dual-use research, environmental impact, drug development. AI raises related questions in your students' lives.</p>
    <p class="text-sm">Ethics expanded from lab to algorithm, using frames you already teach. Continuity, not new vocabulary.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology ethics is about life, not algorithms. They're not really comparable.</p>
    <p class="text-sm mb-2">AI bias in healthcare, genomics, environmental modelling — all of it intersects biology classrooms. Students will face these issues whether or not the curriculum names them.</p>
    <p class="text-sm">Biological ethics extends into AI-mediated biology. You get classroom material for the ethical lessons your students will live in adulthood.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">History is full of ethics. AI ethics is just the latest chapter, not a separate field.</p>
    <p class="text-sm mb-2">Exactly the right view, and a powerful starting point. History teachers are uniquely positioned to refuse the framing of AI ethics as unprecedented and instead teach it through pattern-recognition.</p>
    <p class="text-sm">You'll get a toolkit for teaching AI ethics through historical analogy: who wrote the rules, who benefited, who was excluded. Pre-existing pedagogy, new examples.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Privacy and bias in AI sound like online problems. Geography is about places.</p>
    <p class="text-sm mb-2">AI is reshaping geography directly: location surveillance, predictive policing, climate modelling whose assumptions affect real communities. Place-based ethics has new urgency.</p>
    <p class="text-sm">Geographic concepts — territory, access, scale, vulnerability — become the lens for AI ethics. Your subject becomes the analytical home for these questions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Ethics in language teaching is about respect across cultures. AI doesn't change that.</p>
    <p class="text-sm mb-2">AI absolutely changes it. Whose languages are well-represented in training data; whose voices are simplified, stereotyped, or erased; how translation flattens nuance. These are language-teacher questions.</p>
    <p class="text-sm">You'll get a specifically linguistic frame for AI ethics, where bias isn't only social but also lexical, syntactic, and dialectal. Territory you already cover.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI ethics is part of your curriculum already. You might know more than this module assumes.</p>
    <p class="text-sm mb-2">Possibly so. But the operationalisation in classrooms — how to teach it without lecturing, how to build student agency, how to set classroom AI norms — is still being worked out.</p>
    <p class="text-sm">Less theory, more tested classroom practice. The module respects what you bring and adds tools you can deploy on Monday.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You taught ethics last term. What's new?</p>
    <p class="text-sm mb-2">Most CS ethics curricula focus on developer ethics. Teacher ethics is different: you're not building the system, you're deciding whether to inflict it on students.</p>
    <p class="text-sm">You'll get a teacher-specific ethical lens that complements the developer-specific one your CS curriculum already covers.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE ethics is about fairness in sport, body image, inclusion. AI doesn't enter.</p>
    <p class="text-sm mb-2">AI enters PE through fitness trackers, body-composition apps, performance video analysis. All collecting data on minors. Ethics gets concrete fast.</p>
    <p class="text-sm">You'll get a PE-specific ethics conversation about student bodies and AI surveillance, before the tech reaches your gym uninvited.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI ethics in art is the training-data theft debate. You've heard it.</p>
    <p class="text-sm mb-2">Yes, but also: emotional manipulation through generative content, deepfakes affecting students, identity and authorship in collaborative AI work. Wider than data ethics alone.</p>
    <p class="text-sm">You'll get an art-classroom ethics framework that treats AI as material with provenance, consequences, and meaning. Not just as a copyright case.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Ethics for your students means dignity and individualised support. AI ethics feels parallel.</p>
    <p class="text-sm mb-2">AI bias hurts learners with disabilities specifically: speech recognition that fails non-standard speech, accessibility tools that make assumptions, "personalised learning" trained on neurotypical data.</p>
    <p class="text-sm">You'll get ethics tools to evaluate AI products you might be sold, with your students' particular vulnerabilities in focus.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Your ethics is about safeguarding, attachment, healthy development. AI is too distant to matter.</p>
    <p class="text-sm mb-2">AI products targeting young children — voice toys, "educational" apps, screen-time recommenders — already shape what reaches your classroom. Your ethics framework is the front line.</p>
    <p class="text-sm">You'll get specific criteria for evaluating AI products before they enter your early-years setting, drawn from your existing safeguarding language.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You deal with ethics every day across every subject — friendship rules, fairness, kindness. AI ethics seems like one more abstract topic with no time to fit it in.</p>
    <p class="text-sm mb-2">Primary classrooms are where ethical instincts are formed. AI ethics for ten-year-olds is exactly fairness, honesty, kindness, applied to a new technology. You have the relational base; the topic is just new vocabulary.</p>
    <p class="text-sm">You'll get a primary-classroom-friendly version of AI ethics, integrated into the values teaching you already do, not a separate curriculum strand.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';

-- M2 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Ethics modules tend to be either too abstract or too compliance-focused. Probably this one too.</p>
    <p class="text-sm mb-2">Teacher ethics is neither — it's the daily judgement of what's fair and right in your classroom. AI just creates new versions of old questions.</p>
    <p class="text-sm">You'll get a practical ethics frame for AI decisions you'll actually make: about tools, about student data, about your own use of AI in lesson preparation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M2';


-- ============================================================================
-- M3 — AI Foundations: How It Works
-- ============================================================================

-- M3 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You'll spot the maths underneath quickly. Hopefully not too watered down.</p>
    <p class="text-sm mb-2">This module respects mathematical literacy. It uses vectors, probabilities, and optimisation in ways a maths teacher will recognise and possibly enjoy.</p>
    <p class="text-sm">You'll come away with a clean mental model of how transformers work, from a maths point of view. Adapt it for your students at the right level.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Tokens, embeddings, transformers. All Greek to you, and not the good kind.</p>
    <p class="text-sm mb-2">Large language models are language tools first. They tokenise, model context, and predict next words. Exactly what a language teacher already thinks about, in different vocabulary. You speak this language; you just call it morphology, syntax, semantics.</p>
    <p class="text-sm">You'll get enough technical understanding to know why AI struggles with long literary texts and ambiguity, so you can use it intentionally rather than blindly.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">A black box. Worse than the ones you already complain about in textbooks.</p>
    <p class="text-sm mb-2">Science teachers don't accept "it just works." This module gives you enough internal mechanism to teach AI as a system to be questioned, not an oracle to consult.</p>
    <p class="text-sm">You'll come away with a scientifically respectable model of how AI produces output. Suitable for telling students "here's what's actually happening, not magic."</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You'll see if it's correct or hand-wavy. Most pop-AI explanations are.</p>
    <p class="text-sm mb-2">This module accepts that physics teachers want accuracy. It doesn't pretend gradient descent is rolling down a hill. It treats the maths as the maths.</p>
    <p class="text-sm">You'll get a physics-grade understanding of training and inference. That lets you decide what to bring into your classroom and what to leave for the textbook.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Mechanisms in AI must look very different from chemical mechanisms.</p>
    <p class="text-sm mb-2">Surprisingly similar in structure: layered transformations, energy minimisation, equilibria. Different domain, related thinking.</p>
    <p class="text-sm">You'll find a way to use chemistry's mechanism-thinking habit to grasp AI internals, instead of starting from scratch with unfamiliar metaphors.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Neural networks aren't really like brains. The metaphor is fake.</p>
    <p class="text-sm mb-2">Correct, and worth saying out loud. The module clarifies where the brain analogy holds and where it breaks. Biology teachers need that distinction more than anyone, because students will misunderstand otherwise.</p>
    <p class="text-sm">You'll get precision about what AI shares with biological cognition (statistical learning) and what it doesn't (embodiment, drives, meaning). Useful when teaching nervous systems too.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Technical innards of AI feel disconnected from what you teach.</p>
    <p class="text-sm mb-2">History of AI itself is in here: symbolic AI to neural networks to transformers, each shift driven by who funded research and what data became available. A historian will find friends in this story.</p>
    <p class="text-sm">You'll gain historical perspective on AI's intellectual development. When you talk to students about the current AI moment, you can locate it in time, not eternity.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're surprised AI foundations are even relevant to geography.</p>
    <p class="text-sm mb-2">They are. Most geographic AI uses the same underlying models, applied to spatial data. Image classification on satellite imagery, for example, is the same architecture as image classification on cats.</p>
    <p class="text-sm">You'll see that geography's AI tools share architecture with chatbots. Understanding one helps you understand the other. One module, two domains.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">This is going to be tokens and probabilities. Numbers, not languages.</p>
    <p class="text-sm mb-2">It is, but the framing is linguistic: how does a model represent a word, why does it confuse polysemes, why does it lose context across long passages. Language teachers find these questions familiar.</p>
    <p class="text-sm">You'll pick up technical vocabulary to explain to students why machine translation produces certain errors. Use those errors as language-learning moments.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You want the social side of AI, not the technical innards.</p>
    <p class="text-sm mb-2">The technical innards explain the social effects. Bias comes from training data, which comes from human-generated content, which carries social patterns. The pipeline is the politics.</p>
    <p class="text-sm">You'll come away with technical literacy that strengthens your social analysis instead of being separate from it. Better equipped to teach algorithmic accountability.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You'll know most of this. Hoping for at least one new framing.</p>
    <p class="text-sm mb-2">Likely true. The value here is the teacher framing: how to introduce these concepts to non-CS colleagues and students without losing them in jargon or oversimplifying.</p>
    <p class="text-sm">You'll get pedagogical scaffolding for ideas you already understand. Ready to deploy with non-specialist audiences.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI foundations? In PE? Tempted to skip this.</p>
    <p class="text-sm mb-2">Stay a moment. AI in PE means motion analysis, performance prediction, even biomechanics. Foundations matter when you're deciding whether to trust an app's verdict on a student's movement.</p>
    <p class="text-sm">You'll get enough understanding to evaluate the AI tools entering sport and movement. Not just accept whatever vendors claim about accuracy.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">An inside-the-machine view of generative AI. Not what art is about.</p>
    <p class="text-sm mb-2">Knowing the medium matters in art. A painter understands pigment, a photographer understands optics. AI artists who don't understand training data are missing the medium.</p>
    <p class="text-sm">You'll come away with material knowledge of generative AI. Teach it as a craft with affordances and limits, not as a button that produces images.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">A technical AI module. You need pedagogical practice.</p>
    <p class="text-sm mb-2">The technical side matters in special education specifically. Whether a speech recognition tool will work for your student depends on whose voices were in the training data. Foundation knowledge tells you what to ask vendors.</p>
    <p class="text-sm">You'll pick up vocabulary and concepts to interrogate AI products on behalf of your students before adopting them.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Foundations of AI seem even more remote from your classroom than the AI itself.</p>
    <p class="text-sm mb-2">Children form their first models of how AI works through what adults around them say. Your accuracy matters when a parent asks you why ChatGPT got something wrong.</p>
    <p class="text-sm">You'll get enough technical understanding to give children, parents, and colleagues honest, age-appropriate explanations of what AI actually does.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're not a maths or computer science teacher. Tokens, transformers, embeddings — you'd need a course just to understand the words.</p>
    <p class="text-sm mb-2">Primary generalists explain how everything works in simple terms every day. From photosynthesis to fractions to friendships. AI is one more thing to understand at the level you can re-explain.</p>
    <p class="text-sm">You'll get a primary-school-friendly mental model of AI that you can use across subjects. In language work for text generation, in science for pattern recognition, in social studies for fairness.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';

-- M3 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">A technical module. This will be the slog.</p>
    <p class="text-sm mb-2">Foundations are background knowledge, like geography or grammar. You don't need to master the maths, just understand the shape of what's happening when AI produces output.</p>
    <p class="text-sm">You'll get a non-technical-but-honest model of how AI works, sufficient to make informed decisions in your classroom and resist both overclaiming and panicking.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M3';


-- ============================================================================
-- M4 — AI in the Pedagogical Toolkit
-- ============================================================================

-- M4 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You have your own ways of generating problem sets. Why outsource that?</p>
    <p class="text-sm mb-2">AI is poor at generating mathematically interesting problems. But it's good at varying surface features — numbers, contexts — on problems you've already designed. That frees you for the structural work only you can do.</p>
    <p class="text-sm">You'll get a specific division of labour where AI handles the generative grunt work and you keep the design judgement. Time freed for what you actually trained for.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI marking student writing? That's the worst possible use of it.</p>
    <p class="text-sm mb-2">Agreed for summative assessment. But for low-stakes formative feedback — sentence-level clarity, word choice, structural diagnosis — AI scales what one teacher can't.</p>
    <p class="text-sm">You'll come away with a sharp distinction between AI feedback uses you'll trust (formative, draft-stage) and ones you'll refuse (summative, judgemental). Classroom workflows for each.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson planning shortcuts often produce wrong science. You'd rather write your own.</p>
    <p class="text-sm mb-2">True for content. But AI is decent at scaffolding investigations, generating misconception-rich examples, and drafting student-friendly explanations of your accurate ones. You stay in charge of accuracy; AI multiplies your reach.</p>
    <p class="text-sm">You'll learn a workflow where AI never decides the science but helps you produce more material around what you've already got right.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Most AI examples in physics are wrong or trivial. You've checked.</p>
    <p class="text-sm mb-2">They are. The module assumes that and focuses on uses that don't depend on AI knowing physics: differentiation of existing material, generating worked-example variations, drafting prerequisite checks.</p>
    <p class="text-sm">You'll find AI uses that survive physics-teacher scrutiny because they don't require the AI to actually know physics.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry teaching depends on accuracy and safety. AI introduces both risks.</p>
    <p class="text-sm mb-2">True. The module's chemistry uses are bounded: differentiating language complexity in your existing materials, generating quiz distractors based on your taught misconceptions, drafting parent communications. None of it touches reaction predictions.</p>
    <p class="text-sm">You'll get a safe-zone map of where AI helps in chemistry teaching without putting students at chemical risk.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology is full of detail. AI confidently produces wrong details. Hard pass.</p>
    <p class="text-sm mb-2">Confidence is the problem; the module addresses it head-on. AI uses in biology: differentiating reading levels of a paper you've already vetted, drafting visual descriptions for accessibility, summarising your own lecture notes for revision sheets. Not generating biology.</p>
    <p class="text-sm">You'll find specific uses where the AI works on your verified content rather than producing biology from scratch.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI hallucinates historical detail spectacularly. Why would you let it near your classroom?</p>
    <p class="text-sm mb-2">You wouldn't, for content. The module's history uses are different: generating period-appropriate primary-source analysis questions for sources you've selected, drafting differentiated reading levels of textbook passages you've vetted, creating debate prompts.</p>
    <p class="text-sm">You'll find history uses that route around AI's hallucination problem rather than depending on AI to know history.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography is local and current. AI training data is global and old.</p>
    <p class="text-sm mb-2">Exactly the constraint. The module's geography uses don't ask AI for current local facts. They ask it to draft fieldwork preparation, generate sketch-mapping prompts, produce differentiated atlas-reading questions.</p>
    <p class="text-sm">You'll come away with geography uses tuned to what AI is bad at (current local data) and what it's good at (process scaffolding).</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI in language teaching feels like having students cheat in slow motion.</p>
    <p class="text-sm mb-2">Cheating isn't using AI; it's using AI without cognitive engagement. The module separates lazy uses (AI does the work) from generative uses (AI provides scaffolding for student production).</p>
    <p class="text-sm">You'll get a teacher's playbook for distinguishing AI-as-shortcut from AI-as-scaffolding in language learning. Classroom routines that protect engagement.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Lesson planning AI seems harmless. The bigger issue is what students do with AI.</p>
    <p class="text-sm mb-2">Both matter. The module covers your prep workflow first, since teaching with AI starts with thinking through your own use of it. Student-facing comes in M9 and M14.</p>
    <p class="text-sm">You'll get time-saving prep workflows now. Classroom student practices later. Modular and not overwhelming.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI for lesson planning. Sure. What CS-specific uses are covered?</p>
    <p class="text-sm mb-2">CS-specific uses include: generating beginner-friendly explanations of code you've selected, producing variation problems with similar structure but different surface, drafting commit-by-commit walkthroughs.</p>
    <p class="text-sm">You'll get CS-pedagogy uses tuned to teaching programming to students who haven't yet developed code-reading habits.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI helping you plan PE lessons? Most online plans are nonsense already.</p>
    <p class="text-sm mb-2">True. The module's PE uses are narrow: drafting differentiated rule explanations for inclusive games, producing risk-assessment language for parents, generating warm-up variations for rotation.</p>
    <p class="text-sm">You'll get modest, useful PE applications focused on the paperwork around the practice. Not the practice itself.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI in art education must mean image generation. You'd rather not.</p>
    <p class="text-sm mb-2">That comes in M13. This module is about your prep: drafting artist-statement scaffolds, varying difficulty levels of critique prompts, generating gallery-tour discussion questions.</p>
    <p class="text-sm">You'll get prep-time uses that don't ask you to take a position on student AI image generation. Those decisions stay yours, untouched by this module.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Generic AI tools never accommodate. Adaptation always falls on you.</p>
    <p class="text-sm mb-2">Mostly true. The module's special-ed angle is using AI to lessen your adaptation workload: differentiating reading levels of your materials, generating visual schedules from your lesson plans, drafting parent communications in plain language.</p>
    <p class="text-sm">AI as a labour multiplier for the adaptation work you're already doing. Not as a replacement for your professional judgement.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years prep is observation notes, learning stories, parent communication. None of that is AI work.</p>
    <p class="text-sm mb-2">All of that is exactly AI work, if you want it to be. AI is decent at drafting parent communications from your bullet-point observations, producing learning-story templates, suggesting follow-up activities for emerging interests.</p>
    <p class="text-sm">You'll get time-saving applications that respect your professional judgement (you decide what matters) while accelerating the writing-up work.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You plan five subjects a week. If AI saves you time in one subject, you lose it learning the AI in another. Net zero.</p>
    <p class="text-sm mb-2">Generalists actually benefit most from AI prep tools because the same AI workflow scales across subjects. Learn it once for spelling lists, deploy it for science vocabulary, art prompts, maths word problems.</p>
    <p class="text-sm">You'll get a small set of cross-curricular AI workflows specifically tuned to multi-subject planning, where the time-saving compounds across your week.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';

-- M4 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Another tool to learn. You've been promised efficiency before.</p>
    <p class="text-sm mb-2">Reasonable scepticism. The module shows specific, narrow uses and is honest about what isn't worth the trouble.</p>
    <p class="text-sm">You'll get a short, specific list of AI uses that survive teacher scepticism. Plus equally honest warnings about uses that don't pay off.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M4';


-- ============================================================================
-- M5 — Reflective Prompt Engineering: An Introduction
-- ============================================================================

-- M5 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompting is just clear writing. Why dress it up as engineering?</p>
    <p class="text-sm mb-2">It's clear writing about pedagogical intent — closer to writing a good problem statement than to coding. Maths teachers already do this when they design assessments.</p>
    <p class="text-sm">You'll find a way to externalise your pedagogical thinking as you prompt. That sharpens both the prompt and your awareness of what you're trying to teach.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You write for a living. Surely you don't need a course on writing prompts.</p>
    <p class="text-sm mb-2">Prompting AI is genre writing in a new genre, with conventions still being worked out. Your prose skill is necessary but not sufficient. There are pedagogical moves specific to this genre.</p>
    <p class="text-sm">You'll learn new conventions for a new genre, presented as professional practice rather than tech skill. The familiar made systematic.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Trial and error works fine for finding good prompts. Why a framework?</p>
    <p class="text-sm mb-2">Trial and error works for finding what gets a result. Reflective prompting is about understanding why one prompt produced one outcome and another produced something different. A small experimental design exercise.</p>
    <p class="text-sm">You'll get a framework that converts your prompting from trial-and-error to small reflective experiments. Suitable for thinking, teaching, and eventually research.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompts to AI? This isn't engineering, it's cargo-cult engineering.</p>
    <p class="text-sm mb-2">The "engineering" framing is contested. The module reframes it: not engineering as in robust systems, but engineering as in principled reflective design. Closer to instructional design than to code.</p>
    <p class="text-sm">You'll get a more accurate vocabulary for what's actually happening when you prompt — design, not engineering — which spares you the cargo-cult problem.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You see colleagues posting prompt "spells" online. The whole field looks unserious.</p>
    <p class="text-sm mb-2">It is unserious in many places, which is why this module grounds prompting in instructional design and reflective practice instead. Recognised pedagogical traditions, applied to a new tool.</p>
    <p class="text-sm">You'll get a respectable foundation for prompting that you can defend to colleagues. Distinct from the prompt-magic culture online.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology is detail-heavy. You'll need to specify everything to get anything useful out of AI.</p>
    <p class="text-sm mb-2">The module addresses exactly that. The seven strategies include explicit context-setting, audience definition, and constraints. The very moves you need for accurate biology output.</p>
    <p class="text-sm">You'll get a reliable structure for biology prompts that produces output worth using rather than output worth correcting.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI is unreliable on historical detail. Better prompts won't fix that.</p>
    <p class="text-sm mb-2">True for content generation. But the module's seven strategies aren't only about getting AI to produce content. They're about using AI as a thinking partner: generating counter-arguments, drafting differentiated readings of texts you've vetted.</p>
    <p class="text-sm">You'll learn prompting techniques that route around AI's weakness in historical specifics, focusing on uses where it adds value.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompts that produce useful local geography? Unlikely.</p>
    <p class="text-sm mb-2">Unlikely for current local facts. Useful for: framing fieldwork investigations, generating compare-and-contrast prompts between places, drafting student questionnaires for local studies.</p>
    <p class="text-sm">You'll get geography-tuned uses of the seven strategies that play to AI's strengths (process scaffolding) rather than its weaknesses (current local detail).</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompts produce outputs in language. Language is your subject. There's an awkward overlap here.</p>
    <p class="text-sm mb-2">Productive overlap. Language teachers can prompt AI better than most because they understand register, audience, and form. The seven strategies explicitly require these moves.</p>
    <p class="text-sm">You'll find a framework that promotes language teachers from amateurs in a new genre to natural experts in it. Your existing skill becomes a starting advantage.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompt engineering keeps reframing AI as a tool. The harder questions are political.</p>
    <p class="text-sm mb-2">Both matter. The module's framing as "reflective professional practice" is itself a political stance — it positions teachers as designers, not users. That has implications for the tool/agent debate.</p>
    <p class="text-sm">You'll get a pedagogically grounded framing of prompting that has political weight: teachers as designers, not consumers, of AI in education.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Prompt engineering as a discipline is debatable. Some of you are sceptical.</p>
    <p class="text-sm mb-2">Reasonable. The module sidesteps the debate by reframing the practice as instructional design, drawing on backward design, AI-TPACK, and Schön's reflective practice. Established traditions, new application.</p>
    <p class="text-sm">You'll get a teaching-specific framing that avoids the "is prompt engineering real" argument and roots the practice in established educational theory.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI prompting feels like a desk job. PE is on the field.</p>
    <p class="text-sm mb-2">Most of your prompting will happen at the desk before the field — generating warm-up variations, drafting risk assessments, producing inclusive rule rewrites. Then the field stays purely human.</p>
    <p class="text-sm">You'll get prompting workflows that stay at the prep stage, leaving your actual teaching where it belongs: with bodies in motion, no AI in sight.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're not interested in AI image generation prompts. That's not what you want to teach.</p>
    <p class="text-sm mb-2">Image generation isn't this module. This is about prompting AI to support your prep — drafting critique scaffolds, varying artist-statement structures, producing reading guides for art-history texts you've selected.</p>
    <p class="text-sm">You'll find prompting uses that respect your stance on AI-generated art, focusing on prep instead of production. Your artistic line stays where you draw it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Universal prompting strategies will fail your students. They always do.</p>
    <p class="text-sm mb-2">Universal isn't the framing. The module's strategies include explicit audience and constraints definition, which is exactly where SEN-specific prompting starts: precise about your student, the access need, the cognitive load.</p>
    <p class="text-sm">You'll get prompting moves that operationalise your individualisation expertise. Applied to AI tools that otherwise default to generic outputs.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years isn't a place for AI prompts. Children need humans.</p>
    <p class="text-sm mb-2">Children need humans; the prompts in this module are for the adult prep, never the child interaction. AI for drafting your learning stories, planning provocations, summarising parent conversations.</p>
    <p class="text-sm">You'll get adult-facing prompting that creates time for what early years actually needs: more presence, less paperwork.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Five subjects, one teacher, no time. Learning seven strategies for prompting AI sounds like another commitment.</p>
    <p class="text-sm mb-2">The seven strategies pay off most when you reuse them across subjects. A goal-context-format template you build for spelling-list generation transfers to maths-problem variation, science-vocabulary work, art-discussion prompts.</p>
    <p class="text-sm">You'll get a small investment in seven reusable strategies that compound across your multi-subject week. Instead of needing seven different prompting approaches.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';

-- M5 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Yet another framework with seven strategies. They all promise the world.</p>
    <p class="text-sm mb-2">This one is grounded in teacher professional development theory rather than tech-press hype. It treats prompting as a reflective practice, not a productivity hack.</p>
    <p class="text-sm">You'll get a pedagogically grounded approach to prompting that respects your professional identity. Rather than retraining you as a power user.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M5';


-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Expected: 17 records per module (M1, M2, M3, M4, M5)
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
      AND m.code IN ('M1','M2','M3','M4','M5');

    RAISE NOTICE 'Total subject_intro records for M1-M5: %', v_count;

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
--   AND m.code IN ('M1','M2','M3','M4','M5')
-- GROUP BY m.code
-- ORDER BY m.code;
--
-- Expected: 5 rows, each with hooks=17 and distinct_subjects=17
-- ============================================================================
