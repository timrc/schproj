#! /usr/bin/python
#
#  Wepo core cache
#


from wepo.settings import DEVELOPMENT


def get(key, force=False):
   from django.core.cache import cache
   if not DEVELOPMENT or force:
      return cache.get(key)

   return None


def set(key, val, time=0, force=False):
   from django.core.cache import cache
   if not DEVELOPMENT or force:
      return cache.set(key, val, time)

   return None


def delete(key, time=0):
   return set(key, '', 1)