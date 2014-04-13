from django.db.models import Q
import operator, os
from wepo.settings import PROJECT_ROOT
from core.helper.model_help import get_model


## Import data from csv
#
def import_from_csv(data):
   #
   #  get basic data
   #
   file_name = data['file']
   type = data['type']
   module_name = data['module']
   model_name = data['model']
   fields = data['fields']
   method = data['method']

   path = '%s/apps/%s/install/%s' % (PROJECT_ROOT, module_name, file_name)
   if module_name == 'core':
      path = '%s/%s/install/%s' % (PROJECT_ROOT, module_name, file_name)

   #
   #  get model
   #
   model = get_model(None, model_name)
   model = model['model']

   #print 'Deleting old %ss' % model_name
   #model.objects.all().delete()

   print 'Importing %s from %s: ' % (type, file_name)
   counter = 0

   #
   #  import from csv
   #
   if type == 'csv':
      import csv

      delimiter = data['delimiter']

      #
      #  update data by fields
      #
      if method == 'update':
         update_fields = data['update_fields']
         with open(path, 'rb') as file:
            reader = csv.reader(file, delimiter=delimiter)
            for row in reader:
               #
               #  get old instance or create new instance
               #
               queries = []
               for field, field_index in update_fields.items():
                  kwargs = {'%s' % field: row[field_index]}
                  queries.append(Q(**kwargs))

               q = reduce(operator.or_, queries)
               instance = model.objects.filter(q)

               if instance:
                  instance = instance[0]

               if not instance:
                  instance = model()

               for field, field_index in fields.items():
                  setattr(instance, field, row[field_index])

               instance.save()
               counter += 1

   print 'Finished importing %d %ss: ' % (counter, model_name)