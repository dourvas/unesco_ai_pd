-- ============================================================================
-- SUBJECT INTRO HOOKS — M11 to M15 (Create Level)
-- ============================================================================
-- Phase 4c of Subject Intro Hooks rollout — FINAL BATCH
-- Records inserted: 85 (5 modules × 17 entries: 16 subjects + Universal)
-- Source: RESISTANCE_MATRIX_M11-M15.md (Phase 3 deliverable)
-- Spec: SUBJECT_INTRO_HOOKS_PATCH_APR2026.md
-- ============================================================================
-- Run order: M1-M5 FIRST, then M6-M10, then THIS file
-- Run via pgAdmin Query Tool against the PROODOS database
--
-- After this completes successfully, all 255 subject_intro records will be
-- in place across M1-M15 (15 modules × 17 = 255).
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- Idempotency: clear any existing subject_intro records for M11-M15
-- ----------------------------------------------------------------------------
DELETE FROM modules_modulecontent
WHERE content_type = 'subject_intro'
  AND module_id IN (SELECT id FROM modules_module WHERE code IN ('M11','M12','M13','M14','M15'));


-- ============================================================================
-- M11 — Leading Human-Centred AI Practice
-- ============================================================================

-- M11 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're not a head of department. Talking about leadership in AI doesn't apply to you.</p>
    <p class="text-sm mb-2">Maths departments often follow whichever colleague is most articulate about AI, regardless of position. If you've thought carefully about AI in maths teaching, you're already shaping departmental norms.</p>
    <p class="text-sm">You'll come to recognise the informal influence you may already have. Frames for using it intentionally instead of by accident.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Department politics in English are intense. Stepping forward on AI risks taking sides you'd rather not take.</p>
    <p class="text-sm mb-2">Stepping forward isn't the only mode. Modelling — using AI thoughtfully in your own practice and being honest when you do — is leadership without taking public positions.</p>
    <p class="text-sm">You'll get a leadership-by-modelling approach that doesn't require you to argue the AI debate publicly. Still shapes your department's norms.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science departments respond to evidence, not to leadership rhetoric. Until you have evidence, you shouldn't lead.</p>
    <p class="text-sm mb-2">Evidence-gathering is leadership. The teacher who runs a small classroom inquiry on AI use, shares what they noticed, and invites colleagues to do the same is leading by establishing evidence-norms in the department.</p>
    <p class="text-sm">You'll get a leadership approach grounded in evidence-gathering rather than assertion. Suited to science departments and to teachers reluctant to claim expertise.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics teachers are sceptical by training. Most of what's said about AI in education is overclaimed.</p>
    <p class="text-sm mb-2">Sceptical leadership is leadership too — possibly the most needed kind right now. The teacher who reliably distinguishes evidence-backed claims from hype is doing leadership work.</p>
    <p class="text-sm">You'll get a frame for productive scepticism as a leadership stance, not as withdrawal. Useful in departments where someone needs to keep the conversation honest.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry departments tend to focus on safety and content. AI leadership feels off-topic.</p>
    <p class="text-sm mb-2">Chemistry teachers already lead on safety, which is an analogous form of leadership: setting departmental norms about risks that aren't fully understood. AI raises related questions about new student-facing risks.</p>
    <p class="text-sm">You'll get an extension of the safety-leadership role you already practice. Applied to AI-related decisions about student exposure and data.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You don't want to become the AI-explainer for your department. Too much extra work.</p>
    <p class="text-sm mb-2">Leadership doesn't mean becoming the explainer. It means shaping how the department handles AI when it comes up: who decides, what the criteria are, when to consult specialists. That's a smaller, repeatable role.</p>
    <p class="text-sm">You'll get a leadership pattern that delegates the "explainer" load while keeping the steering. Process-shaping rather than content-producing.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Departments make AI decisions through politics. History departments especially. You can't lead through that.</p>
    <p class="text-sm mb-2">Politics is leadable through process. The teacher who proposes a clear decision process — who's consulted, what's documented, when revisions happen — leads even without status.</p>
    <p class="text-sm">You'll get process-design as leadership, distinct from positional leadership. Suited to teachers who'd rather not enter departmental politics directly.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're new to your department. Leadership talk is premature.</p>
    <p class="text-sm mb-2">Newness is a credible leadership platform on rapidly-changing topics. The teacher who says "I'm new and I'm curious how we should think about this" can convene a conversation that established colleagues would struggle to start.</p>
    <p class="text-sm">You'll get a newness-as-asset frame for AI-related leadership conversations. Useful when established colleagues feel locked into prior positions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Language departments are international by nature. AI leadership conversations get tangled in local-vs-global debates fast.</p>
    <p class="text-sm mb-2">Tangled in productive ways. The teacher who maps the local-vs-global tensions clearly — what's being debated, what's at stake, what trade-offs apply — is leading the conversation by clarifying it.</p>
    <p class="text-sm">You'll get a clarification-as-leadership move that doesn't require taking sides. Suitable for departments where positions are mixed.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You have strong views on AI's social effects. Leading risks pushing your views on colleagues.</p>
    <p class="text-sm mb-2">The module distinguishes view-pushing from norm-shaping. Leadership-by-norm-shaping focuses on how decisions get made (criteria, evidence, voices), not what gets decided. Your views remain yours.</p>
    <p class="text-sm">You'll get a leadership pattern that protects your views from becoming departmental views. While still influencing how the department operates.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You get asked AI questions constantly already. Adding intentional leadership feels like more of the same.</p>
    <p class="text-sm mb-2">Intentional is the difference. Right now you may be defaulting into a reactive role. The module's frame is choosing what to lead on, what to deflect, what to delegate.</p>
    <p class="text-sm">You'll get a frame for shaping your reactive AI-explainer role into a chosen one. Clear scope and explicit handovers.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE gets ignored in school-wide AI conversations. You can't lead a conversation you're not in.</p>
    <p class="text-sm mb-2">PE's exclusion is one of the most important things to surface. The teacher who insists PE is part of the conversation — through brief specific cases, not abstract argument — is leading on inclusion in a department where inclusion gets discussed otherwise.</p>
    <p class="text-sm">You'll get specific moves to bring PE into school-wide AI conversations. Drawing on cases your colleagues won't have considered.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Art teachers aren't usually asked about technology decisions. You're seen as creative, not strategic.</p>
    <p class="text-sm mb-2">The art teacher's stance on AI in art-making is exactly what other departments need help articulating: where does human authorship live, what counts as the student's work, how do you teach process when the product can be generated. Those questions transfer.</p>
    <p class="text-sm">You'll come to recognise the leadership your stance offers to colleagues outside the arts. Working through related questions with less practice than you have.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">SEN voices are the last consulted on AI. Leadership is for departments with positional influence.</p>
    <p class="text-sm mb-2">SEN consultation late is the school's loss; SEN consultation early is leadership. The teacher who insists "before we adopt this, what about my students?" is leading on inclusion at the planning stage, when it matters.</p>
    <p class="text-sm">You'll get a leadership pattern of front-loading SEN considerations into AI adoption decisions. Explicit moves to claim the chair at that table.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years gets bypassed in AI decisions. You're seen as not-yet-relevant.</p>
    <p class="text-sm mb-2">Bypassed for now, until AI reaches early years (already starting). The teacher who establishes early-years AI norms before the products arrive is leading by precedent. Much less resistance than after.</p>
    <p class="text-sm">You'll get a pre-emptive leadership position for early years. Setting norms before the AI-product wave, rather than reacting after.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Primary generalists rarely lead on technology. You're seen as the audience for tech decisions, not the decision-makers.</p>
    <p class="text-sm mb-2">Primary teachers see AI's effects across subjects in ways that secondary specialists can't. That whole-child, whole-curriculum perspective is exactly what AI policy decisions miss when they're left to subject specialists.</p>
    <p class="text-sm">You'll get a leadership claim grounded in primary's unique cross-curricular vantage. Useful in school-wide AI conversations dominated by secondary specialist concerns.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';

