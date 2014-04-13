/**
 * Wepo form blocks element namespace
 */
(function( blocks ) {
   /**
    * wepo form blocks settings
    */
   blocks.callback_url = '/block/core/admin/list/blocks';
   blocks.data = '';

   /* blocks init */
   blocks.init = function(initial_data) {
      jQuery('#page_blocks .sortable').sortable({
         connectWith: jQuery('#page_blocks .sortable'),
         cursor: 'move',
         placeholder: 'placeholder span12 notes',
         forcePlaceholderSize: true,
         opacity: 0.4,
         update: function (event, ui) {
            blocks.update();
         }
      }).disableSelection();

      jQuery('.add_block_link').click(function() {
         var section=jQuery(this).attr('data-section');
         jQuery.ajax({
           dataType: "json",
           url: blocks.callback_url + '?wr=json&section=' + section,
           success: blocks.load_callback
         });
      });

      blocks.enable_blocks();
      blocks.data = initial_data;
   }

   /* enable blocks actions */
   blocks.enable_blocks = function() {
      jQuery('.block-edit').click(function() {
         jQuery(this).closest('li.notes').toggleClass('enabled');
         blocks.update();
      });

      jQuery('.block-delete').click(function() {
         jQuery(this).closest('li.notes').slideUp('fast', function() { jQuery(this).remove(); blocks.update();});
      });

      jQuery('.block-toggle').click(function() {
         jQuery(this).closest('li.notes').toggleClass('enabled');
         if (jQuery(this).closest('li notes').hasClass('enabled')) {
            jQuery(this).html('<i></i> Disabled');
         } else {
            jQuery(this).html('<i></i> Enabled');
         }
         blocks.update();
   });
   }

   /* enable block actions */
   blocks.enable_block = function(block) {
      jQuery('.block-edit', block).click(function() {
         jQuery(this).closest('li.notes').toggleClass('enabled');
         blocks.update();
      });

      jQuery('.block-delete', block).click(function() {
         jQuery(this).closest('li.notes').slideUp('fast', function() { jQuery(this).remove(); blocks.update();});
      });

      jQuery('.block-toggle', block).click(function() {
         jQuery(this).closest('li.notes').toggleClass('enabled');
         if (jQuery(this).html().indexOf('Disable') == -1) {
            jQuery(this).html('<i></i> Disabled');
         } else {
            jQuery(this).html('<i></i> Enabled');
         }
         blocks.update();
      });
   }

   /* after layout is changed */
   blocks.change_layout = function(layout, instance) {
      wepo.log(layout);

      jQuery.ajax({
        dataType: "json",
        url: '/block/core/admin/form/blocks?wr=json&layout=' + layout + '&instance=' + instance,
        success: blocks.layout_change_load_callback
      });
   }
   blocks.layout_change_load_callback = function(data) {
      wepo.log(data);
      jQuery('#page_blocks').html(data.content.html_decode());
      blocks.init({});
      wepo.add_ajax_assets(data);
   }

   /* after block content is successfully loaded */
   blocks.load_callback = function(data) {
      wepo.ajax_popup('Blocks', data);

      jQuery('.select-block').click(function() {
         var block_path=jQuery(this).attr('data-block');
         var block_name=jQuery(this).attr('data-block-name');
         var section=jQuery(this).attr('data-section');

         var item =
            jQuery('<li/>')
               .addClass('span12 glyphicons notes enabled')
               .attr({'style': 'margin-left:0px;','data-block-path':block_path})
               .append(jQuery('<i/>'))
               .append(jQuery('<strong/>')
                  .html(block_name))
               .append(jQuery('<span/>')
                  .addClass('actions')
                  .append(jQuery('<a/>')
                     .addClass('glyphicons edit block-edit')
                     .attr({'href':'#'})
                     .append(jQuery('<i/>'))
                     .append(' Edit'))
                  .append(' |')
                  .append(jQuery('<a/>')
                     .addClass('glyphicons remove_2 block-delete')
                     .attr({'href':'#'})
                     .append(jQuery('<i/>'))
                     .append(' Delete'))
                  .append(' |')
                  .append(jQuery('<a/>')
                     .addClass('glyphicons lock block-toggle')
                     .attr({'href':'#'})
                     .append(jQuery('<i/>'))
                     .append(' Disable'))
               );

         jQuery('.section-' + section).append(item);
         blocks.enable_block(item);

         blocks.update();

         jQuery('.simplemodal-close').click();
      });
   }

   /* update blocks position */
   blocks.update = function() {
      wepo.log('Updating');
      for(var section in blocks.data) {
         var items = [];
         jQuery('#page_blocks .section-' + section + ' li').each(function() {
            var block_path = jQuery(this).attr('data-block-path');
            var block_name = jQuery('strong', this).html();
            var enabled = jQuery(this).hasClass('enabled');

            items.append([{'enabled': enabled, 'name': block_name, 'path': block_path}])
         });
         blocks.data[section] = items;
      }

      jQuery('#page_blocks input[name="blocks"]').val(JSON.stringify(blocks.data));
   }

   window.wf.blocks = blocks;

}( window.wepo.form.blocks = window.wepo.form.blocks || {} ));