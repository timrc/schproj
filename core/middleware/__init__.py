#! /usr/bin/python
#
#  Core wepo middleware
#


from threading import current_thread


## Thread-safe middleware that makes the current request object available globally.
#
#  http://djangosnippets.org/snippets/2853/
#
class GlobalRequest(object):
   _requests = {}

   @staticmethod
   def get_request():
      try:
         return GlobalRequest._requests[current_thread()]
      except KeyError:
         return None

   def process_request(self, request):
      GlobalRequest._requests[current_thread()] = request

   def process_response(self, request, response):
      # Cleanup
      thread = current_thread()
      try:
         del GlobalRequest._requests[thread]
      except KeyError:
         pass
      return response