#! /usr/bin/python
#
#  Wepo core template filters
#

from django.template import Library


register = Library()


## Divide list length from dividend
#
#  @param lst List of elements
#  @param dividend Number to divide from
#
@register.filter(name='divide_list_size_from')
def divide_list_size_from(lst, dividend):
   if len(lst) > 0:
      return dividend / len(lst)
   else:
      return dividend


## Render model field
#
#  @param model Model
#  @param field Field
#
@register.filter(name='render_field')
def render_field(model, field):
   pass


## Translate text
#
#  @param text Text to translate
#  @param lang Language to translate text to
#
@register.filter(name='_')
@register.filter(name='translate')
def translate(text, lang=None):
   text = str(text)
   from core.helper import get_request
   from core.language import translate as trans
   request = get_request()
   return trans(request, text)


## Get file tag
#
#  @param file File to get tag from
#
@register.filter(name='file_tag')
def file_tag(file):
   from core.helper.file_help import get_file_tag
   return get_file_tag(file)


## Get file extension
#
#  @param file File to get extension from
#
@register.filter(name='file_extension')
def file_extension(file):
   from core.helper.file_help import get_file_type
   file_type = get_file_type(file)

   ext = file_type['extension'].replace('.', '')

   return ext


## Get file known extension
#
#  @param file File to get rough mime type from
#
@register.filter(name='known_file_extension')
def known_file_extension(file):
   from core.helper.file_help import get_file_rough_mime_type
   return get_file_rough_mime_type(file)


## Load image of size
#
#  @param file File to check if it's image
#
@register.filter(name='image')
def image(file, size):
   if not file:
      return ''

   if size and is_image(file):
      return '/media/%s/%s_%s' % (file.path, size, file.file_name)

   return '/media/%s/%s' % (file.path, file.file_name)


## Is file image
#
#  @param file File to check if it's image
#
@register.filter(name='is_image')
def is_image(file):
   return file.mime_type.startswith('image')


## Return true if attribute exists on object and is false
#
#  @param object Object
#  @param key Key to check
#
@register.filter(name='exists_and_false')
def exists_and_false(object, key):
   if hasattr(object, key):
      value = getattr(object, key)
      if not value:
         return True

   return False


## Check if wepo form field has label enabled
#
@register.filter(name='wepo_label_visible')
def wepo_label_visible(field):
   if hasattr(field.field.widget.attrs['data-wepo'], 'hide_label'):
      return field.field.widget.attrs['data-wepo'].hide_label

   return True


## Returns attribute value from object
#
#  @param object Object
#  @param key Key to retrieve
#
#  @return A value of key
#
@register.filter(name='get_attribute')
def get_attribute(object, key):
   return getattr(object, key)


## Check if field can be displayed in list
#
#  @param field Field to check
#
#  @return status if field is visible
#
@register.filter(name='is_field_visible_in_list')
def is_field_visible_in_list(field):
   return not (field.field_type.id == 17 or field.field_type.id == 18 or field.field_type.id == 19 or field.field_type.id == 27);


## Join key value from dictionary
#
#  @param dict Dictionary to join
#
#  @return Joined key value pairs
#
@register.filter(name='join_key_value')
def join_key_value(dict):
   if dict == {}:
      return ' '.join(('%s="%s"' % (key, dict[key])) for key in dict.keys())
   else:
      return ''


## Change attribute in url parameter
#
#  @param url Url to change
#  @param key Key to remove from url
#
#  @return changed url
#
@register.filter(name='remove_url_key')
def remove_url_key(url, key):
   if not type(url) == type({}):
      return "?"
      
   q = url.copy()
   if key in q:
      q.pop(key)
   return_url = q.urlencode()
   if len(return_url) == 0:
      return "?"
   else:
      return "?%s&" % return_url


## Remove menu item prefix
#
#  @param menu_item_name Name (Key name) of the menu item
#
@register.filter(name='menu_menu_item_key_name')
def menu_menu_item_key_name(menu_item):
   key_name = menu_item.key_name
   menu_key_name = menu_item.menu.key_name
   return key_name.replace('%s-' % menu_key_name, '')


## Get model seo link
#
#  @param model seo
#
@register.filter(name='seo')
def seo(model):
   return model.get_seo()


## Parse to seo friendly string
#
#  @param text Text to convert
#
@register.filter(name='seo_friendly')
def seo_friendly(text):
   text = text.replace('_', '-')

   return text


## Beautify string
#
#  @param text Text to convert
#
@register.filter(name='beautify')
def beautify(text):
   text = text.replace('_', ' ')
   text = text.replace('-', ' ')

   return text


## Get file preview image
#
@register.filter(name='file_small_preview_image')
def file_small_preview_image(file):
   if file.mime_type.startswith('image/'):
      return file.get_seo()
   else:
      return '/assets/images/mimetypes48x48/%s.png' % file.mime_type.replace('/', '_')
