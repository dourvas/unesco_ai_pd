"""
Service helpers for the apps.modules app.

Phase C C.6 (pre-pilot hardening): get_module_prerequisite_block —
sequential progression gate enforcement. Per the research design, an
educator must complete M_(n-1) before opening M_n; otherwise the AILST
T1 measurement after M5 is contaminated (it would no longer capture
attitudes after the Acquire phase but rather attitudes after an
arbitrary jump in content). Same logic for T2 via the Epilogue.

The helper derives prerequisites from Module.order_index, not from the
existing Module.prerequisites JSONField (which is stored but not
consulted at runtime). Linear order_index matches the UNESCO 15-module
progression and avoids stale prerequisite metadata drift.
"""

from typing import Optional


def get_module_prerequisite_block(user, module) -> Optional['object']:
    """Return the first prior Module the user has not yet completed, or
    None if the user is cleared to open `module`.

    Behaviour:
      - For module with order_index == 1: always returns None (no
        prerequisites).
      - For module with order_index > 1: iterates published modules
        with smaller order_index in ascending order; returns the first
        one whose UserModuleProgress for this user does NOT have
        completed_at set (either no progress row, or row with
        completed_at NULL).

    Returns:
        Module instance to block on, or None if the path is clear.
    """
    from apps.modules.models import Module, UserModuleProgress

    if module.order_index <= 1:
        return None

    earlier_modules = (
        Module.objects
        .filter(order_index__lt=module.order_index, is_published=True)
        .order_by('order_index')
    )
    completed_ids = set(
        UserModuleProgress.objects
        .filter(user=user, completed_at__isnull=False)
        .values_list('module_id', flat=True)
    )
    for prior in earlier_modules:
        if prior.id not in completed_ids:
            return prior
    return None


def user_has_completed_module(user, module_code: str) -> bool:
    """Quick boolean: does the user have a UserModuleProgress row for
    `module_code` with completed_at set? Used by the Epilogue gate to
    enforce M15 completion before /epilogue/ is reachable (TD-013).
    """
    from apps.modules.models import Module, UserModuleProgress

    try:
        module = Module.objects.get(code=module_code)
    except Module.DoesNotExist:
        return False
    return UserModuleProgress.objects.filter(
        user=user, module=module, completed_at__isnull=False,
    ).exists()
