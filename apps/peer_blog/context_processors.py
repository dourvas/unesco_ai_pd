"""
Context processor for Practice Workshop nav presence.
Tier 3 Step 3.5 — top-nav dropdown + modules-list badge data.
"""

from .services import get_workshop_active_modules


def workshop_modules(request):
    """Inject workshop_active_modules into all templates."""
    try:
        modules = get_workshop_active_modules()
    except Exception:
        modules = []
    return {
        'workshop_active_modules': modules,
        'workshop_active_module_codes': [m.code for m in modules],
    }
