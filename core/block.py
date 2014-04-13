#! /usr/bin/python
#
#  Wepo core
#
#     - Block manager, render block from object | url
#

import os, re, json, fnmatch

from core.helper import dict_to_obj, dict_list_to_obj, get_module, get_function
from core.helper.common_help import get_cache_key
from core import cache

from inspect import getmembers, isfunction

from wepo.settings import INSTALLED_APPS, PROJECT_ROOT


## Get the block from given path or directly from the request
#
#  /core/admin/common/header-navigation -> /core/blocks/admin/common/header-navigation
#  /my_module/admin/common/header-navigation -> /apps/my_module/blocks/admin/common/header-navigation
#  /development/admin/common/header-navigation -> /development/admin/common/header-navigation
#
#  @param path
#  @param development
#
def get_block(block_path, development=False):
   clean_block_path = block_path.replace('/', '.').replace('-', '_')

   #
   #  split path to get block's real path and it's function name
   #
   parts = clean_block_path.split('.')

   #
   #  get cached block if exists
   #
   cache_key = get_cache_key('block', *parts)
   block = cache.get(cache_key)

   #
   #  find block from path and it's name
   #
   if not block:
      name = parts[-1]

      #
      #  prepare path
      #
      if not development:
         parts.insert(1, 'blocks')
      if parts[0] not in ['core', 'apps'] and not development:
         parts.insert(0, 'apps')

      path = '.'.join(parts[:-1])

      module = get_module(path)
      if not module:
         return get_block_from_development(clean_block_path, development)

      block = get_function(module, name)
      if not block:
         return get_block_from_development(clean_block_path, development)

      cache.set(cache_key, block)

   return block


## Get block from development environment
#
#  @param path Path of the block
#  @param development
#
def get_block_from_development(path, development):
   #
   #  block not found
   #
   if development:
      return None

   path = path.replace('/apps', '')
   return get_block('development.%s' % path, True)


## Get blocks from installed apps
#
#  @return Block list
def get_blocks():
   cache_key = get_cache_key('blocks')
   blocks = cache.get(cache_key)

   if blocks:
      return blocks

   #
   #  discovery blocks in all apps
   #
   blocks = []
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      path = '%s/%s/blocks' % (PROJECT_ROOT, app)

      for root, dir_names, file_names in os.walk(path):
         #
         #  filter out only modules except __init__
         #
         for filename in fnmatch.filter(file_names, '*.py'):
            block_module_file_name = filename.replace('.py', '')
            block_module_path = root.replace('%s/' % PROJECT_ROOT, '').replace('/', '.')

            if block_module_file_name != '__init__':
               module = get_module('%s.%s' % (block_module_path, block_module_file_name))
               block_path = '%s.%s' % (block_module_path, block_module_file_name)
               blocks += [
                  dict_to_obj({
                     'path': block_path,
                     'name': block[0]
                  }) for block in getmembers(module) if isfunction(block[1]) and block[1].func_globals['__name__'] == block_path]

   cache.set(cache_key, blocks, 86400)

   return blocks


## Get page blocks
#
#  [ {name, path, attributes}, ... ]
#
#  @param request Current request
#
def get_page_blocks(request):
   if not request.wepo.page.blocks:
      return {}

   page_blocks = request.wepo.page.blocks

   blocks = {}
   for section, block_list in page_blocks.items():
      blocks[section] = dict_list_to_obj(block_list)

   return blocks


## Render block
#
#  @param request Current request object
#  @param block Block to render
#  @param attributes Optional block additional attributes
#
#  @return rendered block
#
def render_block(request, block=None):
   name = block.name
   path = block.path

   func = get_block(path)
   if func:
      return func(request, block)

   return ''


## Get block from url by key_name
#
#  @param url Url of the block
#
#  @return block object
#
def get_block_from_url(url):
   key_name = url

   block = get_block_from_cache(key_name, 'key_name')
   if not block:
      block = get_block_from_db(key_name, 'key_name')

      if block:
         return block

   return False


## Get block from cache
#
#  @param block_id Block id
#  @param id_type Type of the id; name, key_name, ...
#
#     @return: block object
#
def get_block_from_cache(block_id, id_type):
   block = cache.get('block::%s::%s' % (id_type, block_id))

   #
   #  return seo if found one
   #
   if block:
      return block

   return False


## Get block from database
#
#  @param block_id Block id
#  @param id_type Type of the id; name, key_name, ...
#
#     @return: block object
#
def get_block_from_db(block_id, id_type):
   kwargs = {
      '{0}__{1}'.format(id_type, 'startswith'): block_id
   }
   block = Block.objects.filter(**kwargs)

   #
   #  return seo if found one
   #
   if block:
      return block[0]

   return False


## Render block as json
#
#  @param block Block code to put into json
#  @param assets a List of assets to be included into json
#
#  @return Json of block code and assets
#
def render_block_json(block, assets = []):
   return json.dump(dict(block=block, assets=assets))