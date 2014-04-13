#! /usr/bin/python
#
#  Wepo object blocks
#

from core.helper.model_help import get_model, get_model_fields
import json


## Edit object from post data
#
def edit(request, block):
   post = request.POST

   object_instance = request.POST.get('object_instance', None)
   object_type = request.POST.get('object_type', None)

   model_obj = get_model(request, object_type)
   model = model_obj['model']

   instance = model.objects.get(id=object_instance) if object_instance else model()

   model_fields = get_model_fields(request, model)
   many_to_many_instances = []

   for field_name, field_settings in model_fields.items():
      field = field_settings['field']
      field_type = field.get_internal_type()
      if hasattr(field, 'get_custom_internal_type'):
         field_type = field.get_custom_internal_type()

      if field_name in post:
         value = post[field_name]
         #
         #  cast to int, pass if no data is set
         #
         if field_type == 'ForeignKey':
            if value == 'none' or value == 'None':
               pass
            try:
               field_value = int(value)
               parent_model = field.related.parent_model
               parent_instance = parent_model.objects.get(id=field_value)
               setattr(instance, field_name, parent_instance)
            except ValueError, e:
               pass
         #
         #  handle many to many fields, usually widget will pass id's as value
         #
         elif field_type == 'ManyToManyField':
            many_to_many_instances.append({'field_name': field_name,
                                           'field_settings': field_settings,
                                           'field': field,
                                           'field_type': field_type,
                                           'value': value})


         #
         #  parse date time
         #
         elif field_type == 'DateTimeField':
            setattr(instance, field_name, value)
         #
         #  get the bool value from the data
         #
         elif field_type == 'BooleanField':
            field_value = value in ['True', '1', 'TRUE', 'true']
            setattr(instance, field_name, field_value)
         #
         #  parse json and try to change it to valid json data if needed
         #
         elif field_type == 'JsonField':
            field_value = value.encode('utf-8')
            field_value = field_value.replace("'", '"')

            if field_value and not '[' in field_value and not '{' in field_value:
               field_value = '["%s"]' % field_value

            field_value = json.loads(field_value)
            setattr(instance, field_name, field_value)
         else:
            value = value.encode('utf-8')
            setattr(instance, field_name, value)

   instance.save()

   for many_to_many in many_to_many_instances:
      field = many_to_many['field']
      value = many_to_many['value']
      field_type = many_to_many['field_type']
      field_name = many_to_many['field_name']
      field_settings = many_to_many['field_settings']

      field_value = value.replace("'", '')
      field_values = json.loads(field_value)
      through_model = field_settings.field.rel.through
      through_to_model = field_settings.field.rel.to

      delete_relations = True
      for field in through_model._meta.fields:
         if field.name == 'enabled':
            delete_relations = False
            break

      #
      #  get old relations
      #
      q = {object_type: instance.id}
      old_relations = through_model.objects.filter(**q).order_by()

      #
      #  deactivate, delete old relations
      #
      for relation in old_relations:
         if delete_relations:
            relation.delete()
         else:
            relation.enabled = False
            relation.save()

      if field_values:
         #
         #  load new objects
         #
         new_linked_objects = through_to_model.objects.filter(id__in=field_values)

         #
         #  enable, add new relations
         #
         for new_object in new_linked_objects:
            #
            #  add new
            #
            if delete_relations:
               through_instance = through_model()
               setattr(through_instance, through_to_model._meta.db_table, new_object)
               setattr(through_instance, object_type, instance)
               through_instance.save()
            else:
               tdata = {object_type:instance, through_to_model._meta.db_table:new_object}
               through_instance = through_model.objects.get(**tdata)
               through_instance.enabled = True
               through_instance.save()

   parent_model_name = post.get('parent_model_name', None)
   parent_id = int(post.get('parent_id', -1))
   parent_field = post.get('parent_field', None)

   if hasattr(model, 'user'):
      if not instance.user:
         from core.user import get_user
         instance.user = get_user(request)

   instance.save()

   #
   #  link new object with it's parent
   #
   if parent_model_name and parent_field and parent_id != -1:
      parent_model = get_model(request, parent_model_name)
      parent_model = parent_model['model']
      parent_instance = parent_model.objects.get(id=parent_id)

      through = getattr(parent_model, parent_field).through
      through_instance = through()
      setattr(through_instance, parent_model_name, parent_instance)
      setattr(through_instance, object_type, instance)
      #
      #  set custom fields
      #
      for field in through._meta.fields:
         if field.name == 'enabled':
            setattr(through_instance, 'enabled', False)

      #
      #  save through object
      #
      through_instance.save()

   request.wepo.response_type = 'json'
   instance_title = str(instance)

   return dict(
      status='success',
      message='Object %s with id %d successfully %s.<br />' % (instance_title, instance.id, 'updated' if object_instance else 'created'),
      id=instance.id,
      instance=str(instance).decode('utf-8')
   )


