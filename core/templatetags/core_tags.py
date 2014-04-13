#! /usr/bin/python
#
#  Wepo core template tags
#

from django.template import Library
from django.template.base import Node, NodeList, TemplateSyntaxError
from core.form import FormItem
from django.template.loader import get_template

register = Library()

## Get key from dictionary
#
@register.simple_tag
def dict_lookup(dictionary, key):
   #
   # Try to fetch from the dict, and if it's not found return an empty string.
   #
   return dictionary[key] if key in dictionary else key


class FieldNode(Node):

   def __init__(self, field_name, field_list, field_var, instance, model, nodelist_field):
      self.field_name = field_name
      self.field_list = field_list
      self.field_var = field_var
      self.instance = instance
      self.model = model
      self.nodelist_field = nodelist_field

   def render(self, context):
      field_name = self.field_name.resolve(context, True)
      field_list = self.field_list.resolve(context, True)
      instance = self.instance.resolve(context, True)
      model = self.model.resolve(context, True)

      field_settings = field_list[field_name]
      field_widget = field_settings.config.widget

      field_defaults = field_settings.config.defaults.__dict__ if 'defaults' in field_settings.config else {}
      field_template = field_settings.config.template if 'template' in field_settings.config else 'form_elements'

      template = get_template('admin/object/%s.html' % field_template)

      field_defaults['class'] = 'span12'
      field_defaults['value'] = getattr(instance, field_name) if hasattr(instance, field_name) else ''
      field_defaults['instance'] = instance
      field_defaults['instance_model'] = model
      field_defaults['name'] = field_name
      field_defaults['field_config'] = field_settings['config']

      from core.helper import get_request
      field_form_field = FormItem(type=field_widget, request=get_request(), **field_defaults)

      context[self.field_var] = field_form_field.render()

      return template.render(context)


@register.tag('field')
#{% field field_name from fields as field %}
def field(parser, token):
   bits = token.contents.split()

   if len(bits) != 6:
      raise TemplateSyntaxError("'model_field' statements should have 6 eight words: %s" % token.contents)

   if bits[2] != 'from' or bits[4] != 'as':
      raise TemplateSyntaxError("'model_field' statements should use the format 'model_field field_name from field_list as field': %s" % token.contents)

   field_name = parser.compile_filter(bits[1])
   field_list = parser.compile_filter(bits[3])
   instance = parser.compile_filter('instance')
   model = parser.compile_filter('model')
   field_var = bits[5]

   nodelist_field = parser.parse(('empty', 'endfield',))
   token = parser.next_token()

   return FieldNode(field_name, field_list, field_var, instance, model, nodelist_field)


class SectionsNode(Node):

   def __init__(self, section, page, output_var, nodelist_field):
      self.section = section
      self.page = page
      self.output_var = output_var
      self.nodelist_field = nodelist_field

   def render(self, context):
      section = self.section.resolve(context, True)
      page = self.page.resolve(context, True)

      import json
      page_blocks = page.blocks if page and page.blocks else []
      page_section = page_blocks[section] if section in page_blocks else []

      nodelist = NodeList()

      context[self.output_var] = page_section

      for node in self.nodelist_field:
         try:
            nodelist.append(node.render(context))
         except Exception as e:
            if not hasattr(e, 'django_template_source'):
               e.django_template_source = node.source
            raise

      return nodelist.render(context)

@register.tag('sections')
def sections(parser, token):
   bits = token.contents.split()

   if len(bits) != 6:
      raise TemplateSyntaxError("'page_sections' statements should have 6 six words: %s" % token.contents)

   if bits[2] != 'from' or bits[4] != 'as':
      raise TemplateSyntaxError("'page_sections' statements should use the format 'sections section from page as sections': %s" % token.contents)

   section = parser.compile_filter(bits[1])
   page = parser.compile_filter(bits[3])
   output_var = bits[5]

   nodelist_field = parser.parse(('empty', 'endsections',))
   token = parser.next_token()

   return SectionsNode(section, page, output_var, nodelist_field)


## Permission tag helper class to render tokens
#
class PermissionNode(Node):

   def __init__(self, permissions, nodelist_permission, nodelist_nopermission):
      self.permissions = permissions
      self.nodelist_permission = nodelist_permission
      self.nodelist_nopermission = nodelist_nopermission

   def render(self, context):
      permissions = [permission.resolve(context, True) for permission in self.permissions]

      #
      #  check if has permissions
      #
      from core.helper import get_request
      from core.permission import check_permissions
      status, action = check_permissions(get_request(), permissions)

      nodelist = NodeList()
      if status:
         for node in self.nodelist_permission:
            try:
               nodelist.append(node.render(context))
            except Exception as e:
               if not hasattr(e, 'django_template_source'):
                  e.django_template_source = node.source
               raise
      else:
         if self.nodelist_nopermission:
            for node in self.nodelist_nopermission:
               try:
                  nodelist.append(node.render(context))
               except Exception as e:
                  if not hasattr(e, 'django_template_source'):
                     e.django_template_source = node.source
                  raise

      return nodelist.render(context)


@register.tag('permission')
## Permission tag to check if current user has permission to view content
#
def permission(parser, token):
   bits = token.contents.split()

   if len(bits) < 2:
      raise TemplateSyntaxError("'permissions' statements should have at least 2 two words: %s" % token.contents)

   permissions = [parser.compile_filter(bit) for bit in bits[1:]]

   nodelist_nopermission = None
   nodelist_permission = parser.parse(('nopermission', 'endpermission'))
   token = parser.next_token()

   #
   # {% nopermission %} (optional)
   #
   if token.contents == 'nopermission':
      nodelist_nopermission = parser.parse(('endpermission',))
      token = parser.next_token()

   return PermissionNode(permissions, nodelist_permission, nodelist_nopermission)


class RequestNode(Node):

   def __init__(self, nodelist_field):
      self.nodelist_field = nodelist_field

   def render(self, context):
      from core.helper import get_request
      request = get_request()
      context['request'] = request
      context['wepo'] = request.wepo

      nodelist = NodeList()

      for node in self.nodelist_field:
         try:
            nodelist.append(node.render(context))
         except Exception as e:
            if not hasattr(e, 'django_template_source'):
               e.django_template_source = node.source
            raise

      return nodelist.render(context)

@register.tag('request')
def request(parser, token):
   bits = token.contents.split()

   nodelist_field = parser.parse(('empty', 'endrequest',))
   token = parser.next_token()

   return RequestNode(nodelist_field)