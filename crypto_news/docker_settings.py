from crypto_news.settings import *
import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME', 'cryptomizrDB'),
        'USER': os.getenv('POSTGRES_USER', 'root'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'changeme'),
        'HOST': os.getenv('POSTGRES_HOST', 'cryptomizr-db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432')
    }
}

ALLOWED_HOSTS = ['*']

# # set proper log levels
# LOGGING['loggers']['agent']['level'] = 'DEBUG'
# LOGGING['loggers']['trading_client']['level'] = 'DEBUG'
