#!usr/bin/env python3
# coding: utf-8

"""Machine Learning experiments."""

import sys
import numpy as np
import pandas as pd
from collections import defaultdict

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.metrics.scorer import make_scorer
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score

import graphviz
from sklearn.tree import export_graphviz


# load data
dataset = pd.read_csv(sys.argv[1], header=0, sep='\t')
df = pd.DataFrame()  # working data


# convert types
df['poses_C'] = dataset['poses_C'].astype('bool')


# numerize target classes
mapping_lab = {'POSSESSIVE': 1, 'DIMINUTIVE': 2, 'FEMALE': 3,
               'ASPECT': 4, 'ITERATIVE': 5, 'NONE': 6}
dataset = dataset.replace({'label': mapping_lab})
df['label'] = dataset['label']


# binarize (affixes) features
for name in ('one_gram_C_end', 'two_gram_C_end', 'three_gram_C_end',
             'four_gram_C_end', 'five_gram_C_end', 'six_gram_C_end',
             'two_gram_P_end', 'three_gram_P_end', 'four_gram_P_end'):
    # make frequency list
    freq_list = defaultdict(int)
    for value in dataset[name]:
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
        df[name + '_' + dum_name] = dummy[dum_name].astype('bool')


# binarize morhological features
for name in ('pos_P', 'pos_C', 'gender_P', 'gender_C', 'aspect_P', 'aspect_C'):
    dummy = pd.get_dummies(dataset[name])
    for dum_name in dummy:
        df[name + '_' + dum_name] = dummy[dum_name].astype('bool')


# set evaluating metrics for cross-validations
scoring = {'f1': make_scorer(f1_score, average='macro'),
           'precision': make_scorer(precision_score, average='macro'),
           'recall': make_scorer(recall_score, average='macro'),
           'accuracy': make_scorer(accuracy_score)}


def print_evaluation(cros_val, model, name):
    """Print results of models."""
    print(name)
    print('c-v acc:', cros_val['test_accuracy'])
    print('c-v pre:', cros_val['test_precision'])
    print('c-v rec:', cros_val['test_recall'])
    print('c-v f1m:', cros_val['test_f1'])
    print('mod CMX: [pos dim fem asp ite non]')
    print(confusion_matrix(y_test, model))
    print('mod acc:', accuracy_score(y_test, model))
    print('mod pre:', precision_score(y_test, model, average='macro'))
    print('mod rec:', recall_score(y_test, model, average='macro'))
    print('mod f1m:', f1_score(y_test, model, average='macro'))
    print()


# 1ST ROUND
print('1ST ROUND OF EXPERIMENTS')
# split on train and test data (for clasic models: 0.1 of df as testing data)
x = np.array(df[[col for col in df if col != 'label']])
y = np.array(df[['label']])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1,
                                                    random_state=123)
y_train = y_train.ravel()
y_test = y_test.ravel()


# define models
GausNB = GaussianNB()
DecTre = DecisionTreeClassifier(min_samples_leaf=100)
LogReg = LogisticRegression(fit_intercept=False, solver='newton-cg',
                            max_iter=1000, multi_class='multinomial')


# train and test 5-fold cross-validations
cv_GausNB = cross_validate(GausNB, x, y.ravel(), scoring=scoring, cv=5,
                           return_train_score=False)

cv_DecTre = cross_validate(DecTre, x, y.ravel(), scoring=scoring, cv=5,
                           return_train_score=False)

cv_LogReg = cross_validate(LogReg, x, y.ravel(), scoring=scoring, cv=5,
                           return_train_score=False)


# train and test classic models: 0.1 of df as testing data
GausNB.fit(x_train, y_train)
y_pred1 = GausNB.predict(x_test)
y_pred1_prob = GausNB.predict_proba(x_test)

DecTre.fit(x_train, y_train)
y_pred2 = DecTre.predict(x_test)
y_pred2_prob = DecTre.predict_proba(x_test)

LogReg.fit(x_train, y_train)
y_pred3 = LogReg.predict(x_test)
y_pred3_prob = LogReg.predict_proba(x_test)


# evaluate all
print('RESULTS OF EXPERIMENTS:')
print_evaluation(cv_GausNB, y_pred1, 'Gaussian Naive Bayes')
print(y_pred1_prob)
print_evaluation(cv_DecTre, y_pred2, 'Decision Tree')
print(y_pred2_prob)
print_evaluation(cv_LogReg, y_pred3, 'Logistic Regression')
print(y_pred3_prob)
print()


# more details about DecTre
print('IMPORTANCE OF EACH FEATURE OF DECISION TREE (CLASIC) MODEL:')
print(DecTre)
colnames = [col for col in df if col != 'label']
print(*zip(colnames, DecTre.feature_importances_), sep='\n')

classnames = ['pos', 'dim', 'fem', 'asp', 'ite', 'non']
dot_data = export_graphviz(DecTre, out_file=None, feature_names=colnames,
                           class_names=classnames,
                           filled=True, rounded=True, special_characters=True)
graph = graphviz.Source(dot_data)
graph.render('../hand-annotated/SemLab-DTree3')
