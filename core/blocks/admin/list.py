#! /usr/bin/python
#
#  Wepo administration list blocks
#

from django.template.loader import get_template
from django.template import Context
from core.asset import get_all_assets
from core.block import get_blocks


## Admin get block list
#
def blocks(request, block):
   template = get_template('admin/list/blocks.html')
   context = {}

   section = request.GET.get('section', None)

   block_list = get_blocks()

   data = {}

   for block in block_list:
      block_path = block.path

      block_path = block_path.replace('apps.', '').replace('.blocks', '').split('.')
      block_app = block_path[0]
      block_group = ' '.join(block_path[1:])
      block_name = block.name

      if not block_app in data:
         data[block_app] = {}

      if not block_group in data[block_app]:
         data[block_app][block_group] = []

      data[block_app][block_group].append({
         'path': block.path,
         'name': block_name.replace('_', ' ')
      })

   context['data'] = data
   context['section'] = section

   return template.render(Context(context))


## Admin get assets list
#
def assets(request, block):
   template = get_template('admin/list/assets.html')
   context = {}

   asset_type = request.GET.get('asset_type', None)
   asset_location = request.GET.get('asset_location', None)

   assets = get_all_assets()

   data = {}

   for asset in assets[asset_type]:
      asset_name = asset['name']
      asset_group = asset_name.split('_')[0] if '_' in asset_name else 'common'

      if not asset_group in data:
         data[asset_group] = []

      data[asset_group].append(dict(type=asset_type, path=asset_name, name=asset_name.replace('_', ' '), location=asset_location))

   context['data'] = data

   return template.render(Context(context))