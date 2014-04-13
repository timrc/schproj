#! /usr/bin/python
#
#  Wepo files blocks
#

import os
import datetime, time, random, json
import shutil
from wepo.settings import MEDIA_ROOT, DEFAULT_IMAGE_SCALES

from django.template.loader import get_template
from django.template import Context

from core.user import get_user
from core.helper.file_help import files_config_dec, get_directory_tree, get_file_tag
from core.helper.file_help import scale_image, get_file_rough_mime_type


## File select block
#
def file_select(request, block):
   template = get_template('files/index.html')

   raw_config = request.GET.get('config', '')
   config = files_config_dec(raw_config if raw_config else {})

   # crop, height, width, prefix, name
   image_scales = config.get('scales', {})
   is_private = config.get('private', False)
   preview = config.get('preview', 'prws')

   #
   #  get directories
   #
   directories = get_directory_tree()

   from core.models import File

   filter = {'directory': 1}
   if is_private:
      filter['owner'] = get_user(request).id

   files = File.objects.filter(**filter).order_by('-id')[:20]

   from core.form import FormItem

   new_directory_input = FormItem('Text', request, name='new_directory', id='new_directory', **{'class': 'col-lg-12'})

   form_file_id = FormItem('Hidden', request, name='file_id', id='file_id', **{'class': 'col-lg-12'})
   form_file_title = FormItem('Text', request, name='file_title', id='file_title', **{'class': 'col-lg-12'})
   form_file_description = FormItem('Textarea', request, name='file_description', id='file_description', rows=10, **{'class': 'col-lg-12'})
   form_file_author = FormItem('Text', request, name='file_author', id='file_author', **{'class': 'col-lg-12'})

   #
   #  generate initial file tags
   #
   file_tags = []
   for file in files:
      tag = get_file_tag(file)
      if not tag in file_tags:
         file_tags.append(tag)

   context = {
      'directories': directories,
      'new_directory_input': new_directory_input,
      'files': files,
      'form_file_id': form_file_id,
      'form_file_title': form_file_title,
      'form_file_description': form_file_description,
      'form_file_author': form_file_author,
      'file_tags': file_tags,
      'scales': image_scales,
      'preview': preview

   }

   #
   #  assets
   #
   from core import wepo_assets
   from core.asset import add_asset

   add_asset(request, type='script', code=wepo_assets.script.nested_sort, position='footer')
   add_asset(request, type='script', code=wepo_assets.script.smooth_zoom, position='footer')
   add_asset(request, type='style', code=wepo_assets.wepo.files.directory_tree, position='head')
   add_asset(request, type='style', code=wepo_assets.wepo.files.file_select, position='head')
   add_asset(request, type='script', code="""
      wepo.files.image_scales=%s;
      wepo.files.widget_config='%s';
   """ % (json.dumps(image_scales), raw_config), include_type='code', position="footer")

   return template.render(Context(context))


## File list
#
def file_list(request, block):
   template_name = 'files/file_list_container.html'
   directory = request.GET.get('directory', 1)
   offset = int(request.GET.get('offset', 0))
   if offset > 0:
      template_name = 'files/file_list.html'

   template = get_template(template_name)

   raw_config = request.GET.get('config', {})
   config = files_config_dec(raw_config)
   is_private = config.get('private', False)

   from core.models import File

   filter = {'directory': directory}
   if is_private:
      filter['owner'] = get_user(request).id

   files = File.objects.filter(**filter).order_by('-id')[offset:offset + 20]

   #
   #  generate file tags
   #
   file_tags = []
   for file in files:
      tag = get_file_tag(file)
      if not tag in file_tags:
         file_tags.append(tag)

   context = {
      'files': files,
      'file_tags': file_tags
   }

   #
   #  assets
   #
   from core import wepo_assets
   from core.asset import add_asset

   add_asset(request, type='style', code=wepo_assets.wepo.files.file_select, position='head')

   return template.render(Context(context))


