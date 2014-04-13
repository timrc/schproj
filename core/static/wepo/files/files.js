/**
 * Wepo form files element namespace
 */
(function( files ) {

   /* settings */
   files.debug = true;
   files.debug_error = true;
   files.debug_warn = true;
   files.debug_info = true;

   files.callback_url = 'core/files/file_select';
   files.data = {};
   files.drop_container = false;
   files.files_container = false;
   files.drops = 0;
   files.hidden_file_input = false;
   files.selected_directory = 1;
   files.current_offset = 20;

   files.selected_placeholder = '';
   files.control_id = '';

   /* uploading settings */
   files.simultaneously_uploads = 3;
   files.current_uploading = 0;
   files.upload_queue = [];
   files.upload_queue_interval = 256; // 256ms

   files.chunk_size = 256; // 256kb

   files.file_tags = [];
   files.image_scales = [];

   files.widget_config = '';


   /* general log */
   files.log = function(data) {
      files.debug && wepo.log(data);
   }
   /* error log */
   files.error = function(data) {
      files.debug_error && wepo.error(data);
   }
   /* warning log */
   files.warn = function(data) {
      files.debug_warn && wepo.warn(data);
   }
   /* info log */
   files.info = function(data) {
      files.debug_info && wepo.info(data);
   }


   /***************************************************************/
   /* Initializations */
   /***************************************************************/

   /**
    * Init file manager
    */
   files.init = function() {
      /* init image */
      files.init_image();
   }

   /**
    * Init image
    */
   files.init_image = function() {
      var selector = '.files-image-select';
      files.init_selector(selector);
   }

   /**
    * Init selector to open manager
    *
    * @param selector
    */
   files.init_selector = function(selector) {
      jQuery(selector).click(function() {
         var config = jQuery(this).attr('data-files');
         files.selected_placeholder = jQuery(this).attr('data-placeholder');
         files.control_id = jQuery(this).attr('data-control-id');

         var random = Math.random();
         wepo.call(wepo.call_url(files.callback_url, {token:random, wr:'json', config: config}), files.load_callback, wepo.on_error);

         return false;
      });
   }

   /**
    * Init file uploader
    *    - add drag&drop events to the container
    */
   files.init_uploader = function() {
      var drop_container = document.getElementById('files_container');
      files.drop_container = drop_container;

      wepo.add_event_handler(drop_container, 'dragover', wepo.files.drag_over_event);
      wepo.add_event_handler(drop_container, 'dragenter', wepo.files.drag_enter_event);
      wepo.add_event_handler(drop_container, 'dragleave', wepo.files.drag_leave_event);
      wepo.add_event_handler(drop_container, 'drop', wepo.files.drop_event);

      files.setup_hidden_file_input();
      //files.files_container.append(files.hidden_file_input);
      files.files_container.click(function() {
         files.log('files container click');
         return files.hidden_file_input.click();
      });
   }

   /**
    * Init directory tree
    *    -  make directory tree nested drag&droppable
    */
   files.init_directory_tree = function() {
      if(jQuery().nestedSortable) {

         var directory_list = jQuery('.files-directory');

         directory_list
            .click(function() {
               var directory_id = jQuery(this)
                  .attr('data-files-directory');
               jQuery('.files-directory').removeClass('btn-warning');
               jQuery(this).addClass('btn-warning');
               files.selected_directory = directory_id;

               files.reload_file_list();
            });

         directory_list
            .first()
            .addClass('btn-warning');

         jQuery('ol.sortable').nestedSortable({
            forcePlaceholderSize: true,
            handle: 'div',
            helper:	'clone',
            items: 'li',
            opacity: .6,
            placeholder: 'placeholder1',
            revert: 250,
            tabSize: 25,
            tolerance: 'pointer',
            toleranceElement: '> div',
            /*maxLevels: 5,*/
            protectRoot: true,
            isTree: true,
            expandOnHover: 700,
            startCollapsed: true
         });

         jQuery('.disclose').on('click', function() {
            jQuery(this)
               .toggleClass('collapsed')
               .toggleClass('expanded')
               .closest('li')
               .toggleClass('mjs-nestedSortable-collapsed')
               .toggleClass('mjs-nestedSortable-expanded');
         })

         jQuery('#serialize').click(function(){
            wepo.info(jQuery('ol.sortable')
               .nestedSortable('serialize'));
         })

         jQuery('#toHierarchy').click(function(e){
            wepo.info(jQuery('ol.sortable')
               .nestedSortable('toHierarchy', {startDepthCount: 0}));
         })

         jQuery('#toArray').click(function(e){
            wepo.info(jQuery('ol.sortable')
               .nestedSortable('toArray', {startDepthCount: 0}));
         });

         jQuery('.add-new-folder-toggle').click(function() {
            jQuery('.new_directory_container').toggle();
            jQuery(this).toggleClass('down_arrow');
            jQuery(this).toggleClass('up_arrow');
         });

         /* add new directory as child of selected */
         jQuery('.new_directory_button').click(function() {
            wepo.files.log('Adding new directory');
            var name = jQuery('#new_directory').val();
            wepo.call(wepo.call_url('core/files/new_directory', {name:name, wr:'json', parent:files.selected_directory, raw:true}), files.new_directory_callback, wepo.on_error);
         });

         jQuery('.save-directories').click(function() {
            var new_directories = files.get_directory_structure();

            var structure = {};
            for(var directory in new_directories) {
               if(directory in files.initial_directories) {
                  if(new_directories[directory] != files.initial_directories[directory]) {
                     structure[directory] = new_directories[directory];
                  }
               }
               else {
                  structure[directory] = new_directories[directory];
               }
            }

            var data = JSON.stringify(structure);
            wepo.call(wepo.call_url('core/files/update_directories', {data:data, wr:'json', raw:true}), wepo.callback_message, wepo.on_error);
         });

         files.initial_directories = files.get_directory_structure();
      }
      else {
         /* retry till the plugin nestedSortable is loaded */
         setTimeout('wepo.files.init_directory_tree()', 50);
      }
   }

   /**
    * Init files list
    *    - init each file
    *    - add load more on scroll (first click, then scroll)
    */
   files.init_file_list = function() {
      files.files_container =  jQuery('#files_container');

      var files_list_file = jQuery('.files_list_file');
      files_list_file.each(function(){
         files.init_file(jQuery(this));
      });

      if(files_list_file.length == 20) {
         /* load more */
         if(jQuery('#files_load_more').length == 0) {
            jQuery('<div/>')
               .attr({'id': 'files_load_more'})
               .append(jQuery('<a/>')
                  .addClass('btn btn-default load_more_button')
                  .css({'display': 'none'})
                  .attr({'href': '#'})
                  .html('Load more')
               )
               .append(jQuery('<img/>')
                  .addClass('loader')
                  .attr({'src': '/assets/images/loader.gif'})
               )
               /*.click(function() {
                  jQuery('.load_more_button').toggle();
                  jQuery('.loader').toggle();

                  files.load_more_files();

                  return false;
               })*/
               .appendTo(jQuery('#files_browse_files'));
         }
      }

      if(files_list_file.length == 0) {
         files.files_container.addClass('dragstart');
      } else {
         if(files.files_container.hasClass('dragstart')) {
            files.files_container.removeClass('dragstart');
         }
      }
   }

   /**
    * Init file (make it deletable, editable, selectable, ...)
    *
    * @param file
    */
   files.init_file = function(file) {
      if(!file.hasClass('initialized')) {
         file.mouseover(function() {
            jQuery('.file_controls', this).toggle();
            jQuery(this).css({'cursor':'pointer'});
         });
         file.mouseout(function() {
            jQuery('.file_controls', this).toggle();
            jQuery(this).css({'cursor':'auto'});
         });

         file.click(function() {
            jQuery(this).toggleClass('alert-info');

            jQuery('.' + files.selected_placeholder).attr({src: (file.attr('data-file'))});
            jQuery('#file_' + files.control_id).val(file.attr('data-id'));

            wepo.popup_close();

            return false;
         });

         /* edit file */
         jQuery('.file-edit', file).click(function() {
            /* get file data */
            wepo.get_data('file', jQuery(this).closest('.files_list_file').attr('data-id'), wepo.files.get_data_callback);

            return false
         });

         /* delete file */
         jQuery('.file-delete', file).click(function() {

         });

         file.addClass('initialized');

         /* init file tag */
         var tag = file.attr('data-file-tag');
         if(files.file_tags.indexOf(tag) == -1) {
            var file_tag = jQuery('<a/>')
               .attr({'href': '#', 'data-type': tag})
               .addClass('btn btn-default btn-small file_tag file_tag_' + tag)
               .html(tag.create_title());    //Uncaught TypeError: Cannot call method 'create_title' of undefined
            jQuery('.file_list_tags').append(file_tag);

            files.init_file_tag(file_tag);
         }
      }
   }

   /**
    * Setup file input hidden element
    *    - Reset that element every time it's called
    *
    * @returns {*}
    */
   files.setup_hidden_file_input = function() {
      if (files.hidden_file_input) {
         document.body.removeChild(files.hidden_file_input);
      }
      files.hidden_file_input = document.createElement("input");
      files.hidden_file_input.setAttribute("type", "file");
      /*if (files.options.uploadMultiple) {*/
      files.hidden_file_input.setAttribute("multiple", "multiple");
      /*}*/
      /*if (files.options.acceptedFiles != null) {
      files.hidden_file_input.setAttribute("accept", _this.options.acceptedFiles);
      }*/
      files.hidden_file_input.style.visibility = "hidden";
      files.hidden_file_input.style.position = "absolute";
      files.hidden_file_input.style.top = "0";
      files.hidden_file_input.style.left = "0";
      files.hidden_file_input.style.height = "0";
      files.hidden_file_input.style.width = "0";
      document.body.appendChild(files.hidden_file_input);
      return files.hidden_file_input.addEventListener("change", function() {
         var drops;
         drops = files.hidden_file_input.files;
         if (drops.length) {
            files.handle_files(drops);
         }
         return files.setup_hidden_file_input();
      });
   }

   /**
    * Init file tags
    */
   files.init_file_tags = function() {
      jQuery('.file_list_tags .file_tag').each(function() {
         files.init_file_tag(jQuery(this));
      });
   }

   files.init_file_tag = function(tag) {
      if(tag.hasClass('initialized')) {
         return;
      }

      files.file_tags.push(tag.attr('data-type'));

      tag.click(function() {
         jQuery('.file_list_tags .file_tag.btn-success')
            .toggleClass('btn-success btn-default');

         var tag = jQuery(this).attr('data-type');

         jQuery(this)
            .toggleClass('btn-success btn-default');

         if(tag == 'all') {
            jQuery('.files_list_file').show();
         }
         else {
            jQuery('.files_list_file').hide();
            jQuery('.files_list_file[data-file-tag="'+tag+'"]').show();
         }

         return false;
      });

      tag.addClass('initialized');
   }


   /***************************************************************/
   /* Callbacks */
   /***************************************************************/

   /**
    * Callback after file update called
    *
    * @param data
    */
   files.file_update_callback = function(data) {
      var file = jQuery('.files_list_file[data-id=' + data.id + ']');
      if(file != undefined) {
         jQuery('.file_name', file).html(data.title);
      }

      jQuery('.file_tabs .files_browse_files').click();
      jQuery('.file_tabs .files_edit_file_li').hide();
      jQuery('.file_tabs .files_image_crop_li').hide();

      wepo.callback_message(data);
   }

   /**
    * Callback after file crop called
    *
    * @param data
    */
   files.file_crop_callback = function(data) {
      jQuery('.file_tabs .files_edit_file').click();

      wepo.callback_message(data);
   }

   /**
    * Get file data callback
    *
    * @param data
    */
   files.get_data_callback = function(data) {
      /* populate data */
      jQuery('.file_edit_form #file_id').val(data.id);
      jQuery('.file_edit_form #file_title').val(data.title);
      jQuery('.file_edit_form #file_description').val(data.description);
      jQuery('.file_edit_form #file_author').val(data.author);

      /* show crop tab if file loaded is of type image */
      if(data.mime_type.startsWith('image')) {
         jQuery('.file_edit_form .crop-tab-switch').show();

         var image_src = jQuery('.files_list_file[data-id=' + data.id + ']');
         var image_link = image_src.attr('data-file');
         var image_width = jQuery('img', image_src).attr('data-width');
         var image_height = jQuery('img', image_src).attr('data-height');

         var image_scales_placeholder = jQuery('#image_scales');
         image_scales_placeholder.html('');

         for(var scale_id in files.image_scales) {
            var scale = files.image_scales[scale_id];
            if(!wepo.is_object(scale)) {
               continue;
            }

            var image_data = data.data.replaceAll(" u'", "'").replaceAll("{u'", "{'").replaceAll("'", '"').replaceAll('True', 'true').replaceAll('False', 'false');
            image_data = JSON.parse(image_data);
            image_data = image_data.scale;

            var image_scale_initial_zoom = "";
            var center_x = 0;
            var center_y = 0;

            if(scale.name in image_data) {
               var image_scale_data = image_data[scale.name];

               image_scale_initial_zoom = 'scaled_width' in image_scale_data ? image_scale_data.scaled_width / image_width * 100 : "";

               center_x = 'center_x' in image_scale_data ? image_scale_data.center_x : 0;
               center_y = 'center_y' in image_scale_data ? image_scale_data.center_y : 0;
            }

            var crop_height = parseInt(600.0 / parseFloat(image_width) * image_height);

            var scale_title = jQuery('<h2/>').html(scale.name);
            var scale_image = jQuery('<img/>')
               .attr({
                  src:image_link,
                  id:'crop_' + scale.prefix,
                  'data-prefix': scale.prefix,
                  'data-width': scale.width,
                  'data-height': scale.height,
                  'data-zoom': image_scale_initial_zoom,
                  'data-center-x': center_x,
                  'data-center-y': center_y
               });

            var wrapper_width = scale.width;
            if(wrapper_width < 800) {
               wrapper_width = 800;
            }

            var scale_image_header = jQuery('<div/>')
               .addClass('widget widget-image-crop')
               .attr({width: wrapper_width + 'px'})
               .append(jQuery('<div/>')
                  .addClass('widget-head')
                  .append(jQuery('<h4/>')
                     .addClass('heading')
                     .html(scale.name)
                  )
               )

            image_scales_placeholder.append(scale_image_header);
            image_scales_placeholder.append(scale_image);
            image_scales_placeholder.append('<hr class="separator" />');

            scale_image.load(function() {

               var smooth_zoom_data = {
                  width: jQuery(this).attr('data-width'),
                  height: jQuery(this).attr('data-height'),

                  /******************************************
                   * http://www.drapertools-online.com/en/assets/smooth-zoom-pan-jquery-image-viewer/Help/Help.html
                  Enable Responsive settings below if needed.
                  Max width and height values are optional.
                  ******************************************/
                  responsive: false,
                  responsive_maintain_ratio: true,
                  max_WIDTH: '',
                  max_HEIGHT: '',
                  zoom_BUTTONS_SHOW : 'NO',
                  pan_BUTTONS_SHOW : 'NO',
                  /*pan_LIMIT_BOUNDARY : 'NO',*/
                  /*animation_SMOOTHNESS: 0.1,
                  animation_SPEED_ZOOM: 0.1,*/
                  background_COLOR: '#cc33ee',
                  border_COLOR: '#33bb66',
                  border_TRANSPARENCY: 50,
                  use_3D_Transform: false
                  /*zoom_SINGLE_STEP: true*/
               };

               if(jQuery(this).attr('data-zoom') != '') {
                  smooth_zoom_data['initial_ZOOM'] = jQuery(this).attr('data-zoom');
                  smooth_zoom_data['initial_POSITION'] = jQuery(this).attr('data-center-x') + ',' + jQuery(this).attr('data-center-y');
               }

               jQuery(this).smoothZoom(smooth_zoom_data);
/*
               var gotozoom = jQuery(this).attr('data-zoom') * 100;
               var gotox = jQuery(this).attr('data-center-x');
               var gotoy = jQuery(this).attr('data-center-y');

               jQuery(this).smoothZoom('focusTo', {x:gotox, y:gotoy, zoom:gotozoom, speed:2});
               */
            });


            //scale_image.imgAreaSelect({handles:true, aspectRatio:parseFloat(scale.width)/parseFloat(scale.height)});
         }
      }
      else {
         jQuery('.file_edit_form .crop-tab-switch').hide();
      }

      /* switch to edit tab */
      jQuery('.file_tabs .files_edit_file_li').show();
      jQuery('.file_tabs .files_edit_file').click();

      return false;
   }

   /**
    * Show file manager callback
    *
    * @param data
    */
   files.load_callback = function(data) {
      wepo.ajax_popup('Files', data);

      /* init file tags */
      files.init_file_tags();

      /* init directory tree */
      files.init_directory_tree();

      /* init file list */
      files.init_file_list();


      /* enable autoload on scroll */
      jQuery('.scroll-content').scroll(function() {
         if(jQuery('#files_load_more').length != 0 && !files.load_more_files_paused && jQuery(this).scrollTop() + jQuery(this).height() > jQuery('#files_browse_files', this).height() - 50) {
            files.load_more_files_paused = true;
            files.load_more_files();
         }
      });

      /* init uploader */
      files.init_uploader();

      /* init edit */
      jQuery('.file-update').click(function() {
         var id = jQuery('.file_edit_form #file_id').val();
         var title = jQuery('.file_edit_form #file_title').val();
         var description = jQuery('.file_edit_form #file_description').val();
         var author= jQuery('.file_edit_form #file_author').val();

          // Save file
         wepo.call(wepo.call_url('core/files/edit', {id:id, title:title, description:description, author:author, wr:'json', raw:true}), files.file_update_callback, wepo.on_error);

      });

      /* init crop */
      /**
       * http://vectorflower.com/preview/smooth_zoom/index.html
       * http://www.drapertools-online.com/en/assets/smooth-zoom-pan-jquery-image-viewer/
       */
      jQuery('.file-image-crop').click(function() {
         var id = jQuery('.file_edit_form #file_id').val();

         //" u'scale': {u'Profile image 3': {u'name': u'Profile image 3', u'crop_y': 39, u'cropped': True, u'height': 350, u'width': 600, u'prefix': u'usrpi4', u'scaled_height': 430, u'sharpen': 1.0, u'quality': 100, u'crop_x': 38, u'scaled_width': 674}, u'Profile image': {u'name': u'Profile image', u'crop_y': 20, u'cropped': True, u'height': 240, u'width': 240, u'prefix': u'usrpi1', u'scaled_height': 260, u'sharpen': 1.0, u'quality': 100, u'crop_x': 31, u'scaled_width': 408}, u'Profile image 1': {u'name': u'Profile image 1', u'crop_y': 19, u'cropped': True, u'height': 100, u'width': 100, u'prefix': u'usrpi2', u'scaled_height': 159, u'sharpen': 1.0, u'quality': 100, u'crop_x': 47, u'scaled_width': 249}, u'Preview': {u'name': u'Preview', u'height': 500, u'width': 500, u'prefix': u'prw', u'steps': [{u'width': 783, u'top': 0, u'height': 500, u'name': u'scale', u'left': 0}, {u'width': 500, u'top': 0, u'height': 500, u'name': u'crop', u'left': 0}], u'scale_to_fit': True, u'sharpen': 1.0, u'quality': 100}, u'Profile image 2': {u'name': u'Profile image 2', u'crop_y': 39, u'cropped': True, u'height': 300, u'width': 200, u'prefix': u'usrpi3', u'scaled_height': 380, u'sharpen': 1.0, u'quality': 100, u'crop_x': 123, u'scaled_width': 597}}}"

         var crop_data = [];
         for(var scale_id in files.image_scales) {
            var scale = files.image_scales[scale_id];
            if(!wepo.is_object(scale)) {
               continue;
            }

            var zoom_data =jQuery('#crop_' + scale.prefix).smoothZoom('getZoomData');

            var scale_data = {
               scaled_width: zoom_data.scaledWidth,   // image scaled to width
               scaled_height: zoom_data.scaledHeight, // image scaled to height
               crop_x: zoom_data.scaledX,             // scale image x offset
               crop_y: zoom_data.scaledY,             // scale image y offset
               center_x: zoom_data.centerX,           // scale image center x
               center_y: zoom_data.centerY,           // scale image center y
               prefix: scale.prefix,                  // scale prefix
               width: scale.width,                    // scale width
               height: scale.height,                  // scale height
               name: scale.name                       // scale name
            };

            crop_data.push(scale_data);
         }

         // Save crops
         wepo.call(wepo.call_url('core/files/crop', {id:id, wr:'json', raw:true, data:JSON.stringify(crop_data)}), files.file_crop_callback, wepo.on_error);

      });

      /* on crop tab click */
      jQuery('.crop-tab-switch').click(function() {
         jQuery('.file_tabs .files_image_crop_li').show();
         jQuery('.file_tabs .files_image_crop').click();
         jQuery('#files_image_crop').show();
      });
   }

   /**
    * Show files from selected directory callback
    *
    * @param data
    */
   files.file_list_container_load_callback = function(data) {
      files.files_container.html(data.content.html_decode());

      /* init file tags */
      files.file_tags = [];
      files.init_file_tags();

      /* init file list */
      files.init_file_list();

      jQuery('.file_tabs .files_browse_files').click();
      jQuery('.file_tabs .files_edit_file_li').hide();
      jQuery('.file_tabs .files_image_crop_li').hide();
   }

   /**
    * Show more files from selected directory callback
    *
    * @param data
    */
   files.file_list_load_callback = function(data) {
      files.load_more_files_paused = false;

      //jQuery('.load_more_button').toggle();
      jQuery('.loader').toggle();

      if(data.content == '' || data.content == ' ') {
         //jQuery('#files_load_more').remove();
         return;
      }
      else {
         files.current_offset+=20;
      }

      jQuery('.files_list_container_clear').remove();
      jQuery('#files_list_container')
         .append(data.content.html_decode())
         .append(jQuery('<div/>')
            .addClass('files_list_container_clear')
            .css({'clear': 'both'}));

      /* init file list */
      jQuery('.files_list_file').each(function(){
         files.init_file(jQuery(this));
      });
   }

   /**
    * Add new directory to the directory tree
    *
    * @param data
    */
   files.new_directory_callback = function(data) {
      var id = data.id;
      var name = data.name;
      var parent_id = data.parent;

      var parent = jQuery('#directory_' + parent_id);
      var hasChilds = jQuery('ol', parent).length != 0;

      if(!hasChilds) {
         parent.removeClass('mjs-nestedSortable-leaf');
         parent.addClass('mjs-nestedSortable-branch mjs-nestedSortable-expanded');

         parent = jQuery('<ol/>').appendTo(parent);
      } else {
         parent = jQuery('ol', parent);
      }

      var directory = jQuery('<li/>')
         .attr({id: 'directory_'  + id})
         .addClass('mjs-nestedSortable-leaf')
         .append(jQuery('<div/>')
            .append(' ')
            .append(jQuery('<span/>')
               .addClass('disclose')
            )
            .append(' ')
            .append(jQuery('<span/>')
               .addClass('directory_icon')
            )
            .append(' ')
            .append(jQuery('<a/>')
               .attr({href:'#', 'data-files-directory':id})
               .addClass('files-directory')
               .html(name)
            )
         );

      parent.append(directory);

      jQuery('.files-directory', directory)
         .click(function() {
            var directory_id = jQuery(this)
               .attr('data-files-directory');
            jQuery('.files-directory').removeClass('btn-warning');
            jQuery(this).addClass('btn-warning');
            files.selected_directory = directory_id;

            files.reload_file_list();
         });

      jQuery('.disclose', directory).on('click', function() {
         jQuery(this)
            .toggleClass('collapsed')
            .toggleClass('expanded')
            .closest('li')
            .toggleClass('mjs-nestedSortable-collapsed')
            .toggleClass('mjs-nestedSortable-expanded');
      });

      jQuery('.add-new-folder-toggle').click();

      wepo.callback_message(data);
   };


   /***************************************************************/
   /* Helpers ! */
   /***************************************************************/


   /**
    * Get directory structure
    *
    * @param type
    * @returns {{}}
    */
   files.get_directory_structure = function() {
      var directories = jQuery('ol.sortable').nestedSortable('toArray', {startDepthCount: 0});

      var structure = {};
      for(var id in directories) {
         if(directories[id].parent_id != null && directories[id].parent_id != 'none') {
            structure[directories[id].item_id] = directories[id].parent_id;
         }
      }

      return structure;
   }

   /**
    * Load new files after new directory is selected helper
    *
    * @returns {boolean}
    */
   files.reload_file_list = function() {
      var random = Math.random();
      wepo.call(wepo.call_url('core/files/file_list', {token:random, wr:'json', directory: files.selected_directory, config:files.widget_config}), files.file_list_container_load_callback, wepo.on_error);

      files.current_offset=20;

      return false;
   }

   /**
    * Handle dropped files helper
    *    - read dropped files with the status bar
    *    - upload files with the status bar
    *    - init all files
    *
    * @param drops
    */
   files.handle_files = function(drops) {
      files.drops = drops.length;
      for (var a=0; a<drops.length; a++) {
         files.log('loading file ' + a);
         var file = drops[a];
         var file_id = files.append_new_file_to_list(file);

         /* add file to upload queue */
         var file_uploader = new FileUploader(file, file_id);
         files.upload_queue.push(file_uploader);
         files.upload_queued_files();

         continue;

         var reader = new FileReader();


         /* attach event handlers here...*/
         // http://stackoverflow.com/questions/14438187/javascript-filereader-parsing-long-file-in-chunks
         // http://www.html5rocks.com/en/tutorials/file/dndfiles/
         reader.readAsDataURL(file);

         /* On load started */
         wepo.add_event_handler(reader, 'loadstart', function(e, file, file_id) {
            files.log('load started: ' + file.name + "["+file_id+"]");
         }.bind_to_event_handler(file, file_id));

         /* Update reading progress bar */
         wepo.add_event_handler(reader, 'progress', function(e) {
            var arguments = Array.prototype.slice.call(arguments);
            var file_id = arguments.pop();
            var file = arguments.pop();

            var percentage = parseInt(e.loaded/e.total*10000)/100.0;
            files.log('load progress: ' + file.name + "["+file_id+"] " + percentage + "%");

            jQuery('#' + file_id + ' .file_progress_bar').css({'width': parseInt(percentage) + 'px'});
            jQuery('#' + file_id + ' .file_progress_bar_status').html(percentage + '%');

         }.bind_to_event_handler(file, file_id));

         /* when file is loaded fully, start uploading it with some delay */
         wepo.add_event_handler(reader, 'loadend', function(e, file, file_id) {
            files.log('load ended: ' + file.name + "["+file_id+"]");

            var bin = this.result;

            var file_ext = file.name.split('.').pop().toLowerCase();
            var images_ext = ['jpg', 'gif', 'png', 'jpeg', 'tiff', 'bmp'];

            if(images_ext.indexOf(file_ext) != -1) {
               jQuery('#' + file_id + ' .file_img_wrapper img').attr({'src' :bin});
            }

            var file_obj = jQuery('#' + file_id);
            var file_progress_bar = jQuery('#' + file_id + ' .file_progress_bar')
            var file_progress_bar_status = jQuery('#' + file_id + ' .file_progress_bar_status')

            file_obj.animate({
               backgroundColor: '#ccffcc'
            }, 500);
            file_progress_bar.slideUp('slow', function() { jQuery(this).remove(); });
            file_progress_bar_status.slideUp('slow', function() { jQuery(this).remove(); });

            var file_uploader = new FileUploader(file, file_id);
            files.upload_queue.push(file_uploader);

            files.drops--;

            files.upload_queued_files();
         }.bind_to_event_handler(file, file_id));
      }
   }

   /**
    * Start uploading next file in queue
    */
   files.upload_queued_files = function() {
      files.log('Files in queue ' + files.upload_queue.length + ', currently uploading ' + files.current_uploading + ' files.');

      var upload_count = files.simultaneously_uploads;
      if(files.upload_queue.length < upload_count) {
         upload_count = files.upload_queue.length;
      }

      for(var a=0; a<upload_count; a++) {
         if(files.current_uploading > files.simultaneously_uploads) {
            break;
         }

         var queued_file = files.upload_queue.pop();
         queued_file.start();

         files.current_uploading++;
      }
   }

   /**
    * Append new file to the file list
    *    - generate random file id
    *    - create file container and add dummy image for preview
    *    - show progress (read, upload) bar
    *
    * @param file
    * @returns {string}
    */
   files.append_new_file_to_list = function(file) {
      /* generate random id for the file */
      var file_id = 'file_' + parseInt(Math.random() * 10000000000);

      var file_ext = file.name.split('.').pop().toLowerCase();
      var preview_src = '_blank';

      var known_ext = ['aac','aiff','ai','avi','bmp','c','cpp','css','dat','dmg','doc','dotx','dwg','dxf','eps','exe','flv','gif','h','hpp','html','ics','iso','java','jpg','key','mid','mp3','mp4','mpg','odf','ods','odt','otp','ots','ott','pdf','php','png','ppt','psd','py','qt','rar','rb','rtf','sql','tga','tgz','tiff','txt','wav','xls','xlsx','xml','yml','zip'];
      if(known_ext.indexOf(file_ext) != -1) {
         preview_src = file_ext;
      }

      preview_src = '/assets/wepo/files/images/file_type_icons/100px/' + preview_src + '.png';

      /* show file */
      var new_file = jQuery('<div/>')
         .addClass('files_list_file file_uploading')
         .attr({'id': file_id})
         .append(jQuery('<div/>')
            .addClass('file_img_wrapper')
            .append(jQuery('<img/>')
               .attr({'src':preview_src,'width':'100'})
            )
         )
         .append(jQuery('<span/>')
            .addClass('file_name')
            .html(file.name)
         )
         .append(jQuery('<div/>')
            .addClass('file_controls')
            .append(jQuery('<p/>')
               .append(jQuery('<a/>')
                  .addClass('file-edit btn btn-info')
                  .attr({'attr':'#'})
                  .html('Edit')
               )
               .append(jQuery('<a/>')
                  .addClass('file-delete btn btn-primary')
                  .attr({'attr':'#'})
                  .html('Delete')
               )
            )
         );
      jQuery('#files_list_container').prepend(new_file);

      /* upload file */
      var file_progress_bar = jQuery('<div/>')
         .addClass('file_progress_bar');
      var file_progress_bar_status = jQuery('<div/>')
         .addClass('file_progress_bar_status')
         .html('reading');

      new_file.append(file_progress_bar);
      new_file.append(file_progress_bar_status);

      return file_id;
   }

   /**
    * Load more files on scroll or on button click
    */
   files.load_more_files = function() {
      jQuery('.loader').toggle();

      var random = Math.random();
      wepo.call(wepo.call_url('core/files/file_list', {token:random, wr:'json', directory: files.selected_directory, offset:files.current_offset}), files.file_list_load_callback, wepo.on_error);
   }


   /***************************************************************/
   /* Events */
   /***************************************************************/

   /**
    * Called when file is dragged over the container
    *
    * @param e
    * @returns {boolean}
    */
   files.drag_over_event = function(e) {
      return wepo.prevent_default_event(e);
   }

   /**
    * Toggle file list (hide it) and show uploader
    *    - called when file entered the container
    *
    * @param e
    * @returns {boolean}
    */
   files.drag_enter_event = function(e) {
      files.log('drag enter');

      jQuery('#files_list_container').toggle(); //hide('scale',{ percent: 0 },50);

      if(!files.files_container.hasClass('dragstart')) {
         files.files_container.addClass('dragstart');
      } else {
         files.files_container.toggleClass('dragstart');
      }

      return wepo.prevent_default_event(e);
   }

   /**
    * Toggle file list (show it) and hide uploader
    *    - called when file left the container
    *
    * @param e
    * @returns {boolean}
    */
   files.drag_leave_event = function(e) {
      files.log('drag leave');

      jQuery('#files_list_container').toggle(); //show('scale',{ percent: 100 },50);

      //files.files_container.removeClass('dragstart');{
      files.files_container.toggleClass('dragstart');

      return wepo.prevent_default_event(e);
   }

   /**
    * Handle dropped file
    *
    * @param e
    * @returns {boolean}
    */
   files.drop_event = function(e) {
      files.log('drop started');
      /* get window.event if e argument missing (in IE) */
      e = e || window.event;
      /* stops the browser from redirecting off to the image. */
      wepo.prevent_default_event(e);

      var dt    = e.dataTransfer;
      var drops = dt.files;

      files.drag_leave_event(e);

      files.handle_files(drops);

      return false;
   }

   window.wf.files = files;

}( window.wepo.files = window.wepo.files || {} ));


