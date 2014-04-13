import unittest


class TestAssets(unittest.TestCase):
   def test_core_user_login_assets(self):

      from core.asset import get_assets_config
      asset_config = get_assets_config()

      import json
      from core.models import Page
      page = Page.objects.get(name='Admin user login')
      page_assets = json.loads(page.assets)

      for location, asset_types in page_assets.items():
         for type, assets in asset_types.items():
            for asset in assets:
               self.assertIn(asset, asset_config[type])