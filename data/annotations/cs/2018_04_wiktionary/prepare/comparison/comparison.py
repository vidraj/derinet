# !usr/bin/env python3
# coding: utf-8

from collections import defaultdict
from derinet.derinet import DeriNet
from derinet.utils import Node

def load_wkt(path): # loading Wiktionary data
    relations = defaultdict(set)
    wordlist = set()
    with open(path, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().split('\t')
            relations[line[0]].add(line[1])
            wordlist.add(line[0])
            wordlist.add(line[1])
    return wordlist, relations

def inDeriNet(word): # function given boolean about existence in DeriNet
    lexeme = word.split('_')[0]
    pos = word.split('_')[1]
    try:
        if (pos == 'N') or (pos == 'A') or (pos == 'D') or (pos == 'V'): state = der.get_lexeme(node=lexeme, pos=pos)
        else: state = der.get_lexeme(node=lexeme)
        return (True, '')
    except:
        try:
            state = der.get_lexeme(node=lexeme, pos=pos+'C')
            return (True, 'C')
        except:
            return (False, '')

def search(nl, target): # searching in recursive list (DeriNet's subtree of lexeme)
    for node in nl:
        if type(node) is list:
            if search(node, target):
                return True
        if node == target:
            return True
    return False

def exist_in_derinet(der, wordlist):
    inside = set()
    inside_one = set() # set of lexeme in DeriNet consisting of one word
    inside_more = set() # set of lexeme in DeriNet consisting of more words
    outside = set()
    outside_one = set() # set of lexeme out of DeriNet consisting of one word
    outside_more = set() # set of lexeme out of DeriNet consisting of more words

    for word in wordlist:
        inD = inDeriNet(word)
        if (inD[0] is True):
            if (' ' in word): inside_more.add(word+inD[1])
            else: inside_one.add(word+inD[1])
            inside.add(word+inD[1])
        else:
            if (' ' in word): outside_more.add(word+inD[1])
            else: outside_one.add(word+inD[1])
            outside.add(word+inD[1])
    return inside, outside, inside_more, inside_one, outside_more, outside_one

def parents_for_derinet_root(der, relations):
    # potential parents from Wiktionary for DeriNet's roots
    allparents = defaultdict(set)
    for nodeid in der._roots:
        root = der.get_lexeme(nodeid).lemma + '_'
        if (root + der.get_lexeme(nodeid).pos[0] in relations):
            for parent in relations[root + der.get_lexeme(nodeid).pos[0]]:
                allparents[root + der.get_lexeme(nodeid).pos].add(parent)
        elif (root + 'None' in relations):
            for parent in relations[root + 'None']:
                allparents[root + der.get_lexeme(nodeid).pos].add(parent)

    # potential parents from Wiktionary for DeriNet's root existed in DeriNet
    existedparents = defaultdict(set)
    for root,parents in allparents.items():
        for parent in parents:
            inD = inDeriNet(parent)
            if (inD[0] is True):
                existedparents[root].add(parent+inD[1])
    return existedparents

def filter_parents_out(der, dic): # filter parents which are childs of root
    parentsout = defaultdict(set)
    for root, parents in dic.items():
        for parent in parents:
            subtree = der.get_subtree(der.get_root(node=root.split('_')[0], pos=root.split('_')[1]))
            if (parent.split('_')[1] == 'N') or (parent.split('_')[1] == 'A') or (parent.split('_')[1] == 'V') or (parent.split('_')[1] == 'D'):
                if (search(subtree, der.get_lexeme(node=parent.split('_')[0], pos=parent.split('_')[1])) is False):
                    parentsout[root].add(parent)
            elif (search(subtree, der.get_lexeme(node=parent.split('_')[0])) is False):
                parentsout[root].add(parent)
    return parentsout

def filter_composites(dic):
    noncomposites = defaultdict()
    composites = defaultdict()
    for root,parents in dic.items():
        if (root.split('_')[1][-1] == 'C'):
            composites[root] = parents
        else:
            noncomposites[root] = parents
    return composites, noncomposites

def rotate_length(dic):
    out = defaultdict(set)
    for root,parents in dic.items():
        parents = list(parents)
        if (len(parents) == 1):
            if (len(root.split('_')[0]) < len(parents[0].split('_')[0])):
                out[parents[0]].add(root+'*')
            else:
                out[root].add(parents[0])
        else:
            for parent in parents:
                out[root].add(parent)
    return out

def print_existance(path, nameside, data):
    with open(file=path, mode='w', encoding='utf-8') as f:
        f.write('### Number of lexemes in Wiktionary and ' + nameside + ' DeriNet (all): ' + str(len(data)) + ' ###\n\n')
        for w in sorted(data):
            f.write(w + '\n')

def print_root_parents(path, dic):
    with open(file=path, mode='w', encoding='utf-8') as f:
        f.write('### Number of DeriNets roots with parents in Wiktionary (in this file): ' + str(len(dic)) + ' ###\n\n')
        for root in sorted(dic, key=lambda root: len(dic[root]), reverse=True):
            parents = list(dic[root])
            strparents = parents[0]
            for parent in parents[1:]:
                strparents += '; ' + parent
            f.write(root + '\t' + strparents + '\n')

if (__name__ == '__main__'):
    # arguments parsing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store', dest='w', required=True, help='the Wiktionary data')
    parser.add_argument('-d', action='store', dest='d', required=True, help='the DeriNet data')
    parser.add_argument('-i', action='store', dest='i', required=False, help='the output for file with inside lexemes')
    parser.add_argument('-o', action='store', dest='o', required=False, help='the output for file with outside lexemes')
    parser.add_argument('-c', action='store', dest='c', required=False, help='the output for file with composites')
    parser.add_argument('-n', action='store', dest='n', required=False, help='the output for file with noncomposites')
    parser.add_argument('-a', action='store', dest='a', required=False, help='the output for file with all lexemes')
    par = parser.parse_args()

    # loading data
    der = DeriNet(par.d)
    wordlist, relations = load_wkt(par.w)

    # creating and saving lists of Wiktionary lexemes inside/outside of DeriNet
    if (par.i) or (par.o):
        inside, outside, inside_more, inside_one, outside_more, outside_one = exist_in_derinet(der, wordlist)
        if (par.i):
            print_existance(par.i, 'inside', inside)
        if (par.o):
            print_existance(par.o, 'outside', outside)

    # creating and saving lists of DeriNets root having parent(s) in Wiktionary
    if (par.c) or (par.n) or (par.a):
        existedparents = parents_for_derinet_root(der, relations)
        allexisted = filter_parents_out(der, existedparents)
        composites, noncomposites = filter_composites(allexisted)
        if (par.c):
            # composites = rotate_length(composites)
            print_root_parents(par.c, composites)
        if (par.n):
            # noncomposites = rotate_length(noncomposites)
            print_root_parents(par.n, noncomposites)
        if (par.a):
            # allexisted = rotate_length(allexisted)
            print_root_parents(par.a, allexisted)
