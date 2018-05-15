# !usr/bin/env python3
# coding: utf-8

from collections import defaultdict

def load(path):
    relations = defaultdict()
    with open(file=path, mode='r', encoding='utf-8') as f:
        for line in f:
            if (line[0] == '#') or (line[0] == '\n'): continue
            line = line.split('\t')
            child = line[0] # it is the DeriNet root
            parents = line[1].strip().split('; ')
            relations[child] = set(parents)
    return relations

def merge_dicts(dic1, dic2):
    outdic = defaultdict(set)
    for child,parents in dic1.items():
        for parent in parents:
            outdic[child].add(parent)
    for child,parents in dic2.items():
        for parent in parents:
            outdic[child].add(parent)
    return outdic

if (__name__ == '__main__'):
    # aguments parsing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', action='store', dest='m', required=True, help='files for merging, separed by commas')
    parser.add_argument('-o', action='store', dest='o', required=True, help='the output file')
    par = parser.parse_args()

    files = par.m.split(',')

    # merging all datas
    merged = load(files[0])
    for fil in files[1:]:
        new = load(fil)
        merged = merge_dicts(merged, new)

    # filtering by length and saving
    from comparison import rotate_length, print_root_parents
    # merged = rotate_length(merged)
    print_root_parents(par.o, merged)
