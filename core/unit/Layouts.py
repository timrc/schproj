import unittest


class TestLayouts(unittest.TestCase):
   def test_admin_layouts(self):

      from core.helper import get_layouts
      layouts = get_layouts()