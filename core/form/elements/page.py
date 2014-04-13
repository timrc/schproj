#! /usr/bin/python
#
#  Core wepo form admin page blocks elements
#

from core.form.elements import Select2


## Form select blocks field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select blocks field
#
def Blocks(request, **data):
   from django.template.loader import get_template
   from django.template import Context
   import json

   template = get_template('form/page/blocks.html')
   context = {}

   instance = data.get('instance', None)
   layout = data.get('layout', 'empty')
   force_layout = data.get('force_layout', False)

   from core.helper import get_page_layout_config
   layout_config = get_page_layout_config(page=instance, default=layout, force_layout=force_layout)
   context['page'] = instance
   context['config'] = layout_config

   #
   #  generate initial page blocks data
   #
   initial_data = {}
   page_blocks = {}
   if instance and instance.blocks:
      page_blocks = data['instance'].blocks

   for part in layout_config:
      for section in part['elements']:
         if not section in initial_data:
            if section in page_blocks:
               initial_data[section] = page_blocks[section]
            else:
               initial_data[section] = []

   json_blocks = json.dumps(data['instance'].blocks if instance else initial_data)

   from core.form import FormItem
   context['input'] = FormItem('Hidden', request, name='blocks', value=json_blocks.replace('"', "'"))

   #
   #  block assets
   #
   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='script', code=wepo_assets.wepo.form.blocks, position='footer')
   add_asset(request, type='script', code="""wepo.form.blocks.init(%s);""" % json_blocks, include_type='code', position='footer')

   return template.render(Context(context))


## Form select assets field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select assets field
#
def Assets(request, **data):
   from django.template.loader import get_template
   from django.template import Context
   from core.asset import get_assets_config
   import json

   template = get_template('form/page/assets.html')
   context = {'page': data['instance']}

   page_assets = {
      'head': {'style': [], 'script': [], 'meta': []},
      #'body': {'style': [], 'script': [], 'meta': []},
      'footer': {'style': [], 'script': [], 'meta': []},
      #'last': {'style': [], 'script': [], 'meta': []}
   }

   instance = data.get('instance', None)
   parent = data.get('parent', None)

   deletable_default = True
   assets_instance = instance
   search_parent = True

   if assets_instance:
      if parent and parent != assets_instance.parent:
         deletable_default = False
         assets_instance = parent
      elif not parent and not request.wepo.is_page:
         search_parent = False
   else:
      deletable_default = False
      assets_instance = parent

   #
   #  generate page-parent hierarchy of assets
   #
   if assets_instance and assets_instance.assets:
      asset_config = get_assets_config()

      #
      #  append asset helper
      #
      def add_page_asset_helper(page_assets, asset, asset_type, location, insert_after=0, parent=None, deletable=False):
         disabled = False
         if asset.startswith('-'):
            disabled = True
            asset = asset[1:]

         data = {
            'name': asset.replace('_', ' '),
            'path': asset,
            'deletable': deletable,
            'disabled': disabled
         }

         index = 0
         if parent:
            asset_parent = parent
            if asset_parent.startswith('-'):
               asset_parent = asset_parent[1:]
            for asset_data in page_assets[location][asset_type]:
               if asset_data['path'] == asset_parent:
                  break
               index += 1

            page_assets[location][asset_type].insert(index + 1 + insert_after, data)
         else:
            if disabled:
               for asset_data in page_assets[location][asset_type]:
                  if asset_data['path'] == asset:
                     asset_data['disabled'] = True
                     break
            else:
               page_assets[location][asset_type].append(data)

      #
      #  generate hierarchy
      #
      def generate_page_assets(page, asset_config, page_assets, deletable=True, search_parent=True):
         #
         #  parent first!
         #
         if page.parent and search_parent:
            generate_page_assets(page.parent, asset_config, page_assets, deletable=False)

         for location, asset_types in page.assets.items():
            for type, assets in asset_types.items():
               for asset in assets:
                  if '+' in asset:
                     asset_set = asset.split('+')
                     asset_parent = asset_set[0]

                     asset_list = asset_set[1].split(',')
                     insert_after = 0

                     if asset_parent.startswith('-'):
                        add_page_asset_helper(page_assets=page_assets, asset=asset_parent, asset_type=type, location=location)

                     for asst in asset_list:
                        add_page_asset_helper(page_assets=page_assets, asset=asst, asset_type=type, location=location, parent=asset_parent, insert_after=insert_after, deletable=deletable)
                        insert_after += 1

                  else:
                     add_page_asset_helper(page_assets=page_assets, asset=asset, asset_type=type, location=location, deletable=deletable)

      generate_page_assets(assets_instance, asset_config, page_assets, deletable=deletable_default, search_parent=search_parent)

   context['assets'] = page_assets

   json_assets = json.dumps(page_assets)

   from core.form import FormItem
   context['input'] = FormItem('Hidden', request, name='assets', value=json_assets.replace('"', "'"))

   #
   #  block assets
   #
   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='style', code=wepo_assets.style.admin_nestable, position='head')

   add_asset(request, type='script', code=wepo_assets.script.admin_nestable, position='footer')
   add_asset(request, type='script', code=wepo_assets.wepo.form.assets, position='footer')

   add_asset(request, type='script', code="""wepo.form.assets.init(%s);""" % json_assets, include_type='code', position='footer')

   return template.render(Context(context))


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#
def Layouts(request, **data):
   attributes = {'name': data['name']}

   from core.helper import get_layouts
   layouts = get_layouts()

   items = {}
   value = data['value'] if 'value' in data else None
   value = value or 'empty'

   for layout in layouts:
      layout_parts = layout['path'].split('.')
      group = layout_parts[0].title() if len(layout_parts) > 1 else 'Basic'

      if not group in items:
         items[group] = []

      selected = value == layout['path']
      items[group].append({'selected': selected, 'key': layout['path'], 'value': layout['name']})

   instance = data['instance'] or None
   instance_id = instance.id if instance else None

   attributes['groups'] = True
   attributes['items'] = items
   attributes['class'] = 'form-control'
   attributes['onchange'] = 'wepo.form.blocks.change_layout(val, "%s");' % instance_id

   return Select2(request, **attributes)


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#
def Parents(request, **data):
   from core.form.elements import Models

   instance = data['instance'] or None
   instance_id = instance.id if instance else None

   attributes = dict(data) if data else {}
   attributes['onchange'] = 'wepo.form.assets.change_parent(val, "%s");' % instance_id

   return Models(request, **attributes)