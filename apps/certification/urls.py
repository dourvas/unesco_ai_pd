"""URL routes for the certification app — Phase H.3 part 2."""

from django.urls import path

from apps.certification import views


app_name = 'certification'

urlpatterns = [
    # Authenticated teacher-facing download endpoint.
    path(
        'download/',
        views.certificate_download_view,
        name='download',
    ),
    # Public verification endpoint (no login required).
    # 16-char verification code is high-entropy + not enumerable.
    path(
        'verify/<str:code>/',
        views.certificate_verify_view,
        name='verify',
    ),
]
