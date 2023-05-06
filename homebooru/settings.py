"""
Django settings for homebooru project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# This can be rotated but it will invalidate all existing sessions
# See https://stackoverflow.com/a/52509362/8736749

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Handle hosts (this should be done properly in the nginx config)
CSRF_TRUSTED_ORIGINS = CORS_ORIGIN_WHITELIST = [
    # Debug
    'http://localhost', 'https://localhost',
] if DEBUG else [
    # Production
    'http://nginx/*', 'https://nginx/*'
]

ALLOWED_HOSTS = [
    # Debug
    'localhost', '127.0.0.1', '::1',
] if DEBUG else [
    # Production
    'nginx'
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'

CELERY_BEAT_SCHEDULE = {}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Homebooru
    'booru.apps.BooruConfig',
    'booru.management.commands.createsecretkey'
]

# Check if we should create a root user
CREATE_ROOT = os.environ.get('CREATE_ROOT', 'False').lower() == 'true'

# Check if debug is enabled
if DEBUG and CREATE_ROOT:
    # Add the create superuser command
    INSTALLED_APPS += [
        'booru.management.commands.createrootuser'
    ]

# Show static files in debug mode
COLLECT_STATIC = os.environ.get('COLLECT_STATIC', 'False').lower() == 'true'
if DEBUG or COLLECT_STATIC:
    INSTALLED_APPS += [
        'django.contrib.staticfiles'
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'homebooru.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'homebooru.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = Path(os.environ.get('STATIC_ROOT', '/static/'))

if not DEBUG:
    # Pipeline Configuration (Compressing and minifying static files)
    # https://django-pipeline.readthedocs.io/en/latest/

    # Make them visible in the above scope
    # TODO review if this is the best way to do this
    global STATICFILES_STORAGE, STATICFILES_FINDERS, PIPELINE

    # Configure Django with django-pipeline
    STATICFILES_STORAGE = 'pipeline.storage.PipelineManifestStorage'
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',

        # Compressor
        'pipeline.finders.PipelineFinder'
    ]

    INSTALLED_APPS += [
        'pipeline'
    ]

    # Configure Pipeline
    from .pipeline import config as PIPELINE
    PIPELINE['PIPELINE_ENABLED'] = True # (Make sure to only enable in production)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Homebooru settings

BOORU_ANON_COMMENTS = os.environ.get('BOORU_ANON_COMMENTS', 'True').lower() == 'true'
BOORU_STORAGE_PATH = Path(os.environ.get("BOORU_STORAGE_PATH", "data/storage"))
BOORU_ALLOWED_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webm", "mp4", "webp"]
BOORU_VIDEO_FILE_EXTENSIONS = ["webm", "mp4"]
BOORU_STORAGE_URL = '/'
BOORU_STORAGE_SUBFOLDERS = ['media', 'thumbnails', 'samples']
BOORU_UPLOAD_FOLDER = Path('/tmp/uploads')

BOORU_DEFAULT_TAG_TYPE_PK = 'general'
BOORU_DEFAULT_RATING_PK = 'safe'

BOORU_SHOW_FFMPEG_OUTPUT = os.environ.get("BOORU_SHOW_FFMPEG_OUTPUT", 'False').lower() == 'true' and DEBUG

BOORU_POSTS_PER_PAGE         = 45 # How many posts to display in the browse page
BOORU_POOLS_PER_SEARCH_PAGE  = 5 # How many pools to display in the pool search box
BOORU_TAGS_PER_PAGE          = 22 # How many tags to display on the tag search page
BOORU_COMMENTS_PER_PAGE      = 5  # How many comments to display on the post page
BOORU_BROWSE_TAGS_PER_PAGE   = 32 # How many tags to display on the browse page
BOORU_BROWSE_POST_TAGS_DEPTH = 45 # How many posts to enumerate for tags to display on the browse page
BOORU_AUTOCOMPLETE_MAX_TAGS  = 15 # How many tags to display in the autocomplete dropdown
BOORU_POOLS_PER_PAGE         = 25 # How many pools to display on the pool page

BOORU_BROWSE_TAGS_SORT = os.environ.get("BOORU_BROWSE_TAGS_SORT", "total") # How to sort the tags on the browse page
if BOORU_BROWSE_TAGS_SORT not in ["total", "name"]:
    raise ValueError("Invalid BOORU_BROWSE_TAGS_SORT value")

# Fixtures
FIXTURE_DIRS = [
    'booru/fixtures'
]

# Auth
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_ALLOW_INSECURE_PASSWORD = False

# Scanner/Mass Import
SCANNER_USE_DEFAULT_TAGS = True
SCANNER_DEFAULT_TAGS = ['tagme']
SCANNER_STALENESS_THRESHOLD = 30 * 24 * 60 * 60 # 30 days in seconds

# Env variables
DIRECTORY_SCAN_ENABLED = os.environ.get('DIRECTORY_SCAN_ENABLED', 'False').lower() == 'true'
SCANNER_ENABLE_DIR_WATCHER = os.environ.get('SCANNER_ENABLE_DIR_WATCHER', 'False').lower() == 'true'
SCANNER_ENABLE_AUTO_SCAN_ALL = os.environ.get('SCANNER_ENABLE_AUTO_SCAN_ALL', 'False').lower() == 'true'

if DIRECTORY_SCAN_ENABLED:
    INSTALLED_APPS += [
        'scanner.apps.ScannerConfig',
    ]

    if SCANNER_ENABLE_AUTO_SCAN_ALL:
        # Add the scanner to the celery beat schedule
        CELERY_BEAT_SCHEDULE['scan_all'] = {
            'task': 'scanner.tasks.scan_all',
            'schedule': 60 * 5, # Every 5 minutes
        }

    if SCANNER_ENABLE_DIR_WATCHER:
        # Add the watchdog task to the celery beat schedule
        CELERY_BEAT_SCHEDULE['register_all_watchdogs'] = {
            'task': 'scanner.tasks.register_all_watchdogs',
            'schedule': 30, # Every 30 seconds
        }
