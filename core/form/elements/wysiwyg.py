#! /usr/bin/python
#
#  Core wepo form wysiwyg elements
#

from core.form.elements import Textarea


## Form tinymce
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered generic input field
#
def TinyMCE(request, **data):
   from django.template import Context

   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   from random import random
   unique_id = 'text_%d' % int(random() * 1000000)
   attributes['id'] = unique_id

   #
   #  block assets
   #
   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='script', code=wepo_assets.script.tinymce, position='footer')
   add_asset(request, type='script', code="""
      tinymce.init({
          selector: "#%s",
          plugins: [
              "advlist autolink lists link image charmap print preview anchor",
              "searchreplace visualblocks code fullscreen",
              "insertdatetime media table contextmenu paste"
          ],
          toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image"
      });
   """ % unique_id, include_type='code', position='footer')

   #attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in attributes.items())
   #value = data['value'] if 'value' in data else ''
   #return '<div %s />%s</div>' % (attributes, value)

   return Textarea(request, **attributes)