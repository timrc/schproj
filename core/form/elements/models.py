#! /usr/bin/python
#
#  Core wepo form admin model objects elements
#

from core.form.elements import Select2


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#model
def Models(request, **data):
   attributes = dict(data) if data else {}

   value = data['value'] if 'value' in data else None

   is_multiple = False

   from core.helper.model_help import get_model_fields
   for field_name, field_data in get_model_fields(request, data['instance_model']).items():
      if field_name == data['name'] and field_data.field_type == 'ManyToManyField':
         is_multiple = True
         break

   show_linked_only = data['field_config'].__contains__('linked_only') and data['field_config']['linked_only']

   from core.helper.model_help import get_model
   model = get_model(request, data['model'])
   model = model['model']

   groupped_items = {}
   list_items = []
   objects = None

   items_order = []

   # sort by ...
   default_sort = model.default_sort if hasattr(model, 'default_sort') else ['id']

   if show_linked_only:
      through = getattr(data['instance'], data['name']).through
      q = {data['instance_model']._meta.db_table:data['instance'].id}
      objects = through.objects.filter(**q).order_by(*default_sort)
   else:
      objects = model.objects.all().order_by(*default_sort)

   if not is_multiple:
      groupped_items['None'] = [{'selected': value is None, 'key': None, 'value': 'None'}]
      items_order = ['None']

   for o in objects:
      object = getattr(o, data['model']) if show_linked_only else o

      group = object.parent.name if hasattr(object, 'parent') and object.parent else 'Root'

      if not group in groupped_items:
         groupped_items[group] = []

      if not group in items_order:
         if group == 'Root':
            items_order.insert(1, group)
         else:
            items_order.append(group)

      selected = False
      if is_multiple:
         if value:
            for val in value.all():
               if val.id == object.id:
                  if show_linked_only:
                     selected = o.enabled
                  else:
                     selected = True
                  break

         list_items.append({'selected': selected, 'key': '%d' % object.id, 'value': str(object)})
         groupped_items[group].append({'selected': selected, 'key': '%d' % object.id, 'value': str(object)})
      else:
         selected = value and value.id == object.id
         name = str(object) #object.name if hasattr(object, 'name') else object.key_name if hasattr(object, 'key_name') else ''
         groupped_items[group].append({'selected': selected, 'key': '%d' % object.id, 'value': name})

   #
   # show add new object button
   #
   add_new_button = ''
   if data['field_config'].__contains__('create_new') and data['instance']:
      from core.form import FormItem
      add_new_button = FormItem('Button', request, value='Add new %s' % data['model'], id='add_new_%s' % data['model'], **{
         'class': 'btn',
         'data-model': data['model'],
         'data-field': data['name'],
         'data-parent': data['instance'].id,
         'data-parent-model': data['instance_model']._meta.db_table
      })

      from core import wepo_assets
      from core.asset import add_asset
      add_asset(request, type='script', code=wepo_assets.wepo.form.model, position='footer')
      add_asset(request, type='script', code="""wepo.form.model.init('%s')""" % data['model'], include_type='code', position='footer')

      add_new_button = add_new_button.render()

   attributes['items_order'] = items_order
   if is_multiple:
      attributes['multiple'] = 'multiple'

   if len(groupped_items) > 1:
      attributes['groups'] = True
      attributes['items'] = groupped_items
   else:
      attributes['items'] = list_items
   attributes['class'] = 'form-control'

   result = '%s%s' % (Select2(request, **attributes), add_new_button)
   return result
