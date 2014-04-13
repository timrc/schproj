#! /usr/bin/python
#
#  Wepo core unit tests management
#

import unittest

from django.core.management.base import BaseCommand

from wepo.settings import APPS_DIR
from core.helper import get_module


## Wepo unit tests
#
class Command(BaseCommand):

   #
   # Options
   #
   option_list = BaseCommand.option_list
   help = 'Unit tests.'

   ## Command handler
   #
   #  @param args Extra arguments passed to the handler
   #  @param options Available options with command
   #
   def handle(self, *args, **options):
      path = args[0]
      test_name = args[1]

      if path != 'core':
         path = '%s.%s' % (APPS_DIR, path)

      path = '%s.unit.%s' % (path, test_name)
      module = get_module(path)

      cls = getattr(module, 'Test%s' % test_name)

      suite = unittest.TestSuite()
      for method in dir(cls):
         if method.startswith("test"):
            suite.addTest(cls(method))
      unittest.TextTestRunner().run(suite)