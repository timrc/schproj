#! /usr/bin/python
#
#  Wepo core
#
#     - JCM (Javascript, Css, Meta) Manager, dynamically add assets to requested page
#

import hashlib, json
from textwrap import dedent
from wepo.settings import STATIC_URL, INSTALLED_APPS

from helper import get_module
from helper.common_help import get_cache_key
from core import cache


## Get asset configs from all apps
#
#  @return app asset config
#
def get_assets_config():
   cache_key = get_cache_key('assets')
   config = cache.get(cache_key)

   if config:
      return config

   #
   #  discovery blocks in all apps
   #
   config = {}
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      module = get_module(app)
      if hasattr(module, 'wepo_assets'):
         app_assets = module.wepo_assets
         for asset_type, assets in app_assets.items():
            if not asset_type in config:
               config[asset_type] = {}

            config[asset_type].update(assets.items())

   cache.set(cache_key, config, 86400)

   return config


## Get asset static url
#
def get_assets_static_path():
   return STATIC_URL


## Get all assets
#
def get_all_assets():
   cache_key = get_cache_key('assets')
   assets = cache.get(cache_key)

   if assets:
      return assets

   #
   #  discovery assets in all apps
   #
   assets = {'script': [], 'style': [], 'meta': []}
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      module = get_module(app)
      if hasattr(module, 'wepo_assets'):
         wepo_assets = module.wepo_assets
         for asset_type in ['script', 'style', 'meta']:
            for asset, asset_conf in wepo_assets[asset_type].__dict__.items():
               assets[asset_type].append(dict(name=asset, conf=asset_conf))

   cache.set(cache_key, assets, 3600)

   return assets


## Generate asset (javascript, css, meta data) to append it to the page
#
#  @param type Asset type (javascript, css, ...)
#  @param code Asset code
#  @param include_type Asset include type; how the asset will be included (link, include, ..)
#
def generate_asset(type='', code=None, include_type='link'):
   asset_code = ''

   #
   #  generate static path
   #
   if include_type == 'link':
      asset_code = {}
      for k, v in code.items():
         asset_code[k] = v

      if type == 'style' and not '://' in asset_code['href']:
         asset_code['href'] = '%s%s' % (get_assets_static_path(), asset_code['href'])
      if type == 'script' and not '://' in asset_code['src']:
         asset_code['src'] = '%s%s' % (get_assets_static_path(), asset_code['src'])
   elif include_type == 'code':
      asset_code = code

   asset = dict(
      include_type = include_type,
      code = asset_code,
      md5 = hashlib.md5(str(asset_code)).hexdigest()
   )

   return asset


## Add asset to page request
#
#  @param request Current request object
#  @param type Asset type (javascript, css, ...)
#  @param code Asset code
#  @param include_type Asset include type; how the asset will be included (link, include, ..)
#  @param position Asset position; where in the page include generated asset
#  @param insert Find asset and insert new one right after that one
#  @param insert_after Insert after few extra positions
#  @param delete Delete asset
#
def add_asset(request, type='', code={}, include_type='link', position='head', insert=None, insert_after=0, delete=False):
   asset = generate_asset(type=type, code=code, include_type=include_type)
   md5 = asset['md5']

   #
   #  due to html rules, style need to be in header
   #
   if type == 'style':
      position = 'head'

   #
   #  do not add duplicates
   #
   if delete and md5 in request.wepo.assets['md5']:
      request.wepo.assets[position][type].remove(asset)
   else:
      if not md5 in request.wepo.assets['md5']:
         request.wepo.assets['md5'].append(md5)

         if insert:
            insert_asset = generate_asset(type=type, code=insert, include_type=include_type)
            index = request.wepo.assets[position][type].index(insert_asset)

            request.wepo.assets[position][type].insert(index + 1 + insert_after, asset)
         else:
            request.wepo.assets[position][type].append(asset)


## Get assets list of current request
#
#  @param request Current request
#
def get_assets_list(request):
         return 'wepo.assets.append(%s);' % json.dumps(request.wepo.assets['md5'])


## Add and Load assets to request
#
#  @param request Current request object
#  @param assets list of assets
#
def add_assets(request, data):
   for location, assets_list in data.iteritems():
      assets = None # Asset.objects.filter(key_name__in=assets_list)
      for asset in assets:
         add_asset(
            request,
            type=asset.type.key_name,
            code=asset.code,
            include_type=asset.include_type.key_name,
            position=location)


## Get assets for html
#
#  @param request Current request
#  @param position Position in page
#  @param request_type Request type for assets
#
def get_assets(request, position, request_type='html'):
   #
   #  json request type
   #
   if request_type == 'json':
      return request.wepo.assets[position]

   #
   #  html request type
   #
   result = ''
   result_inline_style = ''
   result_inline_script = ''
   jquery = []
   items = request.wepo.assets[position]
   for type in ['meta', 'style', 'script']:
      if not type in items:
         continue

      assets = items[type]

      for asset in assets:
         #
         #  include jquery javascript
         #
         if type == 'jquery':
            jquery.append(dedent(asset['code']).replace('\n', ''))

         #
         #  include javascript
         #
         if type == 'script':
            if asset['include_type'] == 'link':
               if request_type == 'html':
                  result += '<script type="text/javascript" %s></script>' % ' '.join('%s="%s"' % (key, value) for key, value in asset['code'].items()) + '\n'
            elif asset['include_type'] == 'code':
               if request_type == 'html':
                  result_inline_script += dedent(asset['code']).replace('\n', '') + '\n'
         #
         #  include css
         #
         elif type == 'style':
            if asset['include_type'] == 'link':
               if request_type == 'html':
                  result += '<link type="text/css" rel="stylesheet" %s />' % ' '.join('%s="%s"' % (key, value) for key, value in asset['code'].items()) + '\n'
            elif asset['include_type'] == 'code':
               if request_type == 'html':
                  result_inline_style += dedent(asset['code']).replace('\n', '') + '\n'
         #
         #  include meta tag
         #
         elif type == 'meta':
            if request_type == 'html':
               result += '<meta %s />' % ' '.join('%s="%s"' % (key, value) for key, value in asset['code'].items()) + '\n'

   if len(jquery) > 0:
      result += '<script type="text/javascript">jQuery(function(){%s});</script>' % (''.join(jquery)) + '\n'

   if position == 'last':
      result_inline_script += get_assets_list(request)

   if len(result_inline_script) > 0:
      result_inline_script = '<script type="text/javascript">%s</script>\n' % result_inline_script

   if len(result_inline_style) > 0:
      result_inline_style = '<style type="text/css">%s</style>\n' % result_inline_style

   return result + '\n' + result_inline_script + result_inline_style