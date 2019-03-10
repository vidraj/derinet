#!usr/bin/env python3
# coding: utf-8

"""Evaluate manual annotation."""

import sys

from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score


# load data and create vector of prediction and true_prediction
data_true = list()
data_pred = list()
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    next(f)
    next(f)
    for line in f:
        line = line.rstrip('\n').split('\t')
        # true values
        if '+' in line[0]:
            data_true.append(line[3].split('|')[0])
        else:
            data_true.append(line[0])
        # predicted values
        data_pred.append(line[3].split('|')[0])


# print results for whole data
print('EVALUATION RESULTS\n', 10*'-', '\n')
print('All predicted data acc:', accuracy_score(data_true, data_pred))
print('All predicted data pre:', precision_score(data_true, data_pred, average='macro'))
print('All predicted data rec:', recall_score(data_true, data_pred, average='macro'))
print('All predicted data f1m:', f1_score(data_true, data_pred, average='macro'))
print()


# print results of each individual label
labels = ('POSSESSIVE', 'DIMINUTIVE', 'FEMALE', 'ASPECT', 'ITERATIVE')
for lab in labels:
    true_label = ['NONE' if item not in labels else item for item in data_true]
    pred_label = ['NONE' if item not in labels else item for item in data_pred]
    pre = precision_score(true_label, pred_label, average='macro')
    rec = recall_score(true_label, pred_label, average='macro')
    print(lab, 'pre:', pre)
    print(lab, 'rec:', rec)
    print()
