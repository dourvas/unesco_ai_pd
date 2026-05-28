"""
Onboarding Views - UNESCO AI Teacher PD Platform
Multi-step onboarding system with session management
"""

import json

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from .models import TeacherProfile
from .forms import TeachingContextForm, AIExperienceForm, GoalsPreferencesForm, ProfileEditForm

# ============================================================================
# ONBOARDING FLOW VIEWS
# ============================================================================

@login_required
def onboarding_welcome(request):
    """
    Welcome page - just intro, NO profile creation.

    Onboarding-complete check uses TeacherProfile.profile_completed as
    the durable truth, with the session marker as a fallback for
    in-flight state. The session-only check used to send users back to
    the dashboard if they had finished onboarding earlier; profile
    flag is more reliable across logout/login cycles.
    """
    try:
        profile = TeacherProfile.objects.get(user=request.user)
        if profile.profile_completed or request.session.get('onboarding_step', 0) >= 3:
            messages.info(request, 'You have already completed onboarding!')
            return redirect('users:dashboard')
        # Has profile but onboarding not complete - continue where they left off
    except TeacherProfile.DoesNotExist:
        # No profile yet - this is fine for welcome page
        pass

    return render(request, 'onboarding/welcome.html')

@login_required
def onboarding_step1(request):
    """
    Step 1: Teaching Context
    CREATES profile here with required fields from form
    """
    # Try to get existing profile
    try:
        profile = TeacherProfile.objects.get(user=request.user)
        # Profile exists - let them edit it
        editing = True
    except TeacherProfile.DoesNotExist:
        profile = None
        editing = False
    
    if request.method == 'POST':
        if profile:
            # Update existing profile
            form = TeachingContextForm(request.POST, instance=profile)
        else:
            # Create new profile (no instance)
            form = TeachingContextForm(request.POST)
        
        if form.is_valid():
            if profile:
                # Just save the existing profile
                form.save()
            else:
                # Create NEW profile with form data
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
            
            request.session['onboarding_step'] = 1
            messages.success(request, '✅ Step 1 completed!')
            return redirect('users:onboarding_step2')
    else:
        if profile:
            # Editing existing profile
            form = TeachingContextForm(instance=profile)
        else:
            # New empty form
            form = TeachingContextForm()
    
    context = {
        'form': form,
        'profile': profile,
        'current_step': 1,
        'total_steps': 3,
        'progress_percentage': 33
    }
    
    return render(request, 'onboarding/step1.html', context)


@login_required
def onboarding_step2(request):
    """
    Step 2: AI Experience
    Profile must exist from Step 1
    """
    # Get profile (should exist from Step 1)
    try:
        profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        # No profile - redirect to Step 1
        messages.warning(request, 'Please complete Step 1 first.')
        return redirect('users:onboarding_step1')
    
    # Check if Step 1 was completed
    if request.session.get('onboarding_step', 0) < 1:
        messages.warning(request, 'Please complete Step 1 first.')
        return redirect('users:onboarding_step1')
    
    if request.method == 'POST':
        form = AIExperienceForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.session['onboarding_step'] = 2
            messages.success(request, '✅ Step 2 completed!')
            return redirect('users:onboarding_step3')
    else:
        form = AIExperienceForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'current_step': 2,
        'total_steps': 3,
        'progress_percentage': 66
    }
    
    return render(request, 'onboarding/step2.html', context)