## File uploader - file upload callback
#
def upload(request, block):
   #
   #  file info
   #
   file_id = request.META.get('HTTP_X_FILE_ID', None)

   chunk = int(request.META.get('HTTP_X_FILE_CHUNK', 0))
   file_size = int(request.META.get('HTTP_X_FILE_SIZE', 0))
   selected_directory = int(request.META.get('HTTP_X_FILE_DIRECTORY', 1))

   file_name = request.META.get('HTTP_X_FILE_NAME', '')
   mime_type = request.META.get('HTTP_X_FILE_TYPE', '')

   if file_id is None:
      return dict(status=False, message='No file defined')

   if file_size == 0:
      return dict(status=False, message='File size is 0')

   if file_name == '':
      return dict(status=False, message='No file name defined')

   #
   #  Get current file chunk data
   #
   bin = request.body

   #
   #  save file to temporary file
   #
   f = open('/tmp/%s' % file_id, 'a')
   f.write(bin)
   f.close()

   #
   #  move uploaded file when completely uploaded
   #
   if chunk == file_size:
      path = datetime.datetime.now().strftime("%Y/%m/%d")
      file_path = '%s/%s' % (MEDIA_ROOT, path)

      # do not override existing images
      full_file_path = '%s/%s' % (file_path, file_name)
      if os.path.exists(full_file_path):
         n = datetime.datetime.now()
         unix_time = time.mktime(n.timetuple())

         file_name = '%d%d_%s' % (unix_time, random.randint(10, 100), file_name)
         full_file_path = '%s/%s' % (file_path, file_name)

      if not os.path.exists(file_path):
         os.makedirs(file_path)

      shutil.move('/tmp/%s' % file_id, full_file_path)

      from core.models import File, Directory

      directory = Directory.objects.get(id=selected_directory)
      created = datetime.datetime.now()

      file, created = File.objects.get_or_create(file_name=file_name, directory=directory, path=path, size=file_size, created=created)
      file.title = ' '.join(part.upper() for part in file_name.split('.')[:-1])
      file.data = {}
      file.mime_type = mime_type

      user = get_user(request)
      if user:
         file.owner = user

      file.save()

      for scale in DEFAULT_IMAGE_SCALES:
         scale_image(file, scale)

      return dict(status=True, message='File uploaded (real size: %d)' % len(bin), file_name=file.file_name, file_path=file.path, file_id=file.id, file_mime_type=file.mime_type, file_rough_mime_type=get_file_rough_mime_type(file))

   return dict(status=True, message='Chunk %d uploaded (real size: %d)' % (chunk, len(bin)))


## Add new directory
#
def new_directory(request, block):
   name = request.GET.get('name', '')
   parent = int(request.GET.get('parent', 0))

   from core.models import Directory

   directory = Directory()
   directory.name = name
   directory.parent = Directory.objects.get(id=parent)
   directory.save()

   return dict(
      name=str(name),
      id=int(directory.id),
      parent=parent,
      status='success',
      message='New folder %s created.' % str(name)
   )


## Update directory structure
#
def update_directories(request, block):
   import json

   data = json.loads(request.GET.get('data', {}))
   from core.models import Directory

   for id, parent in data.items():
      directory = Directory.objects.get(id=int(id))
      parent = Directory.objects.get(id=int(parent))

      directory.parent = parent
      directory.save()

   return dict(status='success', message='Folders were successfully updated.')


## Edit file
#
def edit(request, block):
   id = int(request.GET.get('id', -1))
   title = request.GET.get('title', '')
   description = request.GET.get('description', '')
   author = request.GET.get('author', '')

   if id == -1:
      return dict(status='error')

   from core.models import File

   file = File.objects.get(id=id)

   file.title = title
   file.description = description
   file.author = author
   file.save()

   return dict(status='success', message='File %s was successfully saved.' % file.title, id=id, title=title)


## Crop image file
#
def crop(request, block):
   id = int(request.GET.get('id', -1))
   data = json.loads(request.GET.get('data', []))

   from core.models import File

   file = File.objects.get(id=id)
   file_crop_data = file.data.get('scale', {})

   from pgmagick import Image, Geometry

   file_path = '%s/%s' % (MEDIA_ROOT, file.path)
   full_file_path = '%s/%s' % (file_path, file.file_name)

   for crop_data in data:
      #
      #  do not crop same image twice
      #
      if crop_data['name'] in file_crop_data:
         local_crop_data = file_crop_data[crop_data['name']]
         if 'scaled_width' in local_crop_data and 'scaled_height' in local_crop_data and 'crop_x' in local_crop_data and 'crop_y' in local_crop_data:
            if local_crop_data['scaled_width'] == int(crop_data['scaled_width']) and local_crop_data['scaled_height'] == int(crop_data['scaled_height']) and local_crop_data['crop_x'] == int(crop_data['crop_x']) and local_crop_data['crop_y'] == int(
               crop_data['crop_y']):
               continue

      image = Image(str(full_file_path))

      g = Geometry(int(crop_data['scaled_width']), int(crop_data['scaled_height']), 0, 0)
      image.scale(g)

      gc = Geometry(int(crop_data['width']), int(crop_data['height']), int(crop_data['crop_x']), int(crop_data['crop_y']))
      image.crop(gc)

      image.quality(100)
      image.sharpen(1.0)

      full_scaled_image_path = '%s/%s_%s' % (file_path, crop_data['prefix'], file.file_name)
      image.write(str(full_scaled_image_path))

      scale_data = dict(
         width=int(crop_data['width']),
         height=int(crop_data['height']),
         scaled_width=int(crop_data['scaled_width']),
         scaled_height=int(crop_data['scaled_height']),
         crop_x=int(crop_data['crop_x']),
         crop_y=int(crop_data['crop_y']),
         center_x=crop_data['center_x'],
         center_y=crop_data['center_y'],
         quality=100,
         sharpen=1.0,
         prefix=crop_data['prefix'],
         name=crop_data['name'],
         cropped=True
      )

      file.data['scale'][crop_data['name']] = scale_data

   file.save()

   return dict(status='success', message='Image %s was successfully cropped.' % file.title, id=id)