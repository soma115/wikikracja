from os import path
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, "media"),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DEBUG = False
SECRET_KEY = 'Change_This_To_Random_Chars'

ALLOWED_HOSTS = ['*']  # Change_This

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)
ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
    ('pl', ugettext('Polish')),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'zzz.urls'

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
            'debug': DEBUG,
        },
    },
]

INSTALLED_APPS = (
    'channels',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_extensions',
    'crispy_forms',
    'elibrary',
    'obywatele',
    'glosowania',
    'home',
    'chat',
    'bootstrap4'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/glosowania/status/7'  # LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

DATE_FORMAT = "Y-m-d"
INTERNAL_IPS = '127.0.0.1'

EMAIL_HOST = 'example.imap.gmail.com'  # Change_This
EMAIL_PORT = 587  # Change_This
EMAIL_HOST_USER = 'example@gmail.com'  # Change_This
EMAIL_HOST_PASSWORD = 'example'  # Change_This
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'example <example@gmail.com>'  # Change_This
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # This will display the mail on the console for easy verification.

X_FRAME_OPTIONS = 'DENY'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Channels
ASGI_APPLICATION = "zzz.routing.application"
# WSGI_APPLICATION = 'zzz.wsgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://127.0.0.1:6379/4',],  # change 4 to something different in needed
#            "capacity": 1500,  # default 100
#            "expiry": 10,  # default 60
        },
    },
}


# INSTANCE SPECIFIC PARAMETERS

# citizens
# Higher = harder to accept new person. Higher = easier to ban existing person.
# Above ~0.72 SECOND person in group requires 2 points of acceptance which is a paradox.
# Be careful changing this formula - people rarely accept each other.
ACCEPTANCE_MULTIPLIER = 0.72

# voting
WYMAGANYCH_PODPISOW = 2             # Number of signatures needed to approve request for referendum.
CZAS_NA_ZEBRANIE_PODPISOW = 365     # default 365 days
KOLEJKA = 7                         # default 7 days. Discussion before referendum.
CZAS_TRWANIA_REFERENDUM = 7         # default 7 days
VACATIO_LEGIS = 7                   # default 7 days

# chat
ARCHIVE_CHAT_ROOM = 90              # default 90 days
DELETE_CHAT_ROOM = 365              # default 365 days
