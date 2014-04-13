#! /usr/bin/python
#
#  Wepo core error templates
#

from django.template.loader import get_template
from django.template import Context


## Core error page handler
#
#  @param request Request - current request
#  @param block Block object - block to be rendered
#  @param attributes Optional block additional attributes
#
def core_error_page(request, block, attributes={}):
   template = get_template('error_page.html')

   error_type = request.url_parts[-1] if len(request.url_parts) > 0 else '404'

   error_message = 'Page Not Found (404)'
   if error_type == '403':
      error_message = 'Page Forbidden (403)'

   context = {
      'error_type': error_type,
      'error_message': error_message
   }

   return template.render(Context(context))