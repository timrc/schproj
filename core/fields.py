#! /usr/bin/python
#
#  Wepo core fields
#


from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json


## JSONField is a generic textfield that neatly serializes/unserializes JSON objects seamlessly
#
class JsonField(models.TextField):
   #
   # Used so to_python() is called
   #
   __metaclass__ = models.SubfieldBase

   def get_custom_internal_type(self):
      return "JsonField"

   def to_python(self, value):
      #
      # Convert our string value to JSON after we load it from the DB
      #

      if value == "":
         return None

      try:
         if isinstance(value, basestring):
            return json.loads(value)
      #except ValueError:
      #   if value:
      #      return json.loads(value.replace("'", '"'))
      #   else:
      #      pass
      except ValueError, e:
         pass

      return value

   def get_db_prep_save(self, value, connection):
      #
      # Convert our JSON object to a string before we save
      #

      if value == "":
         return None

      if isinstance(value, dict) or isinstance(value, list):
         value = json.dumps(value, cls=DjangoJSONEncoder)

      return super(JsonField, self).get_db_prep_save(value, connection)