-- M11 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You don't see yourself as a leader. The module title puts you off.</p>
    <p class="text-sm mb-2">Leadership in this module is informal and chosen, not positional and assigned. It's about which conversations you shape and how, not about a job title.</p>
    <p class="text-sm">You'll get a definition of leadership that fits teachers without management positions. Explicit permission to lead small, lead local, lead through example.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M11';


-- ============================================================================
-- M12 — Designing AI Policy and Classroom Norms
-- ============================================================================

-- M12 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You write rules for your classroom; that's not policy. Policy is institutional.</p>
    <p class="text-sm mb-2">Classroom rules become policy when they're shared, debated, and adopted. The maths teacher who drafts a clear AI-on-homework policy, brings it to the department, and lets it spread is doing policy work.</p>
    <p class="text-sm">You'll get a frame for treating your classroom AI rules as policy drafts, rather than personal preferences. That raises their influence within your school.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Writing assessment policy is contested. You don't want your draft to become ammunition.</p>
    <p class="text-sm mb-2">The module's drafting approach foregrounds documentation of trade-offs, not advocacy of positions. A draft that explicitly names what it gives up is harder to weaponise than one that asserts.</p>
    <p class="text-sm">You'll get a drafting style that surfaces trade-offs explicitly. Making your policy contributions harder to caricature in departmental conflicts.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Science teaching has stable norms. AI policy on top of them feels like an add-on layer that won't last.</p>
    <p class="text-sm mb-2">Layer is the right word, and modular layers are easier to revise than integrated ones. Drafting AI policy as a separable layer means it can be updated as AI changes without disturbing the stable science-teaching norms underneath.</p>
    <p class="text-sm">You'll get a modular drafting approach that protects existing science teaching norms from AI-related churn. While still addressing the new AI-specific decisions.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy without enforcement is theatre. You won't enforce; therefore you shouldn't draft.</p>
    <p class="text-sm mb-2">Enforcement is one mode. The module covers policies that work through transparency and explicit norms rather than through punishment. Different design philosophy.</p>
    <p class="text-sm">You'll get policy patterns that operate through transparency and explicit expectation-setting rather than through detection and consequence. Suited to teachers who don't want to be enforcers.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry safety policy is well-established. AI policy is a separate domain.</p>
    <p class="text-sm mb-2">Separate domain, related craft. The same drafting moves that produce good safety policy — explicit hazards, clear boundaries, escalation paths — produce good AI policy. The skill transfers.</p>
    <p class="text-sm">You'll come to recognise that you've drafted policy before, in safety. The same craft applies. Lower learning curve than the topic suggests.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy in your school comes from senior leadership. Drafting from below feels futile.</p>
    <p class="text-sm mb-2">Senior leadership often inherits drafts from below. The teacher whose departmental policy gets adopted, even informally, has effectively contributed to school policy without formal authority.</p>
    <p class="text-sm">You'll get a path from departmental drafting to informal school-level adoption that doesn't require positional authority. Useful when waiting for top-down policy isn't an option.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy-drafting modules teach generic frameworks. History needs specific cases.</p>
    <p class="text-sm mb-2">The module's frameworks are populated with cases, including history-specific ones: handling AI-generated primary sources, citation-of-AI in essays, evaluation of student-AI conversation in research. Cases are the point, not the framework.</p>
    <p class="text-sm">You'll get history-specific policy cases drafted out. Useful as starting points for your own departmental adaptation.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Field-trip and data-collection policy already covers most relevant cases.</p>
    <p class="text-sm mb-2">Mostly. New cases that existing policy may not cover: location-data privacy when students use AI mapping tools, AI-generated demographic claims in projects, satellite imagery interpretation responsibility.</p>
    <p class="text-sm">You'll get specific gap-filling cases for geography departments. Identifying where existing policy doesn't reach AI-era practice.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Translation-tool policy is what colleagues mean when they say "AI policy." That conversation is exhausted.</p>
    <p class="text-sm mb-2">Translation is one cell in a much larger map. Other cells: AI as conversation partner (privacy of student speech data), AI in pronunciation feedback (what counts as cheating), AI in writing support (where the line is in a second language).</p>
    <p class="text-sm">You'll find policy cases beyond the translation-tool debate. Drawn from the wider footprint AI now has in language classrooms.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy-drafting is in your curriculum. The module risks reinventing the wheel for your specialty.</p>
    <p class="text-sm mb-2">Curriculum policy-drafting is content. Classroom AI policy-drafting is operational. Different scale and stakes — closer to a workplace policy than to a public policy.</p>
    <p class="text-sm">You'll get operational policy practice (your classroom, your department) distinct from the public-policy curriculum content you teach.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You're asked to draft school-wide AI policy already. The expectation is that you can do this.</p>
    <p class="text-sm mb-2">Drafting school-wide AI policy is hard, and there's almost no formal preparation for it. The module is exactly the preparation that's currently missing.</p>
    <p class="text-sm">You'll get structured preparation for the school-wide policy drafting you're likely already being asked to do. Replacing the current improvise-from-first-principles approach.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE-specific AI policy doesn't exist anywhere. You'd be drafting from scratch.</p>
    <p class="text-sm mb-2">Drafting from scratch is the contribution. The module supports first-drafts in under-served subjects, where existing policy templates don't reach.</p>
    <p class="text-sm">You'll get drafting support for PE-specific AI policy. Claiming territory where general policy doesn't yet reach. Pioneering work in a small but unique area.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Art policy on AI image generation is impossible to draft cleanly. The lines don't hold.</p>
    <p class="text-sm mb-2">They don't hold cleanly anywhere. The module's drafting approach accepts this and aims for "least-bad" policy rather than coherent policy: explicit known unknowns, planned revisions, documented trade-offs.</p>
    <p class="text-sm">You'll get a drafting approach for genuinely contested territory. Suited to art classrooms where coherent AI policy may not be possible right now.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">SEN gets specific exemptions in most school policies, which means SEN drafting is afterthought work.</p>
    <p class="text-sm mb-2">Drafting SEN-specific provisions early, rather than as exemptions added later, changes the policy entirely. The module supports SEN-leading drafts that other students' provisions get bolted onto.</p>
    <p class="text-sm">You'll get a drafting strategy where SEN provisions structure the policy rather than being attached as exceptions. Explicit moves to claim that drafting position.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years is rarely included in school AI policy because you don't use the AI tools in question.</p>
    <p class="text-sm mb-2">Use is widening fast. Drafting early-years-specific AI policy now, before products arrive, sets the boundaries that later staff will inherit. Pre-emptive policy.</p>
    <p class="text-sm">You'll get a pre-emptive policy drafting approach for early years, ahead of product arrival. The drafting is easier and the resulting boundaries are stronger.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy-drafting feels secondary-school. Primary policy is mostly behaviour and safeguarding.</p>
    <p class="text-sm mb-2">Primary AI policy fits inside safeguarding and behaviour policy frames. The drafting work is updating existing primary-specific policies to address AI cases, not building parallel structures.</p>
    <p class="text-sm">You'll get primary-specific drafting that extends existing safeguarding and behaviour policy to cover AI cases. In the form your school is already used to.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';

