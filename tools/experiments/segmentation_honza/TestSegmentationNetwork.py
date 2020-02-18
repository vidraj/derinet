import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import copy
import time
import random
import json
import importlib
import segmenteddataset
importlib.reload(segmenteddataset)

train=segmenteddataset.train
devel=segmenteddataset.devel
test =segmenteddataset.test

####
#Preprocess data
import SegmentationNetwork
importlib.reload(SegmentationNetwork)

import exp4merge_knowledge
importlib.reload(exp4merge_knowledge)

def findall(word, char):
    i=0
    idx=0
    indices=set()
    while i<len(word):
        if(word[i]==char):
            indices.add(idx)
        else:
            idx+=1
        i+=1
    return indices

def test_on_manually_segmented(predictor,devel):
    testing_words2=devel
    testing_words2=list(filter(lambda x: x[0].lower() not in ["mühlerová","kühnenův","höfler","thubtänův"], testing_words2))
    segments=predictor(testing_words2)


    a_union_b=0
    a_minus_b=0
    b_minus_a=0
    a_intersection_b=0
    for i, (word,split) in enumerate(testing_words2):
        a=segments[i]
        out=""
        for j,c in enumerate(word):
            if(j in a):
                out+="|"
            out+=c

        b=findall(split, "|")

        a_union_b+=len(a.union(b))
        a_minus_b+=len(a-b)
        b_minus_a+=len(b-a)
        a_intersection_b+=len(a.intersection(b))
        #print(out,split)

    print("ok", "oversegmentation", "undersegmentation")
    print(a_intersection_b,a_minus_b,b_minus_a)


    #TODO: jak vyhodnotit a použít negativní informaci ze sítě? (tady není žádná hranice segmentu)

#test_on_manually_segmented(SegmentationNetwork.Predictor1.predict_segments,devel)

def batch_process(f,samples):
    out=[]
    for i,x in enumerate(samples):
        if x[0] in ["čtyřicítikilometrovost", "Kájín"]:
            out.append(set())
            continue
        tree_root=f(x[0])
        if tree_root is None:
            print(x[0])
            continue
        def find_node(root, word):
            if(root.word.lower()==word.lower()):
                return root
            else:
                for ch in root.children:
                    out=find_node(ch,word)
                    if(out is not None):
                        return out
            return None
        word_node=find_node(tree_root, x[0])
        if(word_node.word.lower()!=x[0].lower()):
            print(x,word_node)
        out.append(word_node.segments)
    return out

test_on_manually_segmented(lambda x: batch_process(exp4merge_knowledge.combine_segmentations,x),devel)
