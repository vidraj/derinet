#!python3
import sys
from collections import defaultdict
#import derinet.lexicon as dlex


# Tests prepared for the old DeriNet API, but not tested
def compounding(lexeme):
    segments = lexeme.segmentation
    annotation = [morph["Type"] for morph in segments]
    if lexeme["misc"]["is_compound"]:
        assert annotation.count("R") > 1
    else:
        assert annotation.count("R") <= 1


def tree_root_lexemes(root):
    annotation = [morph["Type"] for morph in root.segmentation]
    init_roots = annotation.count("R")
    for lexeme in root.iter_tree():
        lexeme_annotation = [morph["Type"] for morph in root.segmentation]
        if not lexeme["misc"]["is_compound"]:
            assert lexeme_annotation.count("R") == init_roots


def consistent_annotation(parent, child):
    a, b = parent.segmentation, child.segmentation
    parent_morphs = [morph["Morph"] for morph in a]
    child_morphs = [morph["Morph"] for morph in b]
    while len(a) > 0:
        p_segment, c_segment = a[0], b[0]
        if p_segment["Morph"] == c_segment["Morph"]:
            assert p_segment["Type"] == c_segment["Type"]
            a, b = a[1:], b[1:]
        elif len(a) < len(b):
            b = b[1:]
        else:
            a = a[1:]


# The actual tests. On input, there is a file with columns: node ID, parent(s) ID, relations, misc, segmentation, annotation. This made sense in the process of creating the annotation, but does not anymore.

with open(sys.argv[1], "r") as r:
    trees = defaultdict(lambda:defaultdict(list))
    compound_subtrees = set()
    for line in r:
        ln = line.strip().split("\t")
        tree = ln[0].split(".")[0]
        if ln[0].split(".")[1] == "0":
                compound_subtrees = set()
        node = ln[0]
        parent = ln[1]
        is_compound_type = 'Type=Compounding' in ln[2]
        is_compound = '"is_compound": true' in ln[3]
        segments = ln[4].split()
        annotation = ln[5].split()

        if is_compound_type != is_compound:
            print("Compound mismatch", node, segments, annotation, ln[2], "is_compound", is_compound)
        if is_compound or parent in compound_subtrees:
            compound_subtrees.add(node)

        if node in compound_subtrees and annotation.count("R") <= 1:
            print("Too few roots in compound", node, segments, annotation)
        if node not in compound_subtrees and annotation.count("R") > 1:
            print("Too many roots in non-compound", node, segments, annotation)
        trees[tree][node] = [segments, annotation, is_compound_type, is_compound, []]
        if len(trees[tree][parent]) != 0:
            trees[tree][parent][-1].append(node)
    for tree_id in trees.keys():
        root = trees[tree_id][tree_id + ".0"]
        for nkey in trees[tree_id].keys():
            node = trees[tree_id][nkey]
            if len(node) == 0:
                continue
            nr = node[1].count("R")
            for node_id in node[-1]:
                nn = trees[tree_id][node_id]
                nnc = nn[1].count("R")
                if not nn[2] and nnc != nr:
                    print("New root in non-compound relation", nkey, node[0], node[1], node_id, nn[0], nn[1])
