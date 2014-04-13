#! /usr/bin/python
#
#  Wepo administration object blocks
#

from django.template.loader import get_template
from django.template import Context
from core.form import AdminForm

from core.helper.model_help import get_model, get_model_fields, get_model_groups
from core.language import translate as _


## Admin object edit form
#
def edit(request, block):
   model_name = request.GET.get('model', None) if request.wepo.block else request.wepo.url_parts[3]
   id = request.GET.get('id', None)
   if not request.wepo.block and len(request.wepo.url_parts) > 4:
      id = request.wepo.url_parts[4]

   if id and id == 'me':
      from core.user import get_user
      id = get_user(request).id

   model_obj = get_model(request, model_name)
   model = model_obj['model']
   instance = model.objects.get(id=id) if id else None

   fields = get_model_fields(request, model)
   groups = get_model_groups(request, model)

   template = get_template('admin/object/edit.html')
   context = {'groups': groups, 'fields': fields, 'instance': instance, 'model': model}
   if 'attributes' in block:
      context['attributes'] = block['attributes']

   form = AdminForm(request, model, instance)

   from core.form import FormItem
   context['form'] = form
   context['request_wr'] = FormItem('Hidden', request, name='wr', value="json")
   context['request_raw'] = FormItem('Hidden', request, name='raw', value="true")

   context['edit_object_instance'] = FormItem('Hidden', request, name='object_instance', value=id)
   context['edit_object_type'] = FormItem('Hidden', request, name='object_type', value=model_name)

   #
   #  assets
   #
   from core import wepo_assets
   from core.asset import add_asset
   add_asset(request, type='script', code=wepo_assets.script.jquery_form, position='footer')
   add_asset(request, type='script', code="""
      jQuery('#object-edit #save_object').click(function() {
         jQuery('#object-edit').ajaxForm({
            success: function(responseText, statusText, xhr, $form) {
               wepo.callback_message(responseText);
            }
         });
      });
      jQuery('#object-edit #close_form').click(function() {
         wepo.redirect('/admin/object/list/' + wepo.url_part(3));
      });
      """, include_type='code', position="footer")

   return template.render(Context(context))


## Admin objects list
#
def list(request, block):
   model_name = None
   if hasattr(block, 'model_name'):
      model_name = block.model_name
   else:
      model_name = request.GET.get('model', None) if request.wepo.block else request.wepo.url_parts[3]

   model_name = model_name.replace('-', '_')

   model_obj = get_model(request, model_name)
   model = model_obj['model']

   restricted_content = hasattr(model, 'restricted_content')

   template = get_template('admin/object/list.html')

   fields = get_model_fields(request, model)

   per_page = int(request.GET.get('_per_page', block.limit if hasattr(block, 'limit') else 10))
   page = int(request.GET.get('_page', 0))
   offset = page * per_page

   # sort by ...
   default_sort = [block.order] if hasattr(block, 'order') else model.default_sort if hasattr(model, 'default_sort') else ['id']

   objects = []
   if restricted_content and model.restricted_content:
      permissions_to_check = model.grant_permission if hasattr(model, 'grant_permission') else ['admin.superuser_access']

      from core.permission import check_permissions
      from core.user import get_user
      status, action = check_permissions(request, permissions_to_check)
      if status:
         # ok has permission to list all
         objects = model.objects.all().order_by(*default_sort)

      else:
         # list only owners items and to those who are granted to see
         from django.db.models import Q
         user = get_user(request)
         query = None

         # grant only to those who can access this content
         grant_access = model.grant_access if hasattr(model, 'grant_access') else None
         if grant_access:
            for access in grant_access:
               if not query:
                  query = Q(**{'%s' % access.replace('.', '__'): user})
               else:
                  query |= Q(**{'%s' % access.replace('.', '__'): user})

         # grant to this content if some parameters are not yet set
         grant_access_empty = model.grant_access_empty if hasattr(model, 'grant_access_empty') else None
         if grant_access_empty:
            for access in grant_access_empty:
               if not query:
                  query = Q(**{'%s__isnull' % access.replace('.', '__'): True})
               else:
                  query |= Q(**{'%s__isnull' % access.replace('.', '__'): True})

         if not grant_access:
            return ''

         objects = model.objects.filter(query).order_by(*default_sort).distinct()
   else:
      objects = model.objects.all().order_by(*default_sort)

   # count objects
   count = objects.count()
   objects = objects[offset:offset + per_page]

   # generate pagination
   list_last = int(count / per_page)
   first = max(page - 5, 0)
   last = min(page + 5, list_last)
   pagination = [a for a in range(first, last)]

   show_pagination = True
   if hasattr(block, 'pagination'):
      show_pagination = block.pagination

   context = {
      'objects': objects,
      'fields': fields,
      'list_first': 0,
      'list_page': page,
      'list_last': list_last,
      'pagination': pagination,
      'show_pagination': show_pagination,
      'url': request.wepo.url,
      'query': request.wepo.query,
      'model_name': model_name,
      'page': page,
      'widget_size': block.widget_size if hasattr(block, 'widget_size') else 12,
      'start_row': block.start_row if hasattr(block, 'start_row') else True,
      'end_row': block.end_row if hasattr(block, 'end_row') else True,
      'add_new_button': _(request, 'Add new %s' % model_name.title())
   }

   return template.render(Context(context))