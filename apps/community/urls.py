"""
apps/community/urls.py
======================
URL configuration for the Community (Forum) app.

URL Map:
    /community/                         → community_home (all threads)
    /community/M1/                      → thread_detail (full forum for module)
    /community/M1/post/                 → post_create (AJAX)
    /community/M1/preview/              → forum_preview (AJAX partial for tab triggers)
    /community/post/<id>/reply/         → post_reply (AJAX)
    /community/post/<id>/vote/          → post_helpful_vote (AJAX toggle)
"""

from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Community home - all modules
    path('community/', views.community_home, name='home'),

    # Full thread page per module
    path('community/<str:module_code>/', views.thread_detail, name='thread_detail'),

    # Create top-level post (AJAX)
    path('community/<str:module_code>/post/', views.post_create, name='post_create'),

    # Inline preview partial (AJAX - for tab triggers)
    path('community/<str:module_code>/preview/', views.forum_preview, name='forum_preview'),

    path('community/<str:module_code>/thread-info/', views.thread_info, name='thread_info'),

    # Reply to a post (AJAX)
    path('community/post/<int:post_id>/reply/', views.post_reply, name='post_reply'),

    # Toggle helpful vote (AJAX)
    path('community/post/<int:post_id>/vote/', views.post_helpful_vote, name='post_helpful_vote'),
]
