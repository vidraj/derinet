#!usr/bin/env python3
# coding: utf-8

"""Extraction of semantic labels from VALLEX3."""

import sys
import itertools
import xml.etree.ElementTree as ET


# load VALLEX3 .xml data
tree = ET.ElementTree(file=sys.argv[1])
root = tree.getroot()

# dictionary of semantic labels
translate = {'iter': 'nás.', 'impf': 'ned.', 'pf': 'dok.'}

# go through data and find potential relationship
potential = set()
for head in root.iter('{http://ufal.mff.cuni.cz/vallex-2.0}lexical_forms'):
    # extract clusters of relationship
    lemmas = list()
    for descendant in head.iter():
        if descendant.tag == '{http://ufal.mff.cuni.cz/vallex-2.0}mlemma':
            lemmas.append((descendant.text, 'V', descendant.attrib['aspect']))

    # prepare potential relationship for annotation
    if len(lemmas) > 1:
        for parent, child in itertools.permutations(lemmas, 2):
            if child[2] != 'biasp' and parent[0][:1] == child[0][:1]:
                potential.add((parent[0] + '–' + parent[1],
                               child[0] + '–' + child[1],
                               translate[child[2]]))

# save potential relationship
for relationship in potential:
    print(*relationship, sep='\t')
