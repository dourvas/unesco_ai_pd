# apps/users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 1. Public Landing Page (http://localhost:8000/)
    path('', views.landing_page, name='landing'),
    
    # 2. Authenticated Dashboard (http://localhost:8000/dashboard/)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 3. Authentication System
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 4. Onboarding Flow
    path('onboarding/welcome/', views.onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/skip/', views.onboarding_skip, name='onboarding_skip'),
    path('onboarding/step1/', views.onboarding_step1, name='onboarding_step1'),
    path('onboarding/step2/', views.onboarding_step2, name='onboarding_step2'),
    path('onboarding/step3/', views.onboarding_step3, name='onboarding_step3'),
    path('onboarding/summary/', views.onboarding_summary, name='onboarding_summary'),
    path('onboarding/confirm/', views.onboarding_confirm, name='onboarding_confirm'),
    
    # 5. Profile Management
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]