import os.path


## Wepo apps
WEPO_APPS = [
   'core', 'user', 'admin',
]


## Database
DATABASES = {
   'default': {
      'ENGINE':   'django.db.backends.mysql',
      'NAME':     'wepo',
      'USER':     'root',
      'PASSWORD': '112358',
      'HOST':     'localhost', #/opt/dlamp/mysql/tmp/mysql.sock',
      'PORT':     '3306',
   }
}


## Cache
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CACHES = {
   'default' : dict(
      BACKEND = 'johnny.backends.memcached.MemcachedCache',
      LOCATION = ['127.0.0.1:11211'],
      JOHNNY_CACHE = True,
   )
}
JOHNNY_MIDDLEWARE_KEY_PREFIX='wepo'


## Default apps installation path - It must not be changed
APPS_DIR = 'apps'


## Installed apps
INSTALLED_APPS = (
   'django.contrib.sessions',
   'django.contrib.staticfiles',
   'django.contrib.messages',
)
for app in reversed(WEPO_APPS):
   INSTALLED_APPS += ('%s.%s' % (APPS_DIR, app), )


## Template directories
TEMPLATE_DIRS = (
   os.path.join(os.path.dirname(__file__), '../layouts').replace('\\','/'),
)
for app in WEPO_APPS:
   TEMPLATE_DIRS += (os.path.join(os.path.dirname(__file__), '../%s/%s/templates' % (APPS_DIR, app)).replace('\\','/'), )


## Static file directories
STATICFILES_DIRS = (
   os.path.join(os.path.abspath('.'), '%s/static/' % APPS_DIR).replace('\\','/'),
)
for app in WEPO_APPS:
   TEMPLATE_DIRS += (os.path.join(os.path.abspath('.'), '%s/%s/static/' % (APPS_DIR, app)).replace('\\','/'), )