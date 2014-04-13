import os.path

## Development environment?
DEVELOPMENT = False
PROJECT_ROOT = os.path.abspath('.')

DEFAULT_CHARSET='utf-8'


## Wepo apps
#  List all installed apps here
WEPO_APPS = []

## Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
    }
}


## Cache
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#   }
#}
#CACHES = {
   #'default' : dict(
   #   BACKEND = 'johnny.backends.memcached.MemcachedCache',
   #   LOCATION = ['127.0.0.1:11211', ],
   #   JOHNNY_CACHE = True,
   #),
   #'default' : dict(
   #   BACKEND = 'johnny.backends.redis.RedisCache',
   #   LOCATION = '127.0.0.1:6379',
   #   JOHNNY_CACHE = True,
   #   OPTIONS = dict(
   #      CLIENT_CLASS = "redis_cache.client.DefaultClient",
   #   )
   #),

   #'default': dict(
   #   BACKEND = 'core.json_cache.MemcachedCacheJSON',
   #   KEY_FUNCTION = lambda key, key_prefix, version: key,
   #   LOCATION = ['127.0.0.1:11211', ],
   #   JOHNNY_CACHE = True,
   #)
#}


## Default apps installation settings, no need to change anything bellow
APPS_DIR = 'apps'


## URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL = '/media/'


## Installed apps
INSTALLED_APPS = (
   'django.contrib.sessions',
   'django.contrib.staticfiles',
   'django.contrib.messages',
)
