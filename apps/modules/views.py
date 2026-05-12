from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.db.models import Q, Case, When, IntegerField
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import json
import sys
import os
import markdown
import importlib

from apps.compliance.services import record_ai_provenance

# Phase C C.3 commit 2a — gemini-2.5-flash is the operative model across
# the RAG / RTM / DTP / peer synthesis paths. Centralised here so a future
# model bump is a one-line change. Matches the constant in
# apps/compliance/management/commands/backfill_ai_provenance.py.
PROVENANCE_MODEL_NAME = 'gemini-2.5-flash'

from .models import (
    Module,
    ModuleContent,
    UserModuleProgress,
    Tab3UserActivity,
    Tab3PromptLibrary,
    Assessment,
    Tab3UserToolkit,
    Tab3RepositorySubmission,  # Phase A Tier 2 Step 4 (M13 patch)
)
from apps.users.models import TeacherProfile
from .models import ReflectionTension

# Import RAG system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from rag_query_system import process_reflection


class ModuleListView(LoginRequiredMixin, ListView):
    """Display all available modules with progress indicators"""
    model = Module
    template_name = 'modules/module_list.html'
    context_object_name = 'modules'
    
    def get_queryset(self):
        return Module.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user progress for each module
        user_progress = {}
        for module in context['modules']:
            try:
                progress = UserModuleProgress.objects.get(
                    user=self.request.user,
                    module=module
                )
                user_progress[module.code] = {
                    'started': True,
                    'percentage': progress.completion_percentage,
                    'completed': progress.completed_at is not None,
                    'current_tab': progress.current_tab,
                }
            except UserModuleProgress.DoesNotExist:
                user_progress[module.code] = {
                    'started': False,
                    'percentage': 0,
                    'completed': False,
                    'current_tab': 'introduction',
                }
        
        context['user_progress'] = user_progress
        
        return context