-- M12 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Policy is for someone else to write. You just implement.</p>
    <p class="text-sm mb-2">"Just implement" still requires interpretation, and your interpretation becomes policy by precedent. The module surfaces this implicit drafting and makes it intentional.</p>
    <p class="text-sm">You'll come to recognise that you may already be drafting policy informally through your teaching choices. Frames for doing so explicitly.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M12';


-- ============================================================================
-- M13 — Multimodal AI Content Creation
-- ============================================================================

-- M13 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Maths doesn't need multimodal content. Diagrams, equations, and worked examples are all you produce.</p>
    <p class="text-sm mb-2">Diagrams are a multimodal output. AI diagram tools, animation generators, and even voice-over for video explanations are all multimodal AI applied to maths-teaching content.</p>
    <p class="text-sm">You'll get specific multimodal AI tools for maths content (diagram generation, animated walkthroughs, audio explanations). Judgement on when each pays off.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You want students writing words, not generating images. Multimodal AI is a distraction from your subject.</p>
    <p class="text-sm mb-2">Multimodal AI use as a teaching tool, in your prep, is different from student use of multimodal AI in their work. The module focuses on the first.</p>
    <p class="text-sm">You'll get teacher-side multimodal applications (visual scaffolds for texts, audio versions for accessibility, illustrated vocabulary support). Serving word-focused learning rather than diluting it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Generating science visuals risks producing pretty wrong things. The cost-benefit is poor.</p>
    <p class="text-sm mb-2">Right for content visuals (e.g., "draw a mitochondrion" — risky). Lower-risk applications: animated worked examples, audio explanations of your own diagrams, video summaries of practicals you've recorded.</p>
    <p class="text-sm">You'll get a risk map of multimodal AI in science teaching. Safer applications named explicitly and the risky ones quarantined.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Visualisation of physics concepts is precise work. AI tools will produce convincing nonsense.</p>
    <p class="text-sm mb-2">Convincing nonsense is the central risk. The module's physics applications avoid concept-visualisation and focus on applications where AI produces support material around your accurate visuals — voice-overs, accessibility versions, transcript generation.</p>
    <p class="text-sm">You'll get multimodal applications that respect physics' visualisation precision. Working around your accurate diagrams rather than producing replacement ones.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry visualisations need accuracy down to bond angles. AI image tools won't deliver.</p>
    <p class="text-sm mb-2">They won't, and the module accepts this. Useful applications: producing audio versions of your written explanations, animating chemical processes from your storyboards, generating video transitions between concepts.</p>
    <p class="text-sm">You'll get multimodal applications that use your chemistry expertise as input and produce alternative formats as output. Rather than asking AI to know chemistry.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology image generation produces wrong cellular structure, wrong anatomy, wrong species traits. Useless.</p>
    <p class="text-sm mb-2">Image generation is a small slice. Other applications: audio descriptions of your microscopy images, video walkthroughs of dissections from your photos, narrated animations of your own diagrams.</p>
    <p class="text-sm">You'll get biology multimodal applications that route around image generation entirely. Focused on alternative formats of accurate content you've produced.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">AI-generated historical imagery is a particular ethics problem — fake faces, fake events. You don't want to encourage it.</p>
    <p class="text-sm mb-2">Historical imagery generation isn't recommended in the module. Recommended applications: audio versions of primary sources, narrated map animations, transcript generation for archival video.</p>
    <p class="text-sm">You'll get multimodal applications that respect history's image-ethics problem by avoiding image generation entirely. Focus on audio and animation of accurate sources.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geographic visuals must be accurate to place. AI struggles with specific locations.</p>
    <p class="text-sm mb-2">Specific-location image generation is unreliable, but geographic teaching uses many other multimodal forms: narrated atlas animations, audio descriptions of fieldwork sites, video summaries from your fieldwork footage.</p>
    <p class="text-sm">You'll get multimodal applications grounded in your accurate location data. Using AI only for format conversion and accessibility extension.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI in language teaching means video conversation partners. Privacy and quality concerns make you cautious.</p>
    <p class="text-sm mb-2">Conversation partners are one application. Lower-risk: AI-generated comprehensible-input audio at controlled levels, video transcripts for authentic materials, voice-acted versions of student-written dialogues.</p>
    <p class="text-sm">You'll get lower-risk multimodal applications for language learning that don't require students to interact with AI directly. Focus on AI-as-production-tool for prep materials.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI generates the deepfakes you're trying to teach students to recognise. Using it yourself feels contradictory.</p>
    <p class="text-sm mb-2">Using it intentionally and showing the workings is exactly the lesson. The teacher who creates an AI image, points out the production process, and discusses detection is teaching the literacy directly.</p>
    <p class="text-sm">You'll get a teaching pattern where your own multimodal AI use becomes content for the literacy you're teaching. Instead of a contradiction to it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You know multimodal AI tools. The module won't introduce you to anything new.</p>
    <p class="text-sm mb-2">Tool knowledge is one part. The teacher-decision part — when to use, when not to, how to model decision-making for students — is less covered in CS curricula and more useful in your role.</p>
    <p class="text-sm">You'll get decision-making frames for multimodal AI use that complement your tool knowledge. Useful when modelling AI choice-making to students.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI for PE? Beyond a few stretching videos, hard to imagine.</p>
    <p class="text-sm mb-2">PE-specific applications: voice-narrated drill demonstrations, audio descriptions for accessibility, video summaries of student performance from your footage. Modest but useful.</p>
    <p class="text-sm">You'll get a small set of PE-specific multimodal applications that fit prep-stage work. Keeping class-time AI-free if you choose.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Image generation is core to this module. You have strong reservations about it in art teaching.</p>
    <p class="text-sm mb-2">Reservations are reasonable, and the module includes them. Applications proposed: image generation as a contrast to student work (not a replacement), audio analysis of student work, video time-lapse summaries.</p>
    <p class="text-sm">You'll get an honest treatment of image generation in art teaching. Applications proposed only where the AI image is contrasted-with rather than substituted-for student work.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI tools are accessibility tools first. You should know this content already.</p>
    <p class="text-sm mb-2">Many SEN teachers do, and this module's contribution is more on the production-side: creating multimodal versions of materials you've designed (audio versions, video walkthroughs, image descriptions) at scale.</p>
    <p class="text-sm">You'll get production-side multimodal techniques for SEN teachers who already know the consumption-side accessibility tools. Focused on creating differentiated materials at scale.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early years materials should be human-made and warm. AI multimodal feels cold.</p>
    <p class="text-sm mb-2">AI multimodal can be your prep, with the human-made warmth at delivery. Applications: AI-generated story-prompt images you reflect on with children, audio versions of your own learning stories for parent communication, video summaries of children's work for portfolios.</p>
    <p class="text-sm">You'll get adult-side multimodal AI prep that supports the warm, human delivery early years requires. No AI in child-facing material.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI looks like a media production module. You don't have time to learn five AI tools.</p>
    <p class="text-sm mb-2">The module recommends two or three reusable tools, not five. The same image-generation tool produces visuals across your subjects; the same audio tool reads multiple texts.</p>
    <p class="text-sm">You'll get a short list of multimodal tools selected for primary-generalist reuse across subjects. Not a tour of every available platform.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';

