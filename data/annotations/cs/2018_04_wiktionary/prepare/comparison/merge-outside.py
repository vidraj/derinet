# !usr/bin/env python3
# coding: utf-8

import string
from collections import defaultdict
import argparse

# arguments parsing
parser = argparse.ArgumentParser()
parser.add_argument('-m', action='store', dest='m', required=True, help='files for merging, separed by commas')
parser.add_argument('-o', action='store', dest='o', required=True, help='the output file')
par = parser.parse_args()

files = par.m.split(',')

# mergind data
allOutside = set()

for path in files:
    with open(file=path, mode='r', encoding='utf-8') as f:
        for line in f:
            if (line[0] == '#') or (line[0] == '\n'): continue
            line = line.split('_')

            punct = False
            allPunctuation = string.punctuation + '–“—„ '
            for p in allPunctuation:
                if (p in line[0]):
                    punct = True
                    break

            if not (punct):
                allOutside.add(line[0] + '_' + line[1])

# saving
with open(file=par.o, mode='w', encoding='utf-8') as f:
    f.write('### Number of lexemes: ' + str(len(allOutside)) + ' ###\n\n')
    for word in sorted(allOutside):
        f.write(word)