def _apply_step3_consents(
    *,
    user,
    research_checked,
    data_sharing_checked,
    ip_address,
):
    """Phase C C.2.2 + Phase H H.6 (2026-05-25 redesign) — Step 3
    research-consent policy.

    Translates the Step 3 checkbox state into ConsentRecord writes via the
    canonical record_consent / revoke_consent helpers. The M6 sync signal
    updates the legacy TeacherProfile boolean cache automatically.

    This helper centralises the Step-3-specific mapping:
      - 'consent_research_participation' checkbox -> consent_type='research_participation'
        (Phase H V2: this text now bundles the follow-up email-retention
        permission as one bullet under "What participation involves:" —
        a single broad consent, no separate checkbox)
      - 'consent_data_sharing' checkbox          -> consent_type='data_sharing'

    Idempotent: re-submitting the same checkbox state is a no-op (the
    record_consent supersede check returns the existing active row;
    revoke_consent on already-empty active set returns 0).

    The current research_participation text stored verbatim per submission
    is read from settings.RESEARCH_CONSENT_CURRENT_VERSION (V2 ships with
    the bundled-followup bullet; V1 lingers for IRB-defensibility of
    already-granted rows).
    """
    from django.conf import settings

    from apps.compliance.copy import (
        DATA_SHARING_TEXT_V1_PRE_IRB,
        RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB,
        RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
    )
    from apps.compliance.services import record_consent, revoke_consent

    version = settings.RESEARCH_CONSENT_CURRENT_VERSION

    # Select the verbatim text that matches the active version pointer.
    # If the version pointer flips back to v1_pre_irb (rollback), the
    # corresponding text is written; if it flips forward to a future V3,
    # add the constant + branch here.
    research_text_by_version = {
        'v1_pre_irb': RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB,
        'v2_followup_bundled': RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
    }
    research_text = research_text_by_version.get(
        version, RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
    )

    if research_checked:
        record_consent(
            user=user,
            consent_type='research_participation',
            consent_text=research_text,
            version=version,
            ip_address=ip_address,
        )
    else:
        # Revokes any active row of this consent_type — including legacy
        # v0_pre_phase_c (M6 backfill) if user is opting out for the first
        # time. One consent identity per consent_type.
        revoke_consent(user=user, consent_type='research_participation')

    if data_sharing_checked:
        record_consent(
            user=user,
            consent_type='data_sharing',
            consent_text=DATA_SHARING_TEXT_V1_PRE_IRB,
            version=version,
            ip_address=ip_address,
        )
    else:
        revoke_consent(user=user, consent_type='data_sharing')


