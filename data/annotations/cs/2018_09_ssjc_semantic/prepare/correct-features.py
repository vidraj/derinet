#!usr/bin/env python3
# coding: utf-8

"""Fix incorrect features in MLdata."""

import re
import sys
from collections import OrderedDict


# loads MLdata as matrix in OrderedDict
mldata = OrderedDict()
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    next(f)  # skip first line (header)
    for line in f:
        entry = line.rstrip('\n').split('\t')
        mldata[tuple(entry[0:2])] = entry

# loads header of MLdata
counts = ('one', 'two', 'three', 'four', 'five', 'six')
header = ('parent', 'child', 'pos_P', 'pos_C', 'gender_P', 'gender_C',
          'aspect_P', 'aspect_C', 'poses_P', 'poses_C',
          'same_start', 'same_end',
          *[c + '_gram_P_start' for c in counts],
          *[c + '_gram_C_start' for c in counts],
          *reversed([c + '_gram_P_end' for c in counts]),
          *reversed([c + '_gram_C_end' for c in counts]),
          'label')


# loads corrections (6th column)
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    content = f.read()

corrections = re.findall(r'^[0-9].*', content, flags=re.M)
corrections = [entry.split('\t') for entry in corrections]


# go through corrections, reconstruct it and applied it on data
for fixes in corrections:
    if fixes[-1] == '':
        continue

    for fix in fixes[-1].split(' '):
        idx = header.index(fix.split(':')[0])
        cor = fix.split(':')[1]
        mldata[tuple(fixes[1:3])][idx] = cor


# save corrected data
print(*header, sep='\t')
for key in mldata:
    print(*mldata[key], sep='\t')
