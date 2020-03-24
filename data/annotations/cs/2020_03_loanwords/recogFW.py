#!usr/bin/env python3
# coding: utf-8

"""Script for the recognition of foreign words in the Czech language. (V2)"""

import sys
import itertools as it


# function for the recognition of foreign word
# can be imported and used in any project
def recog_foreign_word(word, pos=None):
    """Return T/F statement if given word (and pos optionaly) is foreign."""
    word = word.lower()

    # foreign letters and czech alphabet
    for letter in 'gxwqóf':
        if letter in word:
            return True

    alphabeth = 'aábcčdďeéěhiíjklmnňoprřsštťuůúvyýzž'
    for letter in word:
        if letter not in alphabeth:
            return True

    # exclude Czech verbs (non-foreign verbs)
    if pos == 'V' and not word.endswith('vat'):
        return False

    # consists 'ú' inside the word
    allowed_u = ('zú', 'zaú', 'poú', 'doú', 'přeú', 'podú', 'předú', 'vyú')
    if 'ú' in word[1:] and not word.startswith(allowed_u):
        return True

    # combinations of vowels (except 'ou', and some others for comp./afixes)
    vowels = 'aeiyouáéěíýůú'

    combinations = list(it.product(vowels, repeat=2))
    del combinations[combinations.index(('o', 'u'))]

    allowed_comb = ('doo', 'poo', 'velkoo', 'těžkoo', 'poloo', 'maloo',
                    'samoo', 'černoo', 'šikmoo', 'světoo', 'světloo', 'tmavoo',
                    'vodoo', 'celoo', 'proo', 'jednoo', 'perloo', 'středoo',
                    'dřevoo', 'hnědoo', 'šedoo', 'vyu', 'sebeu') + allowed_u
    for pair in combinations:
        comb = pair[0] + pair[1]
        if comb in word and not any(prefix in word for prefix in allowed_comb):
            return True

    # doubled consonants
    consonants = 'bcfghlmpqrstvwx'
    for letter in consonants:
        if letter + letter in word:
            return True

    allowed_zz = ('bezz', 'rozz')
    if 'zz' in word:
        if not any(prefix in word for prefix in allowed_zz):
            return True

    allowed_kk = ('kký', 'kká', 'kké', 'kko')
    if 'kk' in word:
        if not any(part in word for part in allowed_kk):
            return True

    # combinations of n-grams or roots
    combinations = ('ajc', 'ajs', 'ajz', 'unk', 'uňk', 'th', 'rm', 'cr', 'dž',
                    'elitn', 'test', 'kredit', 'habit', 'decim', 'zip', 'data',
                    'dato')

    for infix in combinations:
        if infix in word:
            return True

    if 'ir' in word and not ('šir' in word or 'řir' in word):
        return True

    if 'sc' in word and 'sch' not in word:
        return True

    # unrespected palatalization after k, h, ch, r
    ke_allowed = ('kerý', 'kev', 'keř', 'kenní', 'keřný', 'keřně', 'kelný',
                  'kelně')
    re_allowed = ('rev', 'rec', 'revný', 'revně', 'rek', 'recký', 'recky',
                  'rectví', 'rectvo', 'reček', 'rečka', 'rečník', 'rejší')

    for comb in ('re', 'ke'):
        res = True
        if comb in word:
            for end in eval(comb + '_allowed'):
                if word.endswith(end):
                    res = True

            if res is False:
                return True

    if 'he' in word and 'herec' not in word and 'hereč' not in word:
        return True

    if 'che' in word:
        return True

    # unrespected soft and hard consonants
    hard_consonants = ('h', 'ch', 'k', 'r')
    for pair in list(it.product(hard_consonants, 'ií')):
        comb = pair[0] + pair[1]
        if comb in word:
            return True

    soft_consonants = 'žščřcj'
    for pair in list(it.product(soft_consonants, 'yý')):
        comb = pair[0] + pair[1]
        if comb in word:
            return True

    # unrespecting y followed by mixed consonants (b, l, m, p, s, v, z)
    vowels_long = 'áéíýůú'
    vowels_all = 'aeiyouáéěíýůú'

    all_patterns = {'by': ('byt', 'byl', 'aby', 'kdyby', 'čby', 'bych',
                           'bys@', 'byste', 'byv', 'bydl', 'byč', 'byst',
                           'bysl'),

                    'ly': ('slyš', 'mlyn', 'lyka', 'lyká', 'plyn', 'vzlyk',
                           'lysý', 'lysi', 'lyso', 'lysic', 'lyž', 'lyň',
                           'plyš'),

                    'my': ('myd', 'myt', 'myč', 'myc', 'myj', 'mysl', 'myšl',
                           'myl', 'hmyz', 'myš', 'myk', 'mych'),

                    'py': ('pych', 'pyt', 'pyl', 'pysk', 'pyka', 'pyká',
                           'pyš'),

                    'sy': ('syn@', 'synVA', 'sysl', 'syse', 'sytVA', 'syt@',
                           'syre', 'syro', 'sychr', 'sychVA', 'syč', 'syk',
                           'syp', 'sycVA'),

                    # 'vy': ('vys', 'vyš', 'vyk', 'vyd', 'vyž', '#vy'),

                    'zy': ('brzy', 'jazyk', 'jazyl', 'zýv')}

    for name, patterns in all_patterns.items():
        checked = word
        if checked.endswith('y'):
            checked = checked[:-1]

        for pattern in patterns:
            if 'VD' in pattern:  # long vowel insted 'VD'
                for letter in vowels_long:
                    checked = checked.replace(pattern[:-2] + letter, '$')
            elif 'VA' in pattern:  # vowel instead 'VA'
                for letter in vowels_all:
                    checked = checked.replace(pattern[:-2] + letter, '$')
            elif '@' in pattern:  # word ends with this pattern
                if checked.endswith(pattern[:-1]):
                    checked = checked[:-len(pattern)-1]
            elif '#' in pattern:  # word starts with this pattern
                if checked.startswith(pattern[1:]):
                    checked = checked[len(pattern[1:]):]
            else:
                checked = checked.replace(pattern, '$')

        if name in checked:
            return True

    # borrowed nasalisation pattern
    consonants = 'cdghjklrstvzščřžďťň'
    vowels = 'aeiyouáéěíýůú'

    transcribed = ''
    for letter in word:
        if letter in consonants:
            transcribed += 'C'
        elif letter in vowels:
            transcribed += 'V'
        else:
            transcribed += letter

    allowed_der = ('nský', 'nka', 'nství', 'nstvo')
    if 'VnC' in transcribed or 'Vmb' in transcribed or 'Vmp' in transcribed:
        if not any(word.endswith(der) for der in allowed_der):
            return True

    # foreign morphemes (suffixes, derived suffixes, prefixes, infixes)
    suffixes = ('áž', 'ce', 'en', 'én', 'er', 'ér', 'ie', 'ik', 'ín',
                'ns', 'on', 'ón', 'or', 'oř', 'os', 'sa', 'se', 'ta', 'um',
                'má', 'us', 'za', 'ze', 'ace', 'ant', 'bal', 'bus', 'ent',
                'eus', 'fil', 'fob', 'for', 'ice', 'ida', 'ika', 'ina', 'ína',
                'ing', 'ink', 'ism', 'ita', 'ián', 'log', 'man', 'mat', 'men',
                'nom', 'ona', 'óna', 'tor', 'una', 'úna', 'ura', 'úra', 'urg',
                'fon', 'ální', 'iana', 'gate', 'graf', 'álný', 'ánní', 'ánný',
                'ární', 'árný', 'átní', 'átný', 'átor', 'énní', 'énný', 'erie',
                'érie', 'érní', 'érný', 'ézní', 'ézný', 'ický', 'ilní', 'ilný',
                'ista', 'itor', 'ivní', 'ívní', 'ivný', 'ívný', 'orní', 'orný',
                'ózní', 'ózný', 'stor', 'teka', 'téka', 'tura', 'antní',
                'antný', 'asmus', 'atura', 'bilní', 'bilný', 'dozer', 'entní',
                'entný', 'manie', 'mánie', 'holik', 'filie', 'grafie',
                'kracie', 'eskní', 'eskný', 'esmus', 'fobie', 'iální', 'iálný',
                'ismus', 'itura', 'izace', 'izmus', 'logie', 'vální', 'válný',
                'fikace', 'írovat', 'izovat', 'ýrovat', 'lizovat', 'lisovat',
                'ebilita', 'ekalita', 'ibilita', 'ikalita')

    for suffix in suffixes:
        if word.endswith(suffix):
            if len(word.replace(suffix, '')) > 2:
                return True

    deriv_suf = ('ážní', 'ážně', 'ážový', 'ážovost', 'ážovat', 'ážovaný',
                 'ážovaně', 'ážování', 'ážovanost', 'ážovatelný', 'ážovatelně',
                 'ážovatelnost', 'ční', 'čně', 'enový', 'enní', 'énový',
                 'énovost', 'énově', 'ének', 'éneček', 'énkový', 'erový',
                 'erský', 'erovský', 'érka', 'érčin', 'érský', 'érskost',
                 'érsky', 'érství', 'érův', 'érový', 'ikův', 'inový', 'inův',
                 'ínka', 'ínův', 'ínový', 'ínčin', 'ínově', 'ínovost', 'ínský',
                 'ónový', 'ónek', 'ónka', 'ónově', 'ónovost', 'orka', 'orčin',
                 'orův', 'orský', 'orskost', 'orsky', 'ační', 'ačně', 'antka',
                 'balový', 'balově', 'balovost', 'busový', 'busově',
                 'busovost', 'entní', 'entský', 'entův', 'entka', 'entčin',
                 'entskost', 'entsky', 'filní', 'filský', 'filův', 'filně',
                 'filsky', 'filskost', 'filka', 'fobka', 'fobův', 'fobní',
                 'idový', 'idově', 'ingový', 'ingově', 'ingovost', 'inkový',
                 'inkově', 'inkovost', 'iánův', 'iánský', 'iánsky', 'logův',
                 'ložka', 'ložčin', 'logově', 'logický', 'logiskost', 'matový',
                 'matka', 'matčík', 'matův', 'menský', 'menův', 'mensky',
                 'menskost', 'nomka', 'nomický', 'nomův', 'nomčin', 'ónka',
                 'torka', 'torčin', 'torův', 'torský', 'torsky', 'torskost',
                 'urní', 'urně', 'urista', 'uristka', 'álně', 'álnost', 'ánně',
                 'árně', 'árnost', 'átně', 'átnost', 'átorka', 'átorův',
                 'átorčin', 'énně', 'mer', 'érně', 'érnost', 'ézně', 'éznost',
                 'ickost', 'ilně', 'ilnost', 'istický', 'isticky', 'istickost',
                 'istka', 'istův', 'itorka', 'itorský', 'itorčin', 'itorsky',
                 'itorův', 'ivně', 'ivnost', 'ívně', 'ívnost', 'orně',
                 'ornost', 'ózně', 'óznost', 'storka', 'storčin', 'storský',
                 'storův', 'teční', 'turní', 'turka', 'turový', 'turně',
                 'antně', 'antnost', 'aturní', 'aturně', 'aturka', 'bilně',
                 'bilnost', 'dozerista', 'dozeristka', 'dozeristův', 'entně',
                 'entnost', 'manický', 'manickost', 'manicky', 'maniak',
                 'holička', 'holikův', 'holiččin', 'holický', 'holickost',
                 'holicky', 'holismus', 'kratický', 'kratickost', 'kraticky',
                 'eskně', 'esknost', 'fobický', 'iálně', 'iálnost', 'izační',
                 'izačně', 'válně', 'válnost', 'fikační', 'fikačně', 'írovací',
                 'izovací', 'ýrovací', 'ibilitový', 'ibilitově', 'ibilitovost',
                 'izovaný', 'izovatelný', 'izování', 'izovávat', 'írovaný',
                 'írovatelný', 'írovávat', 'ýrovaný', 'ýrovatelný', 'ýrovávat',
                 'izovatelně', 'izovatelnost', 'írovatelně', 'írovatelnost',
                 'ýrovatelně', 'írovatelnost', 'lizující', 'lisující',
                 'lizace', 'lisace', 'lizační', 'lisační', 'lizačně',
                 'lisačně', 'lizovací', 'lisovací', 'lizovaný', 'lisovaný',
                 'lizování', 'lisování', 'lizovatelný', 'lisovatelný',
                 'lizovaně', 'lisovaně', 'lizovatelnost', 'lisovatelnost',
                 'lizovanost', 'lisovanost', 'fonista', 'fonistka', 'fonistův',
                 'fonistčin', 'fonní', 'fonně', 'fonový', 'fonově', 'fonovost')

    for suffix in deriv_suf:
        if word.endswith(suffix):
            if len(word.replace(suffix, '')) > 2:
                return True

    prefixes = ('ab', 'ad', 'an', 'bi', 'de', 'di', 'em', 'en', 'ex', 'im',
                'ks', 'kš', 'in', 'ko', 're', 'ap', 'ana', 'ant', 'apo', 'ato',
                'iso', 'azo', 'bio', 'des', 'dez', 'dia', 'dis', 'dys', 'eko',
                'epi', 'erc', 'geo', 'izo', 'kom', 'kon', 'neo', 'non', 'par',
                'pre', 'sub', 'sur', 'aero', 'agro', 'ante', 'anti', 'amor',
                'arci', 'auto', 'demo', 'etno', 'euro', 'fero', 'foto', 'giga',
                'hypo', 'info', 'kata', 'keto', 'kino', 'lino', 'maxi', 'mega',
                'meta', 'mini', 'mono', 'moto', 'para', 'peta', 'poly', 'post',
                'taxi', 'nano', 'tele', 'tera', 'velo', 'vice', 'orto', 'pedo',
                'amino', 'cyber', 'disko', 'extra', 'femto', 'gramo', 'hydro',
                'infra', 'inter', 'intra', 'intro', 'krimi', 'kupro', 'kvazi',
                'kyber', 'makro', 'mikro', 'nitro', 'porno', 'profi', 'proto',
                'quasi', 'radio', 'rádio', 'rekta', 'retro', 'servo', 'steno',
                'super', 'supra', 'tacho', 'termo', 'trafo', 'trans', 'turbo',
                'ultra', 'vibro', 'video', 'astro', 'mezzo', 'metyl', 'multi',
                'hyper', 'amylo', 'balneo', 'energo', 'kontra', 'pseudo',
                'stereo', 'techno', 'chromo', 'psycho', 'elektro', 'travest',
                'galvano', 'magneto', 'sciento', 'elektron')

    for prefix in prefixes:
        if word.startswith(prefix):
            return True

    # physical quantities
    quantities = ('lumen', 'ampér', 'volt', 'ohm', 'metr', 'gram', 'litr',
                  'kelvin', 'kandela', 'mol', 'candela', 'radián', 'steradián',
                  'hertz', 'newton', 'pascal', 'joule', 'byte', 'watt', 'lux',
                  'coulomb', 'farad', 'siemens', 'weber', 'tesla', 'henry',
                  'sievert', 'parsek', 'alko')

    for quantity in quantities:
        if quantity in word:
            return True

    # non-foreign word
    return False


# running script if it is used in shell (with stdin or path to file)
if __name__ == '__main__':

    if not sys.stdin.isatty():  # read from stdin
        for line in sys.stdin:
            word = line.strip().split('_')
            print(word[0], recog_foreign_word(*word), sep='\t')

    else:  # read from file
        if len(sys.argv) == 2:
            with open(sys.argv[1], mode='r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().split('_')
                    print(word[0], recog_foreign_word(*word), sep='\t')
        else:
            print('Error: Use script in pipeline or give the path '
                  'to the relevant file in the first argument.')
