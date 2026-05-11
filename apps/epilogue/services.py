"""
Cross-app service helpers for the PROODOS Epilogue.

Exposes the integration surface used by apps.modules to send a user
to the Epilogue placeholder when they complete the last UNESCO-aligned
module (M15). The Epilogue itself decides where to go next (T2 if the
user has research_consent and has not yet completed it; dashboard
otherwise) — see apps.epilogue.views._post_epilogue_destination.

Per the C.2.5 design (D4), the Epilogue has no consent gate: it is a
pedagogical feature, not a research instrument. Non-consenting users
still see the placeholder and simply route to /dashboard/ at the end.
"""

from apps.epilogue.models import EpilogueCompletion


# Module-code -> URL the user is sent to after that module completes.
# Currently only M15 -> /epilogue/. Other modules are handled by the
# AILST helper (apps.ailst.services.get_post_module_redirect_url) or
# fall through to the normal next-tab flow.
POST_MODULE_NEXT_FEATURE = {
    'M15': '/epilogue/',
}


def get_post_module_epilogue_redirect_url(user, module_code):
    """Return /epilogue/ when the user has just completed the last
    UNESCO-aligned module (M15) and has not yet completed the Epilogue;
    None otherwise.

    Conditions for a redirect (ALL must hold):
      1. module_code is in POST_MODULE_NEXT_FEATURE (currently only M15).
      2. The user has not already finished the Epilogue. Without this
         guard, an admin-driven progress reset that re-completes M15
         would route the user through the Epilogue placeholder again
         and would also re-fire the post-Epilogue T2 redirect on every
         pass. The completion row is one-shot.

    No research_consent check here. The Epilogue is open to all users.
    """
    if module_code not in POST_MODULE_NEXT_FEATURE:
        return None

    already_completed = EpilogueCompletion.objects.filter(
        user=user, completed_at__isnull=False,
    ).exists()
    if already_completed:
        return None

    return POST_MODULE_NEXT_FEATURE[module_code]
