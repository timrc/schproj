#! /usr/bin/python
#
#  Wepo core actions - ajax callbacks
#

from helper import get_module, get_function


## Invoke called callback
#
#  @param request Current request
def invoke_callback(request):
   callback = request.wepo.seo.callback
   callback_path = callback.split('.')
   callback_name = callback_path[-1]
   callback_path = callback_path[:-1]
   module = get_module(callback_path)
   if module:
      function_call = get_function(module, callback_name)
      if function_call:
         return function_call(request)

   return None