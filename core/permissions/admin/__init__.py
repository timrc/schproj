#! /usr/bin/python
#
#  Wepo core admin permissions
#

from core.permission import check_permissions
from core.user import get_user_permissions
from django.shortcuts import redirect


## Administration permission callback
#
#  @param request Current request
#  @param attributes Permission extra attributes
#
def admin_access(request, attributes=None):
   #
   #  check if user is authenticated
   #
   status, action = check_permissions(request, ['user.authenticated'], ['/admin/login', {'destination': request.wepo.url}])
   if not status:
      return False, action

   user_permissions = get_user_permissions(request)
   if not 'admin.admin_access' in user_permissions:
      return False, redirect('/')

   return True, None


## Can access all data
def superuser_access(request, attributes=None):
   #
   #  check if user has that permissions
   #
   user_permissions = get_user_permissions(request)
   if not 'admin.superuser_access' in user_permissions:
      return False, None

   return True, None


## Can access some data
def editor_access(request, attributes=None):
   #
   #  check if user has that permissions
   #
   user_permissions = get_user_permissions(request)
   if not 'admin.editor_access' in user_permissions:
      return False, None

   return True, None


## Can access some data
def basic_editor_access(request, attributes=None):
   #
   #  check if user has that permissions
   #
   user_permissions = get_user_permissions(request)
   if not 'admin.basic_editor_access' in user_permissions:
      return False, None

   return True, None


## Can access all data
def list_all_items(request, attributes=None):
   #
   #  check if user has that permissions
   #
   user_permissions = get_user_permissions(request)
   if not 'admin.list_all_items' in user_permissions:
      return check_permissions(request, ['admin.list_own_items'])

   return True, ['list_all']


## Can access own data
def list_own_items(request, attributes=None):
   #
   #  check if user has that permissions
   #
   user_permissions = get_user_permissions(request)
   if not 'admin.list_own_items' in user_permissions:
      return False, ['list_none']

   return True, ['list_own']