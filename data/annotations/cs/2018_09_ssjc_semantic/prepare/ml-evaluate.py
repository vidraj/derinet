#!usr/bin/env python3
# coding: utf-8

"""Evaluate manual annotation."""

import sys

from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score


# load data and create vector of prediction and true_prediction
lreg_true = list()
lreg_pred = list()
dtre_true = list()
dtre_pred = list()
with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    next(f)
    next(f)
    for line in f:
        line = line.rstrip('\n').split('\t')
        # true values
        if '+' in line[0]:
            lreg_true.append(line[4].split('|')[0])
            dtre_true.append(line[4].split('|')[0])
        else:
            lreg_true.append(line[0])
            dtre_true.append(line[0])
        # predicted values of dec. tree
        dtre_pred.append(line[4].split('|')[0])
        lreg_pred.append(line[5].split('|')[0])

# print results
print('Decision Tree')
print('acc:', accuracy_score(dtre_true, dtre_pred))
print('pre:', precision_score(dtre_true, dtre_pred, average='macro'))
print('rec:', recall_score(dtre_true, dtre_pred, average='macro'))
print('f1m:', f1_score(dtre_true, dtre_pred, average='macro'))

print()

print('Logistic Regression')
print('acc:', accuracy_score(lreg_true, lreg_pred))
print('pre:', precision_score(lreg_true, lreg_pred, average='macro'))
print('rec:', recall_score(lreg_true, lreg_pred, average='macro'))
print('f1m:', f1_score(lreg_true, lreg_pred, average='macro'))
