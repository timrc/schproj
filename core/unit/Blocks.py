import unittest


class TestBlocks(unittest.TestCase):
   def test_admin_blocks(self):

      from core.block import get_blocks
      blocks = get_blocks()

      block_list = ["add_assets", "assets_static", "get_active_menus", "get_template", "get_user", "header_navigation", "header_search", "header_user_data", "is_menu_item_active", "page_header", "page_message", "side_navigation", "_t", "add_asset", "add_assets", "assets", "blocks", "check_permissions", "get_active", "get_installed_models_groups", "get_int_request", "get_model", "get_model_fields", "get_model_filter_fields", "get_model_form", "get_template", "load_permissions", "models", "objects", "shortcuts", "add_asset", "check_permissions", "core_ajax_add_update_object", "create_object", "edit_object", "get_create_edit_object_context", "get_model", "get_model_field_groups", "get_model_form", "get_template", "init_create_edit_object_validator", "load_permissions"]

      installed_blocks = []
      for block in blocks:
         installed_blocks.append(block.name)

      for block in block_list:
         self.assertIn(block, installed_blocks, 'Block %s does not exists' % block)