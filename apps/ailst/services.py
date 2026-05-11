"""
Cross-app service helpers for the AILST instrument.

This module exposes the integration surface used by other apps that
need to consult AILST state without importing models directly. Keeping
the integration logic here (rather than as a private helper in
apps.modules.views) makes it discoverable: a contributor searching for
"AILST redirect" or "post-module gating" finds the canonical
implementation in the AILST app where it belongs.
"""

from apps.ailst.models import AilstResponse


# Module-code -> AILST timepoint that should be administered immediately
# after that module is completed. Per the research design:
#   - M5  marks the end of the Acquire phase  -> T1
#   - M15 marks the end of the programme       -> T2
# Modules not in this mapping do not trigger any AILST redirect.
POST_MODULE_AILST_TIMEPOINT = {
    'M5':  'T1',
    'M15': 'T2',
}


def get_post_module_redirect_url(user, module_code):
    """Return the AILST URL the user should be sent to after completing
    `module_code`, or None if no AILST redirect is required.

    Called by apps.modules.views.mark_tab_complete immediately after a
    module's `progress.mark_tab_complete(...)` returns. The caller has
    already verified that the module's lifecycle progressed; this
    helper decides whether the next user-visible page should be the
    AILST baseline for the corresponding timepoint.

    Conditions for a redirect (ALL must hold):
      1. `module_code` is mapped (M5 or M15 in POST_MODULE_AILST_TIMEPOINT).
      2. The user has active research_consent (cached on TeacherProfile;
         kept in sync with the canonical ConsentRecord via the M6 signal).
         AILST is a research instrument; non-consenting users continue
         with the modules as a personal learning experience and are NOT
         redirected.
      3. The corresponding AilstResponse for (user, timepoint) does not
         already have completed_at set. This is the idempotency guard
         against repeated module completions (admin progress resets,
         double-submit, parallel tabs) re-sending an already-done user
         through the survey.

    Returns:
        str: lowercase URL path like '/ailst/t1/' or '/ailst/t2/' when
        a redirect is required.
        None: when any condition fails. The caller's response should
        proceed with the normal module-completion flow in that case.
    """
    timepoint = POST_MODULE_AILST_TIMEPOINT.get(module_code)
    if timepoint is None:
        return None

    profile = getattr(user, 'teacher_profile', None)
    if profile is None or not profile.research_consent:
        return None

    already_completed = AilstResponse.objects.filter(
        user=user,
        timepoint=timepoint,
        completed_at__isnull=False,
    ).exists()
    if already_completed:
        return None

    return f'/ailst/{timepoint.lower()}/'
