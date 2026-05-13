"""
Django settings for config project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-sx*zgjka*(ev+pi)qw)rj*vz%+z9ex!*6y4j7ope^5icxfp4#u'

DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Internal Apps
    'apps.users',
    'apps.modules',
    'apps.core',
    'apps.community',
    'apps.peer_blog',
    # Phase C — EU AI Act + AILST baseline (2026-05)
    'apps.compliance',
    'apps.ailst',
    # Phase C C.2.5 — PROODOS Epilogue stub (2026-05)
    'apps.epilogue',
    # Phase E commit 1 — agent layer (BaseAIAgent + RAGFeedbackAgent live
    # alongside rag_query_system.py; monolith still serves traffic).
    'apps.agents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Phase C C.2.0 — EU AI Act Article 50(1) acknowledgment gate.
    # Slot intentionally between AuthenticationMiddleware (needs request.user)
    # and MessageMiddleware (so redirect doesn't lose pending messages).
    'apps.compliance.middleware.AIDisclosureMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Phase A Tier 3 Step 3.5
                'apps.peer_blog.context_processors.workshop_modules',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unesco_ai_teacher_pd',
        'USER': 'postgres',
        'PASSWORD': 'Django123!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'apps' / 'users' / 'static',
    BASE_DIR / 'static',
]

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model (Προετοιμασία για το επόμενο βήμα)
# AUTH_USER_MODEL = 'users.User' # Θα το ενεργοποιήσουμε μόλις φτιάξουμε το μοντέλο
# settings.py

# Tell Django where your login page is
LOGIN_URL = 'users:login'

# Where to redirect after login
LOGIN_REDIRECT_URL = 'users:dashboard'

# Where to redirect after logout
LOGOUT_REDIRECT_URL = 'users:landing'

# ============================================================
# Phase A Tier 2 Step 4 — M13 Repository Submission CTA
# ============================================================
# External URL to the open community-maintained workflows repo.
# Override via env var GITHUB_WORKFLOWS_URL if needed.
import os as _os
GITHUB_WORKFLOWS_URL = _os.environ.get(
    'GITHUB_WORKFLOWS_URL',
    'https://github.com/dourvas/proodos-eduai-teacher-workflows',
)

# ============================================================
# Phase C M4 — AILST instrument version pin
# ============================================================
# Version of AILST items served to NEW T0 administrations. In-progress
# AilstResponse rows preserve their own instrument_version (implicit pin
# via AilstResponse.instrument_version). When transitioning to v2 in
# the future, change this setting; existing in-progress users continue
# with v1 until they complete T0/T1/T2.
AILST_CURRENT_VERSION = 'ning_2025_v1'

# ============================================================
# Phase C C.2.0 — AI Disclosure version pin
# ============================================================
# Version of the AI Disclosure consent text served to NEW users on the
# Step 0 modal. Existing ConsentRecord rows preserve their own version;
# this setting only controls what new acknowledgments record. After
# IRB review, mint 'v2_irb_revised' (or similar) in
# apps/compliance/copy.py and update this value to match.
AI_DISCLOSURE_CURRENT_VERSION = 'v1_pre_irb'

# ============================================================
# Phase C C.1 — AI Impact Assessment (Article 50 transparency) version
# ============================================================
# The participant-facing transparency document rendered at
# /about/ai-act-compliance/. Versioned in lockstep with the AI
# Disclosure consent so that IRB review touches both together.
AI_IMPACT_ASSESSMENT_CURRENT_VERSION = 'v1_pre_irb'

# ============================================================
# Phase E commit 1 — agent audit logger
# ============================================================
# Structured JSON records for every agent.generate.* event and every
# agent.cost record. Goes to stdout in DEBUG so `manage.py runserver`
# shows it inline; in production this can be redirected to a file by
# wrapping the gunicorn/uwsgi process. The formatter emits one-line
# JSON for downstream analysis pipelines (dissertation telemetry).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'agents_json': {
            '()': 'apps.agents.shared.audit.JSONFormatter',
        },
    },
    'handlers': {
        'agents_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'agents_json',
        },
    },
    'loggers': {
        'agents.audit': {
            'handlers': ['agents_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================
# Phase C C.2.2 — Step 3 research consent version pin
# ============================================================
# Single setting for BOTH research_participation and data_sharing texts
# because IHU IRB reviews them together as a combined consent package.
# After IRB feedback, mint 'v2_irb_revised' in apps/compliance/copy.py
# and update this value. record_consent's supersede pattern revokes
# old-version active rows when a user re-consents under the new version.
RESEARCH_CONSENT_CURRENT_VERSION = 'v1_pre_irb'

