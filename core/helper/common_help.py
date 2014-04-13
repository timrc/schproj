# -*- coding: utf-8 -*-
#! /usr/bin/python
#
#  Core common classes and functions helpers
#

import sys
import re
import hashlib
import urllib

from django.shortcuts import redirect


## Returns current pagination page
#
#  @param request Current request
#  @param key Key to get from request
#  @param default Default value if key not found
#
#  @return int value of the key
#
def get_int_request(request, key, default=0):
   if key in request.GET:
      return int(request.GET[key])

   return default


## Generate valid cache key with : for seperator
#  removes all non word|numbers character
#
#  @param args Tuple or list of arguments or string
#
#
#  @return: valid cache_key
#
def get_cache_key(*args):
   if args is None:
      return False

   if type(args) is tuple or type(args) is list:
      return (':'.join(re.sub(r'[^\w\d]', ':', str(part)).strip(':') for part in args).strip(':')).lower()

   return (re.sub(r'[^\w\d]', '', args).strip(':')).lower()


def replace_cache_key_chars(key):
   try:
      return key.encode('utf-8').lower().replace('ü', 'u').replace('ć', 'c').replace('č', 'c').replace('Č', 'C').replace('š', 's').replace('Š', 'S').replace('ž', 'z').replace('Ž', 'Z').replace(' ', '-')
   except UnicodeEncodeError:
      return key
   except UnicodeDecodeError:
      return key.lower().replace('ü', 'u').replace('ć', 'c').replace('č', 'c').replace('Č', 'C').replace('š', 's').replace('Š', 'S').replace('ž', 'z').replace('Ž', 'Z').replace(' ', '-')


## Generate valid cache key with - for seperator
#  removes all non word|numbers character
#
#  @param args Tuple or list of arguments or string
#
#
#  @return: valid cache_key
#
def get_cache_key_2(*args):
   if args is None:
      return False

   if type(args) is tuple or type(args) is list:
      return ('-'.join(re.sub(r'[^\w\d]', '-', replace_cache_key_chars(part)).strip('-') for part in args).strip('-')).replace('--', '-').replace('--', '-').lower()

   return (re.sub(r'[^\w\d]', '', replace_cache_key_chars(args)).strip('-')).replace('--', '-').replace('--', '-').lower()


## Generate valid seo url
#  removes all non word|numbers character
#
#  @param args Tuple or list of arguments or string
#
#  @return: valid seo link
#
def get_seo_link(*args):
   if args is None:
      return False

   if type(args) is tuple or type(args) is list:
      return ('/'.join(re.sub(r'[^\w\d/\.]', '-', str(part)).strip('-') for part in args)).replace('--', '-').replace('--', '-').strip('-').replace('-/', '/').lower()

   return (re.sub(r'[^\w\d/\.]', '', args)).replace('--', '-').replace('--', '-').strip('-').replace('-/', '/').lower()



## Hash string input
#
#  @param string String to encode/hash
#
def hash_it(string):
   return hashlib.sha224(string).hexdigest()


## Get HTTP Referer
#
#  @param request Current request object
#
def get_referer(request):
   if 'HTTP_X_REFERER' in request.META:
      return request.META.get('HTTP_X_REFERER', '/')
   else:
      return request.META.get('HTTP_REFERER', '/')


## Get error page url
#
#  @param error_type Type of the error (404, 403, 500, ...)
#
#  @return url of given error type
#
def get_error_page_url(error_type):
   return '/error/%s' % error_type


## Page not found
#
#  if request is invalid (nonexistent url, etc...) return 404 error
#
#  @param request Current request object
#
#  @return 404 error page or redirect user to 404 error page
#
def page_not_found(request):
   if request.wepo.url.endswith('404'):
      from core.helper.response_help import HttpResponse
      return HttpResponse(request, 'Error 404')

   return redirect(get_error_page_url('404'))


## Page no permission
#
#  if without permission to see the page
#
#  @param request Current request object
#
#  @return 403 forbidden page or redirect user to 404 error page
#
def page_no_permission(request):
   if request.url.endswith('403'):
      from core.helper.response_help import HttpResponse
      return HttpResponse(request, 'Error 403')

   return redirect(get_error_page_url('403'))


## Generate host + port from request
#
#  @param request Current request
#
#  @return Returns generated host + port from request
#
def get_host(request):
   server_settings = dict(name='127.0.0.1', port=80, protocol='http')

   import wepo.settings as wepo_settings
   if hasattr(wepo_settings, 'SERVER'):
      server_settings.update(wepo_settings.SERVER)
   else:
      server_settings['name'] = request.META.get('SERVER_NAME', server_settings['name'])
      server_settings['port'] = int(request.META.get('SERVER_PORT', server_settings['port']))

   server = ''
   if server_settings['protocol'] != 'http':
      server = '%s:' % server_settings['protocol']
   server = '%s//%s' % (server, server_settings['name'])
   if server_settings['port'] != 80:
      server = '%s:%s' % (server, server_settings['port'])

   return server


## Set custom header
#
#  @param request Current request
#  @param key Key name of property
#  @param value Value of property
#
def set_header(request, key, value):
   request.wepo.header[key] = value


## Get from custom header
#
#  @param request Current request
#  @param key Key name of property
#  @param default Default value to return
#
#  @return Returns custom header property
#
def get_header(request, key, default):
   if key in request.wepo.header:
      return request.wepo.header[key]

   return default


## Redirect user to login page
#
#  @param request Current request
#  @param url URL to redirect user
#
#  @return redirect object
#
def redirect_to_login(request, url=None):
   if not url:
      from core.models import Seo
      url_seo = Seo.objects.filter(url='/user/login')
      if url_seo:
         url = url
      else:
         url = '/'

   response = redirect(url)
   response['Location'] += ('?destination=%s' % urllib.quote(request.wepo.url.encode('utf8'), ''))

   return response