class ModuleDetailView(LoginRequiredMixin, DetailView):
    """
    Display module content with 5-tab navigation

    Tab 1 (introduction): Static content from modules table
    Tab 3 (activity): Special TAB 3 handling with prompts
    Tabs 2, 4, 5: Dynamic content from module_content with personalization
    """
    model = Module
    template_name = 'modules/module_detail.html'
    context_object_name = 'module'
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get(self, request, *args, **kwargs):
        """Phase C TD-012 — sequential prerequisite gate.

        Before rendering the module page, check whether the user has
        completed every prior module in order_index sequence. If not,
        redirect to the first uncompleted prior module with an
        informational flash. Staff and superusers bypass for support.
        """
        from django.contrib import messages
        from apps.modules.services import get_module_prerequisite_block

        # Resolve the target module first so we can inspect order_index.
        self.object = self.get_object()

        if not (request.user.is_staff or request.user.is_superuser):
            blocker = get_module_prerequisite_block(request.user, self.object)
            if blocker is not None:
                messages.info(
                    request,
                    'Please complete %s before opening %s.' % (
                        blocker.code, self.object.code,
                    ),
                )
                return redirect('modules:detail', code=blocker.code)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.object
        user = self.request.user
        
        # Get teacher profile
        try:
            teacher_profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            # Redirect to onboarding if profile incomplete
            return redirect('users:onboarding_welcome')
        
        # Get current tab
        current_tab = self.request.GET.get('tab', 'introduction')
        
        # Get or create user progress
        progress, created = UserModuleProgress.objects.get_or_create(
            user=user,
            module=module
        )
        
        # If first access, set enrolled
        if created or progress.status == 'not_started':
            progress.status = 'enrolled'
            progress.enrolled_at = timezone.now()
            progress.save()
        
        # ============================================================
        # TAB 1: INTRODUCTION
        # ============================================================
        if current_tab == 'introduction':
            context.update({
                'hero_image': module.hero_image_url,
                'module_title': module.title,
                'module_description': module.description,
                'learning_objectives': module.learning_objectives,
                'module_overview': module.module_overview,
                'estimated_hours': module.estimated_hours,
                'unesco_aspect': module.get_unesco_aspect_display(),
                'proficiency_level': module.get_proficiency_level_display(),
            })
        
        # ============================================================
        # TAB 3: ACTIVITY (SPECIAL HANDLING)
        # ============================================================
        elif current_tab == 'activity':
            print("\n" + "=" * 70)
            print("TAB 3 ACTIVITY - DEBUG START")
            print("=" * 70)
            
            # Get or create activity record
            activity, created = Tab3UserActivity.objects.get_or_create(
                user=user,
                module_id=module.id
            )
            print(f"✓ Activity record: created={created}")
            
            # Get prompts based on teacher's subject
            subject = teacher_profile.subject_area
            grade_level = teacher_profile.grade_level
            
            print(f"\n📋 User Profile:")
            print(f"   subject_area = '{subject}'")
            print(f"   grade_level = '{grade_level}'")
            
            # FORCE TEST: Try direct Mathematics query
            force_test = Tab3PromptLibrary.objects.filter(
                subject__iexact='Mathematics',
                prompt_type='good'
            ).first()
            print(f"\n🧪 Force test (subject__iexact='Mathematics'): {force_test}")
            
            # ACTUAL QUERY with user's subject
            print(f"\n🔍 Actual query with subject__iexact='{subject}':")
            good_prompt = Tab3PromptLibrary.objects.filter(
                subject__iexact=subject,
                prompt_type='good'
            ).first()
            print(f"   good_prompt = {good_prompt}")
            
            bad_prompt = Tab3PromptLibrary.objects.filter(
                subject__iexact=subject,
                prompt_type='bad'
            ).first()
            print(f"   bad_prompt = {bad_prompt}")
            
            subject_prompts = Tab3PromptLibrary.objects.filter(
                subject__iexact=subject,
                prompt_type__in=['lesson_plan', 'quiz', 'differentiation']
            )
            print(f"   subject_prompts count = {subject_prompts.count()}")
            
            # Show what's in database
            all_in_db = Tab3PromptLibrary.objects.all().count()
            print(f"\n📚 Total prompts in database: {all_in_db}")
            
            print("=" * 70 + "\n")
            
            # AI tools list
            ai_tools = [
                {'value': 'ChatGPT', 'label': 'ChatGPT', 'url': 'https://chat.openai.com', 'description': 'Most versatile, great for creative tasks'},
                {'value': 'Claude', 'label': 'Claude', 'url': 'https://claude.ai', 'description': 'Excellent for long documents and analysis'},
                {'value': 'Gemini', 'label': 'Gemini', 'url': 'https://gemini.google.com', 'description': 'Google integration, strong research'},
                {'value': 'Copilot', 'label': 'Microsoft Copilot', 'url': 'https://copilot.microsoft.com', 'description': 'Best for Microsoft 365 users'},
                {'value': 'Perplexity', 'label': 'Perplexity', 'url': 'https://perplexity.ai', 'description': 'Research-focused with citations'},
                {'value': 'DeepSeek', 'label': 'DeepSeek', 'url': 'https://chat.deepseek.com', 'description': 'Advanced reasoning capabilities'},
                {'value': 'Other', 'label': 'Other (specify)', 'url': '', 'description': 'Use a different AI tool'},
            ]
            
            # Add TAB 3 specific context
            context.update({
                'activity': activity,
                'subject': subject,
                'grade_level': grade_level,
                'good_prompt': good_prompt,
                'bad_prompt': bad_prompt,
                'subject_prompts': subject_prompts,
                'ai_tools': ai_tools,
            })

            extra_context = {}
            try:
                mod_name = f"apps.modules.tab3_content_{module.code.lower()}"
                tab3_mod = importlib.import_module(mod_name)
                extra_context = tab3_mod.get_context()
                context.update(extra_context)
                print(f"✅ TAB3 context loaded for {module.code}: {list(extra_context.keys())}")
            except ImportError:
                pass  # M1 or module with no extra context — no problem
            except Exception as e:
                print(f"⚠️ TAB3 context error for {module.code}: {e}")

            # ============================================================
            # Phase A Tier 3 Step 4 — M9 share defaults + live preview
            # Pre-fill title + summary with sensible scenario-grounded
            # starters (user edits if they want), and pre-render the
            # static auto-generated body so the template can show a
            # live preview block ABOVE the form. Avoids the "blind share"
            # UX where teacher writes from scratch with no idea what's
            # being included alongside their description.
            # ============================================================
            if module.code == 'M9' and activity and activity.challenge3_completed:
                from apps.peer_blog.sharing import _render_m9_lesson_body
                cd = activity.challenge_data or {}
                m9_subject_value = cd.get('challenge3_subject', '') or ''
                m9_subject_label = (
                    m9_subject_value.replace('_', ' ').title() if m9_subject_value else ''
                )

                try:
                    from apps.modules.tab3_content_m9 import LESSON_SCENARIOS as _M9_SCENARIOS
                    m9_scenario = _M9_SCENARIOS.get(m9_subject_value, {}) or {}
                except Exception:
                    m9_scenario = {}

                m9_topic = (m9_scenario.get('topic') or '').strip()

                if m9_topic and m9_subject_label:
                    m9_default_title = f"{m9_topic} ({m9_subject_label})"
                elif m9_topic:
                    m9_default_title = m9_topic
                else:
                    m9_default_title = 'My M9 lesson approach'
                m9_default_title = m9_default_title[:100]

                if m9_subject_label and m9_topic:
                    # Strip year/grade noise (everything after first '—' or '(')
                    import re as _re
                    topic_clean = _re.split(r'\s*[—(]', m9_topic, maxsplit=1)[0].strip()
                    if topic_clean:
                        m9_default_summary = (
                            f"A {m9_subject_label} lesson on {topic_clean.lower()}. "
                            f"Designing AI-supported differentiation for a mixed-ability class — "
                            f"open to peer thoughts on the tradeoffs I'm making."
                        )
                    else:
                        m9_default_summary = (
                            f"A {m9_subject_label} lesson approach — open to peer thoughts on the tradeoffs I'm making."
                        )
                else:
                    m9_default_summary = ''

                # Static body: render with NO user summary so preview can
                # compose live: (live title) + (live summary) + '---' + (static).
                static_cd = dict(cd)
                static_cd.pop('shared_lesson_summary', None)
                m9_static_body = _render_m9_lesson_body(static_cd)

                context.update({
                    'm9_share_default_title': m9_default_title,
                    'm9_share_default_summary': m9_default_summary,
                    'm9_share_static_body': m9_static_body,
                })

            # ============================================================
            # Phase A Tier 3 Step 5 — M14 share defaults + live preview
            # Pattern mirrors M9: pre-fill title + summary with sensible
            # defaults from the user's Challenge 3 (Gamified Unit Planner)
            # data, plus a static-body preview of the auto-generated unit
            # design choices. SAMR Audit (C1) and Five Roles Matcher (C2)
            # do NOT trigger sharing — only the substantive C3 unit plan.
            # ============================================================
            if module.code == 'M14' and activity and activity.challenge3_completed:
                from apps.peer_blog.sharing import _render_m14_unit_body
                cd = activity.challenge_data or {}
                m14_subject_value = cd.get('challenge3_subject', '') or ''
                m14_learning_goal = (cd.get('challenge3_learning_goal') or '').strip()

                # Subject label from c3_subject_options (Title Case-ish)
                m14_subject_label = ''
                for opt in extra_context.get('c3_subject_options', []) or []:
                    if opt.get('value') == m14_subject_value:
                        m14_subject_label = opt.get('label') or ''
                        break
                if not m14_subject_label:
                    m14_subject_label = (
                        m14_subject_value.replace('_', ' ').title() if m14_subject_value else ''
                    )

                # Default title: prefer the user's typed learning goal IF substantive
                # (≥3 distinct lowercase tokens — guards against placeholder noise
                # like "bla bla bla blabla bla bla bla"), else fall back to subject.
                _goal_tokens = {t for t in m14_learning_goal.lower().split() if t}
                if m14_learning_goal and len(_goal_tokens) >= 3:
                    m14_default_title = m14_learning_goal[:100]
                elif m14_subject_label:
                    m14_default_title = f"{m14_subject_label}: Gamified Unit"
                else:
                    m14_default_title = 'My M14 gamified unit'
                m14_default_title = m14_default_title[:100]

                # Default summary: concrete starter, generic across choices to avoid
                # asserting what the teacher chose. Open invitation for peer input.
                if m14_subject_label:
                    m14_default_summary = (
                        f"A {m14_subject_label} gamified unit. Designing engagement "
                        f"mechanics that serve the learning, not decorate it — "
                        f"open to peer thoughts on the design tradeoffs."
                    )
                else:
                    m14_default_summary = (
                        "A gamified unit design — open to peer thoughts on the design tradeoffs."
                    )

                # Static body for preview: render with no user summary
                static_cd = dict(cd)
                static_cd.pop('shared_lesson_summary', None)
                m14_static_body = _render_m14_unit_body(static_cd)

                context.update({
                    'm14_share_default_title': m14_default_title,
                    'm14_share_default_summary': m14_default_summary,
                    'm14_share_static_body': m14_static_body,
                })

            # ============================================================
            # Phase A Tier 3 — M13 Practice Workshop share-modal defaults
            # Pre-populate from existing Challenge 2 canvas so user can
            # one-click share if they accept the synthesised defaults.
            # Synthesis logic:
            #   title  := label of challenge2_learning_goal radio choice
            #             (e.g. 'historical_immersion' → 'Create historical
            #             or cultural immersion'). Empty if not set.
            #   summary := concatenation of challenge2_canvas_step_1..3 with
            #             '. ' separator, truncated to 200 chars (with '…'
            #             ellipsis on truncation). Empty if no steps filled.
            # Both editable in the modal; user can override before sharing.
            # ============================================================
            if module.code == 'M13':
                cd = (activity.challenge_data or {})
                goal_value = cd.get('challenge2_learning_goal') or ''
                goal_label = next(
                    (
                        opt.get('label') or ''
                        for opt in extra_context.get('c2_learning_goal_options', [])
                        if opt.get('value') == goal_value
                    ),
                    '',
                )
                # Render the full canvas as the body that will appear in the
                # M13 Practice Workshop. This is what peers will read; identical
                # content to the PDF download.
                m13_share_canvas_body = _render_m13_canvas_body(cd)

                context.update({
                    'm13_share_default_title': goal_label[:200],
                    'm13_share_canvas_body': m13_share_canvas_body,
                    'm13_share_canvas_ready': bool(m13_share_canvas_body),
                })
        
        # ============================================================
        # TABS 2, 4, 5: STANDARD CONTENT WITH PERSONALIZATION
        # ============================================================
        else:
            content_type_map = {
                'main_content': 'main_content',
                'activity': 'activity',
                'assessment': 'assessment',
                'reflection': 'reflection'
            }
            print(f"DEBUG content_type_map lookup: current_tab={current_tab} content_type={content_type_map.get(current_tab)}")
            
            content_type = content_type_map.get(current_tab)
            
            if content_type:
                # Three-tier personalization query
                # Priority: Subject+Grade > Subject > Grade > Universal
                content = ModuleContent.objects.filter(
                    module=module,
                    content_type=content_type
                ).annotate(
                    # Calculate priority score
                    priority=Case(
                        # Exact match: subject AND grade
                        When(
                            subject_area=teacher_profile.subject_area,
                            grade_level=teacher_profile.grade_level,
                            then=1
                        ),
                        # Subject match only
                        When(
                            subject_area=teacher_profile.subject_area,
                            grade_level='All',
                            then=2
                        ),
                        # Grade match only
                        When(
                            subject_area='Universal',
                            grade_level=teacher_profile.grade_level,
                            then=3
                        ),
                        # Universal (fallback)
                        When(
                            subject_area='Universal',
                            grade_level='All',
                            then=4
                        ),
                        default=5,
                        output_field=IntegerField(),
                    )
                ).order_by('priority').first()
                print(f"DEBUG content query: module={module.code} content_type={content_type} result={content} count={ModuleContent.objects.filter(module=module, content_type=content_type).count()}")
                
                # Get personalized example from metadata
                personalized_example = None
                if content and content.metadata:
                    examples = content.metadata.get('personalization_examples', {})
                    if teacher_profile.subject_area in examples:
                        personalized_example = examples[teacher_profile.subject_area]
                
                # ============================================================
                # SUBJECT-SPECIFIC BOXES
                # Load personalized content boxes based on teacher's subject
                # ============================================================
                subject_box_part2 = None
                subject_box_part3 = None
                subject_box_part4 = None
                subject_box_orchestration = None
                content_html = content.content_data if content else ''
                
                if current_tab == 'main_content':
                    # Box for Part 2: GenAI capabilities for your subject
                    subject_box_part2 = ModuleContent.objects.filter(
                        module=module,
                        content_type='subject_box_part2',
                        subject_area=teacher_profile.subject_area,
                        grade_level='all'
                    ).first()
                    
                    # Box for Part 4: AI Tools for your subject
                    subject_box_part4 = ModuleContent.objects.filter(
                        module=module,
                        content_type='subject_box_part4',
                        subject_area=teacher_profile.subject_area,
                        grade_level='all'
                    ).first()
                    
                    # Box for Part 3: Subject-specific case study
                    subject_box_part3 = ModuleContent.objects.filter(
                        module=module,
                        content_type='subject_box_part3',
                        subject_area=teacher_profile.subject_area,
                        grade_level='all'
                    ).first()

                    # Box for Part 5: Subject-specific orchestration move (M5)
                    subject_box_orchestration = ModuleContent.objects.filter(
                        module=module,
                        content_type='subject_box_orchestration',
                        subject_area=teacher_profile.subject_area,
                        grade_level='all'
                    ).first()

                    # Box for Part 4: AI Tools for your subject
                    subject_box_part4 = ModuleContent.objects.filter(
                        module=module,
                        content_type='subject_box_part4',
                        subject_area=teacher_profile.subject_area,
                        grade_level='all'
                    ).first()

                    # ============================================================
                    # INSERT BOXES AT PLACEHOLDERS
                    # Replace <!-- SUBJECT_BOX_PARTX --> with actual content
                    # ============================================================
                    if subject_box_part2 and '<!-- SUBJECT_BOX_PART2 -->' in content_html:
                        content_html = content_html.replace(
                            '<!-- SUBJECT_BOX_PART2 -->', 
                            subject_box_part2.content_data
                        )
                    if subject_box_part3 and '<!-- SUBJECT_BOX_PART3 -->' in content_html:
                        content_html = content_html.replace(
                            '<!-- SUBJECT_BOX_PART3 -->', 
                            subject_box_part3.content_data
                        )
                    if subject_box_part4 and '<!-- SUBJECT_BOX_PART4 -->' in content_html:
                        content_html = content_html.replace(
                            '<!-- SUBJECT_BOX_PART4 -->',
                            subject_box_part4.content_data
                        )
                    if subject_box_orchestration and '<!-- SUBJECT_BOX_ORCHESTRATION -->' in content_html:
                        content_html = content_html.replace(
                            '<!-- SUBJECT_BOX_ORCHESTRATION -->',
                            subject_box_orchestration.content_data
                        )
                    # Reflection Part 2 subject-specific question (M2+)
                elif current_tab == 'reflection':
                    reflection_part2 = ModuleContent.objects.filter(
                        module=module,
                        content_type='reflection',
                        subject_area=teacher_profile.subject_area,
                        grade_level='All'
                    ).first() or ModuleContent.objects.filter(
                        module=module,
                        content_type='reflection',
                        subject_area='Universal',
                        grade_level='All'
                    ).first()
                
                    reflection_universal = ModuleContent.objects.filter(
                        module=module,
                        content_type='reflection',
                        subject_area='Universal',
                        grade_level='All'
                    ).first()
 
                    context['reflection_part2'] = reflection_part2
                    context['reflection_meta'] = reflection_universal.metadata if reflection_universal else {}
            
                    
                context.update({
                    'content': content,
                    'content_html': content_html,
                    'personalized_example': personalized_example,
                    'content_metadata': content.metadata if content else {},
                    'assessment_questions_json': content.content_data if content and current_tab == 'assessment' else '[]',
                })
                print(f"DEBUG TAB={current_tab} content={content} assessment_json_len={len(content.content_data) if content else 0}")
       # ============================================================
        # COMMON CONTEXT FOR ALL TABS
        # ============================================================
        # Load saved RTM tensions for completed state display
        from .models import ReflectionTension
        saved_tensions = ReflectionTension.objects.filter(
            user=user,
            module=module
        ).order_by('created_at')

        # Load saved AI disputes for completed state display
        from .models import AIOutputDispute

        try:
            dispute_rag = AIOutputDispute.objects.get(
                user=user, module=module, feature_type='rag')
        except AIOutputDispute.DoesNotExist:
            dispute_rag = None

        try:
            dispute_rtm = AIOutputDispute.objects.get(
                user=user, module=module, feature_type='rtm')
        except AIOutputDispute.DoesNotExist:
            dispute_rtm = None

        try:
            dispute_dtp = AIOutputDispute.objects.get(
                user=user, module=module, feature_type='dtp')
        except AIOutputDispute.DoesNotExist:
            dispute_dtp = None

                
        # 🆕 DTP: Check if user has a previous reflection (for M2+ button)
        previous_reflection_exists = False
        try:
            import psycopg2
            from django.conf import settings
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM rag_queries
                    WHERE user_id = %s AND module_id < %s
                )
            """, (user.id, module.id))
            previous_reflection_exists = cursor.fetchone()[0]
            print(f"🔍 DTP CHECK: user={user.id}, module={module.id}({module.code}), previous_exists={previous_reflection_exists}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"⚠️ DTP context check failed: {e}")

        # print(f"🔍 DTP CHECK: user={user.id}, module={module.id}, previous_exists={previous_reflection_exists}")
        # Load saved DTP result if exists
        reflection_dtp = None
        if progress and progress.reflection_dtp:
            try:
                import json
                reflection_dtp = json.loads(progress.reflection_dtp)
                print(f"✅ DTP loaded from DB: {list(reflection_dtp.keys())}")
            except Exception as e:
                print(f"❌ DTP load error: {e}")
        else:
            print(f"⚠️ DTP not in DB: progress={progress}, reflection_dtp={bool(progress.reflection_dtp) if progress else None}")

        context.update({
            'current_tab': current_tab,
            'progress': progress,
            'unlock_status': progress.unlock_status,
            'next_module': module.get_next_module(),
            'prev_module': module.get_previous_module(),
            'teacher_profile': teacher_profile,
            'saved_tensions': saved_tensions,
            'previous_reflection_exists': previous_reflection_exists,
            'reflection_dtp': reflection_dtp,
            'dispute_rag': dispute_rag,
            'dispute_rtm': dispute_rtm,
            'dispute_dtp': dispute_dtp,
        })
        
        return context

@login_required
@require_POST
def mark_tab_complete(request, code, tab_name):
    """
    Mark a specific tab as completed via AJAX
    
    Validates submission data based on tab type:
    - activity: min 100 characters
    - assessment: score >= 80%
    - reflection: 350-800 words + RAG feedback generation
    """
    module = get_object_or_404(Module, code=code)

    # Phase C TD-012 — sequential prerequisite gate (defensive AJAX
    # check). The GET-side guard in ModuleDetailView.get already
    # redirects unprivileged users away from out-of-order module
    # pages, but the AJAX endpoint is callable directly via curl /
    # browser console / parallel-tab race. Staff and superusers bypass
    # for support.
    if not (request.user.is_staff or request.user.is_superuser):
        from apps.modules.services import get_module_prerequisite_block
        blocker = get_module_prerequisite_block(request.user, module)
        if blocker is not None:
            return JsonResponse({
                'success': False,
                'message': 'Please complete %s before completing tabs in %s.' % (
                    blocker.code, module.code,
                ),
            }, status=409)

    try:
        progress = UserModuleProgress.objects.get(user=request.user, module=module)
    except UserModuleProgress.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'No progress record. Please refresh the page!'
        }, status=404)
    
    # Parse request data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = {}
    
    # Variable to hold RAG result outside try block
    rag_result = None
    
    # Validate based on tab type
    try:
        if tab_name == 'assessment':
            # Get score from database - more reliable than frontend data
            assessment = Assessment.objects.filter(
                module=module,
                teacher=request.user
            ).first()
    
            if not assessment or not assessment.passed:
                score = assessment.metadata.get('percentage', 0) if assessment else 0
                return JsonResponse({
                    'success': False,
                    'message': f'You need at least 80% to pass (your score: {score}%).'
                })
            
            score = assessment.metadata.get('percentage', 100)
            kwargs = {'score': score}
        
        elif tab_name == 'activity':
            submission = data.get('submission', '')
            if len(submission) < 100:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter at least 100 characters.'
                })
            kwargs = {'submission': submission}
        
        elif tab_name == 'reflection':
            reflection_text = data.get('reflection_text', '')
            word_count = len(reflection_text.split())
            if not (300 <= word_count <= 800):
                return JsonResponse({
                    'success': False,
                    'message': f'The reflection must be between 300-800 words (current count: {word_count}).'
                })
            
            # ============================================================
            # 🔥 RAG FEEDBACK GENERATION + PEER SYNTHESIS
            # ============================================================
            try:
                # Get teacher profile
                teacher_profile = TeacherProfile.objects.get(user=request.user)
                
                # Build teacher context
                teacher_context = {
                    'name': teacher_profile.first_name or request.user.first_name,
                    'full_name': teacher_profile.full_name,
                    'subject': teacher_profile.get_subject_area_display(),
                    'grade_level': teacher_profile.get_grade_level_display(),
                    'experience': teacher_profile.get_teaching_years_display(),
                    'enable_peer_synthesis': True  # ← NEW: Enable peer synthesis
                }
                
                # Process reflection through RAG system
                print(f"\n🔮 Processing reflection for user {request.user.id}...")
                rag_result = process_reflection(
                    reflection_text=reflection_text,
                    teacher_context=teacher_context,
                    user_id=request.user.id,
                    module_id=module.id
                )
                
                # Check for errors and convert markdown to HTML
                if 'error' in rag_result:
                    print(f"❌ RAG error: {rag_result['error']}")
                    feedback = None
                else:
                    # Convert main feedback markdown to HTML
                    raw_feedback = rag_result.get('feedback', '')
                    if raw_feedback:
                        feedback = markdown.markdown(
                            raw_feedback,
                            extensions=['extra', 'nl2br']
                        )
                        print(f"✅ RAG feedback generated + converted to HTML ({len(feedback)} chars)")
                    else:
                        feedback = None
                
            except Exception as e:
                print(f"❌ RAG system error: {e}")
                import traceback
                traceback.print_exc()
                feedback = None
                rag_result = None  # Ensure it's None on error
            
            kwargs = {
                'reflection_text': reflection_text,
                'rag_feedback': feedback
            }
            # ← NEW: Store reflection in peer_reflections for future users
            try:
                from rag_query_system import embed_query
                import psycopg2
                from django.conf import settings
                
                # Get embedding
                reflection_embedding = embed_query(reflection_text)
                
                if reflection_embedding:
                    # Store in peer_reflections
                    conn = psycopg2.connect(
                        dbname=settings.DATABASES['default']['NAME'],
                        user=settings.DATABASES['default']['USER'],
                        password=settings.DATABASES['default']['PASSWORD'],
                        host=settings.DATABASES['default']['HOST'],
                        port=settings.DATABASES['default']['PORT']
                    )
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO peer_reflections 
                        (subject_area, grade_level, experience_years, reflection_text, 
                         reflection_embedding, is_seed_data, module_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, FALSE, %s, NOW())
                    """, (
                        teacher_profile.subject_area,
                        teacher_profile.grade_level,
                        teacher_profile.teaching_years,
                        reflection_text,
                        reflection_embedding,
                        module.id
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print(f"✅ Reflection stored in peer_reflections")
            except Exception as e:
                print(f"⚠️ Could not store peer reflection: {e}")

        else:
            kwargs = {}
        
        # Mark tab complete.
        # Phase C C.3 commit 2a — CP-9 invariant: wrap save + provenance
        # write in one transaction.atomic. mark_tab_complete calls
        # progress.save() internally, so any state set on the instance
        # (including reflection_rag_feedback from kwargs) is persisted in
        # the same transaction as the provenance row. If the provenance
        # write raises, both rollback.
        with transaction.atomic():
            next_tab = progress.mark_tab_complete(tab_name, **kwargs)
            if tab_name == 'reflection' and kwargs.get('rag_feedback'):
                record_ai_provenance(
                    artefact_kind='rag_feedback',
                    artefact_pk=progress.pk,
                    user=progress.user,
                    module=progress.module,
                    model_name=PROVENANCE_MODEL_NAME,
                    generated_at=timezone.now(),
                )

        # Phase C C.2.4 + C.2.5 — post-module feature redirects.
        # After a module's progress.completed_at is freshly set we ask
        # two helpers in turn which feature (if any) should take over
        # the next page:
        #   1. AILST T1 after M5 (C.2.4, consent-gated).
        #   2. PROODOS Epilogue after M15 (C.2.5, no consent gate);
        #      the Epilogue then routes to /ailst/t2/ for consenting
        #      users who have not yet done T2.
        # Both helpers return None when no redirect applies, in which
        # case we fall through to the normal next-tab flow.
        from apps.ailst.services import get_post_module_redirect_url
        from apps.epilogue.services import get_post_module_epilogue_redirect_url

        ailst_redirect_url = None
        epilogue_redirect_url = None
        if progress.completed_at is not None:
            ailst_redirect_url = get_post_module_redirect_url(
                request.user, module.code,
            )
            epilogue_redirect_url = get_post_module_epilogue_redirect_url(
                request.user, module.code,
            )

        # Build response
        response_data = {
            'success': True,
            'next_tab': next_tab,
            'module_completed': progress.completed_at is not None,
            'completion_percentage': progress.completion_percentage,
        }
        # Re-use the existing ailst_redirect_url JSON key for both
        # destinations so the existing frontend handlers in
        # module_detail.html and tab5_reflection.html keep working
        # without modification — they navigate to whatever URL the
        # server returns. (Key name is now a slight misnomer but
        # changing it would force a frontend churn for zero gain.)
        if ailst_redirect_url:
            response_data['ailst_redirect_url'] = ailst_redirect_url
            response_data['ailst_redirect_label'] = 'Continue to AI Literacy assessment'
        elif epilogue_redirect_url:
            response_data['ailst_redirect_url'] = epilogue_redirect_url
            response_data['ailst_redirect_label'] = 'Continue to PROODOS Epilogue'
        
        # Add feedback and peer synthesis to response if this is reflection
        # Add feedback, peer synthesis, and RTM tensions to response
        if tab_name == 'reflection':
            if feedback:
                response_data['feedback'] = feedback
            
            # Add peer synthesis if available
            # Add peer synthesis if available
            if rag_result and 'peer_synthesis' in rag_result and rag_result['peer_synthesis']:
                try:
                    peer_synthesis_html = markdown.markdown(
                        rag_result['peer_synthesis'],
                        extensions=['extra', 'nl2br']
                    )
                    response_data['peer_synthesis'] = peer_synthesis_html
                    print(f"✅ Peer synthesis added to response ({len(peer_synthesis_html)} chars)")

                    # 🆕 Save peer synthesis to database. CP-9 invariant
                    # (Phase C C.3 commit 2a): save + provenance in one
                    # atomic block.
                    with transaction.atomic():
                        progress.reflection_peer_synthesis = peer_synthesis_html
                        progress.save(update_fields=['reflection_peer_synthesis'])
                        record_ai_provenance(
                            artefact_kind='peer_synthesis',
                            artefact_pk=progress.pk,
                            user=progress.user,
                            module=progress.module,
                            model_name=PROVENANCE_MODEL_NAME,
                            generated_at=timezone.now(),
                        )
                    print(f"✅ Peer synthesis saved to database")
                except Exception as e:
                    print(f"⚠️ Error converting peer synthesis to HTML: {e}")
                   
        return JsonResponse(response_data)
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        print(f"❌ Error in mark_tab_complete: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': 'Παρουσιάστηκε σφάλμα. Παρακαλώ δοκιμάστε ξανά.'
        })


