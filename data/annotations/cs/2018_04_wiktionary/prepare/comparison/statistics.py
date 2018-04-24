# !usr/bin/env python3
# coding: utf-8

from collections import defaultdict
from derinet.derinet import DeriNet

def wkt(path):
    def counting(dic, x): # counting function for questions 4 and 5
        item_number = defaultdict(int)
        y = 0
        for i,j in dic.items():
            item_number[len(j)] += 1
            y += 1
        item_number[0] = x - y
        return item_number

    # loading data
    # 1. how many relations does this resource contain?
    # 2. how many lexemes does this resource contain?
    relations = defaultdict(list)
    n_relations = 0
    wordlist = set()
    with open(path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().split('\t')
            relations[line[0]].append(line[1])
            n_relations += 1
            wordlist.add(line[0])
            wordlist.add(line[1])

    # 3. how many lexemes does the part-of-speech tags include?
    word_pos = defaultdict(int)
    for word in wordlist:
        word = word.split('_')
        word_pos[word[1]] += 1

    # 4. how many children has every parent got?
    parent_children = defaultdict(list)
    for child,parents in relations.items():
        for parent in parents:
            parent_children[parent].append(child)
    parent_children = counting(parent_children, len(wordlist))

    # 5. how many parents has every child got?
    child_parents = counting(relations, len(wordlist))

    # 6. how many propriums does Wiktioary contain?
    # 7. how many more-word lexemes Wiktionary contain?
    propriums = 0
    more_word = 0
    for word in wordlist:
        if (word[:1].isupper() is True): propriums += 1
        if (' ' in word): more_word += 1

    # output
    return (len(wordlist), n_relations, propriums, more_word, word_pos, parent_children, child_parents)

def derinet(path):
    # loading data
    der = DeriNet(path)

    # 1. how many lexemes does this resource contain?
    wordlist = len(der._data)
    relations = 0
    propriums = 0
    more_word = 0
    word_pos = defaultdict(int)
    parent_children = defaultdict(int)
    for node in der._data:
        # 2. how many relations does this resource contain?
        if not (node.parent_id == ''):
            relations += 1
        # 3. how many lexemes does the part-of-speech tags include?
        word_pos[node.pos[0]] += 1
        # 4. how many children has every parent got?
        parent_children[len(node.children)] += 1
        # 5. how many propriums does Wiktioary contain?
        if (node.lemma[:1].isupper() is True): propriums += 1
        # 6. how many more-word lexemes Wiktionary contain?
        if (' ' in node.lemma): more_word += 1

    # 7. how many parents has every child got?
    child_parents = {0 : len(der._roots), 1 : len(der._data)-len(der._roots)}

    # output
    return (wordlist, relations, propriums, more_word, word_pos, parent_children, child_parents)

def save(wordlist, relations, propriums, more_word, word_pos, parent_children, child_parents, name):
    with open(file=name, mode='w', encoding='utf-8') as f:
        f.write('Number of lexemes: ' + str(wordlist) + '\n')
        f.write('Number of relations: ' + str(relations) + '\n')
        f.write('Number of propriums: ' + str(propriums) + '\n')
        f.write('Number of more-word lexemes: ' + str(more_word) + '\n')
        f.write('Number of lexemes by part-of-speech [columns: pos|number]\n')
        for w,p in sorted(word_pos.items()):
            f.write(str(w) + '\t' + str(p) + '\n')
        f.write('Number of children by lexeme [columns: children|lexeme]\n')
        for i,n in sorted(parent_children.items()):
            f.write(str(i) + '\t' + str(n) + '\n')
        f.write('Number of parents by lexeme [columns: parents|lexeme]\n')
        for i,n in sorted(child_parents.items()):
            f.write(str(i) + '\t' + str(n) + '\n')

if (__name__ == '__main__'):
    # arguments parsing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store', dest='w', required=False, help='the Wiktionary data, choose only one (-w OR -d)')
    parser.add_argument('-d', action='store', dest='d', required=False, help='the DeriNet data, choose only one (-w OR -d)')
    parser.add_argument('-s', action='store', dest='s', required=True, help='the file for basic statistics')
    par = parser.parse_args()

    if (par.w):
        results = wkt(par.w)
        save(results[0], results[1], results[2], results[3], results[4], results[5], results[6], par.s)
    elif (par.d):
        results = derinet(par.d)
        save(results[0], results[1], results[2], results[3], results[4], results[5], results[6], par.s)
    else:
        print('Fill some file as argument. Parametr -w is for Wiktionary data, parametr -d for Derinet data.')
