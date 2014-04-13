/**
 * Wepo form assets element namespace
 */
(function( assets ) {
   /**
    * wepo form assets settings
    */
   assets.callback_url = '/block/core/admin/list/assets';
   assets.data = '';

   /* assets init */
   assets.init = function(initial_data) {

      /*jQuery('.dd').each(function() {
         jQuery(this).nestable({maxDepth: 1})
            .on('change', wepo.form.assets.update)
      });
      */

      jQuery('#accordion-assets .sortable-script .dd-list').sortable({
         connectWith: jQuery('#accordion-assets .sortable-script .dd-list'),
         cursor: 'move',
         placeholder: 'placeholder_small',
         forcePlaceholderSize: true,
         opacity: 0.4,
         update: function (event, ui) {
            assets.update();
         }
      }).disableSelection();

      jQuery('#accordion-assets .sortable-style .dd-list').sortable({
         connectWith: jQuery('#accordion-assets .sortable-style .dd-list'),
         cursor: 'move',
         placeholder: 'placeholder_small',
         forcePlaceholderSize: true,
         opacity: 0.4,
         update: function (event, ui) {
            assets.update();
         }
      }).disableSelection();

      jQuery('#accordion-assets .sortable-meta .dd-list').sortable({
         connectWith: jQuery('#accordion-assets .sortable-meta .dd-list'),
         cursor: 'move',
         placeholder: 'placeholder_small',
         forcePlaceholderSize: true,
         opacity: 0.4,
         update: function (event, ui) {
            assets.update();
         }
      }).disableSelection();

      jQuery('.add_asset_link').click(function() {
         var asset_type=jQuery(this).attr('data-asset-type');
         var asset_location=jQuery(this).attr('data-asset-location');
         jQuery.ajax({
           dataType: "json",
           url: assets.callback_url + '?bla=123&wr=json&asset_type=' + asset_type + '&asset_location=' + asset_location,
           success: assets.load_callback
         });
      });

      assets.enable_assets();
      assets.data = initial_data;
      assets.update();
   }

   /* enable assets actions */
   assets.enable_assets = function() {
      jQuery('.delete-asset').click(function() {
         jQuery(this).closest('li').slideUp('fast', function() { jQuery(this).remove(); assets.update();});
      });

      jQuery('.disable-asset').click(function() {
         jQuery(this).closest('li').toggleClass('disabled');

         if (jQuery(this).closest('li').hasClass('disabled')) {
            wepo.log('Disabling asset');
            jQuery('i', this).removeClass('icon-minus');
            jQuery('i', this).addClass('icon-plus');
         } else {
            wepo.log('Enabling asset');
            jQuery('i', this).removeClass('icon-plus');
            jQuery('i', this).addClass('icon-minus');
         }
         assets.update();
      });
   }

   /* enable block actions */
   assets.enable_asset = function(asset) {
      if(jQuery('.delete-asset', asset).length != 0) {
         jQuery('.delete-asset', asset).click(function() {
            jQuery(this).closest('li').slideUp('fast', function() { jQuery(this).remove(); assets.update();});
         });
         return false;
      } else {
         jQuery('.disable-asset', asset).click(function() {
            jQuery(this).closest('li').toggleClass('disabled');

            if (jQuery(this).closest('li').hasClass('disabled')) {
               wepo.log('Disabling asset');
               jQuery('i', this).removeClass('icon-minus');
               jQuery('i', this).addClass('icon-plus');
            } else {
               wepo.log('Enabling asset');
               jQuery('i', this).removeClass('icon-plus');
               jQuery('i', this).addClass('icon-minus');
            }
            assets.update();
         });
         return false;
      }
   }

   /* after page parent is changed */
   assets.change_parent = function(parent, instance) {
      wepo.info(parent);

      jQuery.ajax({
        dataType: "json",
        url: '/block/core/admin/form/assets?wr=json&parent=' + parent + '&instance=' + instance,
        success: assets.parent_change_load_callback
      });
   }
   assets.parent_change_load_callback = function(data) {
      wepo.info(data);
      //jQuery('#page_assets').parent().html(data.content.html_decode());
      jQuery('#accordion-assets').parent().html(data.content.html_decode());
      assets.init({});
      wepo.add_ajax_assets(data);
   }


   /* after asset content is successfully loaded */
   assets.load_callback = function(data) {
      wepo.ajax_popup('Assets', data);

      jQuery('.select-asset').click(function() {
         var asset_path=jQuery(this).attr('data-asset');
         var asset_name=jQuery(this).attr('data-asset-name');
         var asset_type=jQuery(this).attr('data-asset-type');
         var asset_location=jQuery(this).attr('data-asset-location');

         wepo.info('Adding new asset ' + asset_name + ' ' + asset_path + ' ' + asset_type + ' ' + asset_location);

         var item =
            jQuery('<li/>')
               .attr({'class': 'dd-item','data-asset-path': asset_path, 'data-asset-name': asset_name})
               .append(
                  jQuery('<div/>')
                     .attr({'class': 'dd-handle'})
                     .html(asset_name)
                     .append(
                        jQuery('<button/>')
                           .attr({'type': 'button', 'class': 'close close-sm delete-asset'})
                           .append(
                              jQuery('<i/>').attr({'class': 'icon-remove'})
                           )
                     )
               );

         jQuery('.asset-location-'+asset_location+'.asset-type-' + asset_type + ' .dd-list').append(item);
         assets.enable_asset(item);

         assets.update();

         jQuery('.simplemodal-close').click();
      });
   }

   /**
    * @TODO last item in location -> type is not updated (if parent is disabled, it's not added to the list
    * update assets position
    */

   assets.update = function() {
      wepo.log('Updating');
      var local_data = {}
      var locations = ['head'/*, 'body'*/, 'footer'/*, 'last'*/];
      var types = ['meta', 'script', 'style'];
      for (var a=0; a<locations.length; a++) {
         wepo.log('... location ' + locations[a]);
         for(var b=0; b<types.length; b++) {
         wepo.log('... ... type ' + types[b]);
            var items = [];
            var prev_parent = false;
            var current_items = [];
            jQuery('#accordion-assets .asset-location-' + locations[a] + '.asset-type-' + types[b] + ' li').each(function() {
               var asset_path = jQuery(this).attr('data-asset-path');
               var asset_name = jQuery(this).attr('data-asset-name');
               var disabled = jQuery(this).hasClass('disabled');
               var deletable = jQuery('.delete-asset', this).length != 0;

               wepo.log('... ... ... item ' + asset_name + ' [deletable: '+deletable+', disabled: '+disabled+'] ' + (current_items.length));

               /* parent! do not add it except if is disabled or has items to append to it */
               if(!deletable) {
                  wepo.log('... ... ... ... parent');

                  /* if this is new parent, and previous has some items to append, append them with PARENT+ITEM1,ITEM2,ITEM3,... */
                  if(current_items.length > 0) {
                     wepo.log('... ... ... ... append current items to parent');
                     wepo.log(prev_parent + '+' + current_items.join());
                     items.push(prev_parent + '+' + current_items.join());
                     current_items = [];
                  }
                  /* also add parent if it was disabled */
                  else {
                     if(prev_parent != false && prev_parent[0] == '-') {
                        wepo.log('... ... ... ... add parent cause its disabled');
                        items.push(prev_parent);
                        wepo.log(items);
                     }
                  }

                  /* set parent, and add prefix - if it is disabled */
                  prev_parent = asset_path;
                  if(disabled) {
                     wepo.log('... ... ... ... set parent as disabled');
                     prev_parent = '-' + prev_parent;
                     wepo.log(prev_parent);
                  }
               }
               /* normal item, add it to current items */
               else {
                  wepo.log('... ... ... ... mark item as current');
                  current_items.push(asset_path);
                  wepo.log(current_items);
               }
            });
            /* if some items are last in the list, append them to the list*/
            if(current_items.length > 0) {
               wepo.log('... ... ... ... and remainings?');
               wepo.log(current_items);
               items.append(current_items);
            }
            /* add last parent */
            else {
               if(prev_parent != false && prev_parent[0] == '-') {
                 wepo.log('... ... ... ... add last parent');
                  items.push(prev_parent);
               }
            }

            /* add items to location-type map */
            if(!(locations[a] in local_data)) {
               local_data[locations[a]] = {};
            }

            if(items.length > 0) {
               local_data[locations[a]][types[b]] = items;
            }
         }
      }

      wepo.log(local_data);
      assets.data = local_data;

      wepo.log(JSON.stringify(assets.data));
      jQuery('#accordion-assets input[name="assets"]').val(JSON.stringify(assets.data));
   }

   window.wf.assets = assets;

}( window.wepo.form.assets = window.wepo.form.assets || {} ));