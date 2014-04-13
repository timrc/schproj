#! /usr/bin/python
#
#  Wepo core model decorators
#


from core.helper import dict_to_obj


## Add extra field config to class
#
#  @param object Model which will be configured
#
class model_field_configuration(object):
   ## Save passed arguments
   #
   #  @param name Field name to be extended
   #  @param data Field data
   #
   def __init__(self, name, **data):
      self.name = name
      self.data = data

   ## Configure field
   #
   #  get name of the field and widget name from arguments
   #  check if current field is title field in model
   #
   #  @param cls Object we are configuring
   #
   def __call__(self, cls):
      name = self.name
      setattr(cls, '%s__config' % name, dict_to_obj(self.data))

      return cls


## Group fields together
#
#  @param object Model which will be configured
#
class field_group(object):
   ## Save passed arguments
   #
   #     @param kws Arguments
   #
   def __init__(self, name, panels, **data):
      self.name = name
      self.panels = panels
      self.data = data

   ## Configure field
   #
   #  get group name and fields from arguments
   #
   #  @param cls Object we are configuring
   #
   def __call__(self, cls):
      name = self.name
      panels = self.panels

      if not hasattr(cls, 'field__groups'):
         setattr(cls, 'field__groups', [])

      cls.field__groups.append({'name': self.name, 'panels': self.panels, 'data': self.data})

      return cls


## Put model into group
#
#  @param object Model which will be configured
#
#  **Usage**
#  ~~~~~~~~~~~~~~~{.py}
#  @model_settings(group='group_name', description='Model description, Lorem ipsum dolor sit amet...')
#  ~~~~~~~~~~~~~~~
#
class model_settings(object):
   ## Save passed arguments
   #
   #     @param kws Arguments
   #
   def __init__(self, **kws):
      self.kws = kws

   ## Configure model group
   #
   #  set group for model
   #
   #  @param cls Object we are configuring
   #
   def __call__(self, cls):
      for key, value in self.kws.items():
         setattr(cls, '_model_%s' % key, value)

      return cls