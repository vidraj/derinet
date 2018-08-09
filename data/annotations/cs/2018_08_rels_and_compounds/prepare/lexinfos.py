#!usr/bin/env python3
# coding: utf-8

"""Search and save lexical_info of given lexemes."""

import sys

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


# load derinet
derinet = derinet_api.DeriNet(sys.argv[1])

# load annotation
to_save = list()
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        for lex in derinet.search_lexemes(line.strip()):
            to_save.append(lex)

# save lexemes_info
with open(sys.argv[3], mode='w', encoding='utf-8') as f:
    for lex in to_save:
        f.write('%' + '\t' + str(lex) + '\n')
