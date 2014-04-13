#! /usr/bin/python
#
#  Wepo core response helper
#

import json

from django.http import HttpResponse as DHttpResponse
from django.utils.html import escape

import wepo.settings as settings
from core.asset import get_assets
from core.helper.common_help import get_host, get_header


## Redirect - basic redirect helper
#
class HttpRedirect:
   def __init__(self, url):
      self.url = url


## Response
#
def Response(request, response):
   #
   # Set Cache-Control max-age
   #
   MAX_AGE = get_header(request, 'CACHE_CONTROL_MAX_AGE', getattr(settings, 'CACHE_CONTROL_MAX_AGE', 120))
   response['Cache-Control'] = 'max-age=%d' % MAX_AGE

   return response


## HttpResponse
#
def HttpResponse(request, content):
   #
   # return HttpRequest
   #
   #from BeautifulSoup import BeautifulSoup
   #beauty = BeautifulSoup(content)
   response = DHttpResponse(content)

   return Response(request, response)


## An Json response wrapper
#
def JsonResponse(request, content):
   #
   # return HttpRequest with content type application/json
   #
   response = DHttpResponse(content, content_type='application/json; charset=utf-8')
   return Response(request, response)


## An Xml response wrapper
#
def XmlResponse(request, content):
   #
   # return HttpRequest with content type application/json
   #
   response = DHttpResponse(content, content_type='text/xml; charset=utf-8')
   return Response(request, response)


## Generate Json response
#  content goes content
#  all assets are listed under assets
#
#  @param request Current request
#  @param content Content to be rendered
#
def generate_json_response(request, content):
   standalone = request.wepo.extra.get('standalone', False)
   if not standalone:
      standalone = request.GET.get('raw', standalone)
      if not standalone:
         standalone = request.POST.get('raw', standalone)

   include_assets = request.wepo.extra.get('include_assets', True)
   include_host = request.wepo.extra.get('include_host', True)
   include_messages = request.wepo.extra.get('include_messages', True)
   content_only = request.wepo.extra.get('content_only', False)

   #
   #  if standalone return content as it is
   #
   result = content if standalone else dict(
      content=escape(content)
   )

   if not content_only and include_assets:
      result['assets'] = request.wepo.assets

   if not content_only and include_host:
      result['host'] = get_host(request)

   return JsonResponse(request, json.dumps(result, default=lambda obj: obj.__dict__))


## Generate Full block response
#  Standalone block
#
#  @param request Current request
#  @param content Content to be rendered
#
def generate_full_block_response(request, content):
   output = []

   output.append(get_assets(request, 'head'))
   #output.append(get_assets(request, 'body'))
   output.append(content)
   output.append(get_assets(request, 'footer'))
   #output.append(get_assets(request, 'last'))

   return HttpResponse(request, escape(u''.join(output)).replace('\n', ''))
