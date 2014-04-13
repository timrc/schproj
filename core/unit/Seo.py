import unittest


class TestSeo(unittest.TestCase):
   def test_error_seo(self):
      from core.models import Seo

      url = '/error'
      seo = Seo.objects.get(url=url)

      self.assertEqual(seo.url, 'bla')