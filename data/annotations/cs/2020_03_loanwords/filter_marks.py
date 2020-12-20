#!/usr/bin/env python3
# coding: utf-8

"""Filter assigned loanword marks and make the annotation more consistent."""

import os
import sys
import argparse
from collections import defaultdict
from collections import OrderedDict


sys.path.append(os.path.realpath('../../../../tools/data-api/derinet2/'))
from derinet import Lexicon


# set argparse
parser = argparse.ArgumentParser()
parser.add_argument('--DeriNet', action='store', dest='csder', required=True)
parser.add_argument('--Loanwords', action='store', dest='loan', required=True)
parser.add_argument('--Output', action='store', dest='output', required=True)
par = parser.parse_args()


# load loanword marks
loanwords = OrderedDict()
with open(par.loan, mode='r', encoding='U8') as f:
    for line in f:
        lemma, tag, mark = line.rstrip('\n').split('\t')
        loanwords['_'.join([lemma, tag])] = bool(mark.replace('False', ''))


# load derinet
cs_derinet = Lexicon()
cs_derinet.load(par.csder)


# correct loanword marks
for lexeme, mark in loanwords.items():
    # find lexeme in derinet
    node = cs_derinet.get_lexemes(lemma=lexeme.split('_')[0],
                                  pos=lexeme.split('_')[1])[0]

    # propriums and their subtrees are FALSE
    if node.lemma[0].isupper():
        loanwords['_'.join([node.lemma, node.pos])] = False
        for node_child in node.iter_subtree():
            loanwords['_'.join([node_child.lemma, node_child.pos])] = False
        continue

    # compounds and their subtrees are FALSE
    if node.misc.get('is_compound', False) and \
       any(c in node.lemma[2:-2] for c in {'oe', 'oa', 'oi', 'oo', 'ou',
                                           'ie', 'ia', 'ii', 'io', 'iu'}):
        foreign_parts = {'zoo', 'alkal', 'hygi', 'oxid', 'w', 'x', 'q',
                         'atheis', 'ateis', 'energ', 'imped', 'inženýr',
                         'admin', 'instal', 'region', 'organ', 'orgán',
                         'koal', 'video', 'journ', 'inter', 'inform', 'expr',
                         'foto', 'endo', 'skop', 'cyklo', 'adapt', 'ultra',
                         'turbo', 'truck', 'troubl', 'trombo', 'dimenz',
                         'alianc', 'log', 'orid', 'tri', 'hi', 'ki', 'gl',
                         'trans', 'trade', 'toluen', 'th', 'tetra', 'termo',
                         'thermo', 'telev', 'techn', 'ekon', 'graf', 'sé',
                         'system', 'supr', 'super', 'studia', 'studio',
                         'stere', 'stechio', 'sprin', 'spong', 'inic', 'ergo',
                         'sperm', 'spaci', 'soci', 'ski', 'skate', 'boar',
                         'singl', 'silic', 'semi', 'scien', 'scio', 'ident',
                         'fan', 'reál', 'real', 'retro', 'repro', 'radio',
                         'rádio', 'pyrr', 'pyro', 'psych', 'insta', 'proto',
                         'th', 'alko', 'akadem', 'post', 'porn', 'poly',
                         'prof', 'autom', 'polit', 'pneu', 'pleo', 'plag',
                         'piez', 'peri', 'pedag', 'fyz', 'paral', 'paleo',
                         'paddl', 'outs', 'akust', 'osteo', 'orto', 'opto',
                         'onomaz', 'okta', 'neuro', 'neo', 'nefro', 'narko',
                         'nano', 'naftyl', 'nacion', 'myo', 'myko', 'mye',
                         'multi', 'motor', 'mono', 'molek', 'mini', 'mikro',
                         'mili', 'mezo', 'meta', 'medi', 'mechan', 'manio',
                         'makro', 'magnet', 'lymf', 'lump', 'lipto', 'leuko',
                         'lili', 'pourl', 'ismus', 'izmus', 'lakto', 'labio',
                         'kvazi', 'krypto', 'kryo', 'krani', 'komeni',
                         'komedi', 'klient', 'kefal', 'karto', 'karpo',
                         'kardio', 'karbo', 'izo', 'inter', 'inkas', 'info',
                         'imun', 'idio', 'hypo', 'hyper', 'hydro', 'hydat',
                         'homo', 'histo', 'histio', 'hetero', 'hemi', 'hemo',
                         'hema', 'helio', 'hagio', 'gram', 'gum', 'gonio',
                         'gno', 'gly', 'gli', 'gla', 'ger', 'geo', 'gastr',
                         'gal', 'gam', 'gab', 'fyto', 'fort', 'fosf', 'fon',
                         'flu', 'fib', 'fer', 'fen', 'farma', 'fant', 'euro',
                         'evro', 'etyl', 'etno', 'etio', 'eryt', 'epi', 'endo',
                         'ence', 'empir', 'elit', 'elek', 'eko', 'ekkl',
                         'echo', 'e-', 'dynam', 'hekt', 'karbur', 'gól', 'gig',
                         'gam', 'gar', 'feder', 'falc', 'fakult', 'fakt',
                         'etáž', 'dimens', 'dimenz', 'test', 'arch', 'apsid',
                         'dist', 'disk', 'dipl', 'dini', 'dika', 'dii', 'die',
                         'dia', 'debl', 'cyto', 'cine', 'chrono', 'chori',
                         'chondr', 'chlor', 'chemo', 'chemi', 'bronch', 'pool',
                         'broad', 'cast', 'ing', 'chio', 'bina', 'big', 'bibl',
                         'benz', 'barbi', 'bakter', 'azo', 'auto', 'audi',
                         'artio', 'asyr', 'astro', 'arte', 'artif', 'arci',
                         'archeo', 'arachn', 'antrop', 'anto', 'angi',
                         'anestez', 'analyt', 'amin', 'amid', 'amfi', 'alky',
                         'ally', 'alge', 'aku', 'akrom', 'agro', 'aero',
                         'aeci', 'bio', 'meteo', 'mega', 'induk', 'sólo',
                         'tapio', 'tele', 'tacho', 'pód', 'operát', 'opero'}
        if any(l in node.lemma for l in foreign_parts):
            continue
        else:
            loanwords['_'.join([node.lemma, node.pos])] = False
            for node_child in node.iter_subtree():
                loanwords['_'.join([node_child.lemma, node_child.pos])] = False
        continue


# go through derinet trees and save trees with foreign to file
with open(par.output, mode='w', encoding='U8') as f:
    for root in cs_derinet.iter_trees():
        # propriums
        propri = root.lemma[0].isupper()
        if propri:
            loanwords['_'.join([root.lemma, root.pos])] = False
            for node in root.iter_subtree():
                loanwords['_'.join([node.lemma, node.pos])] = False
        else:
            for node in root.iter_subtree():
                if node.lemma.isupper():
                    loanwords['_'.join([node.lemma, node.pos])] = False
                    for child in node.iter_subtree():
                        loanwords['_'.join([child.lemma, child.pos])] = False

        # count of foreign lemmas
        foreign = 0
        for node in root.iter_subtree():
            if loanwords['_'.join([node.lemma, node.pos])]:
                foreign += 1

        # save to file
        if foreign > 0:
            print(str(loanwords['_'.join([root.lemma, root.pos])]),
                  '_'.join([root.lemma, root.pos]), sep='\t', file=f)
            for node_child in root.iter_subtree():
                key = '_'.join([node_child.lemma, node_child.pos])
                print(str(loanwords[key]), key, sep='\t', file=f)
            print(file=f)
