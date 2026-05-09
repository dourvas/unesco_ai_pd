"""
URL Configuration for UNESCO AI Teacher PD Platform
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Admin Interface
    path('admin/', admin.site.urls),
    
    # 2. Users App (Handles Landing, Login, Dashboard, etc.)
    # Note: We keep this at '' because landing_page is our root
    path('', include('apps.users.urls')),
    
    # 3. Modules App
    # We give it a prefix to avoid overlap with the root/landing URLs
    path('modules/', include('apps.modules.urls')),
    path('', include('apps.community.urls')),

    # 4. Practice Workshop (peer_blog) — Phase A Tier 3
    path('blog/', include('apps.peer_blog.urls', namespace='peer_blog')),

]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)