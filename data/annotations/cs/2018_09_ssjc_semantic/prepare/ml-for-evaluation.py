#!usr/bin/env python3
# coding: utf-8

"""Return random sample of predicted data for manual annotation."""

import sys
import random


# load predicted data
predicted = list()
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        predicted.append(line.rstrip('\n').split('\t'))

# return random sample
random.seed(246)
print('# manual annotation: + = predicted label is true')
print('# header: dtree \\t lreg \\t parent \\t child \\t lreg-label')
for entry in random.sample(predicted, 2000):
    print('', *entry, sep='\t')
