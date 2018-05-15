# !usr/bin/env python3
# coding: utf-8

"""Regular expression patterns for part-of-speech extraction."""

regex4 = {
    'cs': r'=={1,} ((podstatné jméno)|(přídavné jméno)|(zájmeno)|(číslovka)'
          r'|(sloveso)|(příslovce)|(předložka)|(spojka)|(citoslovce)'
          r'|(částice)) ((\(1\) )|(=={1,}))',

    'en': r'=={1,}((Noun)|(Adjective)|(Pronoun)|(Numeral)|(Verb)|(Adverb)'
          r'|(Preposition)|(Conjugation))(( \(1\) )|(=={1,}))',

    'de': r'Wortart\|((Substantiv)|(Adjektiv)|(Interrogativpronomen)'
          r'|(Demonstrativpronomen)|(Numerale)|(Verb)|(Adverb)|(Präposition)'
          r'|(Konjunktion)|(Interjektion)|(Pronominaladverb)|(Temporaladverb)'
          r'|(Partikel)|(Komparativ)|(Superlativ))',

    'fr': r'S\|((nom)|(adjectif)|(prénom)|(verbe)|(adverbe)|(numerál)'
          r'|(préposition)|(conjonction)|(particule)|(interjection))\|',

    'pl': r'\{\{znaczenia\}\}\n\'\'((rzeczownik)|(rzeczownik)|(przysłówek)'
          r'|(przymiotnik)|(czasownik)|(partykuła)|(wykrzyknik)|(skrótowiec)'
          r'|(liczebnik)|(zaimek)|(skrót)|(imiesłów)|(przyimek)'
          r'|(spójnik))[\s\,\']',

    # project derinet-connect-family
    'ze': r'=={1,}((Noun)|(Adjective)|(Pronoun)|(Numeral)|(Verb)|(Adverb)'
          r'|(Preposition)|(Conjugation))(( \(1\) )|(=={1,}))',

    'zd': r'Wortart\|((Substantiv)|(Adjektiv)|(Interrogativpronomen)'
          r'|(Demonstrativpronomen)|(Numerale)|(Verb)|(Adverb)|(Präposition)'
          r'|(Konjunktion)|(Interjektion)|(Pronominaladverb)|(Temporaladverb)'
          r'|(Partikel)|(Komparativ)|(Superlativ))',

    'zf': r'S\|((nom)|(adjectif)|(prénom)|(verbe)|(addverbe)|(numerál)'
          r'|(préposition)|(conjonction)|(particule)|(interjection))\|',

    'zp': r'\{\{znaczenia\}\}\n\'\'((rzeczownik)|(rzeczownik)|(przysłówek)'
          r'|(przymiotnik)|(czasownik)|(partykuła)|(wykrzyknik)|(skrótowiec)'
          r'|(liczebnik)|(zaimek)|(skrót)|(imiesłów)|(przyimek)'
          r'|(spójnik))[\s\,\']'
}
