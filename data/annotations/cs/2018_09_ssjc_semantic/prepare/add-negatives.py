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
labeled = list()
counts = defaultdict(int)
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        labeled.append(tuple(line.split('\t')[:2]))
        counts[line.rstrip('\n').split('\t')[2]] += 1

# load data for prediction and filter them
prediction = list()
with open(sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        if tuple(line.split('\t')[:2]) not in labeled:
            prediction.append(tuple(line.split('\t')[:2]))

# choose random sample from prediction and print it with label: NON-LABELED
num = round(sum(counts.values())/len(counts))
random.seed(123)
for entry in random.sample(prediction, num):
    print(*entry, 'non-lab.', sep='\t')