@login_required
def module_home(request):
    modules = Module.objects.filter(is_published=True)
    
    total_modules = modules.count()
    completed_modules = UserModuleProgress.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).count()
    
    overall_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    # Build modules with progress in one list
    modules_with_progress = []
    for module in modules:
        try:
            progress = UserModuleProgress.objects.get(user=request.user, module=module)
            prog_data = {
                'started': True,
                'percentage': progress.completion_percentage,
                'completed': progress.completed_at is not None,
            }
        except UserModuleProgress.DoesNotExist:
            prog_data = {'started': False, 'percentage': 0, 'completed': False}
        
        modules_with_progress.append({'module': module, 'progress': prog_data})
    
    context = {
        'modules': modules,
        'modules_with_progress': modules_with_progress,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'overall_percentage': round(overall_percentage, 1),
    }
    
    return render(request, 'home.html', context)
# ============================================================================
# TAB 3: AI TOOL EXPLORATION ACTIVITY
# ============================================================================

@login_required
def tab3_activity(request, module_code):
    """
    Main view for Tab 3 Activity
    """
    # print("=" * 50)
    # print("DEBUG: tab3_activity called")
    # print("=" * 50)
    
    # Get or create user activity record
    try:
        module = get_object_or_404(Module, code=module_code)
        activity, created = Tab3UserActivity.objects.get_or_create(
        user=request.user,
        module_id=module.id
        )
        # print(f"DEBUG: Activity record: {activity}, Created: {created}")
    except Exception as e:
        # print(f"DEBUG ERROR: Tab3UserActivity error: {e}")
        activity = None
    
    # Get user's subject from onboarding
    # Tier 3 incidental fix: was 'teacherprofile' (no underscore) + '.subject'
    # — both wrong, AttributeError fell through to fallback for all users.
    try:
        user_profile = request.user.teacher_profile
        subject = user_profile.subject_area or "Mathematics"
        grade_level = user_profile.grade_level or "Grade 10"
    except Exception as e:
        print(f"DEBUG ERROR: Profile error: {e}")
        subject = "Mathematics"
        grade_level = "Grade 10"
    
    # Get prompts from library
    try:
        all_prompts = Tab3PromptLibrary.objects.all()
        # print(f"DEBUG: Total prompts in DB = {all_prompts.count()}")
        
        good_prompt = Tab3PromptLibrary.objects.filter(
            subject__iexact=subject,
            prompt_type='good'
        ).first()
        # print(f"DEBUG: Good prompt = {good_prompt}")
        
        bad_prompt = Tab3PromptLibrary.objects.filter(
            subject__iexact=subject,
            prompt_type='bad'
        ).first()
        # print(f"DEBUG: Bad prompt = {bad_prompt}")
        
    except Exception as e:
        # print(f"DEBUG ERROR: Prompt query error: {e}")
        good_prompt = None
        bad_prompt = None
    
    # Get subject-specific prompts for Challenge 3
    try:
        subject_prompts = Tab3PromptLibrary.objects.filter(
            subject__iexact=subject,
            prompt_type__in=['lesson_plan', 'quiz', 'differentiation']
        )
        # print(f"DEBUG: Subject prompts count = {subject_prompts.count()}")
    except Exception as e:
        # print(f"DEBUG ERROR: Subject prompts error: {e}")
        subject_prompts = []
    
    # Available AI tools
    ai_tools = [
        {'value': 'ChatGPT', 'label': 'ChatGPT', 'url': 'https://chat.openai.com', 'description': 'Most versatile, great for creative tasks'},
        {'value': 'Claude', 'label': 'Claude', 'url': 'https://claude.ai', 'description': 'Excellent for long documents and analysis'},
        {'value': 'Gemini', 'label': 'Gemini', 'url': 'https://gemini.google.com', 'description': 'Google integration, strong research'},
        {'value': 'Copilot', 'label': 'Microsoft Copilot', 'url': 'https://copilot.microsoft.com', 'description': 'Best for Microsoft 365 users'},
        {'value': 'Perplexity', 'label': 'Perplexity', 'url': 'https://perplexity.ai', 'description': 'Research-focused with citations'},
        {'value': 'DeepSeek', 'label': 'DeepSeek', 'url': 'https://chat.deepseek.com', 'description': 'Advanced reasoning capabilities'},
        {'value': 'Other', 'label': 'Other (specify)', 'url': '', 'description': 'Use a different AI tool'},
    ]
    
    context = {
        'module_code': module_code,
        'activity': activity,
        'subject': subject,
        'grade_level': grade_level,
        'good_prompt': good_prompt,
        'bad_prompt': bad_prompt,
        'subject_prompts': subject_prompts,
        'ai_tools': ai_tools,
    }
    # M2-specific context
    if module_code == 'M2':
        from .tab3_content import M2_SCENARIO, M2_PRINCIPLES, M2_AUDIT_TOOLS, M2_AUDIT_QUESTIONS
        context.update({
            'scenario': M2_SCENARIO,
            'principles': M2_PRINCIPLES,
            'audit_tools': M2_AUDIT_TOOLS,
            'audit_questions': M2_AUDIT_QUESTIONS,
        })
    template = f'modules/tab3_activity_{module_code.lower()}.html'
    print(f"DEBUG TAB3 TEMPLATE: trying {template}")
    try:
        return render(request, template, context)
    except Exception as e:
        print(f"DEBUG TAB3 TEMPLATE FALLBACK: {e}")
        return render(request, 'modules/tab3_activity.html', context)


