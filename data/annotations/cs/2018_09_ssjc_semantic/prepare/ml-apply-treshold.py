#!usr/bin/env python3
# coding: utf-8

"""Applies given treshold on given data (predicted by ML models)."""

import sys


# go through given data, compare predictions to given treshold and let/change
# predicted result of model
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n').split('\t')
        # result of decision tree
        if line[2].split('|')[1] < sys.argv[2]:
            line[2] = 'NONE|bellow-treshold'
        # result of logistic regression
        if line[3].split('|')[1] < sys.argv[2]:
            line[3] = 'NONE|bellow-treshold'
        # save edited results
        print(*line, sep='\t')
