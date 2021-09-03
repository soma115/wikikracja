# INSTANCE SPECIFIC PARAMETERS

ALLOWED_HOSTS = ['your_domain.com', '*']

DEBUG = True
SECRET_KEY = 'your_secret_alphanumeric_key'

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [ 'redis://127.0.0.1:6379/1', ],
        },
    },
}

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

