#!/usr/bin/env python3
# coding: utf-8

"""Evaluate baseline for semantic labelling."""

import sys
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score


# evaluation
def print_evaluation(y_test, model, name='baseline'):
    """Print results of models."""
    # y_test = y_test['label'].tolist()
    print(name)
    print('mod CMX: [pos dim fem asp ite non]')
    print(confusion_matrix(y_test, model))
    print('mod acc:', accuracy_score(y_test, model))
    print('mod pre:', precision_score(y_test, model, average='macro'))
    print('mod rec:', recall_score(y_test, model, average='macro'))
    print('mod f1m:', f1_score(y_test, model, average='macro'))
    print()
    # print results of each individual label
    labels = ('POSSESSIVE', 'DIMINUTIVE', 'FEMALE', 'ASPECT', 'ITERATIVE', 'NONE')
    for lab in labels:
        true_label = ['NON' if item != lab else item for item in y_test]
        pred_label = ['NON' if item != lab else item for item in model]
        pre = precision_score(true_label, pred_label, average='macro')
        rec = recall_score(true_label, pred_label, average='macro')
        print(lab, 'pre:', pre)
        print(lab, 'rec:', rec)
        print()


# load data
dataset = pd.read_csv(sys.argv[1], header=0, sep='\t')

# split data to train and test
x = np.array(dataset[[col for col in dataset if col != 'label']])
y = np.array(dataset[['label']])
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1,
                                                    random_state=123)
y_train = y_train.ravel()
y_test = y_test.ravel()


# predict baseline
def baseline(data):
    base = list()
    for entry in data:
        if entry[2] == 'N' and entry[3] == 'A':
            base.append('POSSESSIVE')

        elif entry[2] == 'V' and entry[3] == 'V':
            if entry[6] != entry[7]:
                base.append('ASPECT')
            elif entry[6] == 'I' and entry[7] == 'I':
                base.append('ITERATIVE')
            else:
                base.append('NONE')

        elif entry[2] != 'V' and entry[2] == entry[3]:
            if entry[4] == 'M' and entry[5] == 'F':
                base.append('FEMALE')
            elif entry[4] == entry[5]:
                base.append('DIMINUTIVE')
            else:
                base.append('NONE')

        else:
            base.append('NONE')
    return base


print_evaluation(y_train, baseline(x_train), 'basesli-train')
print_evaluation(y_test, baseline(x_test), 'baseline-test')
