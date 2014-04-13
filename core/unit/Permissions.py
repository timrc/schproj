import unittest


class TestPermissions(unittest.TestCase):
   def test_permissions(self):

      from core.permission import get_permissions
      permissions = get_permissions()

      permission_list = ['admin_access', 'authenticated']

      for permission in permissions:
         self.assertIn(permission, permission_list, 'Block %s does not exists' % permission)