/**
 * File uploader
 *    @TODO - Not all files are uploaded correctly!
 *
 * @param file
 * @param file_id
 * @param options
 * @returns {FileUploader}
 * @constructor
 */
function FileUploader (file, file_id, options) {
   if (!this instanceof FileUploader) {
      return new FileUploader(file, file_id, options);
   }
   wepo.files.log('File ' + file.name + ' with id ' + file_id + ' queued.');

   this.file = file;
   this.file_id = file_id;
   this.options = jQuery.extend({
      url: '/block/core/files/upload?wr=json&raw=true'
   }, options);

   this.file_size = this.file.size;
   this.chunk_size = (1024 * wepo.files.chunk_size); // 256KB
   this.range_start = 0;
   this.range_end = this.chunk_size;

   if ('mozSlice' in this.file) {
      this.slice_method = 'mozSlice';
   }
   else if ('webkitSlice' in this.file) {
      this.slice_method = 'webkitSlice';
   }
   else {
      this.slice_method = 'slice';
   }

   this.upload_request = new XMLHttpRequest();
   this.data = {
      file_id: this.file_id,
      chunk: this.range_end,
      file_size: this.file_size,
      name: this.file.name,
      type: this.file.type,
      directory: wepo.files.selected_directory
   };

   this.is_paused = false;

   this.reader = new FileReader();
   this.current_chunk = '';
   this.chunk_upload_tries = 0;

   this.is_ipad = navigator.userAgent.match(/iPad/i) != null;
}

