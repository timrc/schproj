#! /usr/bin/python
#
#  Core wepo helpers
#

import os, fnmatch
from wepo.settings import INSTALLED_APPS, PROJECT_ROOT

from core import cache
from common_help import get_cache_key


## Global get request helper
#
#  @return Current thread request
#
def get_request():
   from core.middleware import GlobalRequest
   return GlobalRequest.get_request()


## Generic class for dictionary parsed to object
#
class WepoGeneric(object):
   def __init__(self, init=None):
      if init is not None:
         self.__dict__.update(init)

   def __getitem__(self, key):
      return self.__dict__[key]

   def __setitem__(self, key, value):
      self.__dict__[key] = value

   def __delitem__(self, key):
      del self.__dict__[key]

   def __contains__(self, key):
      return key in self.__dict__

   def __len__(self):
      return len(self.__dict__)

   def __repr__(self):
      return repr(self.__dict__)

   def default(self):
      return self.__dict__

   def get(self, key, default):
      if self.__contains__(key):
         return self[key]
      return default

   def items(self):
      return self.__dict__.items()


## Dictionary to object (json to object) etc..
#
#  @param d Dictionary to be converted to object
#
#  @return Generated object from dictionary
#
def dict_to_obj(d):
   if isinstance(d, list):
      d = [dict_to_obj(x) for x in d]
   if not isinstance(d, dict):
      return d

   o = WepoGeneric()
   for k in d:
      o.__dict__[k] = dict_to_obj(d[k])

   return o


## List of dictionaries to list of objects (json to object) etc..
#
#  @param l List of dictionaries to be converted to list of objects
#
#  @return Generated list of objects
#
def dict_list_to_obj(l):
   o = []
   for d in l:
      o.append(dict_to_obj(d))

   return o


## Update object attributes with given dictionary
#
#  @param obj Object to update
#  @param dictionary Dictionary to append to object
#
def add_dict_to_object(obj, dictionary):
   obj.__dict__.update(**dictionary)


## Add/update object to wepo request
#
#  @param request Current request
#  @param name Object name
#  @param value Object value
#
def add_to_request(request, name, value):
   request.wepo.__dict__[name] = value


## Build url from list
#
#  @param parts List of url parts (sections)
#  @param to Numerical part of the url
#  @param joint Join operator
#  @param trailing include trailing joint or not
#
#  @return valid url
#
def build_url(parts, to=0, joint='/', trailing=True):
   trailing_joint = joint if trailing else ''

   if len(parts) == 0:
      return trailing_joint
   else:
      if to == 0:
         return '%s%s' % (trailing_joint, joint.join([part for part in parts]))
      else:
         return '%s%s' % (trailing_joint, joint.join([part for part in parts[:to]]))


## Get module from the path
#
#  foo.bar.some_module
#
#  @param path Path to the module
#
def get_module(path):
   module_path = path if type(path) is not list else '.'.join(str(p) for p in path)

   module = None
   try:
      module = __import__(module_path)
   except ImportError as exc:
      print exc
      return False

   components = module_path.split('.')
   for comp in components[1:]:
      if not hasattr(module, comp):
         return False
      module = getattr(module, comp)

   return module


## Get function from the module
#
#  @param module Module
#  @param name Name of the function
#
def get_function(module, name):
   if not hasattr(module, name):
      return False
   return getattr(module, name)


## Get layout config from request
#
#  @param request Current request
#
#  @param return layout configuration
#
def get_layout_config(request):
   return get_page_layout_config(request.wepo.page)


## Get layout config from request
#
#  @param request Current request
#
#  @param return layout configuration
#
def get_page_layout_config(page, default='empty', force_layout=False):
   layout_name = page.layout if page else default
   if force_layout:
      layout_name = default

   cache_key = get_cache_key('layout', layout_name)
   layout = cache.get(cache_key)

   if layout:
      layout = get_module(layout)
      return layout.config

   path = ''
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      path = '%s.templates.layout.%s' % (app, layout_name)
      layout = get_module(path)

      if layout:
         break

   if not layout:
      return {}

   cache.set(cache_key, path)
   return layout.config


## Get page layout sections
#
#  @param request Current request
#
def get_page_sections(request):
   config = get_layout_config(request)
   sections = []
   for part in config:
      sections += part['elements']

   return sections


## Get layouts from installed apps
#
#  @return Layouts list
#
def get_layouts():
   cache_key = get_cache_key('layouts')
   layouts = cache.get(cache_key)

   if layouts:
      return layouts

   #
   #  discovery blocks in all apps
   #
   layouts = []
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      path = '%s/%s/templates/layout' % (PROJECT_ROOT, app)

      for root, dir_names, file_names in os.walk(path):
         #
         #  filter out only modules except __init__
         #
         for filename in fnmatch.filter(file_names, '*.py'):

            layout_path = root.replace('%s/%s/templates/layout' % (PROJECT_ROOT, app), '')
            layout_module_path = root.replace('%s/' % PROJECT_ROOT, '').replace('/', '.')
            if layout_path:
               layout_path = layout_path[1:].replace('/', '.')
               layout_module = get_module(layout_module_path)
               layout_name = layout_module.name if hasattr(layout_module, 'name') else layout_path.replace('.', ' ').title()

               layouts.append({'name': layout_name, 'path': layout_path, 'full_path': layout_module_path})

   cache.set(cache_key, layouts, 86400)

   return layouts