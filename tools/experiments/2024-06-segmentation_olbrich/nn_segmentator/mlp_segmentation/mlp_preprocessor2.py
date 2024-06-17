import numpy as np
import sklearn
from unidecode import unidecode


from parsers import anotated_segmentations_reader
from mlp_segmentation import conv_segmentator_dataset, conv_segmentator_one_hot
from mlp_segmentation import conv_segmentator2
import re

limit = 15

def create_binary_segmentation(word_list, word_segmentation):
    new_word_list = []
    binary_segmentations = []
    for word, segmentation in zip(word_list, word_segmentation):
        morph_split = segmentation.split("-")
        if len(word) <= limit and len(segmentation.replace("-", "")) <= limit:
            new_word_list.append(word)
            zeros_array = [0] * limit
            index = -1
            for i in range(0, len(morph_split) -1 ): # better leave the last edge out, not include the last edge - its worse
                index += len(morph_split[i])
                zeros_array[index] = 1
            binary_segmentations.append(zeros_array)
            # print(word, segmentation,zeros_array)
    return new_word_list, binary_segmentations


def create_binary_masks(word_list, binary_segmentations):
    binary_masks = []
    positional_masks = []
    positional_mask = np.arange(1, limit + 1) / limit
    binary_mask = [1] * limit
    for word, bin_seg in zip(word_list, binary_segmentations):
        bin_array = [0] * limit
        position_array = [0] * limit
        position_array[:len(word)] = positional_mask[:len(word)]
        if len(word) > 2:
            bin_array[:len(word) - 1] = binary_mask[:len(word) - 1]
        binary_masks.append(bin_array)
        positional_masks.append(bin_array)
        # print(bin_array,position_array,word)
    return binary_masks, positional_masks


def pair_word_with_derinet_parent(word_list,word_segmentation):
    new_word_list = []
    binary_segmentations = []
    word_dict = {word_list[i]: word_segmentation[i] for i in range(min(len(word_list), len(word_segmentation)))}
    for lemma in Lemma.id_dict.values():
        if lemma.name in word_dict:
            new_word_list.append(lemma.name + " " + lemma.get_all_predecesors())
            binary_segmentations.append(word_dict[lemma.name])
            # print(lemma.name + " " + lemma.get_all_predecesors())
    return new_word_list, binary_segmentations


def split_data():
    #data_splitter.extact_lemmas_from_conllu()
    data_splitter.read_forms_lemmas()


def iterably_find_in_derinet(segmentation_dict, limit):
    for i in range(0, 1):
        print(i)
        synthetic_data.find_derinet_neighbours(segmentation_dict, limit, i)


def prepare_synthetic_segmentations(pair_dict):
    word_list = pair_dict[0]
    word_segmentation = pair_dict[1]
    word_list, binary_segmentations = create_binary_segmentation(word_list, word_segmentation)
    segmentation_dict = dict(zip(word_list, binary_segmentations))
    iterably_find_in_derinet(segmentation_dict, limit)
    word_list = list(segmentation_dict.keys())
    word_list = ' '.join(word_list).lower().split()
    print("after derinet synth: ", len(word_list))
    binary_segmentations = list(segmentation_dict.values())
    with open('./data_sources/morpho_train_set_synth.tsv', 'w', newline='', encoding='utf-8') as file_w:
        for i, word in enumerate(word_list):
            print(word + "\t" + torch_segmentator.bin_array_to_segments(word, binary_segmentations[i]), file=file_w)


def prepare_train_segmentations(pair_dict):
    word_list = pair_dict[0]
    word_segmentation = pair_dict[1]
    word_list, binary_segmentations = create_binary_segmentation(word_list, word_segmentation)
    with open('./data_sources/morpho_train_set.tsv', 'w', newline='', encoding='utf-8') as file_w:
        for i, word in enumerate(word_list):
            print(word + "\t" + torch_segmentator.bin_array_to_segments(word, binary_segmentations[i]), file=file_w)


def prepare_test_segmentations(pair_dict):
    word_list = pair_dict[0]
    word_segmentation = pair_dict[1]
    word_list, binary_segmentations = create_binary_segmentation(word_list, word_segmentation)
    with open('./data_sources/morpho_test_set.tsv', 'w', newline='', encoding='utf-8') as file_w:
        for i, word in enumerate(word_list):
            print(word + "\t" + torch_segmentator.bin_array_to_segments(word, binary_segmentations[i]), file=file_w)


def prepare_segmented_data(synthetic_data_enabled=True,use_unidecode=False, use_dicritics_channel=False):

    word_list, word_segmentation = anotated_segmentations_reader.read_anot_2023()
    print("anot_2023: ", len(word_list))
    verbs_list, word_segmentation2 = anotated_segmentations_reader.read_Czech_final()
    print("czech verbs infinitive: ", len(verbs_list))
    word_dict = dict(zip(word_list, word_segmentation))

    verbs_dict = dict(zip(verbs_list, word_segmentation2))
    word_dict.update(verbs_dict) # same result should be replaced
    pair_list = [list(word_dict.keys()), list(word_dict.values())]
    # Perform train-test split on the combined data

    train_word_list_d,test_word_list_d,train_word_list_l, test_word_list_l = sklearn.model_selection.train_test_split(
        pair_list[0], pair_list[1] , test_size=2000, random_state=32)
    train_word_list = [train_word_list_d, train_word_list_l]
    test_word_list = [test_word_list_d, test_word_list_l]
    # Perform train-validation split on the combined data
    # train_word_list, val_word_list = sklearn.model_selection.train_test_split(
    #     train_word_list, test_size=2000, random_state=32)
    print("train_word_list", len(train_word_list[0]))
    print("test_word_list",len(test_word_list[0]))

    prepare_train_segmentations(train_word_list)
    prepare_synthetic_segmentations(train_word_list)
    prepare_test_segmentations(test_word_list)


