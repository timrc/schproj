#! /usr/bin/python
#
#  Core wepo form admin select2 elements
#

from core.form.elements import Input, Select, Checkbox


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#
def SelectDefaults(request, **data):
   instance = data['instance']
   field_name = data['name']
   if hasattr(instance, field_name):
      field_value = getattr(instance, field_name)
      if type(data['items'] is dict):
         new_items = []
         for key,value in data['items'].items():
            new_items.append(dict(key=key, value=value, selected=field_value == key))
         data['items'] = new_items

   return Select2(request, **data)


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#
def Select2(request, **data):
   from random import random
   unique_id = int(random() * 1000000)
   data['unique_id'] = unique_id

   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='style', code=wepo_assets.style.select2)
   add_asset(request, type='script', code=wepo_assets.script.select2, position='footer')

   from core.form import FormItem
   import json
   items = []
   if data['items']:
      if type(data['items']) is dict:
         for group, items_list in data['items'].items():
            for item in items_list:
               if item['selected']:
                  items.append(item['key'])
      else:
         for item in data['items']:
            if item['selected']:
               items.append(item['key'])

   if items:
      if 'multiple' in data:
         items = json.dumps(items).replace('"', "'")
      else:
         items = items[0]

   select_item = FormItem('Hidden', request, name=data['name'], value=items)
   #
   #  add custom on change event if set
   #
   onchange = data.get('onchange', '')
   add_asset(
      request,
      type='script',
      code="""
         jQuery('#field_%d').select2();
         jQuery('#field_%d').on("change", function(e){
            var val = e.val;
            if(jQuery(this).attr("multiple") !== undefined) {
               val = JSON.stringify(e.val).replaceAll('"', "'");
            }
            jQuery("input[name=%s]").val(val);
            %s
         });""" % (unique_id, unique_id, data['name'], onchange),
      include_type='code', position='footer')

   data['name'] = 'field_%s' % data['name']

   result = '%s%s' % (Select(request, **data), select_item.render())
   return result


## Form toggle button
#
#  @param data Field data
#
def ToggleButton(request, **data):
   value = data['value'] if 'value' in data else False

   items = [{}]
   data['items'] = items
   data['checked'] = 'checked' if value else ''

   from random import random
   unique_id = int(random() * 1000000)

   from core import wepo_assets
   from core.asset import add_asset
   # @TODO
   #add_asset(request, type='style', code=wepo_assets.style.bootstrap_switch)
   #add_asset(request, type='script', code=wepo_assets.script.bootstrap_switch, position='last')
   #add_asset(request, type='script', code='$("#button_%d input").bootstrapSwitch();' % unique_id, include_type='code', position='last')

   #add_asset(request, type='style', code=wepo_assets.style.bootstrap_toggle_buttons)
   #add_asset(request, type='script', code=wepo_assets.script.jquery_toggle_buttons, position='last')
   #add_asset(request, type='script', code='$("#button_%d").toggleButtons();'  % unique_id, include_type='code', position='last')

   return '<div class="toggle-button" id="button_%d">%s</div>' % (unique_id, Checkbox(request, **data))


## Form email input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered email input field
#
def Date(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'text'

   from random import random
   unique_id = int(random() * 1000000)
   attributes['id'] = 'field_%d' % unique_id

   from core.asset import add_asset
   from core import wepo_assets
   add_asset(request, type='script', code=wepo_assets.script.jquery_ui)
   add_asset(request, type='script', code='jQuery("#field_%d").datepicker({ dateFormat:"yyyy-mm-dd"});' % unique_id, include_type='code', position='footer')

   return Input(request, **attributes)


## Form email input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered email input field
#
def DateTime(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'text'

   from random import random
   unique_id = int(random() * 1000000)
   attributes['id'] = 'field_%d' % unique_id

   from core.asset import add_asset
   from core import wepo_assets
   add_asset(request, type='script', code=wepo_assets.script.bootstrap_datetime)
   add_asset(request, type='style', code=wepo_assets.style.bootstrap_datetime)
   add_asset(request, type='script', code='jQuery("#field_%d").datetimepicker({format: "yyyy-mm-dd hh:ii", autoclose: true, todayBtn: true, pickerPosition: "bottom-left"});' % unique_id, include_type='code', position='footer')

   attributes['value'] = ''
   if data['value'] is None or not data['value']:
      attributes['value']
   else:
      attributes['value'] = data['value'].strftime("%Y-%m-%d %H:%M:%S")
   return Input(request, **attributes)
