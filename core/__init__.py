#! /usr/bin/python
#
#  Wepo core package
#


from helper import WepoGeneric

# Assets pre-defines
wepo_assets = WepoGeneric()

wepo_assets.meta = WepoGeneric()
wepo_assets.meta.view_port                = dict(name='viewport', content='width=device-width, initial-scale=1.0, user-scalable=0, minimum-scale=1.0, maximum-scale=1.0')

# Scripts
wepo_assets.script = WepoGeneric()
wepo_assets.script.wepo                   = dict(src='script/wepo.js')
wepo_assets.script.jquery                 = dict(src='script/jquery-1.8.2.min.js')
wepo_assets.script.jquery_ui              = dict(src='script/lib/jquery-ui.custom.min.js')
wepo_assets.script.bootstrap              = dict(src='script/bootstrap.min.js')
wepo_assets.script.admin_menu             = dict(src='admin/script/menu.js')
wepo_assets.script.admin_nestable         = dict(src='admin/script/lib/jquery.nestable.js')
wepo_assets.script.jquery_form            = dict(src='script/lib/jquery.form.js')
wepo_assets.script.select2                = dict(src='script/lib/jquery-select2/select2.min.js')
wepo_assets.script.bootstrap_datetime     = dict(src='script/lib/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js')
wepo_assets.script.tinymce                = dict(src='script/lib/tinymce/tinymce.min.js')

wepo_assets.script.nested_sort            = dict(src='script/lib/jquery.mjs.nestedSortable.js')
wepo_assets.script.smooth_zoom            = dict(src='script/lib/jquery-smooth-zoom/jquery.smoothZoom.min.js')

# Styles
wepo_assets.style = WepoGeneric()
wepo_assets.style.bootstrap               = dict(href='style/bootstrap.css')
wepo_assets.style.font                    = dict(href='style/font.css')
wepo_assets.style.admin_main              = dict(href='admin/style/admin.css')
wepo_assets.style.admin_style             = dict(href='admin/style/style.css')
wepo_assets.style.admin_screen            = dict(href='admin/style/screen.css')
wepo_assets.style.admin_dashboard         = dict(href='admin/style/dashboard.css')
wepo_assets.style.admin_nestable          = dict(href='admin/style/lib/nestable.css')
wepo_assets.style.select2                 = dict(href='script/lib/jquery-select2/select2.css')
wepo_assets.style.bootstrap_datetime      = dict(href='script/lib/bootstrap-datetimepicker/css/datetimepicker.js')

# Wepo forms
wepo_assets.wepo = WepoGeneric()
wepo_assets.wepo.form = WepoGeneric()
wepo_assets.wepo.form.blocks              = dict(src='wepo/form/blocks.js')
wepo_assets.wepo.form.assets              = dict(src='wepo/form/assets.js')
wepo_assets.wepo.form.model               = dict(src='wepo/form/model.js')

wepo_assets.wepo.files                    = WepoGeneric()
wepo_assets.wepo.files.script             = dict(src='wepo/files/files.js')
wepo_assets.wepo.files.directory_tree     = dict(href='wepo/files/directory_tree.css')
wepo_assets.wepo.files.file_select        = dict(href='wepo/files/file_select.css')
