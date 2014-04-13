#! /usr/bin/python
#
#  Wepo core unit tests
#

from django.test import TestCase

## Simple, dummy test, to test if unit tests are working
#
#  Tests that 1 + 1 always equals 2.
#
class SimpleTest(TestCase):
    def test_basic_addition(self):
        self.assertEqual(1 + 1, 2)
