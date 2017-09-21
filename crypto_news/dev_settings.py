from crypto_news.settings import *

DEBUG = True

SCRAPERS = {
    'IOTA': {
        'scrapers': {
            'twitter': {
                'users': ['@iotatoken', '@tangleblog', '@DomSchiener ', '@DavidSonstebo'],
                'hashtags': ['#iotatoken', '#iota'],
                'exclude_users': ['@coinstats', '@analysisinchain',
                                  '@iota_market', '@dx_alert'],
                'hotness_notifiers': ['important_news'],
            }
        },
        'notifiers': []
    }
}

# set all slack notifies to dev channel
for notifier in [n for n in NOTIFIERS.values() if n['type'] == 'slack']:
    notifier['channel'] = '#dev_dummy'

# concurrent access is not possible with SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME', 'cryptonewsDB'),
        'USER': os.getenv('POSTGRES_USER', 'root'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'changeme'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432')
    }
}
