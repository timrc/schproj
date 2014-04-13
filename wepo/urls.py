#! /usr/bin/python
#
#  Wepo urls
#

from django.conf.urls import patterns

import wepo.settings as settings
from core.views import index, block

from wepo.settings import WEPO_APPS, APPS_DIR
from core.helper import get_module


## Get app urls
#
#  @param app Application to search in
#
def get_app_urls(app):
   try:
      module_name = '%s.%s' % (app, 'urls')
      module = get_module(module_name)
      if module and hasattr(module, 'urlpatterns'):
         return module.urlpatterns
   except ImportError:
      pass

   return None


## Load url patterns
#
def load_urlpatterns():

   urlpatterns = []
   if settings.DEVELOPMENT:
      urlpatterns += patterns(
         '',
         (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
         (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
      )

   #
   #  auto-discovery app urls
   #
   for app in WEPO_APPS:
      urls = get_app_urls(app)
      if urls:
         urlpatterns += urls

   urlpatterns += patterns(
      '',
      ('^(block/.*)$', block),
      ('^(.*)$', index),
   )

   return urlpatterns

urlpatterns = load_urlpatterns()