## Get data of the object
#
def data(request, block):
   model_name = request.GET.get('model', None)
   id = int(request.GET.get('id', -1))

   if model_name and id != -1:

      model = get_model(request, model_name)
      if model:
         model = model['model']
         instance = model.objects.get(id=id)

         fields = get_model_fields(request, model)

         data = {}
         for field in fields:
            if hasattr(instance, field):
               data[field] = str(getattr(instance, field))

         return data

   #
   #  @TODO return model fields with widget settings etc..
   #
   elif model_name and id == -1:
      model = get_model(request, model_name)

      if model:
         model = model['model']
         fields = get_model_fields(request, model)

         #
         #  get parent
         #
         parent_model_name = request.GET.get('parent', None)
         parent_field = request.GET.get('parent_field', None)
         parent_id = int(request.GET.get('parent_id', -1))

         #
         #  create model form
         #
         from django.template import Context
         from django.template.loader import get_template
         from core.form import FormItem

         template = get_template('admin/object/add_new_popup.html')

         data = []

         for field_name, field_settings in fields.items():
            if field_settings.filter == 'AutoField':
               continue

            field_widget = field_settings.config.widget

            field_defaults = field_settings.config.defaults.__dict__ if 'defaults' in field_settings.config else {}
            field_template = field_settings.config.template if 'template' in field_settings.config else 'form_elements'

            field_template = get_template('admin/object/%s.html' % field_template)

            field_defaults['class'] = 'span12'
            field_defaults['value'] = ''
            field_defaults['instance'] = None
            field_defaults['instance_model'] = model
            field_defaults['name'] = field_name
            field_defaults['field_config'] = field_settings['config']

            from core.helper import get_request
            field_form_field = FormItem(type=field_widget, request=get_request(), **field_defaults)

            context = dict(
               field_name = field_name.replace('_', ' '),
               field = field_form_field
            )
            data.append(field_template.render(Context(context)))

         add_new_button = FormItem('SubmitButton', request, value='Add %s' % model_name, id='add_%s' % model_name, **{
            'class': 'btn btn-icon btn-success',
            'data-model': model_name
         })
         object_type = FormItem('Hidden', request, value=model_name, name='object_type', id='object_type')
         response_type = FormItem('Hidden', request, value='json', name='wr', id='wr')

         parent_model_name = FormItem('Hidden', request, value=parent_model_name, name='parent_model_name', id='parent_model_name')
         parent_field = FormItem('Hidden', request, value=parent_field, name='parent_field', id='parent_field')
         parent_id = FormItem('Hidden', request, value=parent_id, name='parent_id', id='parent_id')

         from core import wepo_assets
         from core.asset import add_asset
         add_asset(request, type='script', code=wepo_assets.wepo.form.model, position='footer')
         add_asset(request, type='script', code=wepo_assets.script.jquery_form, position='footer')
         add_asset(request, type='script', code="""wepo.form.model.init_add_new('%s')""" % model_name, include_type='code', position='footer')

         context = dict(
            fields = data,
            add_button = add_new_button,
            object_type = object_type,
            response_type = response_type,
            parent_model_name = parent_model_name,
            parent_id = parent_id,
            parent_field = parent_field
         )

         return template.render(Context(context))

   return dict(error=True)