-- M13 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Multimodal AI sounds like content creation for marketing teams, not classroom teachers.</p>
    <p class="text-sm mb-2">The module's framing is teacher-as-prep-producer, not content-creator. Multimodal applications focus on audio/video versions of materials you already produce, not on becoming a media designer.</p>
    <p class="text-sm">You'll get specific multimodal applications for routine teacher prep. No expectation of becoming a content creator beyond that.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M13';


-- ============================================================================
-- M14 — AI-Engaged Pedagogy: Roles and Strategies
-- ============================================================================

-- M14 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Maths pedagogy is well-developed. Adding "AI roles" risks importing language that doesn't fit.</p>
    <p class="text-sm mb-2">The Five Roles framework is descriptive of moves you may already make: explainer, facilitator, evaluator, designer, learner. Adding "in AI contexts" doesn't change the moves; it labels them.</p>
    <p class="text-sm">You'll get vocabulary for moves you already do, applied to AI-augmented teaching. Useful for talking with colleagues about what you choose to keep human.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Pedagogy modules tend to assume your classroom is more structured than it is.</p>
    <p class="text-sm mb-2">The Five Roles describe what you do in any moment, regardless of structure. They're observation tools, not lesson templates.</p>
    <p class="text-sm">You'll get observation-tool framing for the Five Roles. Useful for noticing your own moves rather than for restructuring your classroom.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Gamification and pedagogy strategies are usually fluffy. You want operational guidance.</p>
    <p class="text-sm mb-2">Gamification in this module is bounded: specific game elements (points, competition, narrative) used for specific purposes, with explicit cases of when each backfires. Operational, not motivational.</p>
    <p class="text-sm">You'll get bounded gamification with specific use cases and explicit failure modes. Suited to teachers who want operational rather than inspirational guidance.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics pedagogy is conceptually careful. Game elements risk making learning superficial.</p>
    <p class="text-sm mb-2">That risk is real, and the module names it. Recommended placements: gamification of practice (drill repetition), not of concept introduction. Different cognitive territory.</p>
    <p class="text-sm">You'll get a clear placement-rule (gamify practice, not concept) that protects physics' conceptual core. While allowing engagement-aiding game elements where they help.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Chemistry classroom strategies are constrained by safety. Most pedagogy modules ignore this.</p>
    <p class="text-sm mb-2">The module's chemistry-specific notes include safety constraints explicitly: which strategies fit lab work, which fit theory, which require seating arrangements that lab benches won't allow.</p>
    <p class="text-sm">You'll get pedagogical strategies that respect chemistry's classroom constraints. Explicit attention to safety-shaped seating, equipment, and group dynamics.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Biology has a content-coverage problem. Adding new pedagogical strategies makes coverage harder.</p>
    <p class="text-sm mb-2">Coverage isn't increased by the strategies; engagement is. The module's case is that engagement-shaped strategies cover content faster, not slower, when applied selectively.</p>
    <p class="text-sm">You'll get a case for selective strategy use focused on coverage-efficiency, not on engagement-for-its-own-sake. Suited to teachers under content-pressure.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">History pedagogy has rich traditions. Importing AI-era strategies risks distracting from them.</p>
    <p class="text-sm mb-2">Importing isn't replacing. The module shows how AI-era strategies extend existing history-teaching moves (source analysis, perspective-taking, narrative comparison) rather than displacing them.</p>
    <p class="text-sm">You'll get extension-of-existing-traditions framing. AI-era strategies plugged into history's pedagogical lineage rather than imported alongside it.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Geography pedagogy depends on fieldwork and place. Classroom strategy modules don't reach this.</p>
    <p class="text-sm mb-2">Strategy applications include: fieldwork-prep gamification, place-based investigation roles, cross-classroom collaboration on shared spatial problems. Not desk-bound.</p>
    <p class="text-sm">You'll get strategies that travel out of the classroom and into the field. Suited to geography's place-based work.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Communicative language teaching has its own well-developed pedagogy. New strategy modules muddy it.</p>
    <p class="text-sm mb-2">The module's CLT-compatibility section is explicit. Strategies that fit communicative aims are included; strategies that pull toward translation-drilling are flagged as anti-CLT.</p>
    <p class="text-sm">You'll get explicit CLT-compatibility analysis for proposed strategies. Adopt selectively without disrupting the communicative orientation you've built.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Social studies pedagogy is contested between content-focused and skills-focused traditions. New strategies often pick a side.</p>
    <p class="text-sm mb-2">The module's strategies are designed to serve either tradition, with explicit notes on how they look in each. You don't have to take a side to use them.</p>
    <p class="text-sm">You'll get tradition-neutral strategy implementations. Notes on how each looks within content-focused vs skills-focused practice.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You gamify naturally — much of CS teaching is project-based already. The module may be repetitive.</p>
    <p class="text-sm mb-2">CS-specific contributions: roles for AI-pair-programming sessions, ethical dilemma scenarios as assessment, code-review-with-AI as a specific pedagogical pattern.</p>
    <p class="text-sm">You'll get CS-specific strategy patterns that go beyond the project-based work you may already use. Focused on the AI-collaboration dynamics increasingly common in your subject.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE is gamified by definition — sport is play. Adding gamification frameworks feels redundant.</p>
    <p class="text-sm mb-2">Sport is one form of gamification; the module covers the other (extrinsic motivation, points/rewards, narrative framing) with explicit notes on PE-specific risks (over-extrinsic motivation displacing intrinsic enjoyment of movement).</p>
    <p class="text-sm">You'll get PE-specific notes on gamification's risks (motivation displacement, competitive harm) alongside its uses. Suited to a subject already deeply gamified in its core practice.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Art teaching values process and presence. Strategy frameworks lean toward product-and-output thinking.</p>
    <p class="text-sm mb-2">Module's arts-specific notes include process-protected strategies: gamification of skill drills (not of art-making), role-rotation for collaborative work (not for solo making), AI-engagement at critique stage (not at making stage).</p>
    <p class="text-sm">You'll get strategy patterns explicitly arranged to protect process-and-presence. AI-engagement quarantined to critique and skill-development moments.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">SEN pedagogy is highly individualised. Strategy frameworks risk over-standardising.</p>
    <p class="text-sm mb-2">Frameworks in the module are presented as menus of options, not as standards. SEN-specific notes include explicit individualisation moves and warnings about over-application.</p>
    <p class="text-sm">You'll get strategy menus with individualisation-first framing. Suited to SEN teaching where standardised strategy implementation usually fails.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Strategy frameworks for early years tend to import secondary patterns inappropriately.</p>
    <p class="text-sm mb-2">The early-years-specific section explicitly resists secondary-import. Strategies are recast in early-years terms (story-based gamification, role-as-character-not-job, AI-as-tool-the-teacher-uses-not-the-child).</p>
    <p class="text-sm">You'll get early-years-recast versions of the strategies. Designed to fit your developmental context rather than imported from secondary.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Strategy modules assume specialist teachers with single-subject planning. Five subjects make most strategy applications fragile.</p>
    <p class="text-sm mb-2">Module includes primary-generalist-specific notes: which strategies survive cross-subject rotation, which ones break, which ones strengthen with cross-subject use.</p>
    <p class="text-sm">You'll get cross-subject viability analysis for each strategy. Suited to multi-subject planning where some strategies that work in single-subject contexts collapse in primary classrooms.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';

