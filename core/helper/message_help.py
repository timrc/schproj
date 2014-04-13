#! /usr/bin/python
#
#  Core message handler and functions helpers
#


## Add message to current request
#
#  @param request Current request
#  @param type Type of the message
#  @param title Message title
#  @param message Description of message
#  @param attributes Extra message attributes
#
def add_message(request, type, title='', message='', attributes={}, persistent=False):
   if not 'messages' in request.session:
      request.session['messages'] = {'success': [], 'info': [], 'warning': [], 'error': []}

   if not type in request.session['messages']:
      request.session['messages'][type] = []

   request.session['messages'][type].append({
      'title': title,
      'message': message,
      'attributes': attributes,
      'persistent': persistent
   })


## Get message
#
#  @param request Current request
#  @param type Type of the message
#
def get_messages(request, type):
   if not 'messages' in request.session:
      return []

   if not type in request.session['messages']:
      return []

   return request.session['messages'][type]


## Delete messages of type
#
#  @param request Current request
#  @param type Type of the message
#
def del_messages(request, type):
   if not 'messages' in request.session:
      return False

   if not type in request.session['messages']:
      return False

   del request.session['messages'][type]
   return True