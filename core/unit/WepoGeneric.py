import unittest
from core.helper import WepoGeneric


class TestWepoGeneric(unittest.TestCase):
   def test_should_init_with_one_dict(self):
      my_dict = WepoGeneric({'foo': 42, 'spam': 'bar'})
      self.assertEquals(my_dict.foo, 42)
      self.assertEquals(my_dict['foo'], 42)
      self.assertEquals(my_dict.spam, 'bar')
      self.assertEquals(my_dict['spam'], 'bar')

   def test_should_not_change_values_by_inited_dict(self):
      base = {'foo': 42, 'spam': 'bar'}
      my_dict = WepoGeneric(base)
      base['foo'] = 123
      self.assertEquals(my_dict.foo, 42)
      self.assertEquals(my_dict['foo'], 42)
      self.assertEquals(my_dict.spam, 'bar')
      self.assertEquals(my_dict['spam'], 'bar')

   def test_get_item(self):
      my_dict = WepoGeneric()
      my_dict.test = 123
      self.assertEquals(my_dict.test, 123)
      self.assertEquals(my_dict['test'], 123)

   def test_set_item(self):
      my_dict = WepoGeneric()
      my_dict['test'] = 123
      self.assertEquals(my_dict['test'], 123)
      self.assertEquals(my_dict.test, 123)

   def test_del_attr(self):
      my_dict = WepoGeneric()
      my_dict['test'] = 123
      my_dict['python'] = 42
      del my_dict['test']
      del my_dict.python
      with self.assertRaises(KeyError):
         temp = my_dict['test']
      with self.assertRaises(AttributeError):
         temp = my_dict.python

   def test_in_should_work_like_in_dict(self):
      my_dict = WepoGeneric()
      my_dict['test'] = 123
      self.assertIn('test', my_dict)
      self.assertNotIn('bla', my_dict)

   def test_len_should_work_like_in_dict(self):
      my_dict = WepoGeneric()
      my_dict['test'] = 123
      my_dict.python = 42
      self.assertEquals(len(my_dict), 2)

   def test_repr(self):
      my_dict = WepoGeneric()
      my_dict['test'] = 123
      my_dict.python = 42
      self.assertEquals(repr(my_dict), "{'test': 123, 'python': 42}")

   def test_equal(self):
      my_dict = WepoGeneric({'test': 123})
      my_dict_2 = WepoGeneric({'test': 123})
      self.assertEquals(my_dict, my_dict_2)