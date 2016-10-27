# -*- encoding: utf-8 -*-
"""
Django settings for xbills2 project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTERNAL_IPS = [
    '127.0.0.1'
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '32$i_g^5!4ms7(c+etxce+rj$k_=n4&m6_%$7%)nw6kjqnri#4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DATABASE_ROUTERS = ['xbills2.dbrouter.MainDBRouter']

# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'config',
    'dv',
    'ipdhcp',
    'debug_toolbar',
    #'djangorpc',
    #'autotranslate',
)
AUTH_USER_MODEL = 'core.Admin'
AUTHENTICATION_BACKENDS = ('core.auth_backend.AuthBackend',)
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'core.middleware.OnlineNowMiddleware',
    'core.middleware.ThreadingDashboardMiddleware',
    #'voip.middleware.ThreadingCallsMiddleware',

]
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default-cache'
    }
}

ROOT_URLCONF = 'xbills2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                #'ws4redis.context_processors.default',
            ],
        },
    },
]

WSGI_APPLICATION = 'xbills2.wsgi.application'

LANGUAGE_CODE = 'en'

ugettext = lambda s: s

LANGUAGES = (
    ('en', ugettext('English')),
    ('uk', ugettext('Ukrainian')),
    ('ru', ugettext('Russian')),
)


TIME_ZONE = 'Europe/Kiev'

DATE_FORMAT = 'Y-m-d'

DATETIME_FORMAT = 'Y-m-d H:s:i'

USE_I18N = True

USE_L10N = False

USE_TZ = False

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
CPU_WARNING_THRESHOLD = 60
CPU_DANGER_THRESHOLD = 80
MEM_WARNING_THRESHOLD = 60
MEM_DANGER_THRESHOLD = 80
SWAP_WARNING_THRESHOLD = 60
SWAP_DANGER_THRESHOLD = 80
UPTIME_FORMAT = '{days} days {hours}:{minutes}:{seconds}'
PAYMENTS_PER_PAGE = 25
FEES_PER_PAGE = 25
USER_ERRORS_PER_PAGE = 25
IPTV_USERS_PER_PAGE = 25
ABILLSIP = '172.16.7.5'
UNIQUE_MAC = True
COMPANY_NAME = 'Xbills'
PROJECT_VERSION = '0.0.8'
SHOW_VERSION = True
# LOGS
#Add logs to Abills history
ABILLS_EMAIL_LOGS = True

STATIC_URL = '/static/'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


SESSION_EXPIRE_AT_BROWSER_CLOSE = True

try:
    from settings_local import *
except ImportError:
    pass