import numpy as np
import sklearn
from unidecode import unidecode


from parsers import anotated_segmentations_reader
from mlp_segmentation import conv_segmentator_dataset, conv_segmentator_one_hot, conv_segmentator_one_hot_original, \
    conv_segmentator_one_hot_3_layers, conv_segmentator_one_hot_all_conv_base, conv_segmentator_one_hot_all_conv, \
    conv_segmentator_one_hot_all_conv_transpose
from mlp_segmentation import conv_segmentator2
import re

limit = 27


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


def prepare_one_hot_labels(word_list, word_segmentation, ft, letter_index_dict=None):

    word_list, binary_segmentations = create_binary_segmentation(word_list, word_segmentation)
    print("word_list", len(word_list))
    print("binary_segmentations", len(binary_segmentations))
    segmentation_dict = dict(zip(word_list, binary_segmentations))
    binary_segmentations = list(segmentation_dict.values())
    word_list = list(segmentation_dict.keys())
    unidecode_word_list = unidecode(' '.join(word_list)).split()
    if letter_index_dict is None:
        letter_index_dict = {' ': 0}
        letter_index_dict.update({letter: index + 1 for index, letter in enumerate(set(''.join(unidecode_word_list)))})
        if '^' not in letter_index_dict:
            letter_index_dict['^'] = len(letter_index_dict)
    char_vocab = len(letter_index_dict)
    diacritics_index = letter_index_dict['^']
    print("char_vocab",char_vocab)
    print("char_vocab",letter_index_dict)
    array_shape = (len(word_list), limit , char_vocab)
    char_array = np.zeros(array_shape, dtype=float)
    embeddings = np.zeros((len(word_list), ft.get_dimension()))
    for i, word in enumerate(word_list):
        vector = ft.get_word_vector(word)
        np_vec = np.array(vector)
        embeddings[i] = np_vec
        for char_position, letter in enumerate(unidecode(word)):
            if len(word) != len(unidecode(word)):
                continue
            dict_index = letter_index_dict[letter]
            char_array[i, char_position, dict_index] = 1
            if letter != word[char_position]:
                char_array[i, char_position, diacritics_index] = 1
    np_segmentation_list = np.array(binary_segmentations)
    return [char_array, np_segmentation_list, word_list, embeddings], letter_index_dict


def preprocess_and_run(ft):
    #word_list, word_segmentation = anotated_segmentations_reader.read_morpho_train_set()
    word_list, word_segmentation = anotated_segmentations_reader.read_morpho_train_set_synth()
    print("word_list", len(word_list))
    print("word_segmentation", len(word_segmentation))
    test_word_list, test_word_segmentation = anotated_segmentations_reader.read_morpho_test_set()
    train_set, char_index_dict = prepare_one_hot_labels(word_list, word_segmentation, ft, letter_index_dict=None)
    test_set, char_index_dict =  prepare_one_hot_labels(test_word_list, test_word_segmentation, ft, char_index_dict)
    print("word_list", len(train_set[0]))
    print("word_segmentation", len(train_set[1]))
    conv_segmentator_one_hot.train_and_predict(train_set, test_set, test_set, limit, len(char_index_dict) )


def preprocess_and_run_sigmorphon(ft):
    word_list, word_segmentation = anotated_segmentations_reader.read_sigmorphon_train_set()
    print("word_list_train", len(word_list))
    print("word_segmentation", len(word_segmentation))
    test_word_list, test_word_segmentation = anotated_segmentations_reader.read_sigmorphon_test_set()
    train_set, char_index_dict = prepare_one_hot_labels(word_list, word_segmentation, ft, letter_index_dict=None)
    test_set, char_index_dict = prepare_one_hot_labels(test_word_list, test_word_segmentation, ft, char_index_dict)
    print("train_set", len(test_set[0]))
    print("test_set", len(train_set[1]))
    print("-----")
    dev_word_list, dev_word_segmentation = anotated_segmentations_reader.read_sigmorphon_dev_set()
    print("dev_word_list", len(dev_word_list))
    dev_set, char_index_dict = prepare_one_hot_labels(dev_word_list, dev_word_segmentation, ft, char_index_dict)
    print("dev_set", len(dev_set[1]))

    # conv_segmentator_one_hot.train_and_predict(train_set, dev_set, test_set, limit, len(char_index_dict), ft)
    conv_segmentator_one_hot_all_conv_transpose.train_and_predict(train_set, dev_set, test_set, limit, len(char_index_dict))
    # conv_segmentator_one_hot_original.train_and_predict(train_set, dev_set, test_set, limit, len(char_index_dict))
