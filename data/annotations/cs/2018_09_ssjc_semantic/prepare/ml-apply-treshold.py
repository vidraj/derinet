#!usr/bin/env python3
# coding: utf-8

"""Applies given treshold on given data (predicted by ML models)."""

import sys
from collections import defaultdict


# extract tresholds
tresholds = defaultdict(int)
for t in sys.argv[2].split('|'):
    label, treshold = t.split(':')
    tresholds[label] = treshold

# go through given data, compare predictions to given treshold and let/change
# predicted result of model
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n').split('\t')
        label, probability = line[2].split('|')
        # result
        if probability < tresholds[label]:
            line[2] = 'NONE|bellow-treshold'
        # save edited results
        print(*line, sep='\t')