def _step3_client_ip(request):
    """Best-effort client IP for ConsentRecord rows (auto-redacted after 30 days
    via apps/compliance/management/commands/redact_old_consent_ips)."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@login_required
def onboarding_step3(request):
    """
    Step 3: Goals & Preferences + research consents.

    Phase C C.2.2 refactor: research_consent and consent_data_sharing are
    written via record_consent() (canonical path), not via direct boolean
    writes. The M6 signal updates the booleans automatically.
    """
    from django.conf import settings

    from apps.compliance.copy import (
        DATA_SHARING_TEXT_V1_PRE_IRB,
        RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB,
        RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED,
    )

    profile = get_object_or_404(TeacherProfile, user=request.user)

    if request.session.get('onboarding_step', 0) < 2:
        messages.warning(request, 'Please complete Step 2 first.')
        return redirect('users:onboarding_step2')

    if request.method == 'POST':
        form = GoalsPreferencesForm(request.POST, instance=profile)
        if form.is_valid():
            # M3 attribution: history rows carry change_source.
            form.instance._change_source = 'onboarding_step3'
            form.save()

            _apply_step3_consents(
                user=request.user,
                research_checked=form.cleaned_data['consent_research_participation'],
                data_sharing_checked=form.cleaned_data['consent_data_sharing'],
                ip_address=_step3_client_ip(request),
            )

            request.session['onboarding_step'] = 3
            messages.success(request, '✅ Step 3 completed!')
            return redirect('users:onboarding_confirm')
    else:
        form = GoalsPreferencesForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'current_step': 3,
        'total_steps': 3,
        'progress_percentage': 100,
        # Verbatim consent texts shown to user; must match what
        # _apply_step3_consents stores via record_consent. The research
        # text rendered to the user follows the active version setting
        # (V2 bundles the follow-up-contact bullet inline).
        'research_text': (
            RESEARCH_PARTICIPATION_TEXT_V2_FOLLOWUP_BUNDLED
            if settings.RESEARCH_CONSENT_CURRENT_VERSION == 'v2_followup_bundled'
            else RESEARCH_PARTICIPATION_TEXT_V1_PRE_IRB
        ),
        'data_sharing_text': DATA_SHARING_TEXT_V1_PRE_IRB,
        'consent_version': settings.RESEARCH_CONSENT_CURRENT_VERSION,
    }

    return render(request, 'onboarding/step3.html', context)


@login_required
def onboarding_summary(request):
    """
    Summary: read-only review of all onboarding information.

    Phase C C.2.5b refactor: this view used to also host the
    "Complete profile and start AILST" POST. That CTA moved to the
    new short interstitial page at /onboarding/confirm/ to reduce
    dropout (the CTA used to sit below several scrollable cards and
    many users would not reach it). The summary page now serves only
    as an optional drill-down for users who want to verify their data
    before confirming.
    """
    profile = get_object_or_404(TeacherProfile, user=request.user)

    if request.session.get('onboarding_step', 0) < 3:
        messages.warning(request, 'Please complete all steps first.')
        return redirect('users:onboarding_step1')

    context = {
        'profile': profile,
        'subject_display': profile.get_subject_area_display() if profile.subject_area else '-',
        'grade_display': profile.get_grade_level_display() if profile.grade_level else '-',
        'years_display': profile.get_teaching_years_display() if profile.teaching_years else '-',
        'location_display': profile.get_school_location_display() if profile.school_location else '-',
        'class_size_display': profile.get_average_class_size_display() if profile.average_class_size else '-',
        'ai_exp_display': profile.get_ai_experience_display() if profile.ai_experience else '-',
        'comm_style_display': profile.get_preferred_communication_style_display(),
        'completion_percentage': profile.completion_percentage
    }

    return render(request, 'onboarding/summary.html', context)


@login_required
def onboarding_confirm(request):
    """
    Short interstitial page after Step 3 with three CTAs:

        - Continue to AI Literacy baseline (primary)
        - Review my profile (drill-down to /onboarding/summary/)
        - Back to Step 3 (edit answers)

    POST is the canonical completion path:
      - Sets profile.profile_completed = True (durable truth used by the
        AILST entry view and the dashboard guard).
      - Sets profile.profile_completion_date and consent_timestamp.
      - Advances request.session['onboarding_step'] to 4.
      - Redirects to /ailst/t0/ to start the AI Literacy baseline.

    GET renders the page; POST performs the state changes and the
    forward redirect.
    """
    profile = get_object_or_404(TeacherProfile, user=request.user)

    if request.session.get('onboarding_step', 0) < 3:
        messages.warning(request, 'Please complete all steps first.')
        return redirect('users:onboarding_step1')

    if request.method == 'POST':
        profile.profile_completed = True
        profile.profile_completion_date = timezone.now()
        profile.consent_timestamp = timezone.now() if profile.research_consent else None
        profile.save()

        request.session['onboarding_step'] = 4
        messages.success(request, 'Profile completed. One more short step before you start the modules.')
        return redirect('ailst:entry', timepoint='t0')

    return render(request, 'onboarding/confirm.html', {'profile': profile})

@login_required
def onboarding_skip(request):
    """
    Skip onboarding - create profile with default values
    User can complete it later from Settings
    """
    # Create profile with first choice defaults
    profile, created = TeacherProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'subject_area': 'mathematics',  # First choice
            'grade_level': 'primary',       # First choice
        }
    )
    
    if created:
        messages.warning(request, 'You skipped onboarding. You can complete your profile anytime from Settings.')
    else:
        messages.info(request, 'Profile already exists.')
    
    return redirect('users:dashboard')
# ============================================================================
# PROFILE MANAGEMENT VIEWS
# ============================================================================

@login_required
def profile_view(request):
    """
    View current profile
    """
    profile = get_object_or_404(TeacherProfile, user=request.user)
    
    context = {
        'profile': profile,
        'subject_display': profile.get_subject_area_display() if profile.subject_area else '-',
        'grade_display': profile.get_grade_level_display() if profile.grade_level else '-',
        'completion_percentage': profile.completion_percentage
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """
    Edit profile after completion
    """
    profile = get_object_or_404(TeacherProfile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            # Phase C M3 attribution: TeacherProfileHistory rows carry the
            # 'profile_edit' source so analytics can distinguish user-driven
            # changes from migrations or admin actions. The signal in
            # apps/users/signals.py reads this transient attribute in post_save.
            form.instance._change_source = 'profile_edit'
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile_view')
    else:
        form = ProfileEditForm(instance=profile)

    context = {
        'form': form,
        'profile': profile
    }

    return render(request, 'users/profile_edit.html', context)


# ============================================================================
# DASHBOARD
# ============================================================================

@login_required
def dashboard(request):
    """
    Dashboard — requires completed profile.

    Phase H.7 redesign (TD-021 resolution, 2026-05-25): replaces the
    duplicate-of-the-Modules-menu module list with a personal UNESCO
    5x3 progress matrix + a single contextual next-action card + a
    Certificate of Attendance panel that surfaces the cert once the
    closing AILST measurement (T2) is complete.

    Hard constraint preserved per TD-021 line 435: the dashboard is
    completion-structure, NOT developmental-evolution. DTP curves
    and RTM tension trajectories belong to the Epilogue Stage 0
    surface, not here.

    Guards:
      - No TeacherProfile row -> send to onboarding welcome.
      - Profile row exists but profile_completed is False (e.g. created
        by ai_disclosure_view's get_or_create before the user reached
        Step 1) -> also send to onboarding welcome. The dashboard
        contents only make sense once the user has filled in their
        teaching context, AI experience, and goals.
    """
    from apps.users.services import (
        build_personal_unesco_matrix,
        certificate_state_for_dashboard,
        next_action_for_dashboard,
    )

    try:
        profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile to access the dashboard.')
        return redirect('users:onboarding_welcome')

    if not profile.profile_completed:
        messages.info(request, 'Please finish your onboarding before opening the dashboard.')
        return redirect('users:onboarding_welcome')

    context = {
        'profile': profile,
        'personal_matrix': build_personal_unesco_matrix(request.user),
        'next_action': next_action_for_dashboard(request.user),
        'certificate_state': certificate_state_for_dashboard(request.user),
    }

    return render(request, 'home.html', context)

def landing_page(request):
    """
    Public landing page - Show landing.html to everyone at /
    """
    return render(request, 'landing.html')


def login_view(request):
    """
    Login page
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'users/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', 'users:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'users/login.html')

