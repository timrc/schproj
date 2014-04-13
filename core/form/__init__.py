# -*- encoding: utf-8 -*-
#! /usr/bin/python
#
#  Core wepo form helpers
#

from __future__ import unicode_literals
from core.helper.model_help import get_model_fields, get_model_groups
from core.helper import get_module, get_function
from core.helper.common_help import get_cache_key
from core import cache

from django.template.loader import get_template
from django.template import Context

from wepo.settings import INSTALLED_APPS


## Wepo admin form class
#
class AdminForm:
   def __init__(self, request, model, instance):
      self.request = request
      self.model = model
      self.instance = instance
      self.fields = get_model_fields(request, model)
      self.groups = get_model_groups(request, model)

   ## Render form
   #
   #  @return Rendered form
   #
   def render(self):
      result = []

      template = get_template('admin/object/form_group.html')
      group_number = 0
      for group in self.groups:
         context = dict(name='', group_number=group_number, active=group_number==0  )
         context['panels'] = self.render_group(group)
         result.append(template.render(Context(context)))
         group_number+=1

      return ''.join(result)

   ## Render admin form group
   #
   def render_group(self, group):
      result = []

      template = get_template('admin/object/form_panel.html')
      for panel in group['panels']:
         panel_name = panel['name'] if 'name' in panel else 'asdf'
         context = dict(name=panel_name)
         context['fields'] = self.render_panel(panel)
         result.append(template.render(Context(context)))

      return result

   ## Render admin form panel
   #
   def render_panel(self, panel):
      result = []

      for _field in panel['fields']:
         context = dict(field_name=_field)

         field = self.fields[_field]

         field_widget = field.config.widget
         field_defaults = field.config.defaults.__dict__ if 'defaults' in field.config else {}
         field_template = field.config.template if 'template' in field.config else 'form_field'

         template = get_template('admin/object/%s.html' % field_template)

         field_defaults['class'] = 'form-control'
         field_defaults['value'] = getattr(self.instance, field.name) if hasattr(self.instance, field.name) else ''
         field_defaults['instance'] = self.instance
         field_defaults['instance_model'] = self.model
         field_defaults['name'] = field.name
         field_defaults['field_config'] = field['config']

         from core.helper import get_request
         field_form_field = FormItem(type=field_widget, request=get_request(), **field_defaults)
         context['field'] = field_form_field

         result.append(template.render(Context(context))) #.encode('utf-8')
      return result


## Wepo form class
#
class Form:
   ## Form constructor
   #
   #  @param request Current request
   #  @param action Form action
   #  @param name Form name
   #  @param method Form method
   #  @param attributes Extra form attributes
   #
   def __init__(self, request, action=None, name=None, method=None, **attributes):
      self.items = []
      self.action = action
      self.name = name
      self.method = method
      self.request = request
      self.attributes = attributes
      self.auto_close = True

   ## Add new item to the form
   #
   #  @param type Form item type
   #  @param request Current request
   #  @param attributes Extra form attributes
   #
   #  @return Create item
   #
   def add_item(self, type, **attributes):
      item = FormItem(type, self.request, **attributes)
      self.items.append(item)
      return item

   ## Remove item from the form
   #
   #  @param index Index of the item to be removed
   #
   def remove_item(self, index):
      self.items.pop(index)

   ## Add new item to the form
   #
   #  @param request Current request
   #  @param attributes Extra form attributes
   #
   #  @return Create group
   #
   def add_group(self, **attributes):
      group = FormGroup(self.request, **attributes)
      self.items.append(group)
      return group

   ## Render form
   #
   #  @return Rendered form
   #
   def render(self):
      result = []
      for item in self.items:
         result.append(item.render())

      attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in self.attributes.items())
      if self.action:
         attributes = '%s action="%s"' % (attributes, self.action)
      if self.name:
         attributes = '%s name="%s"' % (attributes, self.name)
      if self.method:
         attributes = '%s method="%s"' % (attributes, self.method)

      if self.auto_close:
         return '<form %s>%s</form>' % (attributes, '\n'.join(result))
      else:
         return '<form %s>%s' % (attributes, '\n'.join(result))

   ## Render in template
   #
   def __str__(self):
      return self.render()

   ## Iterate trough items
   #
   def __iter__(self):
      for item in self.items:
         yield item


