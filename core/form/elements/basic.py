# -*- coding: utf-8 -*-
#! /usr/bin/python
#
#  Core wepo form basic elements
#


## Form label
#
#  @param data Field data
#     value=''
#
#  @return rendered label
#
def Label(request, **data):
   attributes = {}
   for key, val in data.items():
      if key not in ['value']:
         attributes[key] = val

   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in attributes.items())
   value = data['value'] if 'value' in data else ''

   return '<label %s>%s</label>' % (attributes, value)


## Form html data
#
#  @param data Html tag data
#
#  @return rendered html tag
#
def Html(request, **data):
   attributes = {}
   for key, val in data.items():
      if key not in ['value', 'tag']:
         attributes[key] = val

   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in attributes.items())
   value = data['value'] if 'value' in data else ''
   tag = data['tag'] if 'tag' in data else 'div'

   if tag in ['hr']:
      return '<%s %s />' % (tag, attributes)
   else:
      return '<%s %s>%s</%s>' % (tag, attributes, value, tag)


## Form input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered generic input field
#
def Input(request, **data):
   if 'instance_model' in data:
      del data['instance_model']
   #if 'instance' in data:
   #   del data['instance']
   if 'field_config' in data:
      del data['field_config']

   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in data.items() if k not in ['instance'])
   return '<input %s />' % attributes


## Form text input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered text input field
#
def Text(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'text'

   return Input(request, **attributes)


## Form password input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered password input field
#
def Password(request, **data):
   attributes = {}
   for key, val in data.items():
      if key != 'value':
         attributes[key] = val

   attributes['type'] = 'password'

   return Input(request, **attributes)


## Form hidden input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered hidden input field
#
def Hidden(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'hidden'

   return Input(request, **attributes)


## Form radio input field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1}, {item2}]}
#
#  @return rendered radio input field
#
def Radio(request, **data):
   attributes = {}
   for key, val in data.items():
      if key not in ['items']:
         attributes[key] = val

   attributes['type'] = 'radio'

   items = []
   if 'items' in data:
      for item in data['items']:
         item_attributes = item['attributes'] if 'attributes' in item else {}
         item_attributes.update(attributes)
         items.append(Input(request, **item_attributes))

   return '\n'.join(item for item in items)


## Form checkbox input field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1}, {item2}]}
#
#  @return rendered checkbox input field
#
def Checkbox(request, **data):
   attributes = {'type': 'checkbox'}
   for key, val in data.items():
      if key == 'value' and type(val) is bool and val:
         attributes['checked'] = ''
      else:
         attributes[key] = val

   value = data['value'] if 'value' in data else ''
   if type(value) is bool:
      value = ''

   return '%s%s' % (Input(request, **attributes), value)


## Form button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered button input field
#
def InputButton(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'button'

   return Input(request, **attributes)


## Form select field
#
#  @param data Field data
#     {value='', name='', class='', id='', items=[{item1, value=1}, {item2, value=2}]}
#
#  @return rendered select field
#
def Select(request, **data):
   attributes = {}

   items = {}
   items_order = []

   for key, val in data.items():
      if key not in ['items', 'items_order', 'default_value', 'value', 'groups', 'unique_id', 'onchange', 'field_config', 'instance_model']:
         if key in attributes:
            attributes[key] = "%s %s" % (attributes[key], val)
         else:
            attributes[key] = val
      else:
         if key == 'items':
            items = val
         if key == 'items_order':
            items_order = val

   options = []
   if items:
      if 'groups' in data:
         keys = items_order if items_order else items.keys()
         for key in keys:
            options.append('<optgroup label="%s">' % key)
            for item in items[key]:
               if item['selected']:
                  options.append('<option value="%s" selected>%s</option>' % (item['key'], item['value']))
               else:
                  options.append('<option value="%s">%s</option>' % (item['key'], item['value']))

            options.append('</optgroup>')
      else:
         for item in items:
            if item['selected']:
               options.append('<option value="%s" selected>%s</option>' % (item['key'],  item['value']))
            else:
               options.append('<option value="%s">%s</option>' % (item['key'],  item['value']))

   from random import random
   unique_id = data.get('unique_id', int(random() * 1000000))
   attributes['id'] = 'field_%d' % unique_id

   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in attributes.items())
   joined_options = '\n'.join(option for option in options)
   try:
      joined_options = joined_options.decode('utf-8')
   except UnicodeEncodeError:
      pass
   result = '<select %s>%s</select>' % (attributes, joined_options)
   return result


## Form textarea input field
#
#  @return rendered textarea input field
#     {value='', name='', class='', id='', ...}
#
def Textarea(request, **data):
   attributes = {}
   for key, val in data.items():
      if key not in ['value']:
         attributes[key] = val

   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in attributes.items())
   value = data['value'] if 'value' in data else ''

   return '<textarea %s />%s</textarea>' % (attributes, value)