@login_required
@require_http_methods(["POST"])
def submit_challenge1(request, module_code):
    """
    Generic Challenge 1 submit — works for all modules.
    Saves all challenge data into challenge_data JSONB field.
    """
    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)

        activity, _ = Tab3UserActivity.objects.get_or_create(
            user=request.user,
            module_id=module.id
        )

        activity.challenge1_completed = True
        activity.challenge1_completed_at = timezone.now()

        # Merge incoming data into challenge_data JSONB
        existing = activity.challenge_data or {}
        existing.update({f'challenge1_{k}': v for k, v in data.items()})
        activity.challenge_data = existing
        activity.save()

        return JsonResponse({
            'success': True,
            'message': 'Challenge 1 completed!',
            'next_challenge': 'challenge2'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_challenge2(request, module_code):
    """Generic Challenge 2 submit."""
    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)

        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )

        activity.challenge2_completed = True
        activity.challenge2_completed_at = timezone.now()

        existing = activity.challenge_data or {}
        existing.update({f'challenge2_{k}': v for k, v in data.items()})
        activity.challenge_data = existing
        activity.save()

        return JsonResponse({
            'success': True,
            'message': 'Challenge 2 completed!',
            'next_challenge': 'challenge3'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_challenge3(request, module_code):
    """Generic Challenge 3 submit. M1 toolkit save preserved via module_code check."""
    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)

        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )

        activity.challenge3_completed = True
        activity.challenge3_completed_at = timezone.now()

        existing = activity.challenge_data or {}
        existing.update({f'challenge3_{k}': v for k, v in data.items()})
        activity.challenge_data = existing
        activity.save()

        # M1 toolkit save — preserved for backwards compatibility
        if module_code == 'M1' and data.get('save_to_toolkit'):
            try:
                teacher_profile = TeacherProfile.objects.get(user=request.user)
                subject = teacher_profile.subject_area
                grade_level = teacher_profile.grade_level
            except TeacherProfile.DoesNotExist:
                subject = ''
                grade_level = ''

            Tab3UserToolkit.objects.create(
                user=request.user,
                prompt_text=data.get('prompt_text'),
                ai_result=data.get('result_text'),
                tool_used=data.get('tool'),
                subject=subject,
                grade_level=grade_level,
                prompt_type=data.get('prompt_choice'),
                rating=data.get('rating'),
                notes=data.get('notes', '')
            )

        return JsonResponse({
            'success': True,
            'message': 'Challenge 3 completed!',
            'next_challenge': 'reflection'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================
# Phase A Tier 2 Step 4 (M13 patch) + Tier 3 redesign
# Handlers for the M13 Practice Workshop share flow:
#   - submit_to_repository: persists a Tab3RepositorySubmission row
#                           AND auto-creates a BlogPost whose body is
#                           the rendered canvas (Tier 3 redesign)
#   - export_canvas_pdf: generates a canvas PDF via xhtml2pdf, can read
#                        from either the live Tab3UserActivity (author flow)
#                        or a Tab3RepositorySubmission snapshot (peer flow)
# ============================================================


def _strip_label_extras(label: str) -> str:
    """Trim option-label decorations after '—' or '(' for compact display."""
    import re
    if not label:
        return ''
    return re.split(r'\s*[—(]', label, maxsplit=1)[0].strip()


def _m13_label_lookup(options_list, value, fallback=''):
    """Map an option value to its trimmed label; fall back to title-cased value."""
    for opt in options_list or []:
        if opt.get('value') == value:
            return _strip_label_extras(opt.get('label') or value or '') or (value or '')
    if value is None:
        return fallback
    return (value or '').replace('_', ' ').strip().title() or fallback


def _render_m13_canvas_body(canvas_data: dict) -> str:
    """
    Render a M13 Challenge 2 canvas as a plain-text body for BlogPost.body.

    Reads the same fields as the PDF export, formatted with blank-line
    section separators so Django's |linebreaks filter renders cleanly.
    Returns an empty string if no canvas content is available.

    Tier 3 redesign — peer dialogue post body == rendered canvas (not summary).
    """
    cd = canvas_data or {}

    try:
        from .tab3_content_m13 import get_context as _m13_get_ctx
        m13_ctx = _m13_get_ctx()
    except Exception:
        m13_ctx = {}

    lines = []

    goal = _m13_label_lookup(
        m13_ctx.get('c2_learning_goal_options', []),
        cd.get('challenge2_learning_goal'),
    )
    if goal:
        lines.append(f'Learning goal: {goal}')
        lines.append('')

    modalities = cd.get('challenge2_modalities') or []
    if not isinstance(modalities, list):
        modalities = [modalities]
    modality_str = ', '.join(
        _m13_label_lookup(m13_ctx.get('c2_modality_options', []), m)
        for m in modalities if m
    )

    tools = cd.get('challenge2_tool_categories') or []
    if not isinstance(tools, list):
        tools = [tools]
    tool_str = ', '.join(
        _m13_label_lookup(m13_ctx.get('c2_tool_category_options', []), t)
        for t in tools if t
    )

    prep_time = (cd.get('challenge2_prep_time') or '').strip()

    if modality_str:
        lines.append(f'Modalities: {modality_str}')
    if tool_str:
        lines.append(f'Tool categories: {tool_str}')
    if prep_time:
        lines.append(f'Estimated prep time: {prep_time}')
    if modality_str or tool_str or prep_time:
        lines.append('')

    steps = []
    for i in range(1, 8):  # support up to 7 steps for forward-compat
        s = (cd.get(f'challenge2_canvas_step_{i}') or '').strip()
        if s:
            steps.append(s)
    if steps:
        lines.append('Workflow steps:')
        for i, s in enumerate(steps, start=1):
            lines.append(f'{i}. {s}')

    return '\n'.join(lines).strip()


def _build_m13_pdf_context(canvas_data: dict, module_code: str, author_user) -> dict:
    """
    Build the context dict consumed by templates/pdf/m13_canvas_export.html.
    Used by both the live-export flow (author) and the peer-download flow
    (any logged-in user on a shared post).
    """
    cd = canvas_data or {}

    try:
        profile = author_user.teacher_profile
        author_name = author_user.get_full_name() or author_user.username
        subject_area = cd.get('challenge2_subject_area') or profile.subject_area or '—'
        grade_level = cd.get('challenge2_grade_level') or profile.grade_level or '—'
    except Exception:
        author_name = author_user.username if author_user else '—'
        subject_area = cd.get('challenge2_subject_area') or '—'
        grade_level = cd.get('challenge2_grade_level') or '—'

    steps_raw = []
    for i in range(1, 8):
        text = cd.get(f'challenge2_canvas_step_{i}')
        if text:
            steps_raw.append({'title': f'Step {i}', 'description': text})

    modalities = cd.get('challenge2_modalities') or []
    if isinstance(modalities, list):
        modality_str = ', '.join(modalities)
    else:
        modality_str = str(modalities)

    tool_cats = cd.get('challenge2_tool_categories') or []
    if isinstance(tool_cats, list):
        tool_cats_str = ', '.join(tool_cats)
    else:
        tool_cats_str = str(tool_cats)

    return {
        'title': cd.get('challenge2_workflow_title', 'My Hybrid Workflow'),
        'summary': cd.get('challenge2_workflow_summary', ''),
        'module_code': module_code,
        'author': author_name,
        'subject_area': subject_area,
        'grade_level': grade_level,
        'learning_goal': cd.get('challenge2_learning_goal', ''),
        'modality': modality_str,
        'prep_time': cd.get('challenge2_prep_time', ''),
        'tool_categories': tool_cats_str,
        'steps': steps_raw,
        'exported_at': timezone.now().strftime('%Y-%m-%d %H:%M UTC'),
    }


@login_required
@require_http_methods(["POST"])
def share_to_workshop(request, module_code):
    """
    Generic opt-in share endpoint for module wiring (M9 — Step 4; M14 — Step 5).

    Body: JSON {title, summary}. Server reads existing Tab3UserActivity
    snapshot, validates module-specific completion gate, persists the
    title+summary into challenge_data, renders the artefact body via
    the module's registered renderer, and creates a BlogPost. Returns
    {success, post_id, redirect_url} on success.

    Distinct from M13's submit_to_repository because M9/M14 don't carry
    a Tab3RepositorySubmission row — they live in Tab3UserActivity.
    """
    from django.urls import reverse
    from apps.peer_blog.sharing import (
        MODULE_SHARE_CONFIG,
        share_artefact_to_workshop,
    )

    if module_code not in MODULE_SHARE_CONFIG:
        return JsonResponse(
            {'success': False, 'message': 'Practice Workshop sharing not enabled for this module.'},
            status=400,
        )

    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)
        config = MODULE_SHARE_CONFIG[module_code]

        title = (data.get('title') or '').strip()
        summary = (data.get('summary') or '').strip()

        if not title:
            return JsonResponse({'success': False, 'message': 'Title required.'}, status=400)
        if len(title) > 100:
            return JsonResponse({'success': False, 'message': 'Title must be ≤ 100 characters.'}, status=400)
        if not summary:
            return JsonResponse({'success': False, 'message': 'Summary required.'}, status=400)
        if len(summary) > 500:
            return JsonResponse({'success': False, 'message': 'Summary must be ≤ 500 characters.'}, status=400)

        try:
            activity = Tab3UserActivity.objects.get(user=request.user, module_id=module.id)
        except Tab3UserActivity.DoesNotExist:
            return JsonResponse(
                {'success': False, 'message': 'No activity recorded yet.'},
                status=400,
            )

        gate_attr = config.get('gate_attr')
        if gate_attr and not getattr(activity, gate_attr, False):
            return JsonResponse(
                {'success': False, 'message': config.get('gate_message') or 'Completion gate not met.'},
                status=400,
            )

        post = share_artefact_to_workshop(
            module_code=module_code,
            user=request.user,
            activity=activity,
            title=title,
            summary=summary,
        )

        return JsonResponse({
            'success': True,
            'message': '✅ Shared to the Practice Workshop.',
            'post_id': post.id,
            'redirect_url': reverse('peer_blog:post_detail', kwargs={'post_id': post.id}),
        })

    except ValueError as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_to_repository(request, module_code):
    """
    Phase A Tier 3 (D5+D6+D8) redesign: M13 Challenge 2 submissions go straight
    to the Practice Workshop (apps.peer_blog) — no admin curation gate. The
    BlogPost.body is a rendered representation of the workflow canvas (the
    same artefact that downloads as PDF), not a hand-written summary.

    Body: JSON with keys: title (optional override; falls back to learning-goal
    label), subject_area, grade_level, contact_email (optional). The canvas
    snapshot is read server-side from Tab3UserActivity.challenge_data.

    Returns: {success, submission_id, post_id, redirect_url}.
    """
    from django.urls import reverse
    from django.db import transaction
    from apps.peer_blog.services import create_blog_post

    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)

        title_override = (data.get('title') or '').strip()
        subject_area = (data.get('subject_area') or '').strip()
        grade_level = (data.get('grade_level') or '').strip()
        contact_email = (data.get('contact_email') or '').strip()

        # Snapshot canvas_data from Tab3UserActivity.challenge_data (the
        # immutable record of what the author shared; PDF will render from
        # this same blob for any peer who downloads).
        try:
            activity = Tab3UserActivity.objects.get(user=request.user, module_id=module.id)
            full_cd = activity.challenge_data or {}
            canvas_data = {k: v for k, v in full_cd.items() if k.startswith('challenge2_')}
        except Tab3UserActivity.DoesNotExist:
            canvas_data = {}

        # Render BlogPost body from the canvas (same content as the PDF)
        rendered_body = _render_m13_canvas_body(canvas_data)
        if not rendered_body:
            return JsonResponse({
                'success': False,
                'message': 'Your workflow canvas is empty. Complete Challenge 2 before sharing.',
            }, status=400)

        # Title: user override → else fall back to learning-goal label
        try:
            from .tab3_content_m13 import get_context as _m13_get_ctx
            m13_ctx = _m13_get_ctx()
        except Exception:
            m13_ctx = {}
        goal_label = _m13_label_lookup(
            m13_ctx.get('c2_learning_goal_options', []),
            canvas_data.get('challenge2_learning_goal'),
        )
        title = title_override or goal_label or 'M13 Hybrid Workflow'
        if len(title) > 200:
            title = title[:200]

        # Tab3RepositorySubmission.summary (legacy CharField, NOT NULL): a short
        # subtitle for admin observation — first line of the rendered body.
        first_line = rendered_body.splitlines()[0] if rendered_body else ''
        legacy_summary = (first_line[:200]).strip() or title

        with transaction.atomic():
            sub = Tab3RepositorySubmission.objects.create(
                user=request.user,
                module=module,
                challenge_id=2,
                title=title,
                summary=legacy_summary,
                subject_area=subject_area,
                grade_level=grade_level,
                contact_email=contact_email,
                canvas_data=canvas_data,
                review_status='community_shared',
            )

            post = create_blog_post(
                artefact_type='m13_workflow',
                artefact_id=sub.id,
                title=title,
                body=rendered_body,
                author_user=request.user,
            )

        return JsonResponse({
            'success': True,
            'message': '✅ Shared to the M13 Practice Workshop.',
            'submission_id': sub.id,
            'post_id': post.id,
            'redirect_url': reverse('peer_blog:post_detail', kwargs={'post_id': post.id}),
            'review_status': sub.review_status,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def export_canvas_pdf(request, module_code):
    """
    Render a M13 Challenge 2 canvas as a PDF (xhtml2pdf backend).

    Two flows (Tier 3):
      • Author flow (no query params): reads the live canvas from the
        requesting user's Tab3UserActivity.challenge_data.
      • Peer flow (?submission_id=N): reads from the immutable
        Tab3RepositorySubmission.canvas_data snapshot. Available to any
        logged-in user (community sharing intent — see post_detail page).

    Returns: application/pdf attachment.
    """
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    import io

    try:
        from xhtml2pdf import pisa
    except ImportError:
        return JsonResponse({
            'success': False,
            'message': 'PDF backend (xhtml2pdf) not available on this server.',
        }, status=500)

    module = get_object_or_404(Module, code=module_code)

    submission_id = request.GET.get('submission_id')
    if submission_id:
        # Peer-flow: render from the Tab3RepositorySubmission snapshot.
        try:
            submission = Tab3RepositorySubmission.objects.select_related('user', 'module').get(
                pk=submission_id,
                module=module,
            )
        except (Tab3RepositorySubmission.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'message': 'Workflow not found.'}, status=404)
        cd = submission.canvas_data or {}
        author_user = submission.user
        filename_user = (author_user.username if author_user else 'anonymous')
    else:
        # Author-flow: render from live Tab3UserActivity.
        try:
            activity = Tab3UserActivity.objects.get(user=request.user, module_id=module.id)
        except Tab3UserActivity.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No activity recorded yet.'}, status=404)
        cd = activity.challenge_data or {}
        author_user = request.user
        filename_user = request.user.username

    ctx = _build_m13_pdf_context(cd, module.code, author_user)

    html = render_to_string('pdf/m13_canvas_export.html', ctx)
    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
    if result.err:
        return JsonResponse({
            'success': False,
            'message': f'PDF generation error: {result.err}',
        }, status=500)

    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{module.code}_canvas_{filename_user}.pdf"'
    return response


@login_required
@require_http_methods(["POST"])
def submit_reflection(request, module_code):
    """Generic reflection submit — marks activity complete."""
    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)

        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )

        activity.reflection_completed = True
        activity.reflection_completed_at = timezone.now()
        activity.activity_completed = True
        activity.activity_completed_at = timezone.now()

        existing = activity.challenge_data or {}
        existing.update({f'reflection_{k}': v for k, v in data.items()})
        activity.challenge_data = existing
        activity.save()

        # Update UserModuleProgress
        progress, _ = UserModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )
        progress.activity_completed = True
        progress.activity_completed_at = timezone.now()
        progress.save()

        return JsonResponse({
            'success': True,
            'message': 'Activity completed successfully!',
            'redirect': f'/modules/modules/{module_code}/?tab=assessment'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================

@login_required
def get_custom_prompt(request):
    """
    Generate customized prompt with user's topic and grade
    """
    prompt_type = request.GET.get('type')  # 'lesson_plan', 'quiz', 'differentiation'
    topic = request.GET.get('topic')
    grade = request.GET.get('grade')
    # Tier 3 incidental fix: was 'teacherprofile.subject' (both wrong attribute names).
    # Use __iexact to handle case mismatch between profile.subject_area
    # (lowercase) and Tab3PromptLibrary.SUBJECTS (Title Case).
    try:
        subject = request.user.teacher_profile.subject_area or ''
    except Exception:
        subject = ''

    # Get template
    template = Tab3PromptLibrary.objects.filter(
        subject__iexact=subject,
        prompt_type=prompt_type
    ).first()
    
    if template:
        # Replace placeholders
        customized = template.prompt_template.replace('{{topic}}', topic)
        customized = customized.replace('{{grade}}', grade)
        
        return JsonResponse({
            'success': True,
            'prompt': customized,
            'type': prompt_type
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Template not found'
    }, status=404)


@login_required
def view_toolkit(request):
    """
    View saved prompts and results
    """
    toolkit_items = Tab3UserToolkit.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'modules/toolkit.html', {
        'toolkit_items': toolkit_items
    })

@login_required
@require_http_methods(["POST"])
def submit_assessment(request, code):
    """Handle quiz submission"""
    # print("=" * 50)  # ADD
    # print("🔵 submit_assessment CALLED")  # ADD
    # print(f"🔵 code: {code}")  # ADD
    # print(f"🔵 user: {request.user}")  # ADD
    # print("=" * 50)  # ADD
    
    try:
        # Get module
        # print("🔵 Step 1: Getting module...")  # ADD
        module = Module.objects.get(code=code)
        # print(f"✅ Module found: {module}")  # ADD
        
        # Parse request data
        # print("🔵 Step 2: Parsing request body...")  # ADD
        data = json.loads(request.body)
        # print(f"✅ Data parsed: {data}")  # ADD
        
        score = data.get('score')
        percentage = data.get('percentage')
        passed = data.get('passed')
        answers = data.get('answers')
        attempt_number = data.get('attempt', 1)
        
        print(f"🔵 score={score}, percentage={percentage}, passed={passed}")  # ADD
        
        # Validate data
        print("🔵 Step 3: Validating data...")  # ADD
        if score is None or percentage is None or passed is None:
            print("❌ Validation failed!")  # ADD
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)
        print("✅ Data validated")  # ADD
        
        # Create or get assessment record
        print("🔵 Step 4: Creating/getting assessment...")  # ADD
        assessment, created = Assessment.objects.get_or_create(
            module=module,
            teacher=request.user,
            defaults={
                'score': score,
                'max_score': 15,
                'passed': passed,
                'attempt_number': attempt_number,
                'answers': answers,
                'metadata': {
                    'percentage': percentage,
                    'passing_threshold': 80,
                    'submission_timestamp': str(timezone.now())
                }
            }
        )
        print(f"✅ Assessment: created={created}, obj={assessment}")  # ADD
        
        # If assessment exists, update
        print("🔵 Step 5: Checking if update needed...")  # ADD
        if not created:
            print("🔵 Updating existing assessment...")  # ADD
            is_new_attempt = assessment.answers != answers
            
            if is_new_attempt:
                assessment.attempt_number += 1
                print(f"✅ New attempt detected. Incrementing to {assessment.attempt_number}")
            else:
                print(f"⚠️ Duplicate submission detected. Not incrementing")
            
            if score > assessment.score:
                assessment.score = score
                assessment.passed = passed
                assessment.answers = answers
                assessment.metadata['percentage'] = percentage
                print(f"✅ New high score! Updated to {score}")
            else:
                print(f"ℹ️ Score {score} not higher than existing {assessment.score}")
            
            assessment.metadata['last_attempt_timestamp'] = str(timezone.now())
            assessment.save()
            print("✅ Assessment saved")  # ADD
        
        # If passed, mark assessment tab as complete
        print("🔵 Step 6: Checking if passed...")  # ADD
        if passed:
            print("🔵 Marking assessment complete...")  # ADD
            progress, _ = UserModuleProgress.objects.get_or_create(
                module=module,
                user=request.user
            )
            progress.assessment_completed = True
            progress.assessment_completed_at = timezone.now()
            progress.save()
            print("✅ Progress updated")  # ADD
        
        # Return success
        print("🔵 Step 7: Returning JSON response...")  # ADD
        response_data = {
            'success': True,
            'message': 'Quiz submitted successfully',
            'score': score,
            'percentage': percentage,
            'passed': passed,
            'attempts_used': assessment.attempt_number,
            'attempts_remaining': max(0, 3 - assessment.attempt_number),
            'is_best_score': score >= assessment.score
        }
        print(f"✅ Response: {response_data}")  # ADD
        return JsonResponse(response_data)
        
    except Module.DoesNotExist:
        print("❌ ERROR: Module not found")  # ADD
        return JsonResponse({
            'success': False,
            'error': 'Module not found'
        }, status=404)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: JSON decode error: {e}")  # ADD
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print("=" * 50)  # ADD
        print(f"❌ UNEXPECTED ERROR: {e}")  # ADD
        print(f"❌ ERROR TYPE: {type(e).__name__}")  # ADD
        import traceback
        traceback.print_exc()  # ADD - This will print FULL stack trace!
        print("=" * 50)  # ADD
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_assessment_attempts(request, code):  # ← Changed from module_code to code
    """
    Get all previous assessment attempts for a user on a specific module.
    Used to display attempt history and determine attempts remaining.
    """
    try:
        # Get module
        module = Module.objects.get(code=code)  # ← Uses 'code' now
        
        # Get all attempts (we store highest score, but track attempt count)
        assessment = Assessment.objects.filter(
            module=module,
            teacher=request.user
        ).first()
        
        if not assessment:
            return JsonResponse({
                'success': True,
                'attempts': [],
                'attempts_used': 0,
                'attempts_remaining': 3,
                'highest_score': 0,
                'highest_percentage': 0,
                'has_passed': False
            })
        
        attempts_used = assessment.attempt_number
        attempts_remaining = max(0, 3 - attempts_used)
        
        return JsonResponse({
            'success': True,
            'attempts_used': attempts_used,
            'attempts_remaining': attempts_remaining,
            'highest_score': assessment.score,
            'highest_percentage': assessment.metadata.get('percentage', 0),
            'has_passed': assessment.passed,
            'last_attempt_date': assessment.updated_at.isoformat()
        })
        
    except Module.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Module not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ============================================================================
