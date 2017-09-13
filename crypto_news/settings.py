"""
Django settings for crypto_news project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '79%pozs8r1v)08t5g7obc#d8!z#=kmotzocyg8ssy(820j7ilv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'news_scraper',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'crypto_news.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'crypto_news.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        },
        'news_scraper': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False

        },
        'datefinder': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        },
        'requests': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False

        },
        'oauthlib': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        },
        'requests_oauthlib': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        },
        'scrapy': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        },
        'tweepy': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False

        }
    }
}

# Scrapy settings
CRAWLER_DEFAULTS = {
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'TELNETCONSOLE_ENABLED': False,
    'LOG_ENABLED': False,
    'LOG_FORMATTER': 'news_scraper.scraper.pipelines.PoliteLogFormatter',
    'DOWNLOAD_DELAY': 0.25,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    }
}

# Stanford CoreNLP settings
CORENLP_ENDPOINT = 'http://localhost:9000'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

NOTIFIERS = {
    'iota_slack': {
        'type': 'slack',
        'url': os.getenv('IOTA_SLACK_WEBHOOK_URL')
    },
    'modum_io_slack': {
        'type': 'slack',
        'url': os.getenv('MODUM_SLACK_WEBHOOK_URL')
    },
    'date_found': {
        'type': 'slack',
        'url': os.getenv('DATE_FOUND_WEBHOOK_URL')
    }
}

# Scraper definitions
SCRAPERS = {
    'IOTA': {
        'scrapers': {
            'twitter': {
                'users': ['@iotatoken', '@tangleblog', '@DomSchiener ', '@DavidSonstebo'],
                'hashtags': ['#iotatoken', '#iota'],
                'exclude_users': ['@coinstats', '@analysisinchain',
                                  '@iota_market', '@dx_alert']
            }
        },
        'notifiers': ['iota_slack']
    },
    'MODUM_IO': {
        'scrapers': {
            'twitter': {
                'users': ['@modum_io'],
                'hashtags': ['#modum'],
                'exclude_users': []
            }
        },
        'notifiers': ['modum_io_slack']
    },
    'HACKED': {
        'scrapers': {
            'hacked': {}
        },
        'notifiers': []
    }
}

TWITTER_FOLLOWERS_THRESH = 500
TWITTER_UPDATE_INTERVAL = 30  # in minutes

# Twitter authentication
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
