#! /usr/bin/python
#
#  Wepo core install models fixtures
#

import datetime


## Install objects
#
class Install():

   ## install data
   #
   def install(self, allowed=[]):
      #
      #  language
      #
      from core.models import Language
      print '  Installing language'
      language, created = Language.objects.get_or_create(name='English', code='en')
      language.name = 'English'
      language.code = 'en'
      language.save()

      language, created = Language.objects.get_or_create(name='Slovenian', code='sl')
      language.name = 'Slovenian'
      language.code = 'sl'
      language.save()


      #
      #  group
      #
      from core.models import Group
      print '  Installing group'
      group, created = Group.objects.get_or_create(name='Administrator')
      group.name = 'Administrator'
      group.permissions = ["admin.admin_access"]
      group.save()

      group2, created = Group.objects.get_or_create(name='Super Administrator')
      group2.name = 'Super Administrator'
      group2.permissions = ["admin.admin_access", "admin.superuser_access", "admin.editor_access"]
      group2.save()

      group3, created = Group.objects.get_or_create(name='Editor')
      group3.name = 'Editor'
      group3.permissions = ["admin.admin_access", "admin.basic_editor_access", "admin.editor_access"]
      group3.save()

      group4, created = Group.objects.get_or_create(name='Basic editor')
      group4.name = 'Basic editor'
      group4.permissions = ["admin.admin_access", "admin.basic_editor_access"]
      group4.save()


      #
      #  user
      #
      from core.models import User
      print '  Installing user'
      user, created = User.objects.get_or_create(email='admin@coder.si')
      user.password = 'test'
      user.name = 'Admin'
      user.surname = 'Administrator'
      user.groups.add(group)
      user.save(change_password=True)

      user, created = User.objects.get_or_create(email='tim@coder.si')
      user.password = 'test'
      user.name = 'Tim'
      user.surname = 'Rijavec'
      user.groups.add(group2)
      user.save(change_password=True)

      usere, created = User.objects.get_or_create(email='editor@coder.si')
      usere.password = 'test'
      usere.name = 'Editor'
      usere.surname = 'Coder'
      usere.groups.add(group3)
      usere.save(change_password=True)

      usere, created = User.objects.get_or_create(email='news@coder.si')
      usere.password = 'test'
      usere.name = 'Basic editor'
      usere.surname = 'Coder'
      usere.groups.add(group4)
      usere.save(change_password=True)

      #
      #  core directories
      #
      from core.models import Directory
      print '  Installing directories'
      directory, created = Directory.objects.get_or_create(name='Root')
      user_directory, created = Directory.objects.get_or_create(name='User profile images', parent=directory)


      #
      #  page
      #
      from core.models import Page
      print '  Installing pages...'

      ##################################################################################################################
      ###########################################  Default user login page  ############################################
      ##################################################################################################################
      page, created = Page.objects.get_or_create(name='Admin login')
      page.enabled = True
      page.layout = 'admin.empty'
      page.blocks = dict(
         content=[
            dict(name='Login form', path='core.admin.user.login_form', enabled=True)
         ]
      )
      page.assets = dict(
         head=dict(
            meta=['view_port'],
            style=['bootstrap', 'admin_main', 'font', 'admin_style'],
         ),
         footer=dict(
            script=['jquery', 'bootstrap']
         )
      )
      page.save()


      ##################################################################################################################
      ###############################################  Default admin page  #############################################
      ##################################################################################################################
      page, created = Page.objects.get_or_create(name='Admin')
      page.enabled = True
      page.layout = 'admin'
      page.assets = dict(
         head=dict(
            meta=['view_port'],
            style=['bootstrap', 'admin_main', 'font', 'admin_style'],
         ),
         footer=dict(
            script=['jquery', 'jquery_ui', 'bootstrap', 'admin_menu']
         )
      )

      page.permissions = ["admin.admin_access"]
      page.save()


      ##################################################################################################################
      ###############################################  Admin dashboard  ################################################
      ##################################################################################################################
      page, created = Page.objects.get_or_create(name='Admin dashboard')
      page.parent = Page.objects.get(name='Admin')
      page.enabled = True
      page.layout = 'admin'
      page.blocks = dict(
         header=[
            dict(name='Navbar', path='core.admin.common.navbar', enabled=True),
         ],
         sidebar=[
            dict(name='Menu', path='core.admin.common.menu', enabled=True),
         ]
      )
      page.assets = dict(
         head=dict(
            style=['admin_dashboard'],
         )
      )

      page.permissions = ["admin.admin_access"]
      page.save()


      ##################################################################################################################
      ###########################################  Admin object list page  #############################################
      ##################################################################################################################
      page, created = Page.objects.get_or_create(name='Admin object list')
      page.enabled = True
      page.parent = Page.objects.get(name='Admin')
      page.layout = 'admin'
      page.blocks = dict(
         header=[
            dict(name='Navbar', path='core.admin.common.navbar', enabled=True),
         ],
         sidebar=[
            dict(name='Menu', path='core.admin.common.menu', enabled=True),
         ],
         content=[
            dict(name='Admin object list', path='core.admin.object.list', enabled=True)
         ]
      )
      page.assets = dict()
      page.permissions = ["admin.admin_access"]
      page.save()


      ##################################################################################################################
      ###########################################  Admin object edit page  #############################################
      ##################################################################################################################
      page, created = Page.objects.get_or_create(name='Admin object edit')
      page.enabled = True
      page.parent = Page.objects.get(name='Admin')
      page.layout = 'admin'
      page.blocks = dict(
         header=[
            dict(name='Navbar', path='core.admin.common.navbar', enabled=True),
         ],
         sidebar=[
            dict(name='Menu', path='core.admin.common.menu', enabled=True),
         ],
         content=[
            dict(name='Admin object edit', path='core.admin.object.edit', enabled=True)
         ]
      )
      page.assets = dict()
      page.permissions = ["admin.admin_access"]
      page.save()

      # Default error page
      page, created = Page.objects.get_or_create(name='Error')
      page.enabled = True
      page.layout = 'empty'
      page.save()


      #
      #  menu
      #

      from core.models import Menu, MenuItem, Seo
      print '  Installing menus...'

      # admin main menu
      menu, created = Menu.objects.get_or_create(name='Admin menu')
      menu.save()

      menu_item_seo = Seo.objects.get(key_name='admin-object-list')

      item, created = MenuItem.objects.get_or_create(menu=menu, name='Overview')
      item.seo = Seo.objects.get(key_name='admin')
      item.url = ''
      item.parent = None
      item.menu = menu
      item.sort = 0
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.admin_access"]
      item.save()

      item, created = MenuItem.objects.get_or_create(menu=menu, name='Pages')
      item.seo = menu_item_seo
      item.url = '/page'
      item.parent = None
      item.menu = menu
      item.sort = 1
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.superuser_access"]
      item.save()

      item, created = MenuItem.objects.get_or_create(menu=menu, name='User')
      item.seo = None
      item.url = ''
      item.parent = None
      item.menu = menu
      item.sort = 2
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.editor_access", "admin.superuser_access"]
      item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Users')
      menu_item.seo = menu_item_seo
      menu_item.url = '/user'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 0
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.editor_access", "admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Groups')
      menu_item.seo = menu_item_seo
      menu_item.url = '/group'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 1
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Addresses')
      menu_item.seo = menu_item_seo
      menu_item.url = '/address'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 2
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Countries')
      menu_item.seo = menu_item_seo
      menu_item.url = '/country'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 3
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.editor_access", "admin.superuser_access"]
      menu_item.save()


      item, created = MenuItem.objects.get_or_create(menu=menu, name='File')
      item.seo = None
      item.url = ''
      item.parent = None
      item.menu = menu
      item.sort = 3
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.editor_access", "admin.superuser_access"]
      item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Files')
      menu_item.seo = menu_item_seo
      menu_item.url = '/file'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 0
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.editor_access", "admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Directories')
      menu_item.seo = menu_item_seo
      menu_item.url = '/directory'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 1
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()


      item, created = MenuItem.objects.get_or_create(menu=menu, name='Menu')
      item.seo = None
      item.url = ''
      item.parent = None
      item.menu = menu
      item.sort = 4
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.superuser_access"]
      item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Menus')
      menu_item.seo = menu_item_seo
      menu_item.url = '/menu'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 0
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Menu items')
      menu_item.seo = menu_item_seo
      menu_item.url = '/menu_item'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 1
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()


      item, created = MenuItem.objects.get_or_create(menu=menu, name='Multilingualism')
      item.seo = None
      item.url = ''
      item.parent = None
      item.menu = menu
      item.sort = 5
      item.level = 0
      item.enabled = True
      item.permissions = ["admin.superuser_access"]
      item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Languages')
      menu_item.seo = menu_item_seo
      menu_item.url = '/language'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 0
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Phrases')
      menu_item.seo = menu_item_seo
      menu_item.url = '/phrase'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 1
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()

      menu_item, created = MenuItem.objects.get_or_create(menu=menu, name='Translations')
      menu_item.seo = menu_item_seo
      menu_item.url = '/translation'
      menu_item.parent = item
      menu_item.menu = menu
      menu_item.sort = 2
      menu_item.level = 1
      menu_item.enabled = True
      menu_item.permissions = ["admin.superuser_access"]
      menu_item.save()


      #
      #  seo links
      #

      # update admin redirect to admin dashboard

      print '  Updating seo links...'

      admin_seo = Seo.objects.get(key_name='admin')
      admin_seo.redirect = Seo.objects.get(key_name='admin-dashboard')
      admin_seo.save()

      print '  Installing seo links...'

      seo, created = Seo.objects.get_or_create(url='/user/logout')
      seo.callback = 'core.user.logout'
      seo.save()

      seo, created = Seo.objects.get_or_create(url='/user/enable/language')
      seo.callback = 'core.user.change_language'
      seo.save()



      seo, created = Seo.objects.get_or_create(url='/user/authenticate')
      seo.callback = 'core.user.authenticate'
      seo.save()

      # Install    admin
      #from admin import Install as install_admin
      #install_admin.install(allowed)

   ## Import data from
   #
   def load_csv(self):
      imports = [dict(
         #https://github.com/umpirsky/country-list/blob/master/country/cldr/en/country.csv
         module = 'core',
         file = 'country_list.csv',
         type = 'csv',
         delimiter = ',',
         model = 'country',
         fields = dict(code=0, name=1),
         method = 'update',
         update_fields = dict(code=0)
      )]

      from core.helper.import_help import import_from_csv

      for data in imports:
         import_from_csv(data)

