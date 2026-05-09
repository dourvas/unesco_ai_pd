from django.urls import path

from . import views

app_name = 'peer_blog'

urlpatterns = [
    path('module/<str:module_code>/', views.blog_index, name='index'),
    path('post/<int:post_id>/', views.blog_post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.submit_comment, name='submit_comment'),
    path('post/<int:post_id>/thumbs-up/', views.toggle_post_thumbs_up, name='post_thumbs_up'),
    path('comment/<int:comment_id>/thumbs-up/', views.toggle_comment_thumbs_up, name='comment_thumbs_up'),
    path('settings/filter-mode/', views.update_filter_mode, name='update_filter_mode'),

    # Phase A Tier 3 Step 3.5 — author self-service
    path('post/<int:post_id>/edit-title/', views.edit_post_title, name='edit_post_title'),
    path('post/<int:post_id>/withdraw/', views.withdraw_post, name='withdraw_post'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Phase A Tier 3 Step 12 — public moderation policy page (no auth)
    path('moderation-policy/', views.moderation_policy, name='moderation_policy'),
]
