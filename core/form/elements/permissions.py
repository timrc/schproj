#! /usr/bin/python
#
#  Core wepo form admin permissions elements
#

from core.form.elements import Select2


## Form select permissions field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select permissions field
#
def Permissions(request, **data):
   attributes = {'name': data['name']}

   from core.permission import get_permissions
   permissions = get_permissions()

   items = {}
   value = data['value'] if 'value' in data else []

   for key, settings in permissions.items():
      group_key = key.split('.')[0].title()
      if not group_key in items:
         items[group_key] = []

      selected = key in value if value else False
      items[group_key].append({'selected': selected, 'key': key, 'value': settings['name'].title().replace('_', ' ')})

   attributes['groups'] = True
   attributes['multiple'] = 'multiple'
   attributes['items'] = items
   attributes['class'] = 'form-control'

   return Select2(request, **attributes)