#! /usr/bin/python
#
#  Core user, authentication manager
#

from datetime import datetime
import urllib, json

from django.template.loader import get_template
from django.template import Context
from django.shortcuts import redirect

from core.helper.common_help import hash_it, redirect_to_login
from core.models import User
from core.helper.message_help import add_message


## Authenticate user callback
#
#  @param request Current request
#
def authenticate(request):
   if request.method == 'POST':
      #
      #  check for errors
      #
      error = False

      destination_after_authentication = request.POST.get('destination', '/')

      user_id = request.POST.get('user_id', '')
      password = request.POST.get('password', '')

      if user_id == '':
         error = True
         add_message(request, 'error', 'Field error', 'Please enter a valid username.')
      if password == '':
         error = True
         add_message(request, 'error', 'Field error', 'Please enter a valid password.')

      if not error:
         #
         #  try to login user
         #
         user = user_authenticate(request, user_id, password)
         if user:
            login(request, user)
            return redirect(destination_after_authentication)

         add_message(request, 'login_error', message='The given information is invalid.', persistent=True)

   #
   #  check if user is already authenticated in and redirect it to index
   #
   user = get_user(request)
   if user:
      return redirect(destination_after_authentication)

   #
   #  cannot authenticate user, show message on login page
   #
   return redirect_to_login(request, url=destination_after_authentication)


## Authenticate user
#
#  @param request Current request object
#  @param email User email address
#  @param password User password
#
#  @return user if exists, otherwise False
#
def user_authenticate(request, email, password):
   #
   #  try to authenticate
   #
   user = User.objects.filter(email=email, password=hash_it(password))

   if len(user) != 0:
      return user[0]
   else:
      return False


## Login
#
#  @param request Current request object
#  @param user User object saved to session
#
def login(request, user):
   #
   #  save user to session
   #
   request.session['authenticated'] = True
   request.session['login_date'] = datetime.now()

   user.last_login = datetime.now()
   user.save(change_password=False)
   request.session['user'] = user


## Get user
#
#  @param request Current request object
#
#  @return user
#
def get_user(request):
   if 'user' in request.session:
      return request.session['user']

   return None


## Get user permissions
#
#  @param request Current request object
#
def get_user_permissions(request):
   user = get_user(request)
   permissions = []

   if user and user.permissions:
      permissions = user.permissions

   #
   #  add user group permissions
   #
   group_permissions = get_user_group_permissions(request)
   for group_permission in group_permissions:
      if not group_permission in permissions:
         permissions.append(group_permission)

   return permissions


## Get user group permissions
#
#  @param request Current request object
#
def get_user_group_permissions(request):
   user = get_user(request)
   permissions = []

   if user:
      for group in user.groups.all():
         if group.permissions:
            permissions += group.permissions

   return permissions


## Logout user
#
#  @param request Current request object
#
def logout(request):
   #
   #  load authenticated user and logout it
   #
   user = get_user(request)
   if user:
      request.session.flush()

   destination = request.GET.get('destination', '/')
   return redirect(destination)


## Change default language
#
#  @param request Current request object
#
def change_language(request):
   from wepo.settings import DEFAULT_LANGUAGE
   language = DEFAULT_LANGUAGE
   if len(request.wepo.url_parts) > 3:
      language = request.wepo.url_parts[3]

   request.session['user_language'] = language

   return redirect(request.GET.get('destination', '/'))

## Is authenticated
#
#  @param request Current request object
#
def is_authenticated(request):
   #
   #  check if is authenticated
   #
   return get_user(request) is not None


## User data block
#
#  @param request Current request object
#  @param block Block object to be rendered
#  @param attributes Optional block additional attributes
#
def user_data(request, block, attributes={}):
   template = get_template('user_data.html')

   context = {
      'user_email': ''
   }

   user = get_user(request)
   if user:
      context['user_email'] = user.email

   return template.render(Context(context))


## User login
#
#  @param request Current request object
#  @param block Block object to be rendered
#  @param attributes Optional block additional attributes
#
#  @return Page after successful login
#
def core_user_authenticate(request, block, attributes={}):

   if request.method == 'POST':
      #
      #  check for errors
      #
      error = False

      destination_after_authentication = request.POST.get('destination', '/')

      email = request.POST.get('email', '')
      password = request.POST.get('password', '')

      if email == '':
         error = True
         add_message(request, 'error', 'Please enter a valid username.', '')
      if password == '':
         error = True
         add_message(request, 'error', 'Please enter a valid password.', '')

      if not error:
         #
         #  try to login user
         #
         user = authenticate(request, email, password)
         if user:
            login(request, user)
            return redirect(destination_after_authentication)

         add_message(request, 'error', '  The given information is invalid.', '')

   #
   #  check if user is already authenticated in and redirect it to index
   #
   user = get_user(request)
   if user:
      return redirect(destination_after_authentication)

   #
   #  cannot authenticate user, show message on login page
   #
   return redirect_to_login(request)
