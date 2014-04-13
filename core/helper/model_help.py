#! /usr/bin/python
#
#  Core model classes and functions helpers
#

import os, sys

from core import cache
from django.db.models.base import ModelBase

from wepo.settings import INSTALLED_APPS
from core.helper.common_help import get_cache_key
from core.helper import get_module, dict_to_obj
# shortcuts
from core.language import translate as _t


## Get model for given key-name
#
#  @param request Current request object
#  @param key_name Key name of the model
#  @param by_model Return by model name instead of by model db name
#
#  @return Valid model or None
#
def get_model(request, key_name, by_model=False):
   cache_key = get_cache_key('model', key_name)
   model = cache.get(cache_key)
   if model:
      return model

   #
   #  get model from installed models
   #
   models = get_installed_models(by_model=by_model)
   if key_name in models:
      cache.set(cache_key, models[key_name])
      return models[key_name]

   return None


## Get models from installed apps
#
#  @param by_model Return by model name instead of by model db name
#
def get_installed_models(by_model=False):
   cache_key = get_cache_key('models', 'list', by_model)
   models = cache.get(cache_key)
   if models:
      return models

   #
   # do discovery on models
   #
   models = {}

   for app in INSTALLED_APPS:
      module_path = '%s.models' % app
      module = get_module(module_path)
      if module:
         for fixture in dir(module):
            if type(getattr(module, fixture)) == ModelBase:
               model_fixture = getattr(module, fixture)
               model_name = model_fixture._meta.db_table
               if by_model:
                  model_name = fixture

               models[model_name] = dict(
                  name=fixture,
                  model=getattr(module, fixture)
               )

   if not by_model:
      cache.set(cache_key, models)

   return models


## Get model field settings
#
#  @param request Current request
#  @param model Database model
#
#  @return fields from given model
#
def get_model_fields(request, model):

   fields = {}

   # load single fields
   for field in model._meta.fields + model._meta.many_to_many:
   #for field in model._meta.fields:

      model_config = getattr(model, '%s__config' % field.name) if not field.name == 'id' and hasattr(model, '%s__config' % field.name) else {}

      field_type = field.get_internal_type()
      if hasattr(field, 'get_custom_internal_type'):
         field_type = field.get_custom_internal_type()

      fields[field.name] = dict_to_obj({
         '_name': _t(request, field.name), # @TODO, translation_type='Model field name'),
         'name': field.name,
         'field': field,
         'field_type': field_type,
         'filter': field.get_internal_type(),
         'config': model_config
      })

   return fields


## Get model field groups
#
#  @param request Current request
#  @param model Database model
#
#  @return fields groups from given model
#
def get_model_groups(request, model, include_multiple=True, include_read_only=True, excludes=[]):

   # load single fields
   if hasattr(model, 'field__groups'):
      model_groups = getattr(model, 'field__groups')
      valid_groups = []
      for group in model_groups:
         if 'permissions' in group['data']:
            from core.permission import check_permissions
            status, action = check_permissions(request, group['data']['permissions'])
            if status:
               valid_groups.append(group)
         else:
            valid_groups.append(group)

      return valid_groups