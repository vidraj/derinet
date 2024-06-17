import os
import time
from datetime import datetime
import numpy as np
import sklearn
from sklearn import metrics

def clean_predictions(word, bin_array):
    cleaned_array = np.zeros_like(bin_array)
    cleaned_array[:len(word)-1] = bin_array[:len(word)-1]
    return cleaned_array


def bin_array_to_segments(word, bin_array):
    segmented_word = word[0]
    for i in range(1, len(word)):
        if bin_array[i-1] == 1:
            segmented_word += "-"
        segmented_word += word[i]
    return segmented_word


def bin_array_to_sigmorphon_segments(word, bin_array):
    segmented_word = word[0]
    for i in range(1, len(word)):
        if bin_array[i-1] == 1:
            segmented_word += " @@"
        segmented_word += word[i]
    return segmented_word


def bin_array_to_classes(word, bin_array):
    segmented_classes = []
    for i in range(len(word)):
        if bin_array[i] == 1:
            segmented_classes.append(i)
    if not segmented_classes:
        segmented_classes.append(0)
    return segmented_classes


def save_sigmorphon_predicted(test_set, test_pred):
    clean_predicted = []
    now = datetime.now()
    with open(os.path.join("./results/sigmorphon_predictions.txt"), "w", encoding="utf-8") as predictions:
        for i, word in enumerate(test_set[2]):
            first_word = word.split(" ")[0]
            clean_predicted.append(clean_predictions(first_word, test_pred[i]))
            print(first_word + "\t" + bin_array_to_sigmorphon_segments(first_word,clean_predicted[i]), file=predictions)


def evaluate_predicted(train_set,test_set,train_pred, test_pred, log_dir):

    accuracy_score_train = sklearn.metrics.accuracy_score(train_set[1], train_pred)
    accuracy_score = sklearn.metrics.accuracy_score(test_set[1], test_pred)
    clean_predicted = []
    clean_target = []
    print("accuracy_score train ", accuracy_score_train)
    print("accuracy_score ", accuracy_score)


    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H-%M-%S")

    with open(os.path.join("./results/correct_" + dt_string + ".txt"), "w", encoding="utf-8") as correct:
        with open(os.path.join("./results/wrong_" + dt_string + ".txt"), "w", encoding="utf-8") as wrong:

            for i, word in enumerate(test_set[2]):
                first_word = word.split(" ")[0]
                clean_predicted.append(clean_predictions(first_word, test_pred[i]))
                clean_target.append(clean_predictions(first_word, test_set[1][i]))
                if not np.array_equal(test_set[1][i] , clean_predicted[i]):
                    print(first_word,"\t",bin_array_to_segments(first_word, test_set[1][i]),"\t",
                          bin_array_to_segments(first_word,clean_predicted[i]), file=wrong)
                else:
                    print(first_word, "\t", bin_array_to_segments(first_word, test_set[1][i]), "\t",
                          bin_array_to_segments(first_word, clean_predicted[i]), file=correct)
            accuracy_score_clean = sklearn.metrics.accuracy_score(clean_target, clean_predicted)
            precision = sklearn.metrics.precision_score(test_set[1], test_pred, pos_label=1, average='micro')
            recall = sklearn.metrics.recall_score(test_set[1], test_pred, pos_label=1, average='micro')
            precision_clean = sklearn.metrics.precision_score(test_set[1], clean_predicted, pos_label=1, average='micro')
            recall_clean = sklearn.metrics.recall_score(test_set[1], clean_predicted, pos_label=1, average='micro')
            f1_clean = sklearn.metrics.f1_score(test_set[1], clean_predicted, pos_label=1, average='micro')

    with open(os.path.join( "./results/overall_" + dt_string + ".txt"), "w", encoding="utf-8") as overall_results:
        print(log_dir, file=overall_results)
        print(f"word accuracy_score train: {accuracy_score_train:.3f}", file=overall_results)
        print(f"word accuracy_score test: {accuracy_score:.3f}", file=overall_results)
        print(f"word accuracy_score cleaned: {accuracy_score_clean:.3f}", file=overall_results)
        print(f"positive edge Precision: {precision:.3f}", file=overall_results)
        print(f"positive edge Recall: {recall:.3f}", file=overall_results)
        print(f"positive edge Precision clean: {precision_clean:.3f}", file=overall_results)
        print(f"positive edge Recall clean: {recall_clean:.3f}", file=overall_results)
        print(f"positive edge f1 clean: {f1_clean:.3f}", file=overall_results)
        print("-----------------------", file=overall_results)