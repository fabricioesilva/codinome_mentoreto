"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os
from django.contrib import messages
from celery.schedules import crontab

# Configurando dotenv para Secret-Key segura
path_to_config = find_dotenv(
    filename='config.env', raise_error_if_not_found=True)
load_dotenv(dotenv_path=path_to_config)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv('SECRET_KEY'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'usuarios.apps.UsuariosConfig',
    'politicas.apps.PoliticasConfig',
    'mentorias.apps.MentoriasConfig',
    'estudantes.apps.EstudantesConfig',

    'django_summernote',
    'celery',
    'django_celery_results',
    'chartjs'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.custom_middleware.CustomMiddleware'
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'usuarios.context_processors.custom_site_info',
                'usuarios.context_processors.custom_get_language',
                # 'usuarios.context_processors.check_user_has_email_checked',
                # 'usuarios.context_processors.get_user_new_msgs',
                # 'usuarios.context_processors.check_accepted_policy',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'templates/static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGOUT_URL = 'logout'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'usuarios:index'
LOGIN_REDIRECT_URL = 'usuarios:home_mentor'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]


# Sessão em dias: 60s * 60m * 24h * 1d
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7

# Salvar a cada requisição
SESSION_SAVE_EVERY_REQUEST = False

AUTH_USER_MODEL = 'usuarios.CustomUser'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SUMMERNOTE_THEME = 'bs4'
# Variáveis de trabalho

SITE_NAME = 'Experts Zone'
SITE_CONTACT_EMAIL = 'contato@expertszone.com.br'
SITE_CONTACT_FONE = '32 - 3232-3232'
DOMAIN = '127.0.0.1:8000'
SITE_NAME = 'Experts Zone'
SITE_SLOGAN = 'Conectando mentores e estudantes.'
NO_REPLY = 'noreply@expertszone.com.br'
LOCALHOST_URL = 'http://localhost:8000/'
CONTACTUS_EMAIL = 'contact@epesquisa.com.br'
NOREPLY_EMAIL = 'no-reply@epesquisa.com.br'
PROTOCOLO = 'http'

# Celery Configuration Options
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERY_ENABLE_UTC = False
CELERY_BEAT_SCHEDULE = {
    'envia_aviso_simulado': {
        'task': 'mentorias.tasks.envia_aviso_simulado',
        'schedule': crontab(hour=0),
        'options': {
            'expires': 15.0,
        },
    },
}
DJANGO_CELERY_RESULTS_TASK_ID_MAX_LENGTH = 191
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_EXTENDED = True
# REDIS_URL = os.getenv('REDIS_URL')
# REDIS_HOST = os.getenv('REDIS_HOST')
# REDIS_PORT = os.getenv('REDIS_PORT')
# REDIS_DB = os.getenv('REDIS_DB')


try:
    from core.local_settings import *
except ImportError:
    ...