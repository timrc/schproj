#! /usr/bin/python
#
#  Wepo core page manager, main intro for page request
#

import re, os
import json

from core import cache
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import redirect as page_redirect

from helper import dict_to_obj, add_dict_to_object, build_url, get_page_sections
from helper.response_help import HttpResponse, HttpRedirect

from block import get_page_blocks, render_block
from asset import add_asset, get_assets, get_assets_config, get_assets_list
from models import Seo


## Get url parts from url
#
#  @param url Url
#
def get_url_parts(url):
   url = '/%s' % url
   url = url.replace('.html', '')
   url_regex = '(/([\w\d\-.]*))'
   url_parts = re.findall(url_regex, url)
   url_parts = [part[1] for part in url_parts if part[1] != '']

   return url, url_parts


## prepare request for the page
#
#  @param request Current request object
#  @param url Url of the request
#
def prepare_request_url(request, url):
   #
   #  prepare url
   #
   url, url_parts = get_url_parts(url)

   #
   #  basic assets locations with basic groups
   #     @TODO - enable group expansion
   #
   assets = {
      'head':     {'script': [], 'style': [], 'meta': []},
      'body':     {'script': [], 'style': [], 'meta': []},
      'footer':   {'script': [], 'style': [], 'meta': []},
      'last':     {'script': [], 'style': [], 'meta': []},
      'md5':      []
   }

   #
   #  basic message types
   #
   messages = {'success': [], 'info': [], 'warning': [], 'error': []}

   #
   #  get explicit response type
   #     wr - wepo response; default to http
   #
   response_type = 'http'
   request_method = request.method
   if request_method == 'PUT':
      response_type = getattr(request, 'GET').get('wr', 'http')
   else:
      response_type = getattr(request, request_method).get('wr', 'http')

   #
   #  add setting to request
   #
   page_settings = {
      'page_title': '',
      'url': url,
      'url_parts': url_parts,
      'body_class': '',
      'query': request.META.get('QUERY_STRING', ''),
      'assets': assets,
      'messages': messages,
      'response_type': response_type,
      'header': {},
      'extra': {},
      'lang': None,
      'seo': None,
      'page': None,
      'block': None,
      'instance': None,
      'is_page': False,
      'is_block': False,
      'is_callback': False
   }

   add_dict_to_object(request, {'wepo': dict_to_obj(page_settings)})

   from core import wepo_assets
   add_asset(request, type='script', code=wepo_assets.script.wepo, position='head')


## Get seo
#
#  load seo object of requested page from cache or db
#
#  @param request Current request object
#
#  @return seo object
#
def get_seo(request, url=None):
   url_parts = request.wepo.url_parts
   if url:
      url, url_parts = get_url_parts(url)
   #
   #  for each part, from longest possible to 0 length
   #
   if not len(url_parts):
      #
      # return seo if in cache
      #
      cache_key = 'seo::/'
      seo = cache.get(cache_key)
      if seo:
         return seo
      seo = Seo.objects.filter(url='/')
      if seo:
         cache.set(cache_key, seo[0], 3600)
         return seo[0]

   else:
      for i in range(0, len(url_parts)):
         url = ''
         if i == 0:
            url = build_url(url_parts)
         else:
            url = build_url(url_parts, -i)

         #
         # return seo if in cache
         #
         cache_key = 'seo::%s' % url
         seo = cache.get(cache_key)
         if seo:
            return seo

         #
         #  return seo if in db
         #
         seo = Seo.objects.filter(url=url)
         if seo:
            cache.set(cache_key, seo[0], 3600)
            return seo[0]

   return False


