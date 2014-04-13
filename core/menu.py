#! /usr/bin/python
#
#  Wepo core menu manager, build menu breadcrumbs from request, get active menu item etc..
#

import re

from core import cache

from core.helper import build_url
from core.helper.common_help import get_cache_key
from core.models import Menu, MenuItem
from core.permission import check_permissions


## Get active item from breadcrumb list
#
#  @param request Current request object
#
def get_active(request):
   #breadcrumbs = get_breadcrumbs(request)
   #if breadcrumbs is not None and len(breadcrumbs) > 0:
   #   return breadcrumbs[-1]

   return None

def get_active_item(request):
   #breadcrumbs = get_breadcrumbs(request)
   #if breadcrumbs is not None and len(breadcrumbs) > 0:
   #   return breadcrumbs[-1]

   return None


##  Get active menus
#
#  @param request Current request object
#  @param seo Page seo object
#
def get_active_menus(request):
   #
   #  get breadcrumbs from cache
   #
   seo = request.wepo.seo
   while seo:
      for i in range(0, len(request.wepo.active_url_parts) + 1):
         url = ''
         if i == 0:
            url = build_url(request.wepo.active_url_parts, trailing=True)
         else:
            url = build_url(request.wepo.active_url_parts, to=-i, trailing=True)

         url = url.lower()
         cache_url = '%s/%s' % (seo.url, url)
         cache_url = cache_url.replace('//', '/')
         cache_key = get_cache_key('active', 'menus', cache_url)
         menus = cache.get(cache_key)

         #
         # return breadcrumbs if found one
         #
         if menus:
            return menus

         menu_item = MenuItem.objects.filter(seo=seo, url=url)

         #
         # generate breadcrumbs if found one
         #
         if menu_item:
            menus = {}
            for item in menu_item:
               breadcrumbs = generate_menu_breadcrumbs(item)
               if breadcrumbs:
                  menu = breadcrumbs[0].menu

                  #
                  #  add active menu parts
                  #
                  breadcrumbs_extend = breadcrumbs[:]
                  breadcrumbs_extend_all = breadcrumbs[:]

                  for active_url_part in request.wepo.active_url_parts:
                     last_menu_item = breadcrumbs_extend[-1]

                     active_url_menu_item = dict(
                        name = active_url_part,
                        url = '%s/%s' % (last_menu_item.seo.url if last_menu_item.seo else last_menu_item.url, active_url_part)
                     )

                     breadcrumbs_extend += [MenuItem(**active_url_menu_item)]
                     break

                  for active_url_part in request.wepo.active_url_parts:
                     last_menu_item = breadcrumbs_extend_all[-1]

                     active_url_menu_item = dict(
                        name = active_url_part,
                        url = '%s/%s' % (last_menu_item.seo.url if last_menu_item.seo else last_menu_item.url, active_url_part)
                     )

                     breadcrumbs_extend_all += [MenuItem(**active_url_menu_item)]

                  menus[menu.key_name] = dict(menu=menu, breadcrumbs=breadcrumbs, breadcrumbs_extend=breadcrumbs_extend, breadcrumbs_extend_all=breadcrumbs_extend_all)

            #cache.set(cache_key, menus)
            return menus

      if seo.page and seo.page.parent:
         seo = seo.page.parent.seo_set.get()
      else:
         seo = None

   ## @TODO add logic to load menu objects based on page rules
   #     for example: news object with only seo and categories ... return categories list
   #     generate_list_breadcrumbs
   #
   return []


## Returns list of menu items from root to current
#
#  @param menu_item Menu item object
#
def generate_menu_breadcrumbs(menu_item):
   menu_items = []
   while menu_item:
      menu_items.insert(0, menu_item)

      if not menu_item.parent:
         break

      menu_item = menu_item.parent

   return menu_items


## Returns list of active items from root to current
#
#  @param item Leaf item of the breadcrumbs
#
def generate_list_breadcrumbs(item):
   pass


## Check if menu item is active
#
#  @param active_menu_items List of active menu objects
#  @param menu_item Menu item object
#
#  @return status of menu item (True | False)
#
def is_menu_item_active(active_menu_items, menu_item):
   for active_item in active_menu_items:
      if active_item.key_name == menu_item.key_name:
         return True

   return False


## @TODO Get menu by key_name
#  Load all menu items recursively
#
#  @param key_name Menu key name
#
def get_menu(request, key_name, active_menus):
   menu = Menu.objects.get(key_name=key_name)
   items = load_menu_items(request, menu, active_menus)

   return menu, items


## Load menu items from the menu, sorted by level|sort
#
#  @param menu Menu
#  @param level Level of the menu items
#  @param parent Menu item parent
#
def load_menu_items(request, menu, active_menus, level=0, parent=None):
   items = []
   menu_items = MenuItem.objects.filter(menu=menu, level=level, parent=parent).order_by('sort')
   for menu_item in menu_items.all():
      user_has_access = False
      for permission in menu_item.permissions:
         status, action = check_permissions(request, [permission])
         if status:
            user_has_access = True
            break
      if user_has_access:
         items.append({
            'item': menu_item,
            'childs': load_menu_items(request, menu, active_menus, level=level+1, parent=menu_item),
            'active': is_menu_item_active(active_menus, menu_item)
         })

   return items