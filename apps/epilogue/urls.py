"""URL configuration for the PROODOS Epilogue (post-deprecation).

Phase G closure (2026-05-24) — the Epilogue narrows to:
  - GET  /epilogue/             → Stage 0 Personal Evolution Dashboard
  - POST /epilogue/complete/    → flip completed_at + route to T2 or dashboard

The previously-defined dialogue + portrait routes were deactivated as
part of the Aletheia deprecation. See
`proodos_files/PHASE_G_DIALOGUE_DEPRECATION_20260524.md` §3.2 for the
exact list of removed paths:
  - /epilogue/dialogue/
  - /epilogue/dialogue/advance/
  - /epilogue/portrait/
  - /epilogue/portrait/regenerate/
  - /epilogue/portrait/accept/
  - /epilogue/portrait/pdf/

The route names (`dialogue`, `dialogue_advance`, `portrait`,
`portrait_regenerate`, `portrait_accept`, `portrait_pdf`) are
intentionally NOT redefined — any stale {% url %} reference in a
template, link, or test will raise NoReverseMatch loudly rather than
silently 404, which surfaces the deprecation at first use.
"""

from django.urls import path

from apps.epilogue import views


app_name = 'epilogue'

urlpatterns = [
    path('',          views.epilogue_placeholder_view, name='placeholder'),
    path('complete/', views.epilogue_complete_view,    name='complete'),
]