## Render page
#
#  @param request Current request object
#
#  @return rendered page
#
def render_page(request):
   if 'messages' in request.session:
      persistent = {}
      for message_type, messages in request.session['messages'].items():
         for message in messages:
            if 'persistent' in message and message['persistent']:
               if not type in persistent:
                  persistent[message_type] = []
               persistent[message_type].append(message)

      del request.session['messages']
      if persistent:
         request.session['messages'] = persistent

   content = {'page_title': request.wepo.page.name}

   #
   #  add page sections to context content
   #
   for section in get_page_sections(request):
      content[section.replace('-', '_')] = ''

   #
   #  load page assets
   #
   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='script', code=wepo_assets.script.wepo, position='footer')
   page_load_assets(request, request.wepo.page)

   #
   #  set url parts
   #
   add_asset(request, type='script', code="""wepo.url_parts=%s;""" % json.dumps(request.wepo.url_parts), include_type='code', position="footer")

   #
   #  load page blocks
   #
   for section, block_list in get_page_blocks(request).items():
      for block in block_list:
         if not block.enabled:
            continue

         section_name = section.replace('-', '_')
         rendered_block = render_block(request, block)

         if type(rendered_block) is Seo:
            return page_redirect(rendered_block.url)
         elif hasattr(rendered_block, '__class__') and rendered_block.__class__ is HttpRedirect:
            return page_redirect(rendered_block.url)

         content[section_name] += rendered_block

   #
   #  join assets to include them in layout
   #
   for asset in ['head', 'body', 'footer', 'last']:
      content['%s_assets' % asset] = get_assets(request, asset)

   if 'messages' in request.session:
      messages_result = []
      for message_type, messages in request.session['messages'].items():
         message_type_result = []
         for message in messages:
            message_type_result.append('<strong>%s</strong>%s' % (message['title'], message['message']))

         if message_type_result:
            messages_result.append('<div class="alert alert-%s"><button type="button" class="close" data-dismiss="alert">&#215;</button>%s</div>' % (message_type, '<br />\n'.join(message_type_result)))

      if messages_result:
         content['body_assets'] = '%s<div class="message" style="position: fixed; bottom: 0;">%s</div>' % (content['body_assets'], '\n'.join(messages_result))

   #
   #  render layout and return html of the page
   #
   layout = get_template('layout/%s/index.html' % request.wepo.page.layout.replace('.', '/'))
   content['body_class'] = request.wepo.body_class

   html = layout.render(Context(content))
   html = os.linesep.join([s for s in html.splitlines() if s.strip()])
   return HttpResponse(request, html)


## Load assets recursive from page and it's parent, parent first
#
#  @param request Current request object
#  @param page Page object
#
def page_load_assets(request, page):
   if page.parent:
      page_load_assets(request, page.parent)

   asset_config = get_assets_config()
   page_assets = page.assets or {}

   def add_asset_local(asset_config, asset, type, position, insert_after=0, insert=None):
      delete = False
      if asset.startswith('-'):
         delete = True
         asset = asset[1:]
      config = asset_config[type][asset]

      add_asset(
         request,
         type=type,
         code=config,
         position=position,
         insert=insert,
         insert_after=insert_after,
         delete=delete)

   for location, asset_types in page_assets.items():
      for type, assets in asset_types.items():
         for asset in assets:
            if '+' in asset:
               asset_set = asset.split('+')
               asset_pref = asset_set[0]
               asset_pref = asset_config[type][asset_pref]

               asset_list = asset_set[1].split(',')

               insert_after = 0
               for asst in asset_list:
                  add_asset_local(asset_config=asset_config, asset=asst, type=type, position=location, insert=asset_pref, insert_after=insert_after)
                  insert_after += 1

            else:
               add_asset_local(asset_config=asset_config, asset=asset, type=type, position=location)


## Extract active (dynamic) parts of url based on seo url
#
#  @param request Current request object
#
def update_request_urls(request):
   #
   #  extract parts of url not in seo
   #
   seo_url = request.wepo.seo.url
   active_part = request.wepo.url.replace(seo_url, '')

   url_regex = '(/([\w\d\-.]*))'
   url_parts = re.findall(url_regex, active_part)
   url_parts = [part[1] for part in url_parts if part[1] != '']

   request.wepo.active_url_parts = url_parts

   seo = request.wepo.seo
   instance = None
   if seo.content:
      from core.helper.model_help import get_model
      model = get_model(request, seo.content_type)
      if model:
         model = model['model']
         instance = model.objects.get(id=seo.content)

   request.wepo.instance = instance