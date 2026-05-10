"""
URL configuration for the AILST instrument app.

Three routes, all parameterised by timepoint (T0 / T1 / T2). T0 is
reachable from the onboarding Summary POST (C.2.3). T1 and T2 routes
exist now but only become reachable once C.2.4 wires post-M5 and
post-M15 redirects.
"""

from django.urls import path

from apps.ailst import views


app_name = 'ailst'

urlpatterns = [
    path('<str:timepoint>/',                 views.ailst_entry_view,    name='entry'),
    path('<str:timepoint>/page/<int:page>/', views.ailst_page_view,     name='page'),
    path('<str:timepoint>/complete/',        views.ailst_complete_view, name='complete'),
    path(
        '<str:timepoint>/research-consent-required/',
        views.ailst_research_consent_required_view,
        name='research_consent_required',
    ),
    path('<str:timepoint>/restart/', views.ailst_restart_view, name='restart'),
]
