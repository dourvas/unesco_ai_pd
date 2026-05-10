"""
AI Disclosure middleware — enforce EU AI Act Article 50(1) acknowledgment.

Every authenticated user must have a non-null
TeacherProfile.ai_disclosure_acknowledged_at before accessing any
authenticated route. Unacknowledged users are redirected to the
disclosure modal (or, for AJAX/JSON requests, returned a 403 with a
machine-readable JSON body).

Bypass set is conservative: disclosure URL itself, logout, static/media
assets, public information pages, anon-only auth flows, and health-check
endpoints. Health-check paths are bypassed defensively even before such
endpoints exist, so deployment monitoring keeps working when added.

State machine per request:
  1. Anonymous user                              → pass-through
  2. Request path in BYPASS_PATHS                → pass-through
  3. Request path starts with BYPASS_PREFIXES    → pass-through
  4. User has profile.ai_disclosure_acknowledged_at IS NOT NULL → pass-through
  5. Else: AJAX → 403 JSON; non-AJAX → 302 to /onboarding/ai-disclosure/?next=<path>

Edge case: a freshly-registered user with no TeacherProfile row at all
is treated as not-acknowledged (rule 4 fails) and gets redirected. The
disclosure view get_or_creates the profile on POST, so the next request
passes through.
"""

from django.http import JsonResponse
from django.shortcuts import redirect


# Exact-match bypass paths (request.path == X)
BYPASS_PATHS = frozenset({
    '/onboarding/ai-disclosure/',           # the modal itself
    '/logout/',                             # users:logout (allow exit)
    '/users/logout/',                       # safety alias if reverse changes
    '/login/',                              # users:login (anon route)
    '/register/',                           # users:register (anon route)
    '/',                                    # users:landing (public)
    '/admin/login/',
    '/admin/logout/',
    '/about/ai-act-compliance/',            # "Learn more" stub (C.1 final later)
    '/privacy-policy/',                     # public, when implemented
    '/terms/',                              # public, when implemented
    '/health/',                             # ops monitoring (when added)
    '/healthz/',
    '/_status/',
})

# Prefix bypass (request.path.startswith(X))
BYPASS_PREFIXES = (
    '/static/',
    '/media/',
)


def _is_ajax(request):
    """Detect AJAX/JSON request to choose response format.

    Returns True if X-Requested-With is XMLHttpRequest, or if the Accept
    header explicitly prefers JSON over HTML. False otherwise (default
    to HTML/redirect path for ordinary browser navigation).
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept', '')
    if 'application/json' in accept and 'text/html' not in accept:
        return True
    return False


class AIDisclosureMiddleware:
    """Redirect authenticated users to AI Disclosure modal until acknowledged."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._needs_disclosure(request):
            return self._block_response(request)
        return self.get_response(request)

    def _needs_disclosure(self, request):
        if not request.user.is_authenticated:
            return False
        path = request.path
        if path in BYPASS_PATHS:
            return False
        if any(path.startswith(p) for p in BYPASS_PREFIXES):
            return False
        # Authenticated, non-bypass: check acknowledgment via profile.
        try:
            ack_at = request.user.teacher_profile.ai_disclosure_acknowledged_at
        except Exception:
            # No teacher_profile yet (just-registered user) → must acknowledge.
            return True
        return ack_at is None

    def _block_response(self, request):
        if _is_ajax(request):
            return JsonResponse(
                {
                    'error': 'ai_disclosure_required',
                    'redirect_url': '/onboarding/ai-disclosure/',
                },
                status=403,
            )
        original_path = request.get_full_path()
        return redirect(f'/onboarding/ai-disclosure/?next={original_path}')
