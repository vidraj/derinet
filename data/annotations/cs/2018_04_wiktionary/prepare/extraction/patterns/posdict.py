# !usr/bin/env python3
# coding: utf-8

"""Dictionaries of part-of-speech tags in all used wiktionary mutations."""


def choose(lang, name):
    """Choose right dictionary and return tag for given pos name."""
    return eval(lang + '_pos')[name]


cs_pos = {'podstatné jméno': 'N', 'přídavné jméno': 'A', 'zájmeno': 'P',
          'číslovka': 'C', 'sloveso': 'V', 'příslovce': 'D', 'předložka': 'R',
          'spojka': 'J', 'citoslovce': 'I', 'částice': 'T'}

en_pos = {'Noun': 'N', 'Adjective': 'A', 'Pronoun': 'P', 'Numeral': 'C',
          'Verb': 'V', 'Adverb': 'D', 'Preposition': 'R', 'Conjugation': 'J'}

de_pos = {'Substantiv': 'N', 'Adjektiv': 'A', 'Interrogativpronomen': 'P',
          'Demonstrativpronomen': 'P', 'Numerale': 'C', 'Verb': 'V',
          'Adverb': 'D', 'Präposition': 'R', 'Konjunktion': 'J',
          'Interjektion': 'I', 'Pronominaladverb': 'D', 'Temporaladverb': 'D',
          'Partikel': 'T', 'Komparativ': 'A', 'Superlativ': 'A'}

fr_pos = {'verbe': 'V', 'nom': 'N', 'adjectif': 'A', 'prénom': 'N',
          'adverbe': 'D', 'numerál': 'C', 'préposition': 'R',
          'conjonction': 'J', 'particule': 'T', 'interjection': 'I'}

pl_pos = {'rzeczownik': 'N', 'rzeczownik': 'N', 'przymiotnik': 'A',
          'przysłówek': 'D', 'czasownik': 'V', 'partykuła': 'T',
          'wykrzyknik': 'I', 'skrótowiec': 'N', 'liczebnik': 'C',
          'zaimek': 'P', 'skrót': 'N', 'imiesłów': 'V', 'przyimek': 'R',
          'spójnik': 'J'}

# project derinet-connect-family
ze_pos = {'Noun': 'N', 'Adjective': 'A', 'Pronoun': 'P', 'Numeral': 'C',
          'Verb': 'V', 'Adverb': 'D', 'Preposition': 'R', 'Conjugation': 'J'}

zd_pos = {'Substantiv': 'N', 'Adjektiv': 'A', 'Interrogativpronomen': 'P',
          'Demonstrativpronomen': 'P', 'Numerale': 'C', 'Verb': 'V',
          'Adverb': 'D', 'Präposition': 'R', 'Konjunktion': 'J',
          'Interjektion': 'I', 'Pronominaladverb': 'D', 'Temporaladverb': 'D',
          'Partikel': 'T', 'Komparativ': 'A', 'Superlativ': 'A'}

zf_pos = {'verbe': 'V', 'nom': 'N', 'adjectif': 'A', 'prénom': 'N',
          'adverbe': 'D', 'numerál': 'C', 'préposition': 'R',
          'conjonction': 'J', 'particule': 'T', 'interjection': 'I'}

zp_pos = {'rzeczownik': 'N', 'rzeczownik': 'N', 'przymiotnik': 'A',
          'przysłówek': 'D', 'czasownik': 'V', 'partykuła': 'T',
          'wykrzyknik': 'I', 'skrótowiec': 'N', 'liczebnik': 'C',
          'zaimek': 'P', 'skrót': 'N', 'imiesłów': 'V', 'przyimek': 'R',
          'spójnik': 'J'}