def register_view(request):
    """
    Registration - create user and redirect to onboarding
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'users/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'users/register.html')
        
        # Create user
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Log user in
            login(request, user)
            
            messages.success(request, 'Account created! Please complete your profile.')
            
            # Redirect to ONBOARDING (not dashboard!)
            return redirect('users:onboarding_welcome')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'users/register.html')
    
    return render(request, 'users/register.html')

def logout_view(request):
    """
    Logout user
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('users:landing')


# ============================================================================
# ALETHEIA HELP CHAT (Phase J.1)
# ============================================================================

_HELP_SESSION_KEY = 'help_turns'

@login_required
@require_POST
@csrf_protect
def help_chat_view(request):
    """AJAX endpoint for the Aletheia always-on help bot.

    Receives a JSON POST with {question: str}. Manages the conversation
    history in request.session['help_turns']. Enforces the 20-turn hard
    limit. Returns JSON {reply, turn_count, at_limit, error?}.

    No DB writes — conversation is session-only, cleared on logout.
    """
    from apps.agents.help_agent import HelpAgent, HELP_TURN_LIMIT

    try:
        body = json.loads(request.body)
        question = (body.get('question') or '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'invalid_request'}, status=400)

    if not question:
        return JsonResponse({'error': 'empty_question'}, status=400)

    turns: list = request.session.get(_HELP_SESSION_KEY, [])
    turn_count = sum(1 for t in turns if t.get('role') == 'user')

    if turn_count >= HELP_TURN_LIMIT:
        return JsonResponse({
            'reply': (
                'The maximum number of help messages per session has been reached. '
                'For further support, please contact idourvas@ihu.gr.'
            ),
            'turn_count': turn_count,
            'at_limit': True,
        })

    agent = HelpAgent()
    reply = agent.extract(history=turns, question=question)

    if reply is None:
        return JsonResponse({
            'reply': (
                'The help service is temporarily unavailable. Please try again '
                'in a moment, or contact idourvas@ihu.gr.'
            ),
            'turn_count': turn_count,
            'at_limit': False,
            'error': 'api_failure',
        })

    turns.append({'role': 'user', 'content': question})
    turns.append({'role': 'assistant', 'content': reply})
    request.session[_HELP_SESSION_KEY] = turns
    request.session.modified = True

    new_turn_count = sum(1 for t in turns if t.get('role') == 'user')
    return JsonResponse({
        'reply': reply,
        'turn_count': new_turn_count,
        'at_limit': new_turn_count >= HELP_TURN_LIMIT,
    })