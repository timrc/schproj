#! /usr/bin/python
#
#  Wepo core database sync
#

from django.core.management.base import BaseCommand

from wepo.settings import INSTALLED_APPS
from core.helper import get_module


## Wepo sync db for installed apps
#
class Command(BaseCommand):

   ## Options
   #
   option_list = BaseCommand.option_list

   help = 'Import fixtures from installed applications.'

   ## Command handler
   #
   #  @param args Extra arguments passed to the handler
   #  @param options Available options with command
   #
   def handle(self, *args, **options):
      self.import_from_all()

   ## Import fixtures from all installed apps
   #
   def import_from_all(self):
      # load and sort apps
      apps = []
      for app in INSTALLED_APPS:
         if not app.startswith('django'):
            app_path = '%s.install' % app
            app_module = get_module(app_path)

            print 'Installing %s' % app
            instance = app_module.Install()

            # first import data from csv etc..
            if hasattr(instance, 'load_csv'):
               instance.load_csv()

            # import data
            instance.install()