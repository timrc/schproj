#! /usr/bin/python
#
#  Wepo administration user blocks
#

from django.template.loader import get_template
from django.template import Context
from core.form import Form


## Admin user login form
#
def login_form(request, block):
   request.wepo.body_class = 'login-body'

   form = Form(request=request, action='/user/authenticate', method='post', **{'class': 'no-margin'})
   form.auto_close = False
   form.add_item(type='Html', tag='h2', value='Prijava v administracijo', **{'class': 'form-title'})


   # Input data
   fieldset = form.add_group()


   # Email input
   group = fieldset.add_group(type='div', **{'class': 'form-group no-margin'})

   # field label
   group.add_item(type='Label', value='E-naslov', **{'for': 'user_id'})

   # wrappper
   input_group = group.add_group(type='div', **{'class': 'input-group input-group-lg'})

   # field icon
   input_icon = input_group.add_group(type='span', **{'class': 'input-group-addon'})
   input_icon.add_item(type='Html', tag='i', **{'class': 'icon-user'})

   # field
   input_group.add_item(type='Email', name='user_id', placeholder='E-naslov', **{'class': 'form-control input-lg'})


   # Password input
   group = fieldset.add_group(type='div', **{'class': 'form-group no-margin'})

   # field label
   group.add_item(type='Label', value='Geslo', **{'for': 'password'})

   # wrappper
   input_group = group.add_group(type='div', **{'class': 'input-group input-group-lg'})

   # field icon
   input_icon = input_group.add_group(type='span', **{'class': 'input-group-addon'})
   input_icon.add_item(type='Html', tag='i', **{'class': 'icon-lock'})

   # field
   input_group.add_item(type='Password', name='password', placeholder='Geslo', **{'class': 'form-control input-lg'})


   # Hidden destination
   form.add_item(type='Hidden', name='destination', value=request.GET.get('destination', '/'))

   from core.helper.message_help import get_messages, del_messages
   login_error_messages = get_messages(request, 'login_error')
   if login_error_messages:
      del_messages(request, 'login_error')

   template = get_template('admin/login.html')
   context = {
       'form': form,
       'error_messages': login_error_messages
   }
   return template.render(Context(context))