-- M14 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Pedagogy strategy modules lean inspirational. You want practical.</p>
    <p class="text-sm mb-2">This module's strategies come with explicit boundary conditions, contraindications, and known failure modes. Practical, not inspirational.</p>
    <p class="text-sm">You'll get strategy implementations with explicit boundaries and warnings. Useful as a working menu rather than as a vision document.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M14';


-- ============================================================================
-- M15 — Professional Transformation and Research Leadership
-- ============================================================================

-- M15 × mathematics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'mathematics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Mathematics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Maths-teaching research is dominated by university researchers. Your contribution would be ignored.</p>
    <p class="text-sm mb-2">Classroom-research traditions in maths are well-established (Lesson Study, Action Research). Most aren't published academically and don't aim to be. They circulate among practitioners and inform practice.</p>
    <p class="text-sm">You'll get a practitioner-research framing distinct from academic publication. Examples of how maths-teaching research moves through practitioner networks regardless of academic recognition.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × language_arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'language_arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Language Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You write professionally elsewhere. Research writing is a different genre you haven't trained in.</p>
    <p class="text-sm mb-2">Practitioner research writing is closer to professional reflection essays than to academic articles. Existing strong writing transfers more directly than the research-writing label suggests.</p>
    <p class="text-sm">You'll get genre clarification — practitioner research is a transferable extension of professional reflection writing. Useful for teachers who already write but feel research-writing is alien.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Action research in education isn't real science. The methods are loose.</p>
    <p class="text-sm mb-2">True for educational research generally, and the module accepts it. The framing isn't "this is rigorous" but "this is structured noticing." A small step up from informal teacher reflection, not a small step down from controlled experiment.</p>
    <p class="text-sm">You'll get an honest framing of action research as structured noticing, neither inflated nor dismissed. Suited to science teachers who'd see through false rigour-claims.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × physics
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physics', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physics</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Physics teachers are particularly likely to call out methodological weakness in education research. You'd rather not produce something you'd criticise yourself.</p>
    <p class="text-sm mb-2">The module's research patterns emphasise observation over claim. The action-research output documents what you tried and what you noticed; it doesn't claim cause-effect or generalisability.</p>
    <p class="text-sm">You'll get research patterns suited to physics teachers' methodological scepticism. Focused on observation-documentation rather than causal claims.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × chemistry
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'chemistry', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Chemistry</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You have no research training. This module assumes capacities you don't have.</p>
    <p class="text-sm mb-2">No formal research training is needed. The capacities required are noticing, recording, reflecting — which you already deploy in safety supervision and lab observation. New domain, same skills.</p>
    <p class="text-sm">You'll get a no-formal-training framing that draws on capacities you already use in classroom supervision. Redirected into structured AI noticing.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × biology
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'biology', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Biology</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Practitioner research is a genre you don't read. You wouldn't know what good looks like.</p>
    <p class="text-sm mb-2">Module includes practitioner-research examples specifically chosen for accessibility — short, structured, modest in claim. Looking like good is closer to your written reflections than to academic articles.</p>
    <p class="text-sm">You'll get examples of practitioner research at the level you might produce. Demystifying the genre.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × history
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'history', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">History</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">History teachers research history; you're not researchers of teaching.</p>
    <p class="text-sm mb-2">Researching teaching uses many of the same skills as researching history: contextualisation, source-evaluation, narrative-construction. The historian-as-teacher-researcher is a natural transfer.</p>
    <p class="text-sm">You'll get a skill-transfer framing for history teachers. Action research as a redirection of historical-research skills toward classroom phenomena.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × geography
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'geography', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Geography</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Field-research skills don't translate cleanly to classroom research.</p>
    <p class="text-sm mb-2">They translate more than expected: observation protocols, sampling questions, contextualisation, write-up under length constraints. Field-research literacy is closer to classroom-research literacy than either is to laboratory science.</p>
    <p class="text-sm">You'll get a transfer-framing for geographic field-research literacy, applied to classroom AI-noticing.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × foreign_languages
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'foreign_languages', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Foreign Languages</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Language-teaching research has been dominated by SLA theory. Without that training, your research contribution feels weak.</p>
    <p class="text-sm mb-2">Practitioner research isn't competing with SLA theory. It's documentation of classroom phenomena that SLA researchers can't observe directly. Distinct contribution, not weaker version.</p>
    <p class="text-sm">You'll get a complementary-not-competitive framing for language teachers' practitioner research. Distinct from the SLA tradition.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × social_studies
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'social_studies', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Social Studies</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">You research and teach research. The module risks duplicating what you already deliver.</p>
    <p class="text-sm mb-2">Curricular research-teaching is distinct from teacher-as-researcher work. The module's contribution is doing research yourself, on your own classroom, for your own development. Different position from teaching research methods to students.</p>
    <p class="text-sm">You'll get researcher-position practice for teachers who already teach research methods. Complementing the curricular role with personal practice.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × computer_science
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'computer_science', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Computer Science</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">CS-education research is well-funded and well-staffed. Your informal observations won't add to it.</p>
    <p class="text-sm mb-2">Most CS-education research is on undergraduates and on coding-specific learning. K-12 CS-with-AI is largely under-researched, with practitioners better positioned to observe than university researchers.</p>
    <p class="text-sm">You'll find a specifically under-researched territory (K-12 CS in AI era) where practitioner observation has unusual value. Partially addressing the "won't add" concern.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × physical_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'physical_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Physical Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">PE research outside university physiology departments is rare. You don't have a model for what to produce.</p>
    <p class="text-sm mb-2">Module includes PE-specific examples: classroom-observation studies of student engagement during AI-assisted skill development, comparison studies of pre/post AI-tool adoption, case studies of inclusion in AI-mediated PE.</p>
    <p class="text-sm">You'll get PE-specific practitioner research models. Drawn from a small but growing literature of teacher-led PE research.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × arts
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'arts', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Arts</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Arts research is mostly arts-production-as-research. Practitioner research in art teaching is rare.</p>
    <p class="text-sm mb-2">Rare and emerging. The module includes art-specific examples: action research on AI in critique, longitudinal observation of student creative confidence, case studies of AI-resistant studio cultures.</p>
    <p class="text-sm">You'll get art-teaching-specific research examples in an emerging space. Useful as starting points for your own work.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × special_education
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'special_education', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Special Education</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">SEN research has higher methodological bars. Practitioner research in this space risks being dismissed.</p>
    <p class="text-sm mb-2">Practitioner research in SEN is one of the more accepted forms because controlled studies are often ethically and practically impossible. Single-case practitioner research has standing in SEN literature.</p>
    <p class="text-sm">You'll come to recognise that practitioner research has stronger standing in SEN than in many other educational areas. Examples drawn from SEN literature.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × early_childhood
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'early_childhood', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Early Childhood</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Early-years research lives in a separate field. Practitioner research patterns from primary or secondary may not translate.</p>
    <p class="text-sm mb-2">Early-years-specific practitioner research is well-established (learning stories as research artefacts, observation-narrative-reflection cycles). The module's framing fits early years more than secondary, in fact.</p>
    <p class="text-sm">You'll get early-years-fit research patterns, drawn from learning-story traditions. Redirected toward AI-noticing in early-years contexts.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × other (Primary Generalist)
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'other', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Primary Generalist</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Primary research is usually small in scope and limited to in-house dissemination. The module's "leadership" language doesn't match your reality.</p>
    <p class="text-sm mb-2">Small-scope, in-house dissemination is exactly the form practitioner research takes. The module's leadership framing is informal: shaping what colleagues consider plausible, through documented examples from your own practice.</p>
    <p class="text-sm">You'll get a small-scope, low-status framing of leadership that fits primary-generalist reality. Distinct from the institutional-leadership language elsewhere in the module.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';

