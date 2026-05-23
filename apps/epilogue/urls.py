"""URL configuration for the PROODOS Epilogue placeholder app (C.2.5)."""

from django.urls import path

from apps.epilogue import views


app_name = 'epilogue'

urlpatterns = [
    path('',                     views.epilogue_placeholder_view,         name='placeholder'),
    path('dialogue/',            views.epilogue_dialogue_view,            name='dialogue'),
    path('dialogue/advance/',    views.epilogue_dialogue_advance_view,    name='dialogue_advance'),
    path('portrait/',            views.epilogue_portrait_view,            name='portrait'),
    path('portrait/regenerate/', views.epilogue_portrait_regenerate_view, name='portrait_regenerate'),
    path('portrait/accept/',     views.epilogue_portrait_accept_view,     name='portrait_accept'),
    path('portrait/pdf/',        views.epilogue_portrait_pdf_view,        name='portrait_pdf'),
    path('complete/',            views.epilogue_complete_view,            name='complete'),
]
