#!/usr/bin/env python3
# coding: utf-8

import sys
import json
import requests
from collections import defaultdict

"""Label verbal class of given Czech verbs."""


def give_class(lemma):
    """Return verbal class."""
    if not lemma:
        return ('#', '#')

    url = 'http://lindat.mff.cuni.cz/services/morphodita/api/generate?data='
    r = json.loads(requests.get(url + lemma).text)['result'].strip()

    paradigm = set()
    classes = set()

    if not r:
        paradigm.add('#')
        classes.add('#')
    else:
        # store paradigm
        r = r.split('\t')
        lem = defaultdict(set)
        for i in range(0, len(r), 3):
            lem[r[i+2]].add(r[i])

        # 3rd singular
        end3s = {l[-2:] for l in lem['VB-S---3P-AA---']}
        end3s = end3s.union({l[-1:] for l in lem['VB-S---3P-AA---']})
        if 'á' in end3s:
            if 'e' in end3s:
                paradigm.add('kopá')
            else:
                paradigm.add('dělá')

        if 'í' in end3s:
            # 3rd singular past
            end3spast = {l[-2] for l in lem['VpYS---XR-AA---']}
            if 'i' in end3spast and 'e' in end3spast:
                paradigm.add('prosí')
                paradigm.add('sází')
            elif 'ě' in end3spast or 'e' in end3spast:
                # 2rd singular imperative
                end2simper = {l[-2:] for l in lem['Vi-S---2--A----']}
                if 'ej' in end2simper or 'ěj' in end2simper:
                    paradigm.add('sází')
                else:
                    paradigm.add('trpí')
            elif 'i' in end3spast:
                paradigm.add('prosí')

        if 'je' in end3s:
            # 3rd singular past
            end3spast = {l[-4:-1] for l in lem['VpYS---XR-AA---']}
            if 'ova' in end3spast:
                paradigm.add('kupuje')
            else:
                paradigm.add('kryje')

        if 'ne' in end3s or lemma.endswith('jmout'):
            # 3rd singular past
            end3spast = {l[-2:-1] for l in lem['VpYS---XR-AA---']}
            if 'a' in end3spast:
                paradigm.add('začne')
            elif 'u' in end3spast:
                paradigm.add('mine')
            else:
                paradigm.add('tiskne')

        if 'e' in end3s and not any(i in ('ne', 'je') for i in end3s):
            # 3rd singular before last letter
            end3sbl = {l[-2] for l in lem['VB-S---3P-AA---']}
            soft = any(item in 'žščřcjďťň' for item in end3sbl)
            # 3rd singular past
            end3spast = {l[-2:-1] for l in lem['VpYS---XR-AA---']}
            if soft or (any(i in 'dtn' for i in end3sbl) and 'ě' in end3spast):
                if 'a' in end3spast:
                    paradigm.add('maže')
                elif 'e' in end3spast or 'ě' in end3spast:
                    paradigm.add('tře')
                else:
                    paradigm.add('peče')
            if not soft:
                if 'a' in end3spast:
                    paradigm.add('bere')
                else:
                    paradigm.add('nese')

        # dont know
        if paradigm == set():
            return ('#', '#')

        # distinguish classes
        cl = {'nese': 1, 'bere': 1, 'maže': 1, 'peče': 1, 'tře': 1,
              'tiskne': 2, 'mine': 2, 'začne': 2,
              'kryje': 3, 'kupuje': 3,
              'prosí': 4, 'trpí': 4, 'sází': 4,
              'dělá': 5, 'kopá': 5}
        for par in paradigm:
            classes.add(str(cl[par]))

    return ('#'.join(paradigm), '#'.join(classes))


# running script if it is used in shell (with stdin or path to file)
if __name__ == '__main__':
    if not sys.stdin.isatty():  # read from stdin
        for line in sys.stdin:
            line = line.strip()
            print(line, *give_class(line), sep='\t')

    else:  # read from file
        if len(sys.argv) == 2:
            with open(sys.argv[1], mode='r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    print(line, *give_class(line), sep='\t')
        else:
            print('Error: Use script in pipeline or give the path '
                  'to the relevant file in the first argument.')
