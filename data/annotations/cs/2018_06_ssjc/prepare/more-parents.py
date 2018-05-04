# !usr/bin/env python3
# coding utf-8

"""Print all relation (with more parents) for annotation."""

import sys
from collections import defaultdict


# Loading data
relations = defaultdict()  # all relations with more than one parent
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        if line[0] == '#' or line[0] == '\n':
            continue
        line = line.split('\t')
        child = line[0]
        parents = line[1].strip().split('; ')
        if len(parents) > 1:
            relations[child] = parents

# Creating groups according to the longest common suffix of children
children = list(relations)  # the list of all childs from loaded data

word_pos = list()  # the list of all child from loaded data and their pos
for child in children:
    word_pos.append({'word': child.split('_')[0], 'pos': child.split('_')[1]})

n = 10  # max length of suffix
database = defaultdict(list)  # database of groups

while n > 0:
    cont = list()  # storage of word for processing in next step

    # go through all children and save suffixes
    for entry in word_pos:
        child = entry['word']
        pos = entry['pos']
        if len(child) < n:  # word is identified for processing in next step
            cont.append({'word': child, 'pos': pos})
        else:  # word is saved with its suffix
            database[child[-n:]].append({'word': child, 'pos': pos})

    # go through whole database and delete groups with just one word
    fordel2 = list()  # list of groups for deleting
    for suf, words in database.items():
        if len(words) == 1:
            cont.append(words[0])  # before deleting, save word in storage
            fordel2.append(suf)

    for d in fordel2:
        del database[d]

    # preparation for processing next step in cycle
    word_pos = list()  # delete list of children
    word_pos += cont  # save storage to list for processing
    n -= 1  # decreasing the length of suffix

# Printing data for annotation
for suffix, words in database.items():
    for word in words:
        word = word['word'] + '_' + word['pos']
        for parent in relations[word]:
            print(word, parent, sep='\t')
        print()
    print()

for word in cont:
    word = word['word'] + '_' + word['pos']
    for parent in relations[word]:
        print(word, parent, sep='\t')
    print()