/**
 * Extend file uploader with upload, start, pause, resume functionality
 *
 * @type {{_upload: Function, start: Function, pause: Function, resume: Function}}
 */
FileUploader.prototype = {

   /**
    * Upload file chunk
    *    - upload chunk by chunk
    *    - @TODO encode uploaded chunks
    *
    * @private
    */
   _upload: function(chunk) {
      var self = this;

      /* slight timeout needed here (File read / AJAX readystate conflict?) */
      setTimeout(function() {

         wepo.files.log('[' + self.data.file_id + '] Sending chunk');

         self.upload_request.onload = function(e) {
            var response = JSON.parse(self.upload_request.responseText);
            wepo.files.log('Response result: ' + response.message);

            var read_next_chunk = true;

            if(response.status) {
               wepo.files.log('Chunk uploaded.');
            }
            else {
               read_next_chunk = false;
               wepo.files.log('Error while uploading chunk.');
            }

            /* try to re-upload current chunk */
            if(!read_next_chunk) {
               if(self.chunk_upload_tries > 5) {
                  wepo.files.log('Too many retries on single chunk. Pausing upload.');
               }

               self.chunk_upload_tries++;
               self._upload(chunk);
            }

            var percentage = parseInt(self.range_end/self.file_size*10000)/100.0;

            var file_progress_bar = jQuery('#' + self.file_id + ' .file_progress_bar');
            var file_progress_bar_status = jQuery('#' + self.file_id + ' .file_progress_bar_status');

            file_progress_bar.css({'width': parseInt(percentage) + 'px'});
            file_progress_bar_status.html(percentage + '%');

            /* finish uploading right after the last chunk is send */
            if (self.range_end == self.file_size) {
               wepo.files.log('Last chunk send');

               var file_obj = jQuery('#' + self.file_id);

               file_obj.animate({
                  backgroundColor: '#ffffff'
               }, 500);
               file_progress_bar.slideUp('slow', function() { jQuery(this).remove(); });
               file_progress_bar_status.slideUp('slow', function() { jQuery(this).remove(); });

               file_obj.attr({
                  'data-id':response.file_id,
                  'data-mime-type':response.file_mime_type,
                  'data-file-tag':response.file_rough_mime_type,
                  'data-file': '/media/' + response.file_path + '/' + response.file_name
               });
               setTimeout(wepo.files.upload_queued_files(), wepo.files.upload_queue_interval);

               var file_ext = self.data.name.split('.').pop().toLowerCase();
               var images_ext = ['jpg', 'gif', 'png', 'jpeg', 'tiff', 'bmp'];

               if(images_ext.indexOf(file_ext) != -1) {
                  jQuery('#' + self.data.file_id + ' .file_img_wrapper img').attr({'src': '/media/' + response.file_path + '/tmbs_' + response.file_name});
               }

               wepo.files.init_file(file_obj);
               wepo.files.current_uploading--;

               return;
            }

            // Update our ranges
            self.range_start = self.range_end;
            self.range_end = self.range_start + self.chunk_size;

            // Continue as long as we aren't paused
            if (!self.is_paused) {
               self._read();
            }
         };

         self.upload_request.open('PUT', self.options.url, true);

	      self.upload_request.setRequestHeader("Content-Type","application/json");
         self.upload_request.setRequestHeader("Cache-Control", "no-cache");
         self.upload_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
         // Refused to set unsafe header "Content-Length"
         //self.upload_request.setRequestHeader("Content-Length", '' + (self.range_end - self.range_start));
         self.upload_request.setRequestHeader("X-File-Id", self.data.file_id);
         self.upload_request.setRequestHeader("X-File-Size", self.data.file_size);
         self.upload_request.setRequestHeader("X-File-Name", self.data.name);
         self.upload_request.setRequestHeader("X-File-Type", self.data.type);
         self.upload_request.setRequestHeader("X-File-Chunk", '' + self.range_end);
         self.upload_request.setRequestHeader("X-File-Directory", '' + self.data.directory);

         if(self.is_ipad) {
            self.upload_request.send(chunk);
         }
         else {
            var uInt8chunk = new Uint8Array(chunk);
            self.upload_request.send(uInt8chunk);
         }
      }, wepo.random_int(50, 150));
   },

   /**
    * Read file chunk
    *    - read chunk by chunk
    *    - @TODO encode uploaded chunks
    *
    * @private
    */
   _read: function() {
      var self = this;

      /* slight timeout needed here (File read / AJAX readystate conflict?) */
      setTimeout(function() {
         /* Prevent range overflow */
         if (self.range_end > self.file_size) {
            self.range_end = self.file_size;
         }

         wepo.files.log('[' + self.data.file_id + '] Reading chunk ' + self.range_start  + ' - ' + self.range_end  + ' ('+(self.range_end - self.range_start)+') of ' + self.file_size);
         self.reader = new FileReader();
         var chunk = self.file[self.slice_method](self.range_start, self.range_end);

         /* push chunk to server */
         self.reader.onload = function(e) {
            self._upload(e.target.result);
         };

         //if(self.is_ipad) {
         //   self.reader.readAsBinaryString(chunk);
         //}
         //else {
            self.reader.readAsArrayBuffer(chunk);
         //}

      }, wepo.random_int(50, 150));
   },

   /**
    * Start uploading
    *    - update upload progress bar
    */
   start: function() {
      wepo.files.log('File ['+this.file_id+'] of size ' + this.file_size + ' started uploading.');

      this.new_file = jQuery('#' + this.file_id);

      /* upload file */
      var file_progress_bar = jQuery('<div/>')
         .addClass('file_progress_bar');
      var file_progress_bar_status = jQuery('<div/>')
         .addClass('file_progress_bar_status')
         .html('uploading');

      this.new_file.append(file_progress_bar);
      this.new_file.append(file_progress_bar_status);

      this._read();
   },

   /**
    * Pause uploading
    */
   pause: function() {
      this.is_paused = true;
   },

   /**
    * Resume uploading
    */
   resume: function() {
      this.is_paused = false;
      this._read();
   }
};