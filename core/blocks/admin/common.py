#! /usr/bin/python
#
#  Wepo administration common blocks
#

from django.template.loader import get_template
from django.template import Context
import urllib
from core.models import Language
from core.language import get_user_language


## Admin top navigation bar block
#
def navbar(request, block):
   template = get_template('admin/navbar.html')
   context = {}
   if 'attributes' in block:
      context['attributes'] = block['attributes']

   context['logout_link'] = '/user/logout?destination=%s' % urllib.quote(request.wepo.url.encode('utf8'), '')

   from core.user import get_user
   context['user'] = get_user(request)
   context['destination'] = urllib.quote(request.wepo.url.encode('utf8'), '')
   context['active_language'] = get_user_language(request)
   context['languages'] = Language.objects.all()

   return template.render(Context(context))


## Admin pages menu bar
#
def menu(request, block):
   template = get_template('admin/menu.html')

   from core.menu import get_menu, get_active_menus
   active_menus = get_active_menus(request)
   active_menu = active_menus['admin-menu']['breadcrumbs_extend_all'] if 'admin-menu' in active_menus else []

   menu, items = get_menu(request, 'admin-menu', active_menu)

   context = {
      'include_template': 'admin/menu_item.html',
      'menu': menu,
      'items': items
   }
   return template.render(Context(context))


## Admin pages dashboard page
#
def dashboard(request, block):
   template = get_template('admin/dashboard.html')
   context = {}
   return template.render(Context(context))