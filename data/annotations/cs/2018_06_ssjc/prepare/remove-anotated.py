# !usr/bin/env python3
# coding: utf-8

"""Remove already annotated relations with one potential parent."""

import sys

allData = list()  # file with all data for anotating
prev = None
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        if line == '\n':
            if prev != '\n':
                allData.append([])
            else:
                allData.append({})
        else:
            child = line.strip().split('\t')[0].split('_')[0]
            childPos = line.strip().split('\t')[0].split('_')[1]
            parent = line.strip().split('\t')[1].split('_')[0]
            parentPos = line.strip().split('\t')[1].split('_')[1]
            allData.append([{'child': child, 'pos': childPos},
                            {'parent': parent, 'pos': parentPos}])
        prev = line


def find_in(child, parent, data):
    """Find relation in data. Return True/False and index/0."""
    for entry in data:
        if entry == [] or entry == {}:
            continue
        elif entry[0]['child'] == child and entry[1]['parent'] == parent:
            return True, data.index(entry)
    return False, None


# checking file with already anotated data from allData
anot = 0
new = 0
with open(file=sys.argv[2], mode='r', encoding='utf-8') as f:
    for line in f:
        if line == '\n':
            continue

        child = line.strip().split('\t')[0].split('_')[0]
        parent = line.strip().split('\t')[1].split('_')[0]

        found, index = find_in(child, parent, allData)

        if found:
            del allData[index]
            anot += 1

# print data for annotating
prev = None
for relation in allData:
    if relation == []:
        if prev != [] and prev != {}:
            print()
    elif relation == {}:
        if prev == []:
            print()
    else:
        child = relation[0]['child'] + '_' + relation[0]['pos']
        parent = relation[1]['parent'] + '_' + relation[1]['pos']
        print(child, parent, sep='\t')
    prev = relation
