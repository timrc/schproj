#! /usr/bin/python
#
#  Wepo core user permissions
#

import urllib
from core.user import get_user
from django.shortcuts import redirect


## Administration permission callback
#
#  @param request Current request
#  @param attributes Permission extra attributes
#     - ['/user/login']: provides url to redirect user if not authenticated
#
def authenticated(request, attributes=None):

   redirect_url = attributes[0] if attributes else '/user/login'
   url_parameters = {}
   if attributes and len(attributes) > 1:
      url_parameters = attributes[1]

   url_parameters = urllib.urlencode(url_parameters)
   if url_parameters:
      redirect_url = '%s?%s' % (redirect_url, url_parameters)

   #
   #  redirect user to login if not logged in
   #
   user = get_user(request)
   if not user:
      return False, redirect(redirect_url)
   else:
      return True, None