import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import copy
import time
import random
import json
import importlib
import derinet
lexicon=derinet.Lexicon()
lexicon.load("derinet-2-0.tsv")


import segmenteddataset
importlib.reload(segmenteddataset)

train=segmenteddataset.train
devel=segmenteddataset.devel
test =segmenteddataset.test



#######Combine segmentation:
import Segmenters
import DerinetTreeBuilder
import SegmentationNetwork
import TripletLossNetwork
import TripletLossRootDetectors
importlib.reload(DerinetTreeBuilder)
importlib.reload(Segmenters)
importlib.reload(SegmentationNetwork)
importlib.reload(TripletLossNetwork)
importlib.reload(TripletLossRootDetectors)

Node=DerinetTreeBuilder.Node
loader=DerinetTreeBuilder.DerinetTreeBuilder(lexicon)

triplet_loss_network=TripletLossNetwork.TripletLoss_RNN_Network("tri-MixedTraining")
triplet_loss_network.load("tfsaves\\tf_tripletloss_model_76perc-4761")


def add_derinet_segments(node):
    len_=len(node.word)
    for start,end,segment_struct in node.derinet_segments:
        if(start!=0 and start!=len_):
            node.segments.add(start)
        if(end!=0 and end!=len_):
            node.segments.add(end)

def remove_segmentation_of_derinet_nodes(node):
    if(node.derinet_root is not None):
        start,end,segment=node.derinet_root
        for i in range(start+1, end):
            node.segments.discard(i)


#we compute predictions for each node within the tree
def predict_for_node(node):
    out=SegmentationNetwork.Predictor1.predict_segments_with_likelihoods([node.word])
    if(len(out)==1): #this is not satisfied only if the classifier skips the sample because of e.g. "-" or foreign letters
        node.classifier_segments=out[0]
    else:
        node.classifier_segments=[]



#aggregate predictions from all neighbors into one node
def aggregate_neighbors_predictions(node):
    sums=[[0.0, 0] for x in range(len(node.word)+1)]
    nodes_to_process=node.children
    if(node.parrent is not None):
        nodes_to_process=nodes_to_process+[node.parrent]

    for n2 in nodes_to_process:
        segments2=Segmenters.Segmenter._translate_segments(n2.word,node.word,n2.classifier_segments)
        for position,likelihood in segments2:
            sums[position][0]+=likelihood
            sums[position][1]+=1


    node.classifier_segments_from_neighbors=[]
    for position, (likelihoods, count) in list(enumerate(sums))[1:-1]:
        if(count==0):
            continue
        node.classifier_segments_from_neighbors.append((position,likelihoods/count))


def tramslate_predictions_to_segments(node):
    for pos,likelihood in node.classifier_segments:
        if(pos==0 or pos==len(node.word)-1):
            continue
        else:
            if(likelihood>=SegmentationNetwork.Predictor1.decission_boundary):
                node.segments.add(pos)

def filter_segments(node):
    for pos,likelihood in node.classifier_segments:
        if(pos==0 or pos==len(node.word)-1):
            continue
        else:
            if(likelihood<=0.8):
                node.segments.discard(pos)

    add_derinet_segments(node)



def triplet_loss_root_prediction(node):
    global counter
    best_root,best_distance,best_indices=TripletLossRootDetectors.detect_root3(triplet_loss_network,loader, node.word, root_length=None, used_words_strategy="ALL")
    node.triplet_loss_root=(best_root,best_distance,best_indices)


def combine_segmentations(word, complete=False):
    #Diff-based segmenter
    derinet_tree=loader.find_derinettree_root(word)
    mynode_tree=DerinetTreeBuilder.DerinetTreeBuilder.build_segmentation_tree(derinet_tree)


    mynode_tree.subtree_map(add_derinet_segments)


    #Neural segmentation predictor
    mynode_tree.subtree_map(predict_for_node)
    mynode_tree.subtree_map(tramslate_predictions_to_segments)

    #number of correct/incorrect segments
    #ok oversegmentation undersegmentation
    #~440 18 443 ~> just neural classifier
    #~611 117 272 ~> combination of all (or almost all) those things. The oversegmentation is caused by ReplacingSegmenter
    #~567 26 316  ~> we still use the segmenter, but use the classifier to filter out the unlikelz segments


    #Run standard Replacing Segmenter, but this time we will propagate also the derinet- and neural- segments,
    segmenter=Segmenters.ReplacingSegmenter(mynode_tree)


    #BEWARE!!!!
    #neighbors prediction aggregates predictions from neighbors, which may give
    #us a better idea about segments. But
    #IT DOES NOT KNOW ANYTHING ABOUT CHANGES SPECIFIC TO OUR WORD! (eg newly added letters)
    if(complete):
        mynode_tree.subtree_map(aggregate_neighbors_predictions) #todo: use this?



    #Triplet loss based predictions of root
    if(complete):
        mynode_tree.subtree_map(triplet_loss_root_prediction) #todo: not good enough


    #remove oversegmentation done inside the derinet nodes
    mynode_tree.subtree_map(remove_segmentation_of_derinet_nodes)

    #remove segments with too low a confidence
    mynode_tree.subtree_map(filter_segments)

    return mynode_tree


f=open("outputs\\exp4\\CombinedSegmenter_complete_derinet.txt","w", 1024**2, encoding="utf-8")
if __name__ == '__main__':
    start=time.time()
    for i,word in enumerate(lexicon.iter_trees()): # ["dar","noha","barva","plesat", "loď", "sníh", "poslouchat", "dynda","stěžeň","pohnout","sníh","výška", "měnit"]:
        mynode_tree=combine_segmentations(word.lemma)
        f.write(mynode_tree.return_tree())
        f.write("\n"*6)
        if(i%100==0):
            mynode_tree.print_tree()
            print(i, time.time()-start)
    print(time.time()-start)
f.close()

#todo: fix behavior on words containing strange characters.

#TODO: this was written against an older version of the code above!
"""
#compare the results of segmentation by different methods
def experiment1(word):
    mynode_tree=combine_segmentations(word, complete=True)


    f=open("outputs\\exp4\\exp1-segmentation_comparison\\ReplacingSegmenter_"+word+".txt","w", encoding="utf-8")
    f.write(mynode_tree.return_tree())
    f.close()

    #!!!REPLACE STANDARD SEGMENTS WITH CLASSIFICATION SEGMENTS!!!!
    def replace_segments(node):
        node.segments=set()
        for pos,lik in node.classifier_segments:
            if(lik>=SegmentationNetwork.Predictor1.decission_boundary):
                node.segments.add(pos)

    mynode_tree.subtree_map(replace_segments)
    f=open("outputs\\exp4\\exp1-segmentation_comparison\\Classifier_"+word+".txt","w", encoding="utf-8")
    f.write(mynode_tree.return_tree())
    f.close()



    def replace_segments2(node):
        node.segments=set()
        for pos,lik in node.classifier_segments_from_neighbors:
            if(lik>=SegmentationNetwork.Predictor1.decission_boundary):
                node.segments.add(pos)

    mynode_tree.subtree_map(replace_segments2)
    f=open("outputs\\exp4\\exp1-segmentation_comparison\\ClassifierNeighbors_"+word+".txt","w", encoding="utf-8")
    f.write(mynode_tree.return_tree())
    f.close()
"""

#if __name__ == '__main__':
#    for word in ["dar","noha","barva","plesat", "loď", "sníh", "poslouchat", "dynda","stěžeň","pohnout","sníh","výška", "měnit"]:
#        experiment1(word)

