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

# TODO change these to your own domain
ALLOWED_HOSTS = [
    '*'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost'
]


CORS_ORIGIN_WHITELIST = [
    'http://localhost'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Homebooru
    'booru.apps.BooruConfig',
    'booru.management.commands.createsecretkey',
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

# Pipeline Configuration (Compressing and minifying static files)
# https://django-pipeline.readthedocs.io/en/latest/

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
PIPELINE['PIPELINE_ENABLED'] = not DEBUG # (Make sure to only enable in production)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Homebooru settings

BOORU_STORAGE_PATH = Path(os.environ.get("BOORU_STORAGE_PATH", "data/storage"))
BOORU_ALLOWED_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webm", "mp4", "webp"]
BOORU_VIDEO_FILE_EXTENSIONS = ["webm", "mp4"]
BOORU_STORAGE_URL = '/'
BOORU_STORAGE_SUBFOLDERS = ['media', 'thumbnails', 'samples']
BOORU_UPLOAD_FOLDER = Path('/tmp/uploads')

BOORU_DEFAULT_TAG_TYPE_PK = 'general'
BOORU_DEFAULT_RATING_PK = 'safe'

BOORU_SHOW_FFMPEG_OUTPUT = os.environ.get("BOORU_SHOW_FFMPEG_OUTPUT", 'False').lower() == 'true' and DEBUG

BOORU_POSTS_PER_PAGE = 20   # How many posts to display in the browse page
BOORU_TAGS_PER_PAGE  = 22   # How many tags to display on the tag search page

# Fixtures
FIXTURE_DIRS = [
    'booru/fixtures'
]

# Auth
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_ALLOW_INSECURE_PASSWORD = False