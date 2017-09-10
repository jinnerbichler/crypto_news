from crypto_news.settings import *

DEBUG = True

SCRAPERS['IOTA']['notifiers'] = []
# SCRAPERS['IOTA']['scrapers'] = {}
SCRAPERS['MODUM_IO']['notifiers'] = []
SCRAPERS['MODUM_IO']['scrapers'] = {}
SCRAPERS['HACKED']['notifiers'] = []
SCRAPERS['HACKED']['scrapers'] = {}

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