# TAB 5: RTM - REFLECTIVE TENSION MAPPER
# ============================================================================

@login_required
@require_POST
def save_tensions(request, code):
    """
    Save user's tension positioning responses.
    Called via AJAX when user clicks 'Save Positions' in RTM card.
    Locked after module completion (research integrity).
    """
    from .models import ReflectionTension
    
    module = get_object_or_404(Module, code=code)
    
    # Check edit lock
    try:
        progress = UserModuleProgress.objects.get(user=request.user, module=module)
    except UserModuleProgress.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Progress record not found'}, status=404)
    
    # Allow save if tensions not yet saved for this module
    existing_tensions = ReflectionTension.objects.filter(
        user=request.user, module=module
    ).count()
    
    # if progress.reflection_completed and existing_tensions > 0:
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Module completed - positions cannot be edited'
    #     }, status=403)
    
    try:
        data = json.loads(request.body)
        tensions_data = data.get('tensions', [])
        
        if not tensions_data:
            return JsonResponse({'success': False, 'message': 'No tension data provided'})
        
        # Validate positions
        for t in tensions_data:
            position = t.get('position')
            if not isinstance(position, int) or not (1 <= position <= 5):
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid position: {position}. Must be 1-5.'
                })
        
        # Save or update each tension. CP-9 invariant (Phase C C.3
        # commit 2a): save + provenance write in one atomic block per
        # tension. Provenance is recorded for the row by (kind, pk);
        # on update_or_create's "update" branch (existing tension being
        # re-positioned by the user), record_ai_provenance is a silent
        # no-op due to get_or_create idempotency in the helper.
        saved_count = 0
        for t in tensions_data:
            comment = t.get('comment', '') or ''
            with transaction.atomic():
                tension, _created = ReflectionTension.objects.update_or_create(
                    user=request.user,
                    module=module,
                    tension_label=t['tension_label'],
                    defaults={
                        'left_pole': t['left_pole'],
                        'right_pole': t['right_pole'],
                        'grounding_quote': t['grounding_quote'],
                        'selected_position': t['position'],
                        'optional_comment': comment.strip() or None,
                        'time_spent_ms': t.get('time_spent_ms'),
                        'comment_used': bool(comment.strip()),
                        'position_confirmed': t.get('position_confirmed', False)
                    }
                )
                record_ai_provenance(
                    artefact_kind='rtm_position',
                    artefact_pk=tension.pk,
                    user=tension.user,
                    module=tension.module,
                    model_name=PROVENANCE_MODEL_NAME,
                    generated_at=timezone.now(),
                )
            saved_count += 1
        
        print(f"✅ RTM: Saved {saved_count} tensions for user {request.user.id}, module {module.code}")
        
        return JsonResponse({'success': True, 'saved_count': saved_count})
    
    except Exception as e:
        print(f"❌ RTM save error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'}, status=500)


@login_required
def get_tensions(request, code):
    """
    Retrieve saved tension positions for a module.
    Used when user revisits TAB 5 before/after module completion.
    Returns module_completed flag so frontend can lock/unlock editing.
    """
    from .models import ReflectionTension
    
    module = get_object_or_404(Module, code=code)
    
    try:
        progress = UserModuleProgress.objects.get(user=request.user, module=module)
        
        tensions = ReflectionTension.objects.filter(
            user=request.user,
            module=module
        ).order_by('created_at')
        
        if not tensions.exists():
            return JsonResponse({
                'tensions': [],
                'module_completed': progress.completed_at is not None
            })
        
        tensions_data = [{
            'tension_label': t.tension_label,
            'left_pole': t.left_pole,
            'right_pole': t.right_pole,
            'grounding_quote': t.grounding_quote,
            'selected_position': t.selected_position,
            'optional_comment': t.optional_comment
        } for t in tensions]
        
        return JsonResponse({
            'tensions': tensions_data,
            'module_completed': progress.completed_at is not None
        })
    
    except UserModuleProgress.DoesNotExist:
        return JsonResponse({'tensions': [], 'module_completed': False})
    except Exception as e:
        print(f"❌ RTM get_tensions error: {e}")
        return JsonResponse({'tensions': [], 'module_completed': False})

@login_required
@require_POST
def extract_tensions_view(request, code):
    """
    Async RTM endpoint - called by frontend after feedback is displayed.
    Separates RTM extraction from main reflection submission for better UX.
    """
    from rag_query_system import extract_tensions
    from .models import ReflectionTension
    
    module = get_object_or_404(Module, code=code)
    
    try:
        data = json.loads(request.body)
        reflection_text = data.get('reflection_text', '')
        
        if not reflection_text:
            return JsonResponse({'tensions': None, 'message': 'No reflection text'})
        
        # Build teacher context
        try:
            from apps.users.models import TeacherProfile
            profile = TeacherProfile.objects.get(user=request.user)
            teacher_context = {
                'name': profile.first_name,
                'full_name': f"{profile.first_name} {profile.last_name}",
                'subject': profile.subject_area,
                'grade_level': profile.grade_level,
                'experience': profile.teaching_years,
                'enable_peer_synthesis': True,
            }
        except Exception:
            teacher_context = {'subject': 'Unknown'}
        
        tensions = extract_tensions(reflection_text, teacher_context)
        
        if tensions:
            return JsonResponse({'success': True, 'tensions': tensions})
        else:
            return JsonResponse({'success': False, 'tensions': None})
    
    except Exception as e:
        print(f"❌ Async RTM error: {e}")
        return JsonResponse({'success': False, 'tensions': None})

@login_required
@require_POST
def extract_peer_synthesis_view(request, code):
    from rag_query_system import search_peer_reflections, synthesize_peer_insight, embed_query
    import markdown
    
    module = get_object_or_404(Module, code=code)
    print(f"🔍 PEER SYNTHESIS VIEW CALLED - module={code}, user={request.user.id}")
    
    try:
        data = json.loads(request.body)
        reflection_text = data.get('reflection_text', '')
        print(f"🔍 reflection_text length: {len(reflection_text)}")
        
        if not reflection_text:
            return JsonResponse({'success': False})
        
        # Build teacher context
        try:
            from apps.users.models import TeacherProfile
            profile = TeacherProfile.objects.get(user=request.user)
            teacher_context = {
                'name': profile.first_name,
                'subject': profile.subject_area,
                'enable_peer_synthesis': True,
            }
            print(f"🔍 Profile: {profile.first_name}, subject={profile.subject_area}")
        except Exception as ex:
            print(f"❌ Profile error: {ex}")
            teacher_context = {'subject': 'Unknown', 'enable_peer_synthesis': True}
        
        # Connect to DB
        import psycopg2
        from django.conf import settings
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
        )
        # print(f"✅ DB connected")
        
        query_embedding = embed_query(reflection_text)
        peer_reflections = search_peer_reflections(
            conn, query_embedding,
            user_subject=teacher_context.get('subject', 'General'),
            top_k=2
        )
        
        if not peer_reflections:
            print(f"⚠️ No peer reflections found")
            conn.close()
            return JsonResponse({'success': False, 'message': 'No peer reflections found'})
        
        print(f"✅ Found {len(peer_reflections)} peer reflections")
        
        peer_synthesis = synthesize_peer_insight(
            reflection_text, teacher_context, peer_reflections
        )
        conn.close()
        
        if peer_synthesis:
            peer_synthesis_html = markdown.markdown(
                peer_synthesis, extensions=['extra', 'nl2br']
            )
            progress = UserModuleProgress.objects.get(
                user=request.user, module=module
            )
            # CP-9 invariant: save + provenance in one atomic block.
            with transaction.atomic():
                progress.reflection_peer_synthesis = peer_synthesis_html
                progress.save(update_fields=['reflection_peer_synthesis'])
                record_ai_provenance(
                    artefact_kind='peer_synthesis',
                    artefact_pk=progress.pk,
                    user=progress.user,
                    module=progress.module,
                    model_name=PROVENANCE_MODEL_NAME,
                    generated_at=timezone.now(),
                )
            print(f"✅ Peer synthesis saved ({len(peer_synthesis_html)} chars)")
            return JsonResponse({'success': True, 'peer_synthesis': peer_synthesis_html})
        else:
            return JsonResponse({'success': False})
    
    except Exception as e:
        print(f"❌ Async peer synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False})

@login_required
@require_POST
def extract_dtp_view(request, code):
    """
    Async DTP endpoint - called by frontend after feedback is displayed.
    Only activates from M2+ (requires previous reflection in rag_queries).
    """
    from rag_query_system import compute_dtp
    
    module = get_object_or_404(Module, code=code)
    
    try:
        data = json.loads(request.body)
        current_reflection = data.get('reflection_text', '')
        
        if not current_reflection:
            return JsonResponse({'success': False, 'message': 'No reflection text'})
        
        # Find most recent previous reflection from a DIFFERENT module
        import psycopg2
        from django.conf import settings
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rq.reflection_text, m.code
            FROM rag_queries rq
            JOIN modules_module m ON rq.module_id = m.id
            WHERE rq.user_id = %s
              AND rq.module_id != %s
            ORDER BY rq.created_at DESC
            LIMIT 1;
        """, (request.user.id, module.id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return JsonResponse({'success': False, 'message': 'No previous reflection found'})
        
        previous_reflection, previous_module_code = row
        
        # Compute DTP
        dtp_result = compute_dtp(
            previous_reflection_text=previous_reflection,
            current_reflection_text=current_reflection,
            previous_module=previous_module_code,
            current_module=module.code
        )
        
        if dtp_result:
            # Save DTP result to database. CP-9 invariant: save +
            # provenance in one atomic block.
            try:
                progress = UserModuleProgress.objects.get(user=request.user, module=module)
                with transaction.atomic():
                    progress.reflection_dtp = json.dumps(dtp_result)
                    progress.save()
                    record_ai_provenance(
                        artefact_kind='dtp_narrative',
                        artefact_pk=progress.pk,
                        user=progress.user,
                        module=progress.module,
                        model_name=PROVENANCE_MODEL_NAME,
                        generated_at=timezone.now(),
                    )
            except Exception as e:
                print(f"⚠️ Could not save DTP: {e}")

            return JsonResponse({'success': True, 'dtp': dtp_result})
        else:
            return JsonResponse({'success': False, 'message': 'DTP computation failed'})
    
    except Exception as e:
        print(f"❌ DTP view error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def execute_prompt(request, module_code):
    """
    Phase 2 of M8 TAB3.
    Takes the saved prompt from challenge_data.challenge1_prompt,
    runs it through Gemini 2.5 Flash, returns HTML output.
    One-time use — does not save to DB (that happens in challenge2 submit).
    """
    try:
        module = get_object_or_404(Module, code=module_code)
        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )
 
        prompt_text = activity.challenge_data.get('challenge1_prompt', '')
        if not prompt_text:
            return JsonResponse({'success': False, 'message': 'No prompt found. Complete Phase 1 first.'})
 
        # Run prompt through Gemini
        try:
            from google import genai as genai_client
            from google.genai import types as genai_types
            client = genai_client.Client(api_key=os.environ.get('GEMINI_API_KEY', ''))
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Important: Do not use LaTeX notation. Write all fractions in plain text format (e.g. 3/4 instead of LaTeX fraction notation).\n\n{prompt_text}",
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=16000
                )
            )
            output_text = response.text
        except ImportError:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt_text)
            output_text = response.text
 
        # Convert markdown to HTML for display
        try:
            output_html = markdown.markdown(
                output_text,
                extensions=['nl2br', 'tables']
            )
        except Exception:
            # Fallback: simple newline to <br> conversion
            output_html = output_text.replace('\n', '<br>')
 
        return JsonResponse({
            'success': True,
            'output_html': output_html,
            'output_text': output_text
        })
 
    except Tab3UserActivity.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Activity not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
 
 
@login_required
@require_http_methods(["POST"])
def get_rpe_feedback(request, module_code):
    """
    Phase 4 of M8 TAB3 (optional).
    Assesses BOTH the prompt (RPE lens) AND the output (pedagogical lens).
    Returns HTML feedback. Does not save — saving handled by save_rpe_feedback.
    """
    try:
        module = get_object_or_404(Module, code=module_code)
        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )
 
        prompt_text = activity.challenge_data.get('challenge1_prompt', '')
        output_html = activity.challenge_data.get('challenge2_output', '')
        eval_usability = activity.challenge_data.get('challenge3_usability', '')
        eval_cognitive = activity.challenge_data.get('challenge3_cognitive', '')
 
        if not prompt_text or not output_html:
            return JsonResponse({'success': False, 'message': 'Complete Phases 1-3 first.'})
 
        # Strip HTML tags from output for cleaner analysis
        import re
        output_text = re.sub(r'<[^>]+>', ' ', output_html)
        output_text = re.sub(r'\s+', ' ', output_text).strip()[:1500]
 
        meta_prompt = f"""You are an expert in teacher professional development and the RPE (Reflective Prompt Engineering) Framework.
 
Analyse the following educational AI prompt and its output. Provide structured feedback in two sections.
 
THE PROMPT:
{prompt_text}
 
THE OUTPUT (first 1500 chars):
{output_text}
 
TEACHER SELF-EVALUATION:
- Usability rating: {eval_usability}
- Cognitive level match: {eval_cognitive}
 
Provide feedback in exactly this structure:
 
## How Strong Is Your Prompt?
 
Assess the prompt against the 5 RPE strategies:
- **S1 Goals**: [one sentence — is the learning outcome explicit?]
- **S2 Context**: [one sentence — does it describe the students specifically?]
- **S3 Format**: [one sentence — is the output structure specified?]
- **S4 Cognitive Level**: [one sentence — is Bloom's level explicit and appropriate?]
- **S5 Examples/Avoid**: [one sentence — are include/avoid instructions present?]
 
**Overall prompt strength**: [Strong / Developing / Needs work] — [one sentence explanation]
 
**One specific improvement**: [one concrete suggestion — max 2 sentences]
 
## How Useful Is the Output?
 
- **Pedagogical fit**: [Does the output match the stated learning goal? One sentence.]
- **Student-readiness**: [Could this be used directly with students, or does it need editing? One sentence.]
- **What worked**: [The strongest element of the output. One sentence.]
- **What to watch**: [One concern or limitation in the output. One sentence.]
 
Keep the entire response under 350 words. Be direct and specific — avoid generic praise."""
 
        # Run meta-prompt through Gemini
        try:
            from google import genai as genai_client
            from google.genai import types as genai_types
            client = genai_client.Client(api_key=os.environ.get('GEMINI_API_KEY', ''))
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=meta_prompt,
                config=genai_types.GenerateContentConfig(
                    max_output_tokens=800
                )
            )
            feedback_text = response.text
        except ImportError:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(meta_prompt)
            feedback_text = response.text
 
        # Convert to HTML
        try:
            feedback_html = markdown.markdown(
                feedback_text,
                extensions=['nl2br', 'tables']
            )
        except Exception:
            feedback_html = feedback_text.replace('\n', '<br>')
 
        return JsonResponse({
            'success': True,
            'feedback_html': feedback_html
        })
 
    except Tab3UserActivity.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Activity not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
 
 
@login_required
@require_http_methods(["POST"])
def save_rpe_feedback(request, module_code):
    """Save AI feedback HTML to challenge_data."""
    try:
        data = json.loads(request.body)
        module = get_object_or_404(Module, code=module_code)
        activity = Tab3UserActivity.objects.get(
            user=request.user,
            module_id=module.id
        )
        existing = activity.challenge_data or {}
        existing['ai_feedback'] = data.get('feedback_html', '')
        activity.challenge_data = existing
        activity.save()
 
        return JsonResponse({'success': True})
 
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# ============================================================
# save_ai_dispute view
# Add to apps/modules/views.py
# ============================================================
# Also add to apps/modules/urls.py:
#   path('modules/<str:code>/dispute/', views.save_ai_dispute, name='save_ai_dispute'),

@login_required
@require_POST
def save_ai_dispute(request, code):
    """
    Save teacher dispute/rating for an AI output in TAB5.

    HITL (Human-in-the-Loop) mechanism.
    Research instrument for AI Alignment measurement.

    Accepts:
        feature_type: 'rag' | 'rtm' | 'dtp'
        rating: 'yes' | 'no' | 'partial'
        reason: optional categorisation
        comment: optional free text (max 300 chars)

    Returns:
        success: bool
        message: acknowledgment string
    """
    from .models import AIOutputDispute

    module = get_object_or_404(Module, code=code)

    try:
        data = json.loads(request.body)

        feature_type = data.get('feature_type', '')
        rating = data.get('rating', '')
        reason = data.get('reason', '') or None
        comment = (data.get('comment', '') or '').strip()[:300] or None

        # Validate feature_type
        valid_features = ['rag', 'rtm', 'dtp']
        if feature_type not in valid_features:
            return JsonResponse({
                'success': False,
                'message': f'Invalid feature type: {feature_type}'
            }, status=400)

        # Validate rating
        valid_ratings = ['yes', 'no', 'partial']
        if rating not in valid_ratings:
            return JsonResponse({
                'success': False,
                'message': f'Invalid rating: {rating}'
            }, status=400)

        # Save or update — one per user/module/feature
        dispute, created = AIOutputDispute.objects.update_or_create(
            user=request.user,
            module=module,
            feature_type=feature_type,
            defaults={
                'rating': rating,
                'reason': reason,
                'comment': comment,
            }
        )

        action = 'saved' if created else 'updated'
        print(f"✅ AI Dispute {action}: user={request.user.id} module={module.code} "
              f"feature={feature_type} rating={rating}")

        return JsonResponse({
            'success': True,
            'message': 'Thank you — your feedback has been recorded and will help improve PROODOS.',
            'action': action
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"❌ save_ai_dispute error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=500)


# ============================================================
# Subject Intro Hooks (TAB1) — Phase 2
# Spec: SUBJECT_INTRO_HOOKS_PATCH_APR2026.md
# Pattern mirrors apps/community/views.py::thread_info
# ============================================================

@login_required
@require_GET
def subject_intro_view(request, code):
    """
    Returns the subject-specific intro hook for TAB1.
    Falls back to subject_area='Universal' if no subject-specific record exists.
    """
    try:
        module = Module.objects.get(code=code)
    except Module.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Module not found'}, status=404)

    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
        subject = teacher_profile.subject_area
    except TeacherProfile.DoesNotExist:
        subject = None

    intro = None
    if subject:
        intro = ModuleContent.objects.filter(
            module=module,
            content_type='subject_intro',
            subject_area=subject,
            grade_level='all'
        ).first()

    if not intro:
        intro = ModuleContent.objects.filter(
            module=module,
            content_type='subject_intro',
            subject_area='Universal',
            grade_level='all'
        ).first()

    if not intro:
        return JsonResponse({'success': False, 'error': 'No intro found'})

    return JsonResponse({
        'success': True,
        'html': intro.content_data,
        'subject': subject or 'Universal'
    })

