#! /usr/bin/python
#
#  Wepo core - permission manager
#

import os, fnmatch, json

from helper import get_module, get_function
from helper.common_help import get_cache_key
from core.user import get_user_permissions

from core import cache

from inspect import getmembers, isfunction

from wepo.settings import INSTALLED_APPS, PROJECT_ROOT


## Get permissions from installed apps
#
#  @return Permissions list
def get_permissions():
   cache_key = get_cache_key('permissions')
   permissions = cache.get(cache_key)

   if permissions:
      return permissions

   #
   #  discovery blocks in all apps
   #
   permissions = {}
   for app in INSTALLED_APPS:
      if app.startswith('django'):
         continue

      path = '%s/%s/permissions' % (PROJECT_ROOT, app)

      for root, dir_names, file_names in os.walk(path):
         for filename in fnmatch.filter(file_names, '*.py'):
            permission_module_file_name = filename.replace('.py', '')
            permission_module_path = root.replace('%s/' % PROJECT_ROOT, '').replace('/', '.')
            module = get_module('%s.%s' % (permission_module_path, permission_module_file_name))

            for permission in getmembers(module):
               permission_path = ('%s.%s' % (permission_module_path, permission_module_file_name)).replace('.__init__', '')
               permission_full_path = '%s.%s' % (permission_module_path, permission_module_file_name)
               permission_module = permission_path.split('.')
               permission_module = permission_module[-1]

               if isfunction(permission[1]) and permission[1].func_globals['__name__'] == permission_full_path:
                  permission_key_name = '%s.%s' % (permission_module, permission[0])
                  permissions[permission_key_name] = dict(path=permission_path, name=permission[0], key_name=permission_key_name)

   cache.set(cache_key, permissions, 86400)

   return permissions


## Get permission
#
#  @param permission_name Permission name
#
def get_permission(permission_name):
   permissions = get_permissions()
   if permission_name in permissions:
      permission_config = permissions[permission_name]

      permission = get_module(permission_config['path'])
      permission = get_function(permission, permission_config['name'])
      return permission

   return False


## Check permissions
#
#  @param request Current page request
#  @param permissions Permissions to check
#  @param attributes Extra list of attributes for permission callbacks
#
def check_permissions(request, permissions, attributes=None):
   for permission in permissions:
      permission_callback = get_permission(permission)
      if permission_callback:
         status, action = permission_callback(request, attributes)
         if not status:
            return False, action
      else:
         user_permissions = get_user_permissions(request)
         if not permission in user_permissions:
            return False, no_permission_default_action(request)

   return True, None


## No permission default action
#
#  @param request Current request
#
def no_permission_default_action(request):
   pass


## Check page permissions
#
#  @param request Current page request
#
def check_page_permissions(request):
   if not hasattr(request.wepo.page, 'permissions'):
      return True, None

   permissions = request.wepo.page.permissions
   if not permissions:
      return True, None

   return check_permissions(request, permissions)