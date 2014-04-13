#! /usr/bin/python
#
#  Core wepo form button elements
#

from core.form.elements import Input


## Form reset button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered reset button input field
#
def ResetButton(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'reset'

   return Input(request, **attributes)


## Form submit button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered submit button input field
#
def SubmitButton(request, **data):
   attributes = {}
   for key, val in data.items():
      attributes[key] = val

   attributes['type'] = 'submit'

   return Input(request, **attributes)


## Form button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered button input field
#
def Button(request, **data):
   attributes = {}
   for key, val in data.items():
      if key not in ['value']:
         attributes[key] = val

   value = data['value'] if 'value' in data else ''
   attributes = ' '.join(('%s="%s"' % (k, v)) for k, v in data.items())

   return '<button %s>%s</button>' % (attributes, value)


## Form submit button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered submit button input field
#
def Submit(request, **data):
   return Button(request, type='submit', **data)


## Form reset button input field
#
#  @param data Field data
#     value='', name='', class='', id='', ...
#
#  @return rendered reset button input field
#
def Reset(request, **data):
   return Button(request, type='reset', **data)

