#!/usr/bin/env python3
# coding: utf-8

"""Automatic checking of relations with multiple labels."""

import sys
from collections import defaultdict


data = defaultdict(list)
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        entry = tuple(line.rstrip('\n').split('\t'))
        data[entry[:2]].append(entry[2])

for rel, labels in data.items():
    if len(labels) > 1:
        print(*rel, *labels, sep='\t')
