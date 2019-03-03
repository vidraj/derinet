#!usr/bin/env python3
# coding: utf-8

"""Predict DeriNet relations using Logistic reg. and Decision tree models."""

import sys
import numpy as np
import pandas as pd
from collections import defaultdict

from sklearn.model_selection import train_test_split

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score

import graphviz
from sklearn.tree import export_graphviz


# load and merge data
dataset1 = pd.read_csv(sys.argv[1], header=0, sep='\t', low_memory=False)
dataset2 = pd.read_csv(sys.argv[2], header=0, sep='\t', low_memory=False)
dataset = pd.concat([dataset1, dataset2])

dataset1 = pd.DataFrame()
dataset2 = pd.DataFrame()


# save relations for final print
identificators = ['parent', 'child', 'pos_P', 'pos_C']
rels = dataset[dataset['label'].isnull()][identificators].values.tolist()


# ignore/delete non-relevant features
non_relevant = ('parent', 'child', 'poses_P', 'same_start', 'same_end',
                'one_gram_P_start', 'two_gram_P_start', 'three_gram_P_start',
                'four_gram_P_start', 'five_gram_P_start', 'six_gram_P_start',
                'one_gram_C_start', 'two_gram_C_start', 'three_gram_C_start',
                'four_gram_C_start', 'five_gram_C_start', 'six_gram_C_start',
                'one_gram_P_end', 'six_gram_P_end',
                'one_gram_C_end')
for name in non_relevant:
    del dataset[name]


# convert types
dataset['poses_C'] = dataset['poses_C'].astype('bool')


# binarize morhological features
for name in ('pos_P', 'pos_C', 'gender_P', 'gender_C', 'aspect_P', 'aspect_C'):
    dummy = pd.get_dummies(dataset[name])
    for dum_name in dummy:
        dataset[name + '_' + dum_name] = dummy[dum_name].astype('bool')
    del dataset[name]


# numerize target classes
mapping_lab = {'POSSESSIVE': 1, 'DIMINUTIVE': 2, 'FEMALE': 3,
               'ASPECT': 4, 'ITERATIVE': 5, 'NONE': 6}
dataset = dataset.replace({'label': mapping_lab})


# binarize (affixes) features
for name in ('two_gram_C_end', 'three_gram_C_end', 'four_gram_C_end',
             'five_gram_C_end', 'six_gram_C_end',
             'two_gram_P_end', 'three_gram_P_end', 'four_gram_P_end',
             'five_gram_P_end'):
    # make frequency list
    freq_list = defaultdict(int)
    for value in dataset.loc[dataset['label'].notnull(), name]:
        freq_list[value] += 1
    # make list of allowed affixes (with freq > 5)
    allowed_affixes = list()
    for affix, freq in freq_list.items():
        if freq > 5:
            allowed_affixes.append(affix)
    # replace low-frequency affixes to NaN
    new = dataset[name].apply(lambda i: i if i in allowed_affixes else np.nan)
    # binarize new feature
    dummy = pd.get_dummies(new)
    for dum_name in dummy:
        dataset[name + '_' + dum_name] = dummy[dum_name].astype('bool')
    del dataset[name]


# split data on training data and data for predicting
dataset_for_predict = dataset[dataset['label'].isnull()]
del dataset_for_predict['label']
x_predict = np.array(dataset_for_predict)

dataset = dataset[dataset['label'].notnull()]
dataset['label'] = dataset['label'].astype('int')
x = np.array(dataset[[col for col in dataset if col != 'label']])
y = np.array(dataset[['label']]).ravel()
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1,
                                                    random_state=123)
y_train = y_train.ravel()
y_test = y_test.ravel()


# train models
DecTre = DecisionTreeClassifier(min_samples_leaf=30)
DecTre.fit(x_train, y_train)

LogReg = LogisticRegression(fit_intercept=False, solver='newton-cg',
                            max_iter=1000, multi_class='multinomial')
LogReg.fit(x_train, y_train)


# predict test data
y_tpred_prob_dectre = DecTre.predict_proba(x_test)
y_tpred_clas_dectre = DecTre.predict(x_test)
y_tpred_prob_logreg = LogReg.predict_proba(x_test)
y_tpred_clas_logreg = LogReg.predict(x_test)


# print evaluations of prediction of test data according to various tresholds
def print_evaluation(probabilities, classes, treshold, true_data):
    """Print results of models."""
    for i in range(len(classes)):
        if probabilities[i][classes[i]-1] < treshold:
            classes[i] = 6
    print('treshold:', treshold)
    print('CMX:')
    print(pd.DataFrame(confusion_matrix(true_data, classes),
                       index=['true:pos', 'true:dim', 'true:fem',
                              'true:asp', 'true:ite', 'true:non'],
                       columns=['pred:pos', 'pred:dim', 'pred:fem',
                                'pred:asp', 'pred:ite', 'pred:non']))
    print('acc:', accuracy_score(true_data, classes))
    print('pre:', precision_score(true_data, classes, average='macro'))
    print('rec:', recall_score(true_data, classes, average='macro'))
    print('f1m:', f1_score(true_data, classes, average='macro'))
    print()


tresholds = (0, 0.25, 0.5, 0.75, 0.8, 0.9, 0.95, 0.97, 0.99)
for tr in tresholds:
    print('METHOD: Decision Tree')
    print_evaluation(y_tpred_prob_dectre, y_tpred_clas_dectre, tr, y_test)
    print('METHOD: Logistic Regression')
    print_evaluation(y_tpred_prob_logreg, y_tpred_clas_logreg, tr, y_test)


# print graph of decision tree
colnames = [col for col in dataset if col != 'label']
classnames = ['pos', 'dim', 'fem', 'asp', 'ite', 'non']
dot_data = export_graphviz(DecTre, out_file=None, feature_names=colnames,
                           class_names=classnames,
                           filled=True, rounded=True, special_characters=True)
graph = graphviz.Source(dot_data)
graph.render('../hand-annotated/SemLab-DTree')


# predict unknown data
y_pred_prob_dectre = DecTre.predict_proba(x_predict).tolist()
y_pred_prob_logreg = LogReg.predict_proba(x_predict).tolist()


# save resulted probabilities and classes
inv_map = {v: k for k, v in mapping_lab.items()}  # inverted mapping_lab
r_dtre = [(inv_map[ex.index(max(ex))+1], max(ex)) for ex in y_pred_prob_dectre]
r_lreg = [(inv_map[ex.index(max(ex))+1], max(ex)) for ex in y_pred_prob_logreg]

with open(sys.argv[3], mode='w', encoding='utf-8') as f:
    for i in range(len(rels)):
        parent = rels[i][0] + '–' + rels[i][2]
        child = rels[i][1] + '–' + rels[i][3]
        dtre = r_dtre[i][0] + '|' + str(r_dtre[i][1])
        lreg = r_lreg[i][0] + '|' + str(r_lreg[i][1])
        f.write(parent + '\t' + child + '\t' + dtre + '\t' + lreg + '\n')
