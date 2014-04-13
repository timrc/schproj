#! /usr/bin/python
#
#  Wepo core language, translation manager
#  @TODO rewrite multi-language stuff
#

from core import cache

from wepo.settings import DEFAULT_LANGUAGE
from core.helper.common_help import get_cache_key

from core.models import Translation, Language, Phrase


## Translate given phrase
#
#  @param request Current request object
#  @param phrase Phrase to translate
#  @param language Language to which you want to translate phrase (sl, en, de, ...)
#  @param translation_type Translation type (Admin interface, Page, ...)
#
def translate(request, phrase, language=None, translation_type=None):
   if not language:
      language = get_user_language(request)

   # Not implemented yet
   if translation_type:
      cache_key = get_cache_key('translation', language, 'group', translation_type)
      translations = cache.get(cache_key)
      if not translations:
         translations = {}
         all_translations = None #Translation.objects.filter(language__code=language, translation_type__name=translation_type)
         if all_translations:
            for translation in all_translations:
               translations[translation.phrase.text] = translation.text

         cache.set(cache_key, translations)

      if phrase in translations:
         return translations[phrase]

      return phrase

   else:
      from core.helper.common_help import get_cache_key_2
      phrase_key_name = get_cache_key_2(phrase)
      cache_key = get_cache_key('translation', language, phrase_key_name)
      translation = cache.get(cache_key)

      result = phrase
      if not translation:
         phrase_obj = Phrase.objects.filter(key_name=phrase_key_name)
         if phrase_obj and len(phrase_obj) > 0:
            phrase_obj = phrase_obj[0]
            translations = Translation.objects.filter(language__code=language, phrase=phrase_obj)
            if translations and len(translations) > 0:
               translation = translations[0]
               stat = cache.set(cache_key, translation)
            else:
               new_translation = Translation()
               new_translation.translation = phrase
               new_translation.phrase = phrase_obj
               new_translation.language = Language.objects.get(code=language)
               new_translation.save()
         else:
            new_phrase = Phrase()
            new_phrase.text = phrase
            new_phrase.save()

            new_translation = Translation()
            new_translation.translation = phrase
            new_translation.phrase = new_phrase
            new_translation.language = Language.objects.get(code=language)
            new_translation.save()
      else:
         result = translation.translation

      return result


## Get user language
#
#  @param request Current request object
#
def get_user_language(request):
   if 'user_language' in request.session:
      return request.session['user_language']
   else:
      request.session['user_language'] = DEFAULT_LANGUAGE
      return DEFAULT_LANGUAGE


## Get language by name
#
#  @param code Language code
#
def get_language_by_code(code):
   languages = None # Language.object.filter(code=code)
   if languages and len(languages) > 0:
      return languages[0]

   return None


## Get language by name
#
#  @param name Language name
#
def get_language_by_name(name):
   languages = None # Language.object.filter(name=name)
   if languages and len(languages) > 0:
      return languages[0]

   return None


## Get translation type by name
#
#  @name Translation type name
#
def get_translation_type_by_name(name):
   translation_types = None #TranslationType.object.filter(name=name)
   if translation_types and len(translation_types) > 0:
      return translation_types[0]

   return None