-- M15 × Universal
INSERT INTO modules_modulecontent (module_id, content_type, subject_area, grade_level, content_data, metadata, created_at, updated_at)
SELECT id, 'subject_intro', 'Universal', 'all',
$INTRO$
<div class="card bg-base-100 border-l-4 border-info shadow-sm my-6">
  <div class="card-body p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="badge badge-info">Your subject</span>
      <span class="font-semibold text-sm">Why this matters for you</span>
    </div>
    <p class="text-sm mb-2">Capstone modules tend to ask for outputs you're unlikely to produce.</p>
    <p class="text-sm mb-2">This module's outputs are scaled to what's possible: a short structured reflection, a colleague conversation with notes, a one-page case study. Floor outputs, not ceiling outputs.</p>
    <p class="text-sm">You'll get floor-level capstone outputs explicitly designed for completion. Rather than for impressive deliverable production.</p>
  </div>
</div>
$INTRO$,
'{}'::jsonb, NOW(), NOW()
FROM modules_module WHERE code = 'M15';


-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Expected: 17 records per module (M11, M12, M13, M14, M15)
-- Total: 85 records in this batch
-- Grand total across M1-M15: 255 records
-- ============================================================================

DO $$
DECLARE
    v_count INTEGER;
    v_total INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM modules_modulecontent mc
    JOIN modules_module m ON mc.module_id = m.id
    WHERE mc.content_type = 'subject_intro'
      AND m.code IN ('M11','M12','M13','M14','M15');

    RAISE NOTICE 'Total subject_intro records for M11-M15: %', v_count;

    IF v_count != 85 THEN
        RAISE EXCEPTION 'Expected 85 records for M11-M15, found %. Rolling back.', v_count;
    END IF;

    SELECT COUNT(*) INTO v_total
    FROM modules_modulecontent
    WHERE content_type = 'subject_intro';

    RAISE NOTICE 'GRAND TOTAL subject_intro records across M1-M15: %', v_total;

    IF v_total != 255 THEN
        RAISE WARNING 'Expected 255 grand total, found %. M1-M5 or M6-M10 may not have run yet.', v_total;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- POST-COMMIT VERIFICATION QUERY (run separately if desired)
-- ============================================================================
-- Final check: all 15 modules should have 17 hooks each = 255 total
--
-- SELECT m.code, COUNT(*) AS hooks, COUNT(DISTINCT mc.subject_area) AS distinct_subjects
-- FROM modules_modulecontent mc
-- JOIN modules_module m ON mc.module_id = m.id
-- WHERE mc.content_type = 'subject_intro'
-- GROUP BY m.code
-- ORDER BY
--     CASE m.code
--         WHEN 'M1' THEN 1 WHEN 'M2' THEN 2 WHEN 'M3' THEN 3 WHEN 'M4' THEN 4
--         WHEN 'M5' THEN 5 WHEN 'M6' THEN 6 WHEN 'M7' THEN 7 WHEN 'M8' THEN 8
--         WHEN 'M9' THEN 9 WHEN 'M10' THEN 10 WHEN 'M11' THEN 11 WHEN 'M12' THEN 12
--         WHEN 'M13' THEN 13 WHEN 'M14' THEN 14 WHEN 'M15' THEN 15
--     END;
--
-- Expected: 15 rows, each with hooks=17 and distinct_subjects=17
-- Grand total when summed: 255
-- ============================================================================
