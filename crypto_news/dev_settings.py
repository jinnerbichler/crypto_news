from crypto_news.settings import *

DEBUG = True

SCRAPERS = {
    'IOTA': {
        'scrapers': {
            'reddit': {
                'subreddits': ['Iota'],
                'notifiers': ['important_news'],
                'update_interval': 30
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
