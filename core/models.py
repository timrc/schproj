#! /usr/bin/python
#
#  Wepo core models
#

import json

from django.db import models as dmodels
from core.decorators import model_field_configuration as field_config
from core.decorators import field_group, model_settings

from core.fields import JsonField

from core.helper.common_help import hash_it
from django.utils.encoding import force_bytes


## Directory
#
#  File directories
#
@field_config(name='name',       widget='Text')
@field_config(name='parent',     widget='Models',    defaults=dict(model='directory'))
@field_group(name='Settings',    panels=[
   {'name': 'Details', 'fields': ['name', 'parent']}
])
@model_settings(name='File', description='File')
class Directory(dmodels.Model):
   ## @var name
   #  Name of the directory
   name        = dmodels.CharField(max_length=255, db_index=True)
   ## @var parent
   #  Directory parent
   parent      = dmodels.ForeignKey('self', null=True, blank=True)

   def __unicode__(self):
      return "%s" % (self.name, )

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "directory"

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      super(Directory, self).save(force_insert, force_update, using, update_fields)


## File
#
#  Files
#
@field_config(name='file_name',     widget='Text', readonly=True)
@field_config(name='mime_type',     widget='Text', readonly=True)
@field_config(name='size',          widget='Text', readonly=True)
@field_config(name='title',         widget='Text')
@field_config(name='description',   widget='Text')
@field_config(name='path',          widget='Text', hidden=True)
@field_config(name='data',          widget='Text', hidden=True)
@field_config(name='author',        widget='Text', hidden=True)
@field_config(name='created',       widget='DateTime')
@field_config(name='directory',     widget='Text', hidden=True)
@field_config(name='owner',         widget='Text', readonly=True)
@field_group(name='File details',   panels=[
   {'name': 'Details', 'fields': ['file_name', 'mime_type']},
   {'name': 'Information', 'fields': ['size', 'created']},
   {'name': 'Basic', 'fields': ['title', 'description', 'owner']}
   # More complex group
   # [{'fields': [ ['phone', 'email', 'website'], ['facebook', 'twitter', 'skype', 'yahoo']], 'title': 'Contact details', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'}]
])

@model_settings(name='File', description='File')
class File(dmodels.Model):
   ## @var file_name
   #  File name of the file
   file_name = dmodels.CharField(max_length=255, db_index=True)
   ## @var mime_type
   #  Unique identifier of the file
   mime_type = dmodels.CharField(max_length=255, db_index=True)
   ## @var size
   #  File size
   size = dmodels.CharField(max_length=255)
   ## @var title
   #  Title of the file
   title = dmodels.TextField()
   ## @var description
   #  Description of the file
   description = dmodels.TextField()
   ## @var author
   #  Author of the file
   author = dmodels.TextField()
   ## @var path
   #  File path
   path = dmodels.TextField()
   ## @var data
   #  Data about crops, different sizes, etc...
   data = JsonField(null=True, blank=True)
   ## @var created
   #  Date time  of creation
   created = dmodels.DateTimeField(db_index=True)
   ## @var directory
   #  Virtual directory
   directory = dmodels.ForeignKey('Directory', null=True, blank=True)
   ## @var owner
   #  File owner (uploader)
   owner = dmodels.ForeignKey('User', null=True, blank=True)

   def __unicode__(self):
      return "%s" % (self.file_name, )

   def __str__(self):
      return force_bytes('%s' % self.file_name)

   class Meta:
      app_label = 'core'
      db_table = "file"
      unique_together = ('file_name', 'created', )

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      super(File, self).save(force_insert, force_update, using, update_fields)

   ## Get seo link
   #
   def get_seo(self):
      return '/media/%s/%s/%s/%d/%s' % (self.created.year, self.created.month, self.created.day, self.id, self.file_name)


