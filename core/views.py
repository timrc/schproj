#! /usr/bin/python
#
#  Wepo core views, entry point for any request
#

from core.helper.response_help import HttpResponse, HttpRedirect
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import redirect as page_redirect

from core.models import Seo

from core.ajax import invoke_callback
from core.block import get_block
from core.helper import dict_to_obj

from core.page import prepare_request_url, get_seo, render_page, render_block, update_request_urls

from core.helper.common_help import page_not_found
from core.permission import check_page_permissions


## Web page entry point
#
#  @param request Current request object
#  @param url Request url
#
#  @return rendered page
#
def index(request, url):
   #
   #  prepare url
   #
   prepare_request_url(request, url)
   #
   #  get page
   #
   seo = get_seo(request)

   if not seo:
      seo = get_seo(request, 'error/404')
   else:
      #
      #  properly redirect if url is not active
      #
      if not seo.enabled:
         seo = get_seo(request, 'error/404')

   #
   #  redirect if redirect is set
   #
   if seo.redirect:
      return page_redirect(seo.redirect.url, permanent=True)

   #
   #  update url based on seo
   #
   request.wepo.seo = seo
   update_request_urls(request)

   #
   #  render page
   #
   if seo.page:
      #
      #  Update request status and render the page
      #
      request.wepo.is_page = True
      request.wepo.page = seo.page

      #
      #  Check permissions
      #
      status, action = check_page_permissions(request)
      if not status and action:
         return action

      return render_page(request)

   #
   #  if process callback
   #
   if seo.callback:
      #
      #  update callback status
      #
      request.wepo.is_callback = True
      action = invoke_callback(request)
      if action:
         return action

      return page_not_found(request)

   #
   #  try to render block
   #
   if not seo.page and not seo.callback:
      if seo.url.startswith('/block/'):
         request.wepo.is_block = True
         request.wepo.block = seo.url.replace('/block/', '')

         block_path = request.wepo.block.split('.')
         block_name = block_path[-1]
         block_path = '.'.join(str(b) for b in block_path[:-1])

         html = render_block(dict_to_obj(dict(path=block_path, name=block_name)))

         #
         #  if redirect request
         #
         if type(html) is HttpResponseRedirect or type(html) is HttpResponsePermanentRedirect:
            return html

         #
         #  @TODO support xml
         #
         if request.response_type == 'json':
            from core.helper.response_help import generate_json_response
            return generate_json_response(request, html)
         if request.response_type == 'full':
            from core.helper.response_help import generate_full_block_response
            return generate_full_block_response(request, html)
         else:
            return HttpResponse(request, html)

   return page_not_found(request)


## Wep page part - block
#
#  @param request Current request object
#  @param url Request url
#
#  @return rendered block
#
def block(request, url):
   #
   #  prepare url
   #
   prepare_request_url(request, url)

   #
   #  load block based on url
   #
   request.wepo.block = True
   block_path = '.'.join(request.wepo.url_parts[1:])
   func = get_block(block_path)

   rendered_block = ''
   if func:
      rendered_block = func(request, request.GET.__dict__)

      if type(rendered_block) is Seo:
         return page_redirect(rendered_block.url)
      elif hasattr(rendered_block, '__class__') and rendered_block.__class__ is HttpRedirect:
         return page_redirect(rendered_block.url)

   #
   #  @TODO support xml
   #
   if request.wepo.response_type == 'json':
      from core.helper.response_help import generate_json_response
      return generate_json_response(request, rendered_block)
   if request.wepo.response_type == 'full':
      from core.helper.response_help import generate_full_block_response
      return generate_full_block_response(request, rendered_block)
   else:
      return HttpResponse(request, rendered_block)


## User login
#
#  @param request Current request object
#
#  @return Page after successful login
#
def save_create_object(request):
   #permission = get_permission('administration-access')
   #if permission:
   #   status, redirect = check_permissions(request, [permission])
   #   if not status and redirect:
   #      return redirect

   if not request.method == 'POST':
      return page_not_found(request)

   #
   #  save or create object
   #
   return index(request, '/admin')
