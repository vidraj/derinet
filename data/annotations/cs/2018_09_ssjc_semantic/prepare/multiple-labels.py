#!/usr/bin/env python3
# coding: utf-8

"""Automatic checking of relations with multiple labels."""

import sys
from collections import defaultdict


data = defaultdict(set)
for line in sys.stdin:
    entry = tuple(line.rstrip('\n').split('\t'))
    data[entry[:2]].add(entry[2])

for rel, labels in data.items():
    if len(labels) > 1:
        print(*rel, *labels, sep='\t')