## Wepo form field sets class
#
class FormGroup:
   def __init__(self, request, type='fieldset', **attributes):
      self.items = []
      self.type = type
      self.request = request
      self.attributes = attributes

   ## Add new item to the form
   #
   #  @param request Current request
   #  @param attributes Extra form attributes
   #
   #  @return Create group
   #
   def add_group(self, **attributes):
      group = FormGroup(self.request, **attributes)
      self.items.append(group)
      return group

   ## Add new item to the form
   #
   #  @param type Form item type
   #  @param request Current request
   #  @param attributes Extra form attributes
   #
   #  @return Create item
   #
   def add_item(self, type, **attributes):
      item = FormItem(type, self.request, **attributes)
      self.items.append(item)
      return item

   ## Remove item from the form
   #
   #  @param index Index of the item to be removed
   #
   def remove_item(self, index):
      self.items.pop(index)

   ## Render form group
   #
   #  @return Rendered form group
   #
   def render(self):
      result = []
      for item in self.items:
         result.append(item.render())

      attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in self.attributes.items())

      return '<%s %s>%s</%s>' % (self.type, attributes, '\n'.join(result), self.type)

   ## Iterate trough items
   #
   def __iter__(self):
      for item in self.items:
         yield item


## Wepo form item class
#
class FormItem:
   def __init__(self, type, request, **attributes):
      self.type = type
      self.request = request
      self.prefix = ''
      self.postfix = ''
      self.wrapper = ''
      self.wrapper_data = ''
      self.attributes = attributes

   ## Add prefix to form item
   #
   #  @param type Html tag type of the prefix
   #  @param value Value of the prefix
   #
   def add_prefix(self, type, value, **data):
      attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in data.items())
      if type:
         self.prefix = '<%s %s>%s</%s>' % (type, attributes, value, type)
      else:
         self.prefix = value

   ## Add postfix to form item
   #
   #  @param type Html tag type of the postfix
   #  @param value Value of the postfix
   #
   def add_postfix(self, type, value, **data):
      attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in data.items())
      if type:
         self.postfix = '<%s %s>%s</%s>' % (type, attributes, value, type)
      else:
         self.postfix = value

   ## Add wrapper to form item
   #
   #  @param type Html tag type of the wrapper
   #  @param value Value of the wrapper
   #
   def add_wrapper(self, type, **data):
      self.wrapper = type
      self.wrapper_data = data

   ## Render item
   #
   #  @return Rendered item
   #
   def render(self):
      form_items = get_form_items()
      if not self.type in form_items:
         return ''

      module = get_module(form_items[self.type])
      func = get_function(module, self.type)

      result = '%s%s%s' % (self.prefix, func(self.request, **self.attributes), self.postfix)
      if self.wrapper:
         wrapper_attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in self.wrapper_data.items())
         result = '<%s %s>%s</%s>' % (self.wrapper, wrapper_attributes, result, self.wrapper)

      return result.encode('utf-8')

   ## Render in template
   #
   def __str__(self):
      return self.render()


## Get form items from installed apps
#
#  @return Form items list
#
def get_form_items():
   cache_key = get_cache_key('form_elements')
   form_items = cache.get(cache_key)

   if form_items:
      return form_items

   #
   #  discovery form items in all apps
   #
   form_items = {}
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      path = '%s.form.elements' % app
      module = get_module(path)

      if not module:
         continue

      for element in dir(module):
         if not element.startswith('__'):
            form_items[element] = path

   cache.set(cache_key, form_items, 86400)

   return form_items