from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    # Module list (no separate dashboard needed)
    path('modules/', views.ModuleListView.as_view(), name='list'),
    
    # Module detail with tab navigation
    path('modules/<str:code>/', views.ModuleDetailView.as_view(), name='detail'),
    
    # AJAX: Mark tab complete
    path('modules/<str:code>/complete/<str:tab_name>/', 
         views.mark_tab_complete, 
         name='mark_tab_complete'),
    
    # TAB 3: AI Tool Exploration Activity
    path('modules/<str:module_code>/tab3/challenge1/', views.submit_challenge1, name='submit_challenge1'),
    path('modules/<str:module_code>/tab3/challenge2/', views.submit_challenge2, name='submit_challenge2'),
    path('modules/<str:module_code>/tab3/challenge3/', views.submit_challenge3, name='submit_challenge3'),
    path('modules/<str:module_code>/tab3/reflection/', views.submit_reflection,  name='submit_reflection'),
    path('modules/M1/tab3/custom-prompt/', views.get_custom_prompt, name='get_custom_prompt'),
    path('modules/toolkit/', views.view_toolkit, name='view_toolkit'),
    path('modules/<str:module_code>/tab3/execute-prompt/', views.execute_prompt, name='execute_prompt'),
    path('modules/<str:module_code>/tab3/rpe-feedback/', views.get_rpe_feedback, name='get_rpe_feedback'),
    path('modules/<str:module_code>/tab3/save-rpe-feedback/', views.save_rpe_feedback, name='save_rpe_feedback'),

    # Phase A Tier 2 Step 4 — M13 Repository Submission CTA
    path('modules/<str:module_code>/tab3/submit-to-repository/', views.submit_to_repository, name='submit_to_repository'),
    path('modules/<str:module_code>/tab3/export-canvas-pdf/', views.export_canvas_pdf, name='export_canvas_pdf'),

    # Phase A Tier 3 Step 4 — M9 / Step 5 — M14 generic Practice Workshop share
    path('modules/<str:module_code>/tab3/share-to-workshop/', views.share_to_workshop, name='share_to_workshop'),
    
    # TAB 4: Assessment (FIXED - using 'code' instead of 'module_code')
    path('modules/<str:code>/submit-assessment/', 
         views.submit_assessment, 
         name='submit_assessment'),
    
    path('modules/<str:code>/get-assessment-attempts/', 
         views.get_assessment_attempts, 
         name='get_assessment_attempts'),

     # TAB 5: RTM - Reflective Tension Mapper
    path('modules/<str:code>/save-tensions/', views.save_tensions, name='save_tensions'),
    path('modules/<str:code>/get-tensions/', views.get_tensions, name='get_tensions'),
    path('modules/<str:code>/extract-tensions/', views.extract_tensions_view, name='extract_tensions'),
    path('modules/<str:code>/extract-peer-synthesis/', views.extract_peer_synthesis_view, name='extract_peer_synthesis'),
    path('modules/<str:code>/extract-dtp/', views.extract_dtp_view, name='extract_dtp'),
    path('modules/<str:code>/dispute/', views.save_ai_dispute, name='save_ai_dispute'),

    # TAB 1: Subject Intro Hooks (AJAX)
    path('modules/<str:code>/subject-intro/', views.subject_intro_view, name='subject_intro'),
]