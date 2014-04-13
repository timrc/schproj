#! /usr/bin/python
#
#  Wepo user blocks
#


from core.user import user_logout
from django.shortcuts import redirect


## User logout
#
#  @return Redirect to index or after_logout page
#
def logout(request, block, attributes={}):
   user_logout(request)
   return redirect('/', logout=True)