## Groups
#
#  To group specified permissions.
#
@field_config(name='name',          widget='Text')
@field_config(name='permissions',   widget='Permissions')
@field_config(name='key_name',      widget='Text',    hidden=True)
@field_group(name='Group details',  panels=[
   {'name': 'Details', 'fields': ['name', 'permissions']}
])
@model_settings(group='User', description='A group is a number of things or persons being in some relation to one another.')
class Group(dmodels.Model):
   ## @var name
   #  Name of the group
   name        = dmodels.CharField(max_length=64)
   ## @var key_name
   #  Unique identifier of the group
   key_name    = dmodels.CharField(max_length=64, db_index=True)
   ## @var permissions
   #  List of permissions in group
   permissions = JsonField(null=True, blank=True)

   def __unicode__(self):
      return self.name

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "group"
      ordering = ["id"]
      unique_together = ('key_name', )

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2(self.name)
      super(Group, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/group/%s' % self.key_name)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Country
#
#  Countries
#
@field_config(name='name',          widget='Text')
@field_config(name='code',          widget='Text')
@field_config(name='key_name',      widget='Text',    hidden=True)
@field_group(name='Country details',  panels=[
   {'name': 'Details', 'fields': ['name', 'code']},
])
@model_settings(group='User', description='A country is a region legally identified as a distinct entity in political geography.')
class Country(dmodels.Model):
   ## @var name
   #  Country name
   name = dmodels.CharField(max_length=64)
   ## @var code
   #  Code of the language by ISO 639-1 Code standard (Upgradeable to ISO 639-2 Code standard)
   code = dmodels.CharField(max_length=2, db_index=True)
   ## @var key_name
   #  Unique identifier of the country
   key_name = dmodels.CharField(max_length=64, db_index=True)

   def __unicode__(self):
      return self.name

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "country"
      ordering = ["id"]
      unique_together = ('code', )

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2(self.name)
      super(Country, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/country/%s' % self.name)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Address
#
#  User address
#
@field_config(name='first_name', widget='Text')
@field_config(name='last_name',  widget='Text')
@field_config(name='address',    widget='Text')
@field_config(name='address2',   widget='Text')
@field_config(name='country',        widget='Models',  defaults=dict(model='country'))
@field_config(name='postcode',   widget='Text')
@field_config(name='city',    widget='Text')
@field_group(name='Address details',  panels=[
   [{'fields': ['first_name', 'last_name', 'address', 'address2']}],
   [{'fields': ['postcode', 'city', 'country']}]
])
@model_settings(group='User', description="A code and abstract concept expressing a location on the Earth's surface .")
class Address(dmodels.Model):
   ## @var name
   #  User name
   first_name     = dmodels.CharField(max_length=255, null=True, blank=True)
   ## @var surname
   #  User surname
   last_name      = dmodels.CharField(max_length=255, null=True, blank=True)
   ## @var address
   #  Address address
   address        = dmodels.CharField(max_length=255)
   ## @var address
   #  Address address
   address2        = dmodels.CharField(max_length=255, null=True, blank=True)
   ## @var city
   #  Address city
   city  = dmodels.CharField(max_length=255, db_index=True)
   ## @var postcode
   #  Address postcode
   postcode  = dmodels.CharField(max_length=64)
   ## @var country
   #  Linked country to address
   country  = dmodels.ForeignKey(Country, null=True, blank=True, db_index=True)

   def __unicode__(self):
      return "%s %s" % (self.address, self.city)

   def __str__(self):
      return force_bytes('%s %s' % (self.address, self.city))

   class Meta:
      app_label = 'core'
      db_table = "address"
      ordering = ["id"]
      index_together = []


## User
#
#  Core user to login into the system etc.
#
@field_config(name='email',         widget='Email')
@field_config(name='password',      widget='Password')
@field_config(name='name',          widget='Text')
@field_config(name='surname',       widget='Text')
@field_config(name='groups',        widget='Models',  defaults=dict(model='group'))
@field_config(name='permissions',   widget='Permissions')
#@field_config(name='addresses',     widget='Models',  create_new=True,  linked_only=True,  multiple=True,   defaults=dict(model='address'))
@field_config(name='last_login',    widget='Text')
#@field_config(name='image',         widget='Image',   count=1,  owner_only=True,    template="form_elements_image", scales=[
#   dict(name='Profile image', prefix='usrprofi', width=240, height=240, crop=True),
#])
#@field_config(name='date_of_birth', widget='HtmlDateTime')
#@field_config(name='gender',        widget='SelectDefaults', defaults={'items': {'none': 'None', 'male': 'Male', 'female': 'Female'}, 'items_order': ['none', 'male', 'female']}, multiple=False)
#@field_group(name='Profile image', panels=[
#   {'name': 'User image', 'fields': ['image']}
#])
@field_group(name='User access informations', panels=[
   {'name': 'Groups', 'fields': ['groups']},
   {'name': 'Permissions', 'fields': ['permissions']},
   #{'name': 'Addresses', 'fields': ['addresses']}
], permissions=['admin.superuser_access'])
@field_group(name='User login informations', panels=[
   {'name': 'Login informations', 'fields': ['email', 'password']},
])
@field_group(name='User details', panels=[
   {'name': 'Basic nformation', 'fields': ['name', 'surname']},
   #{'name': 'Addresses', 'fields': ['addresses']}
])
@model_settings(group='User', description='A user need to have an account and is identified by a username (also email).')
class User(dmodels.Model):
   ## @var email
   #  User email address for authentication
   email       = dmodels.EmailField(db_index=True)
   ## @var password
   #  User password for authentication
   password    = dmodels.CharField(max_length=64, db_index=True)
   ## @var name
   #  User name
   name     = dmodels.CharField(max_length=128, db_index=True)
   ## @var surname
   #  User surname
   surname  = dmodels.CharField(max_length=128, db_index=True)
   ## @var groups
   #  List of groups in user
   groups      = dmodels.ManyToManyField(Group)
   ## @var permissions
   #  List of permissions for user
   permissions = JsonField(null=True, blank=True)
   ## @var addresses
   #  List of addresses for user
   #addresses = dmodels.ManyToManyField(Address, through="UserAddress")
   ## @var last_login
   #  Date time of last login
   last_login  = dmodels.DateTimeField(null=True, blank=True, db_index=True)
   ## @var postcode
   #  Address postcode
   #image   = dmodels.ManyToManyField(File)
   #image   = dmodels.ForeignKey(File, null=True, blank=True)
   ## @var date_of_birth
   #  Date of birth
   #date_of_birth = dmodels.DateTimeField(db_index=True, null=True, blank=True)
   ## @var gender
   #  User gender
   #gender = dmodels.CharField(max_length=6, db_index=True)

   def __unicode__(self):
      return self.email

   def __str__(self):
      return force_bytes('%s' % self.email)

   class Meta:
      app_label = 'core'
      db_table = "user"
      ordering = ["id"]
      unique_together = ('email', )
      index_together = [['email', 'password'], ]

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None, change_password=True):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2(self.email)
      if change_password and self.password:
         hash_password = True
         if self.id:
            old_user = User.objects.get(id=self.id)
            # has the password already been hashed
            if old_user.password == self.password:
               hash_password = False

         if hash_password:
            self.password = hash_it(self.password)

      #if type(self.permissions) is list:
      #   self.permissions = json.dumps(self.permissions)

      super(User, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/user/%s' % self.email)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## User address
#
class UserAddress(dmodels.Model):
   user = dmodels.ForeignKey(User)
   address = dmodels.ForeignKey(Address)
   enabled = dmodels.BooleanField(default=True)

   class Meta:
      app_label = 'core'
      db_table = "user_address"
      ordering = ["id"]
      unique_together = ('user', 'address')
      index_together = [['user', 'address'], ]


## Page
#
@field_config(name='parent',        widget='Parents',    base_widget='Models',  defaults=dict(model='page'))
@field_config(name='name',          widget='Text')
@field_config(name='key_name',      widget='Text',    hidden=True)
@field_config(name='enabled',       widget='ToggleButton')
@field_config(name='layout',        widget='Layouts',    base_widget='Select2')
@field_config(name='permissions',   widget='Permissions')
@field_config(name='blocks',        widget='Blocks',  template="form_elements_blocks")
@field_config(name='assets',        widget='Assets')
@field_group(name='Page assets', panels=[
   {'name': 'Assets', 'fields': ['assets']},
])
@field_group(name='Page blocks', panels=[
   {'name': 'Blocks', 'fields': ['blocks']},
])
@field_group(name='Page details', panels=[
   {'name': 'Basic details', 'fields': ['name', 'parent']},
   {'name': 'Details', 'fields': ['enabled', 'layout']},
   {'name': 'Permissions', 'fields': ['permissions']}
])
@model_settings(group='Page', description='A web page is a web document that is suitable for the World Wide Web and can be accessed through a web browser and displayed on a monitor or mobile device.')
class Page(dmodels.Model):
   ## @var parent
   #  Parent of the page
   parent      = dmodels.ForeignKey('self', null=True, blank=True)
   ## @var name
   #  Page name
   name        = dmodels.CharField(max_length=64, db_index=True)
   ## @var key_name
   #  Unique identifier of the layout
   key_name    = dmodels.CharField(max_length=64, db_index=True)
   ## @var enabled
   #  Status if the page is enabled
   enabled     = dmodels.BooleanField(default=True)
   ## @var layout
   #  Page layout
   layout      = dmodels.CharField(max_length=255, db_index=True)
   ## @var permissions
   #  Page permissions
   permissions = JsonField(null=True, blank=True)
   ## @var blocks
   #  Page blocks
   blocks      = JsonField(null=True, blank=True)
   ## @var assets
   #  Page assets
   assets      = JsonField(null=True, blank=True)

   #
   #  remove unnecessary help text
   #
   permissions.help_text = ''
   blocks.help_text = ''
   assets.help_text = ''

   #
   #  temporary counter
   #
   wepo_counter = 0

   def __unicode__(self):
      return self.name

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "page"
      ordering = ["id"]
      unique_together = ('key_name', )

   ## Custom delete method
   #
   def delete(self):
      #
      #  disable page, don't delete it
      #
      self.enabled = False
      self.save()
      return 'disabled'

   ## Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2(self.name)
      #if type(self.blocks) is dict:
      #   self.blocks = json.dumps(self.blocks)

      #if type(self.assets) is dict:
      #   self.assets = json.dumps(self.assets)

      #if type(self.permissions) is list:
      #   self.permissions = json.dumps(self.permissions)

      super(Page, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self, page=self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper import build_url
      from core.helper.common_help import get_cache_key_2
      return build_url(self.key_name.split('-'))

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Seo
#
@model_settings(group='Page', description='Search engine optimization (SEO) is the process of affecting the visibility of a website or a web page in a search engines "natural" or un-paid ("organic") search results')
class Seo(dmodels.Model):
   ## @var url
   #  Url of the seo link
   url            = dmodels.URLField(db_index=True, max_length=255)
   ## @var key_name
   #  Unique identifier of the menu item
   key_name       = dmodels.CharField(max_length=255, db_index=True)
   ## @var redirect
   #  Redirect to another seo link
   redirect       = dmodels.ForeignKey('self', null=True, blank=True)
   ## @var content
   #  Id of the content with which the seo is linked
   content        = dmodels.PositiveIntegerField(null=True, blank=True)
   ## @var content content
   #  Type of the content with which the seo is linked (usually model name,...)
   content_type   = dmodels.CharField(max_length=128, db_index=True, null=True, blank=True)
   ## @var enabled
   #  Status if the seo link is enabled
   enabled         = dmodels.BooleanField(default=True)
   ## @var page
   #  Page to display under this seo
   page           = dmodels.ForeignKey(Page, null=True, blank=True)
   ## @var callback
   #  Block callback
   callback       = dmodels.TextField(null=True, blank=True)

   def __unicode__(self):
      return self.url

   def __str__(self):
      return force_bytes('%s' % self.url)

   class Meta:
      app_label = 'core'
      db_table = "seo"
      ordering = ["page"]
      unique_together = ('key_name', )

   ## Custom delete method
   #
   def delete(self):
      #
      #  disable seo, don't delete it
      #
      self.enabled = False
      self.save()
      return 'disabled'

   ## Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key
      self.key_name = get_cache_key(self.url).replace(':', '-')
      super(Seo, self).save(force_insert, force_update, using, update_fields)

   ## Get seo for model
   #
   #  @param model Model
   #
   @classmethod
   def get_model_seo(cls, model):
      seo = Seo.objects.filter(content=model.id, content_type=model._meta.db_table, enabled=1)
      if seo and len(seo) > 0:
         return seo[0]

      return None


   ## Update/create seo for model
   #
   @classmethod
   def update_seo(cls, model, page=None, block=None, force_new=True):
      from core.helper.common_help import get_cache_key
      if hasattr(model, '_get_seo_link'):
         #
         #  get url and prepare seo key_name
         #
         url = model._get_seo_link()
         key_name = get_cache_key(url).replace(':', '-')

         id = model.id
         type = model._meta.db_table

         #
         #  prepare new seo
         #
         s = Seo()
         s.url = url
         s.key_name = key_name
         s.content = id
         s.content_type = type
         s.enabled = True
         s.page = page
         s.block = block
         # s.language

         #
         #  check for old seo
         #
         old_seo = Seo.objects.filter(content=id, content_type=type, enabled=1)
         if old_seo and len(old_seo) > 0:
            old_seo = old_seo[0]
            if old_seo.key_name == key_name:
               return old_seo
            else:
               if force_new:
                  test_old = Seo.objects.filter(key_name=s.key_name, content=id, content_type=type)
                  if test_old and len(test_old) > 0:
                     test_old = test_old[0]
                     test_old.enabled = True
                     test_old.redirect = None
                     test_old.save()
                     old_seo.redirect = test_old

                  else:
                     old_seo.redirect = s
                     s.save()

                  old_seo.enabled = False
                  old_seo.save()
         else:
            s.save()

      return s

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Menu
#
#  (Main menu, Admin side menu, Admin top menu, ...)
#
@field_config(name='name',          widget='Text')
@field_config(name='key_name',      widget='Text',    hidden=True)
@field_group(name='Details', panels=[
   {'name': 'Details', 'fields': ['name']}
])
@model_settings(group='Menu', description='A menu is a list of options or commands presented to the user.')
class Menu(dmodels.Model):
   ## @var name
   #  Name of the menu
   name     = dmodels.CharField(max_length=64)
   ## @var key_name
   #  Unique identifier of the menu
   key_name = dmodels.CharField(max_length=64, db_index=True)

   def __unicode__(self):
      return "%s" % (self.name, )

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "menu"
      unique_together = ('key_name', )

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2(self.name)
      super(Menu, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/menu/%s' % self.name)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Menu item
#
#  (Main menu, Admin side menu, Admin top menu, ...)
#
@field_config(name='name',          widget='Text')
@field_config(name='seo',           widget='Models', defaults=dict(model='seo'))
@field_config(name='url',           widget='Text')
@field_config(name='key_name',           widget='Text',    hidden=True)
@field_config(name='parent',        widget='Models', defaults=dict(model='menu_item'))
@field_config(name='menu',          widget='Models', defaults=dict(model='menu'))
@field_config(name='sort',          widget='Text')
@field_config(name='level',         widget='Text')
@field_config(name='enabled',       widget='ToggleButton')
@field_config(name='permissions',   widget='Permissions')
@field_group(name='Permissions', panels=[
   {'name': 'Permissions', 'fields': ['permissions']}
])
@field_group(name='Details', panels=[
   {'name': 'Details', 'fields': ['name', 'enabled']},
   {'name': 'Links', 'fields': ['seo', 'url']},
   {'name': 'Advanced', 'fields': ['parent', 'menu']},
   {'name': 'Order', 'fields': ['level', 'sort']}
])
@model_settings(group='Menu items', description='A menu item is a menu list option or command presented to the user.')
class MenuItem(dmodels.Model):
   ## @var name
   #  Name of the menu item
   name     = dmodels.CharField(max_length=255)
   ## @var key_name
   #  Unique identifier of the menu item
   key_name = dmodels.CharField(max_length=255, db_index=True)
   ## @var seo
   #  Seo link, linked to the menu item
   seo      = dmodels.ForeignKey(Seo, null=True, blank=True)
   ## @var url
   #  Extra menu item url
   url      = dmodels.URLField()
   ## @var parent
   #  Parent menu item
   parent   = dmodels.ForeignKey('self', null=True, blank=True)
   ## @var menu
   #  Menu of the relation
   menu     = dmodels.ForeignKey(Menu, db_index=True)
   ## @var sort
   #  Numerical position of the relation
   sort     = dmodels.PositiveSmallIntegerField(default=0)
   ## @var level
   #  Level of the relation
   level    = dmodels.PositiveSmallIntegerField(default=0)
   ## @var enabled
   #  Status if the relation is enabled
   enabled  = dmodels.BooleanField(default=True)
   #  List of permissions in group
   permissions = JsonField(null=True, blank=True)

   def __unicode__(self):
      return "%s - %s" % (self.menu.name, self.name, )

   def __str__(self):
      return force_bytes("%s - %s" % (self.menu.name, self.name, ))

   class Meta:
      app_label = 'core'
      db_table = "menu_item"
      unique_together = ('key_name', )

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2('%s-%s' % (self.menu.name, self.name))
      super(MenuItem, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/%s/%s' % (self.menu.name, self.name))

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)









## Language
#
#  Language
#
@field_config(name='name',       widget='Text')
@field_config(name='code',       widget='Text')
@field_config(name='key_name',           widget='Text',    hidden=True)
@field_group(name='Details',    panels=[
   {'name': 'Details', 'fields': ['name', 'code']}
])
@model_settings(name='Language', description='Language')
class Language(dmodels.Model):
   ## @var name
   #  Name of the language
   name        = dmodels.CharField(max_length=255, db_index=True)
   ## @var code
   #  Short code of the language
   code        = dmodels.CharField(max_length=255, db_index=True)
   ## @var key_name
   #  Unique identifier of the language
   key_name = dmodels.CharField(max_length=255, db_index=True)

   def __unicode__(self):
      return "%s" % (self.name, )

   def __str__(self):
      return force_bytes('%s' % self.name)

   class Meta:
      app_label = 'core'
      db_table = "language"

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2('%s' % self.code)
      super(Language, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/language/%s' % self.key_name)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Phrase
#
#  Phrase
#
@field_config(name='text',       widget='Text')
@field_config(name='key_name',           widget='Text',    hidden=True)
@field_group(name='Details',    panels=[
   {'name': 'Details', 'fields': ['text']}
])
@model_settings(name='Phrase', description='Phrase')
class Phrase(dmodels.Model):
   ## @var name
   #  Name of the translation source
   text        = dmodels.CharField(max_length=255, db_index=True)
   ## @var key_name
   #  Unique identifier of the translation source
   key_name = dmodels.CharField(max_length=255, db_index=True)

   def __unicode__(self):
      return "%s" % (self.text, )

   def __str__(self):
      return force_bytes('%s' % self.text)

   class Meta:
      app_label = 'core'
      db_table = "phrase"

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2('%s' % self.text)
      super(Phrase, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/phrase/%s' % self.key_name)

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)


## Translation
#
#  Translation
#
@field_config(name='translation',       widget='Text')
@field_config(name='key_name',           widget='Text',    hidden=True)
@field_config(name='language',   widget='Models', defaults=dict(model='language'))
@field_config(name='phrase',   widget='Models', defaults=dict(model='phrase'),    hidden=True)
@field_group(name='Details',    panels=[
   {'name': 'Details', 'fields': ['translation', 'language', 'phrase']}
])
@model_settings(name='Translation', description='Translation')
class Translation(dmodels.Model):
   ## @var name
   #  Translation
   translation        = dmodels.CharField(max_length=255)
   ## @var key_name
   #  Unique identifier of the language
   key_name = dmodels.CharField(max_length=255, db_index=True)
   ## @var menu
   #  Source of the translation
   phrase     = dmodels.ForeignKey(Phrase, db_index=True)
   ## @var menu
   #  Language of the translation
   language     = dmodels.ForeignKey(Language, db_index=True)

   def __unicode__(self):
      return "%s" % (self.translation, )

   def __str__(self):
      return force_bytes('%s' % self.translation)

   class Meta:
      app_label = 'core'
      db_table = "translation"
      ordering = ["-id"]

   ##  Custom save method
   #
   def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
      from core.helper.common_help import get_cache_key_2
      self.key_name = get_cache_key_2('%s' % self.translation)
      super(Translation, self).save(force_insert, force_update, using, update_fields)
      Seo.update_seo(self)

      # update cache
      from core import cache
      from core.helper.common_help import get_cache_key
      cache_key = get_cache_key('translation', self.language.code, self.phrase.key_name)
      cache.set(cache_key, self)

   ##  Generate seo link
   #
   def _get_seo_link(self):
      from core.helper.common_help import get_seo_link
      return get_seo_link('/translation/%s/%s' % (self.language.key_name, self.key_name))

   ## Get seo link
   #
   def get_seo(self):
      return Seo.get_model_seo(self)