"""
Django settings for thief project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import json
with open("config.json", "r") as f:
    config = json.load(f)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.get('DEBUG', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = config.get('ALLOWED_HOSTS', [])


# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'thief.bootstrap3',
    'thief.products',
    'thief.auction',
    'thief.vendors'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'thief.urls'

WSGI_APPLICATION = 'thief.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-tw'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, "thief", "static"), )

STATICFILES_FINDERS = ("django.contrib.staticfiles.finders.FileSystemFinder",
 "django.contrib.staticfiles.finders.AppDirectoriesFinder")

AWS_ACCESS_KEY = config["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = config["AWS_SECRET_KEY"]
AWS_ASSOCITATE_TAG = config["AWS_ASSOCITATE_TAG"]

os.environ['AWS_ACCESS_KEY'] = AWS_ACCESS_KEY
os.environ['AWS_SECRET_KEY'] = AWS_SECRET_KEY
os.environ['AWS_ASSOCITATE_TAG'] = AWS_ASSOCITATE_TAG

RAKUTEN_KEYS = config['RAKUTEN_KEYS']

GOOGLE_CUSTOM_SEARCH_API_KEYS = config["GOOGLE_CUSTOM_SEARCH_API_KEYS"]
