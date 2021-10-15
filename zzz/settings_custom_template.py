# INSTANCE SPECIFIC PARAMETERS

ALLOWED_HOSTS = ['domain.com']

DEBUG = False
SECRET_KEY = 'your_secret_key'

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'
ugettext = lambda s: s
LANGUAGES = (
    # Turn on more than one only for multi language sites. Normaly use just one
    ('en', ugettext('English')),
    ('pl', ugettext('Polish')),
)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [ 'redis://127.0.0.1:6379/1', ],
        },
    },
}

EMAIL_HOST = 'imap.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'login@gmail.com'
EMAIL_HOST_PASSWORD = 'secret_password'
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'your_page.com <login@gmail.com>'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# This will display the mail on the console for Easy Verification:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# citizens
ACCEPTANCE_MULTIPLIER = 2.164

# voting
WYMAGANYCH_PODPISOW = 2             # Number of signatures needed to approve request for referendum.
CZAS_NA_ZEBRANIE_PODPISOW = 365     # default 365 days
KOLEJKA = 7                         # default 7 days. Discussion before referendum.
CZAS_TRWANIA_REFERENDUM = 7         # default 7 days
VACATIO_LEGIS = 7                   # default 7 days

# chat
ARCHIVE_CHAT_ROOM = 90              # default 90 days
DELETE_CHAT_ROOM = 365              # default 365 days
SLOW_MODE = {
    "room name or *": 10            # delay between messages in seconds
}
UPLOAD_IMAGE_MAX_SIZE_MB = 10       # max size of uploaded image, MB
