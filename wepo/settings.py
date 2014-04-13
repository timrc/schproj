#! /usr/bin/python
#
#  Portal settings
#

import os.path

PROJECT_ROOT = os.path.abspath('.')

## Wepo apps
#  List all installed apps here
WEPO_APPS = []

## Debug settings
DEBUG = True
DEVELOPMENT = False
TEMPLATE_DEBUG = DEBUG


## Default Admins - Not in used
ADMINS = (
   # ('Tim Rijavec', 'tim@coder.si'),
)
MANAGERS = ADMINS


## Database default settings; may be overriden in settings_local.py
#  ENGINE:   Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#  NAME:     Or path to database file if using sqlite3.
#  USER:     Not used with sqlite3.
#  PASSWORD: Not used with sqlite3.
#  HOST:     Set to empty string for localhost. Not used with sqlite3.
#  PORT:     Set to empty string for default. Not used with sqlite3.
DATABASES = {
   'default': {
      'ENGINE':   'django.db.backends.mysql',
      'NAME':     'wepo',
      'USER':     'root',
      'PASSWORD': '',
      'HOST':     '/opt/dlamp/mysql/tmp/mysql.sock',
      'PORT':     '3306',
   }
}

## Local time zone for this installation. Choices can be found here:
#  http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
#  although not all choices may be available on all operating systems.
#  In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Ljubljana'


## Language code for this installation. All choices can be found here:
#  http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'


## Default uploaded image scales
#
DEFAULT_IMAGE_SCALES = [
   dict(name='Thumbnail square', prefix='tmbs', width=100, height=100, crop=True),
   dict(name='Thumbnail rectangle', prefix='tmbr', width=100, height=60, crop=True),
   dict(name='Preview small', prefix='prws', width=400, height=210, scale_to_fit=True),
   dict(name='Preview big', prefix='prwb', width=850, height=470, scale_to_fit=True),
]


## Default language - Not in use
DEFAULT_LANGUAGE = 'en'


## Site id - Not in use
SITE_ID = 1


## If you set this to False, Django will make some optimizations so as not
#  to load the internationalization machinery.
USE_I18N = True


## If you set this to False, Django will not format dates, numbers and
#  calendars according to the current locale.
USE_L10N = True


## If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False


## Absolute filesystem path to the directory that will hold user-uploaded files.
#  Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(os.path.abspath('.'), 'upload/').replace('\\','/')


## URL that handles the media served from MEDIA_ROOT. Make sure to use a
#  trailing slash.
#  Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/upload/'


## Absolute path to the directory static files should be collected to.
#  Don't put anything in this directory yourself; store your static files
#  in apps' "static/" subdirectories and in STATICFILES_DIRS.
#  Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.abspath('.'), 'assets/').replace('\\','/')


## URL prefix for static files.
#  Example: "http://media.lawrence.com/static/"
STATIC_URL = '/assets/'


## Additional locations of static file
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = ()


## List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = (
   'django.contrib.staticfiles.finders.FileSystemFinder',
   'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

## Cache in use
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

CACHES = {
   'default' : dict(
      BACKEND = 'johnny.backends.memcached.MemcachedCache',
      LOCATION = ['127.0.0.1:11211', ],
      JOHNNY_CACHE = True,
   ),
}


JOHNNY_MIDDLEWARE_KEY_PREFIX='wepo'


## Session manager
SESSION_CACHE_ALIAS = 'memcached'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


## Make this unique, and don't share it with anybody.
SECRET_KEY = '-4igw#l4%nlkoab1#d&amp;1a$_@ksk8e70a%*m6re+uu@-(7u%t72'


## List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
   'django.template.loaders.filesystem.Loader',
   'django.template.loaders.app_directories.Loader',
)


## Installed middleware from contrib or others
MIDDLEWARE_CLASSES = (
   'django.middleware.common.CommonMiddleware',
   'django.contrib.sessions.middleware.SessionMiddleware',
   'django.contrib.messages.middleware.MessageMiddleware',

   'core.middleware.GlobalRequest',

   'johnny.middleware.LocalStoreClearMiddleware',
   'johnny.middleware.QueryCacheMiddleware',
)


## Default apps dir - Do not change this, it's a static location of installed applications
APPS_DIR = 'apps'


## Path to the root url config
ROOT_URLCONF = 'wepo.urls'


## Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wepo.wsgi.application'


## Hook directory - No in use
#  @TODO - Remove 'hook' directory variable after...
HOOK_DIR = os.path.join(os.path.abspath('.'), 'overrides').replace('\\','/')


## Where the templates are located - Not in use
#  Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
#  Always use forward slashes, even on Windows.
#  Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
   os.path.join(os.path.dirname(__file__), '../layouts').replace('\\','/'),
)


## Fixture directory for installing basic data into database - Not in use
FIXTURE_DIRS = ()


## List of installed applications
INSTALLED_APPS = (
   'django.contrib.sessions',
   'django.contrib.staticfiles',
   'django.contrib.messages',
)


## A sample logging configuration. The only tangible logging
#  performed by this configuration is to send an email to
#  the site admins on every HTTP 500 error when DEBUG=False.
#  See http://docs.djangoproject.com/en/dev/topics/logging for
#  more details on how to customize your logging configuration.
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

## Customized local configuration.
#  !!! put all customized settings into the file bellow
#  !!! Copy whole variable you want to change, do not change only some parts
from wepo.settings_local import *

INSTALLED_APPS += ('core', )
for app in reversed(WEPO_APPS):
   INSTALLED_APPS += ('%s.%s' % (APPS_DIR, app), )

## Template directories
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '../core/templates').replace('\\', '/'), )
for app in WEPO_APPS:
   TEMPLATE_DIRS += (os.path.join(os.path.dirname(__file__), '../%s/%s/templates' % (APPS_DIR, app)).replace('\\', '/'), )

## Static file directories
STATICFILES_DIRS = (os.path.join(os.path.abspath('.'), 'core/static/').replace('\\', '/'), )
for app in WEPO_APPS:
   STATICFILES_DIRS += (os.path.join(os.path.abspath('.'), '%s/%s/static/' % (APPS_DIR, app)).replace('\\', '/'), )
