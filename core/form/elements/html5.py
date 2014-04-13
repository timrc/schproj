#! /usr/bin/python
#
#  Core wepo form html5 elements
#

from core.form.elements import Input


## Form email input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered email input field
#
def Email(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'email'

   return Input(request, **attributes)


## Form html date input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered html date input field
#
def HtmlDate(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'date'

   return Input(request, **attributes)


## Form html date time input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered html date input field
#
def HtmlDateTime(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'datetime-local'

   return Input(request, **attributes)


