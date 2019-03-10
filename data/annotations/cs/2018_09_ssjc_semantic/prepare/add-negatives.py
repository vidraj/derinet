#!usr/bin/env python3
# coding: utf-8

"""Add random negative examples (as 'non-lab.') from data for prediction.

Random sample of negative examples is filtered by given file with already
labeled relations.
"""

import sys
import random
from collections import defaultdict


# load already labeled data
labeled = set()
counts = defaultdict(int)
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        labeled.add(tuple(line.split('\t')[:2]))
        counts[line.rstrip('\n').split('\t')[2]] += 1

# suffixes of lemmas potentialy labelable as DIM./POSS./ASPECT/ITERAT./FEM.
suf = ('ův–A', 'in–A', 'ová–N', 'á–N', '–V', 'ek–N', 'átko–N',
       'íčko–N', 'ičko–N', 'čký–A', 'nký–A', 'yně–N')

# load data for prediction and filter them
prediction = list()
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n').split('\t')
        # positive filter of N-N, A-A, V-V, D-D and N-A relations
        par_pos = line[0].split('–')[1].replace('C', '')
        chi_pos = line[1].split('–')[1].replace('C', '')
        if par_pos == chi_pos or (par_pos == 'N' and chi_pos == 'A'):
            # positive filter of same start of parent and child
            # and negative filter of suffixes of lemmas potentialy labelable
            if (line[0][:2].lower() == line[1][:2].lower() and not
               any([True if p in line[1] else False for p in suf])):
                # negative filter of already labeled relations
                if tuple(line[:2]) not in labeled:
                    prediction.append(tuple(line[:2]))

# choose random sample from prediction and print it with label: NON-LABELED
num = round(sum(counts.values())/len(counts)*1.5)
random.seed(234)
for entry in random.sample(prediction, num):
    print('%', *entry, 'non-lab.', sep='\t')
