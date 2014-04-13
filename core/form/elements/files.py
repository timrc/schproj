def Image(request, **data):
   from django.template.loader import get_template
   from django.template import Context

   from core.helper.file_help import files_config_enc

   from wepo.settings import DEFAULT_IMAGE_SCALES

   model = data.get('instance_model', None)
   scales = {}

   if not 'preview_size' in data:
      data['preview_size'] = 'prws'

   if model:
      if hasattr(model, '%s__config' % data['name']):
         field_config = getattr(model, '%s__config' % data['name'])
         scales = field_config.get('scales', scales)
         tmp_scales = []
         for scale in scales:
            tmp_scales.append(scale.__dict__)

         #
         #  add default image scales
         #
         for scale in DEFAULT_IMAGE_SCALES:
            tmp_scales.append(scale)

         scales = tmp_scales

   data_files_config = dict(
      quantity=1,
      type='image',
      private=data['field_config'].get('owner_only', False),
      preview=data['preview_size'],
      upload=True,
      edit=True,
      scales=scales
   )
   data_files = files_config_enc(data_files_config)

   file = None
   file_id = ''
   if data['value']:
      file = data['value']
      file_id = file.id

   from core.form import FormItem
   file_data = FormItem('Hidden', request, name=data['name'], id='file_%s' % data['name'], value=file_id)

   template = get_template('form/files/image.html')

   context = {
      'data_files': data_files,
      'control_id': data['name'],
      'file': file,
      'file_data': file_data
   }
   from core import wepo_assets
   from core.asset import add_asset

   add_asset(request, type='script', code=wepo_assets.wepo.files.script, position='footer')
   add_asset(request, type='script', code="""wepo.files.init();""", include_type='code', position='footer')

   return template.render(Context(context))
