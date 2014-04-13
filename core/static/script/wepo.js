/**
 * Core wepo namespace,
 *    extend it to create new functionalities
 */


/**
 * Core namespace
 */
(function( wepo ) {
   /* wepo version */
   var version = '0.91';


   /***************************************************************/
   /* Wepo debug logging */
   /***************************************************************/
   wepo.debug = true;

   wepo.debug_general = true;
   wepo.debug_info = true;
   wepo.debug_error = true;
   wepo.debug_warn = true;

   /* general log */
   wepo.log = function(data) {
      wepo.debug && wepo.debug_general && console.log(data);
   }
   /* error log */
   wepo.error = function(data) {
      wepo.debug && wepo.debug_error && console.error(data);
   }
   /* warning log */
   wepo.warn = function(data) {
      wepo.debug && wepo.debug_warn && console.warn(data);
   }
   /* info log */
   wepo.info = function(data) {
      wepo.debug && wepo.debug_info && console.info(data);
   }


   /* wepo vars */
   wepo.assets = [];
   wepo.url_parts = [];


   /***************************************************************/
   /* Wepo popup */
   /***************************************************************/

   /* settings */
   wepo.popup_settings = {
      open: function (d) {
         var self = this;
         self.container = d.container[0];
         d.overlay.fadeIn(100, function () {
            jQuery("#modal", self.container).show();
            var title = jQuery(".widget-head", self.container);
            title.show();
            d.container.slideDown(100, function () {
               setTimeout(function () {
                  var h = jQuery(".widget-body", self.container).height() + title.height() + 20;
                  d.container.animate(
                     {height: h},
                     100,
                     function () {
                        jQuery(".widget-body", self.container).show();
                     }
                  );
               }, 100);
            });
         })
      },
      close: function (d) {
         var self = this;
         d.container.animate(
            {top:"-" + (d.container.height() + 20)},
            100,
            function () {
               self.close();
            }
         );
      }
   };

   /**
    * Open popup after ajax callback
    *
    * @param title
    * @param data
    */
   wepo.ajax_popup = function(title, data) {
      wepo.popup_title(title);
      wepo.popup_content(data.content);
      wepo.add_ajax_assets(data);
      wepo.popup_show();
   }

   /**
    * Set popup title
    *
    * @param title
    */
   wepo.popup_title = function(title) {
      jQuery("#modal .modal-title").html(title);
   }

   /**
    * Set popup content
    *
    * @param content
    */
   wepo.popup_content = function(content) {
      jQuery("#modal .modal-body").html(content.html_decode());
   }

   /**
    * Close popup window
    */
   wepo.popup_close = function() {
      jQuery('#modal .modal-header .close').click();
   }

   /**
    * Show popup window
    */
   wepo.popup_show = function() {
      jQuery("#modal").modal(/*{
         overlayId: 'modal_overlay',
         closeHTML: null,
         minHeight: 80,
         maxHeight: 400,
         opacity: 65,
         position: ['0'],
         overlayClose: true,
         onOpen: wepo.popup_settings.open,
         onClose: wepo.popup_settings.close
      }*/);
   }


   /***************************************************************/
   /* Define helper functions */
   /***************************************************************/

   /**
    * Get part of url at the specified position
    *
    * @param position
    */
   wepo.url_part = function(position) {
      if (wepo.url_parts.length > position) {
         return wepo.url_parts[position];
      }

      return '';
   }

   /**
    * Redirect user to desired location
    *
    * @param url
    */
   wepo.redirect = function(url) {
      window.location = url;
   }

   /**
    * Returns a random number between min and max
    *
    * @param min
    * @param max
    * @returns {number}
    */
   wepo.random = function(min, max) {
       return Math.random() * (max - min) + min;
   }

   /**
    * Returns a random integer between min and max
    * Using Math.round() will give you a non-uniform distribution!
    *
    * @param min
    * @param max
    * @returns {number}
    */
   wepo.random_int = function(min, max) {
       return Math.floor(Math.random() * (max - min + 1)) + min;
   }


   /***************************************************************/
   /* Define helper prototype functions */
   /***************************************************************/

   /**
    * Remove range from array - By John Resig (MIT Licensed)
    *
    * @param from
    * @param to
    * @returns {Number}
    */
   Array.prototype.remove = function(from, to) {
     var rest = this.slice((to || from) + 1 || this.length);
     this.length = from < 0 ? this.length + from : from;
     return this.push.apply(this, rest);
   };

   /**
    * Append array to array
    *
    * @param array
    */
   Array.prototype.append = function(array) {
      this.push.apply(this, array)
   };

   /**
    * Decode encoded html
    *
    * @returns {string}
    */
   String.prototype.html_decode = function() {
      return this
         .replace(/&amp;/g, "&")
         .replace(/&gt;/g, ">")
         .replace(/&lt;/g, "<")
         .replace(/&quot;/g, '"')
         .replace(/&#39;/g, "'")
         .replace(/u'/g, "'");
   };

   /**
    * Replace single quotes with double quotes and vv
    *
    * @returns {string}
    */
   String.prototype.switch_quotes = function() {
      return this
         .replace(/"/g, '&quot;')
         .replace(/'/g, '"')
         .replace(/&quot;/g, "'")
   };

   /**
    * Title-ize string
    */
   String.prototype.create_title = function () {
      return this.replace(/\w\S*/g, function(txt) {
         return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
      });
   };

   /**
    * Replace all occurrence of substring in string
    *
    * @param find
    * @param replace
    * @returns {string}
    */
   String.prototype.replaceAll = function (find, replace) {
      return this.replace(new RegExp(find, 'g'), replace);
   };

   /**
    * Check if string starts with substring
    *
    * @param str
    * @returns {boolean}
    */
   String.prototype.startsWith = function (str){
      return this.slice(0, str.length) == str;
   };

   /**
    * Check if string ends with substring
    *
    * @param str
    * @returns {boolean}
    */
   String.prototype.endsWith = function (str){
      return this.slice(-str.length) == str;
   };

   /* bind to event handler */
   Function.prototype.bind_to_event_handler = function bind_to_event_handler() {
      var handler = this;
      var boundParameters = Array.prototype.slice.call(arguments);
      //create closure
      return function(e) {
         e = e || window.event; // get window.event if e argument missing (in IE)
         boundParameters.unshift(e);
         handler.apply(this, boundParameters);
      }
   };


   /***************************************************************/
   /* Define helper functions */
   /***************************************************************/

   /**
    *  Ajax block callback
    *
    * @param url
    * @param callback
    * @param data
    */
   wepo.call = function(url, callback, on_error, data) {
      if(data == undefined) {
         data = {}
      }

      if(data.dataType == undefined) {
         data.dataType = 'json';
      }

      /* auto append block if internal url is called */
      if(url.startsWith('http') || url.startsWith('ftp')) {
         data.url = url;
      }
      else {
         data.url = '/block/' + url;
      }

      data.success = callback;
      data.error = on_error;

      jQuery.ajax(data);
   }

   /**
    * Generate callback url
    *
    * @param url
    * @param params
    */
   wepo.call_url = function(url, params) {
      var data = [];
      if(params != undefined) {
         for(var p in params) {
            data.push(encodeURIComponent(p) + '=' + encodeURIComponent(params[p]));
         }
      }

      /* join items with & sign */
      if(data.length > 0) {
        return url + '?' + data.join("&");
      }

      return url;
   }

   /**
    * Get object data
    *
    * @param model
    * @param id
    */
   wepo.get_data = function(model, id, callback) {
      var random = Math.random();
      wepo.call(wepo.call_url('core/object/data', {model:model, id:id, wr:'json', raw:true, token:random}), callback);
   }

   /**
    * Append assets from ajax callback
    *
    * @param assets: dict
    */
   wepo.add_ajax_assets = function(data) {
      var assets = data.assets

      /* for each asset in the location->type mapping */
      for(var asset_location in assets) {
         for(var asset_type in assets[asset_location]) {
            for(var index in assets[asset_location][asset_type]) {
               var asset = assets[asset_location][asset_type][index];
               if(asset.code != 'undefined') {
                  wepo.add_asset(asset_location, asset_type, asset.code, asset.include_type, asset.md5);
               }
            }
         }
      }
   }

   /**
    * Append asset
    *
    * @param location: head|body|footer|last
    * @param type: script\style|meta
    * @param code
    * @param include_type: code|link
    *
    */
   wepo.add_asset = function(location, type, code, include_type, md5) {
      if(code == undefined) {
         return;
      }

      if(wepo.assets.indexOf(md5) != -1 && include_type == 'link') {
         return;
      }

      wepo.info('Adding new asset of type ' + type + ' to ' + location);

      wepo.assets.push(md5);

      var asset = '';
      if(type == 'script') {
         asset = document.createElement("script");
         asset.type  = "text/javascript";

         if(include_type == 'code') {
            asset.text = code;
         }
         if(include_type == 'link') {
            asset.src = code.src;
         }
      }
      else if(type == 'style') {
         if(include_type == 'code') {
            asset = document.createElement("style");
            asset.text = code;
         }
         if(include_type == 'link') {
            asset = document.createElement("link");
            asset.type  = "text/css";
            asset.rel   = "stylesheet";
            asset.href  = code.href;
         }
      }

      if(location == 'head') {
         document.head.appendChild(asset);
      }
      else if(location == 'body') {
         document.body.prependChild(asset);
      }
      else if(location == 'footer' || location == 'last') {
         document.body.appendChild(asset);
      }
   }

   /**
    * Check if object is array
    *
    * @param obj
    * @returns {boolean}
    */
   wepo.is_array = function(obj) {
      return (!!obj) && (obj.constructor === Array);
   }

   /**
    * Check if object is objects
    *
    * @param obj
    * @returns {boolean}
    */
   wepo.is_object = function(obj) {
      return (!!obj) && (obj.constructor === Object);
   }


   /***************************************************************/
   /* Callbacks */
   /***************************************************************/

   /**
    * Display callback message (error, success,... )
    *
    * @param data
    */
   wepo.callback_message = function(data) {
      wepo.log('Message ' + data.message + ' with status ' + data.status);

      var messages = jQuery('#messages');

      if(messages) {
         var message_status = 'Success! ';
         if(data.status == 'error') {
            message_status = 'Oh snap! '
         }
         var item =
            jQuery('<div/>')
               .attr({'class': 'alert alert-' + data.status + ' alert-block fade in'})
               .append(
                  jQuery('<button/>')
                     .attr({'type': 'icon', 'class': 'close close-sm', 'data-dismiss': 'alert'})
                     .append(
                        jQuery('<i/>')
                           .attr({'class': 'icon-remove'})
                     )
               )
               .append(
                  jQuery('<strong/>')
                     .html(message_status)
               )
               .append(data.message);
         messages.append(item);
      }

      var notification = jQuery('.notification');
      if(notification) {
         var today = new Date();
         var hours = today.getHours();
         var minutes = today.getMinutes();

         var item =
            jQuery('<li/>')
               .append(
                  jQuery('<a/>')
                     .attr({'href': '#'})
                     .append(
                        jQuery('<span/>')
                           .attr({'class': 'label label-success'})
                           .append(
                              jQuery('<i/>').attr({'class': 'icon-plus'})
                           )
                     )
                     .append(
                        jQuery('<span/>')
                           .attr({'class': 'message'})
                           .html(data.message)
                     )
                     .append(
                        jQuery('<span/>')
                           .attr({'class': 'time'})
                           .html(hours + ':' + minutes)
                     )
               );
         notification.append(item);

         var counter = jQuery('.notification-counter').html();
         counter = parseInt(counter) + 1;
         jQuery('.notification-counter').html(counter);
      }
   }


   /***************************************************************/
   /* Events */
   /***************************************************************/

   /**
    * Prevent default event
    *    - try to prevent default event and return false status
    *
    * @param e
    * @returns {boolean}
    */
   wepo.prevent_default_event = function(e) {
      if (e.preventDefault) {
         e.preventDefault();
      }
      return false;
   }

   /**
    * Add event handler
    *
    * @param obj Object to append handler
    * @param evt Event to add
    * @param handler Event callback function
    */
   wepo.add_event_handler = function (obj, evt, handler) {
       if(obj.addEventListener) {
           // W3C method
           obj.addEventListener(evt, handler, false);
       } else if(obj.attachEvent) {
           // IE method.
           obj.attachEvent('on'+evt, handler);
       } else {
           // Old school method.
           obj['on'+evt] = handler;
       }
   }

   /* wepo namespace shortcut */
   window.w = wepo

}( window.wepo = window.wepo || {} ));


/***************************************************************/
/* Currently unused namespaces */
/***************************************************************/

/**
 * Wepo form elements namespace
 */
(function( form ) {
   /* wepo form elements shortcut */
   window.wf = form

}( window.wepo.form = window.wepo.form || {} ));

/**
 * Wepo controls namespace
 */
(function( control ) {
   /* wepo control shortcut */
   window.wc = control

}( window.wepo.control = window.wepo.control || {} ));