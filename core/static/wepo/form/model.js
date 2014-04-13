/**
 * Wepo form model element namespace
 */
(function( model ) {
   /**
    * wepo form model settings
    */
   model.callback_url = 'core/object/data';
   model.current_model = '';


   /***************************************************************/
   /* Initializations */
   /***************************************************************/

   /**
    * Model init
    *
    * @param model
    */
   model.init = function(model) {
      jQuery('#add_new_' + model).click(function(e) {
         var random = Math.random();
         wepo.form.model.current_model = jQuery(this).attr('data-model');
         wepo.form.model.current_field = jQuery(this).attr('data-field');

         var parent_model = jQuery(this).attr('data-parent-model');
         var parent_model_id = jQuery(this).attr('data-parent');
         var current_field = jQuery(this).attr('data-field');

         wepo.call(wepo.call_url('core/object/data', {token:random, wr:'json', model:model, parent:parent_model, parent_id:parent_model_id, parent_field:current_field}), wepo.form.model.load_callback, wepo.on_error);

         return wepo.prevent_default_event(e);
      });
   }

   /**
    * Model init add new
    *
    * @param model
    */
   model.init_add_new = function(model) {
      jQuery('#object-new').submit(function() {
         $(this).ajaxSubmit({
            success: function(responseText, statusText, xhr, $form) {
               wepo.log(responseText);
               wepo.callback_message(responseText);

               wepo.log(wepo.form.model.current_field);
               var field = jQuery('select[name="field_' + wepo.form.model.current_field + '"]');
               wepo.log(field);

               field.select2('destroy');
               field.append(new Option(responseText.instance, responseText.id, true, true));
               field.select2();

               wepo.popup_close();
            }
         });

         return false; // wepo.prevent_default_event(e);
      });
   }


   /***************************************************************/
   /* Callbacks */
   /***************************************************************/

   /**
    * Callback after model data is received
    *
    * @param data
    */
   model.load_callback= function(data) {
      wepo.log(data);
      wepo.ajax_popup('Adding new model', data);
   }

   window.wf.model = model;

}( window.wepo.form.model = window.wepo.form.model || {} ));