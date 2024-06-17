import csv
from typing import List, Dict
import re


def read_verbs():
    verb_list = []
    verb_segmentation = []
    with open("./data_sources/ces_verbs.csv") as file:
        tsv_file = csv.reader(file, delimiter=",")

        for line_num, line in enumerate(tsv_file):
            if line_num == 0:
                continue
            if len(line[0]) <= 15:
                morph_split = ""
                for i in range(8,14):
                    morph_split += line[i] + " "
                for i in range(15,19):
                    morph_split += line[i] + " "
                morph_split = re.sub(r'\s+', '-', morph_split)
                morph_split = morph_split[1:] + "t"
                verb_segmentation.append(morph_split)
                verb_list.append(line[0])
    return verb_list, verb_segmentation


def read_Czech_final(limit=15):
    verb_list = []
    verb_segmentation = []
    with open("./data_sources/Czech_final.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")

        for line_num, line in enumerate(tsv_file):
            if line_num == 0:
                continue
            if len(line[1]) <= limit:
                morph_split = ""
                for i in range(10,16):
                    morph_split += line[i] + " "
                cand_morph_split = ""
                for i in range(38,47):
                    cand_morph_split += line[i] + " "
                if re.sub(r'\s+', '', cand_morph_split) == "":
                    morph_split += line[26] + " "
                else:
                    morph_split += cand_morph_split + " "
                for i in range(27,35):
                    morph_split += line[i] + " "
                morph_split = re.sub(r'\s+', '-', morph_split)
                morph_split = morph_split[1:]
                if morph_split[-1:] != "t":
                    morph_split += "t"
                if line[1] == "".join(morph_split.split("-")):
                    verb_segmentation.append(morph_split)
                    verb_list.append(line[1])
    return verb_list, verb_segmentation


def read_anot_old():
    word_list = []
    word_segmentation = []
    with open("./data_sources/all.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            word_list.append(line[0])
            word_segmentation.append(line[2])
            # print(line[0], "\t", line[2])
    return word_list, word_segmentation


def read_anot_2023():
    word_list = []
    word_segmentation = []
    with open("./data_sources/segmentation_2023.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            word_list.append(line[0].replace(" ", ""))
            word_segmentation.append(line[0].replace(" ", "-"))
            # print(line[0].replace(" ", ""),line[0].replace(" ", "-") )
    return word_list, word_segmentation


def read_morpho_train_set():
    word_list = []
    word_segmentation = []
    with open("./data_sources/morpho_train_set.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            word_list.append(line[0])
            word_segmentation.append(line[1])
    return word_list, word_segmentation


def read_morpho_test_set():
    word_list = []
    word_segmentation = []
    with open("./data_sources/morpho_test_set.tsv") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tsv_file:
            word_list.append(line[0])
            word_segmentation.append(line[1])
    return word_list, word_segmentation
