#Tries to convert the words into a vector representation where word and it's derivation parent are close,
#and different words are far apart. The results are not good so far, but after some fixing we may get something more useful.
#(It is inspired by Google Facenet and the triplet loss)
#Todo:
#  If we make this method work we can try to use it for segmentation of words.
#  [is the represetnation("přirůst") close to representation("řirůst") or reprepresentation("irůst") or representation("růst")?]


###
import time
import importlib
import random
import math
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np
from collections import defaultdict
from TripletLossDataPreparation import *

###


import TripletLossNetwork
importlib.reload(TripletLossNetwork)
network=TripletLossNetwork.TripletLoss_RNN_Network("tri-MixedTraining")


###

import TripletLossRootDetectors
importlib.reload(TripletLossRootDetectors)

LOAD=True

if(LOAD):
    network.load("tfsaves\\tf_tripletloss_model_76perc-4761")
else:
    model_fname=TripletLossNetwork.do_the_training(network, train_words, devel_words,devel_all_pairs )
    print("Trained model:",model_fname)






def experiment3(network):
    dist=lambda x:np.mean((x[0]-x[1])**2)
    measure=lambda a,b: dist(network.compute_representations(network.preprocess_data([a,b])))
    print(measure("^petr$","^petrův$"))
    print(measure("^petr$","^petrovice$"))
    print(measure("^petr$","^patro$"))
    print(measure("^petr$","^slon"))


experiment3(network)





#TODO: distance (nearest neighbors) experiments
def experiment4_nearest_neighbors(network):
    pass
    #compute all representations
    """
    all_words=[]
    for x in train_words:
        all_words+=x

    outputs=[]
    i=0
    while i<len(all_words):
        data=network.compute_representations(network.preprocess_data(all_words[i:i+500]))
        outputs.append(data)
        i+=500

    outputs=np.concatenate(outputs, axis=0)
    print(outputs.shape)

    k=27072
    print(all_words[k])
    print("-"*3)
    distances=np.mean((outputs-outputs[k])**2, axis=1)
    argsorted_distances=np.argsort(distances)
    out=[]
    for i in range(20):
        i2=argsorted_distances[i]
        out.append((all_words[i2],distances[i2]))

    print(out)
    """


#train {'words': 127981, 'trees': 566}
#devel {'words': 56787, 'trees': 231}
#test {'words': 59167, 'trees': 193}









#TODO: what should I do with this?
def experiment5(network):
    print(TripletLossRootDetectors.detect_root(network,"podložka"))
    for i in range(1, len("podložka")+1):
        print((i,TripletLossRootDetectors.detect_root2(network,"podložka",i)))









##
#Try a different threshold on the precomuted data.
#print(out[0][0])
#TripletLossRootDetectors.detect_root(None, out[0][0], 0.7, likelihoods=out[0][3])


###########
import numpy as np
import importlib
import DerinetTreeBuilder
import segmenteddataset
importlib.reload(DerinetTreeBuilder)
importlib.reload(segmenteddataset)

train=segmenteddataset.train
devel=segmenteddataset.devel
test =segmenteddataset.test







##test root prediction with use of the manually segmented dataset.
#TODO / issues:
# - separation of train/test of the network does not match the separation here
# - we do not know roots for sure, We are just guessing them from all the segments



#Manually segmented data
#train | devel | WITH_KNOWLEDGE_OF_ROOT_LENGTH | USED_WORDS_STRATEGY
#0.3822937625754527 | 0.32388663967611336  | False | SELF
#0.4507042253521127 | 0.4251012145748988   | False | ROOT
#0.46680080482897385| 0.41700404858299595  | False | RANDOM
#0.4869215291750503 | 0.44534412955465585  | False | RANDOM5
#0.4949698189134809 | 0.44129554655870445  | False | ALL


def experiment1_evaluate_rootdetector3_on_manually_segmented_dataset():
    tree_builder=DerinetTreeBuilder.DerinetTreeBuilder(lexicon)
    results=[]
    for WITH_KNOWLEDGE_OF_ROOT_LENGTH in [False]: #we cannot implement True, since we do not have data for that.
        for USED_WORDS_STRATEGY in ["SELF","ROOT","RANDOM", "RANDOM5","ALL"]:
            result=[]
            for dataset in [train, devel]:
                ok=0
                cnt=0
                for processed_word,true_segmentation in dataset:
                    if("ü" in processed_word or "ö" in processed_word or "ä" in processed_word or processed_word in ["čtyřicítikilometrovost", "Kájín"]):
                        continue
                    print(processed_word)
                    best_root,best_distance,best_indices=TripletLossRootDetectors.detect_root3(network,tree_builder, processed_word, root_length=None, used_words_strategy=USED_WORDS_STRATEGY)
                    print(best_root)
                    num_bars=0
                    num_chars=0
                    i=0
                    segm="|"+true_segmentation+"|"
                    while i<len(segm):
                        if(segm[i]=="|"):
                            num_bars+=1
                        else:
                            num_chars+=1
                        if(num_chars==best_indices[0]+1):
                            if(segm[i-1:i+best_indices[1]-best_indices[0]+1 ].lower() == "|"+best_root.lower()+"|"):
                                print("ok")
                                ok+=1
                            else:
                                break
                        i+=1
                    cnt+=1
                result.append(ok/cnt)
                print(ok,cnt)
            result=result+[WITH_KNOWLEDGE_OF_ROOT_LENGTH,USED_WORDS_STRATEGY]
            results.append(result)

    print("Manually segmented data")
    print("train | devel | WITH_KNOWLEDGE_OF_ROOT_LENGTH | USED_WORDS_STRATEGY")
    for r in results:
        print(" | ".join(list(map(str,r))))

experiment1_evaluate_rootdetector3_on_manually_segmented_dataset()


#######
##test root prediction with use of the root segments within the tree.

#TODO:
#- somehow ballance the results so that we take more into account the less frequent trees.

#Roots from derinet
#train  | devel  | WITH_KNOWLEDGE_OF_ROOT_LENGTH | USED_WORDS_STRATEGY
#0.7872 | 0.7673 |                True           | SELF
#0.9109 | 0.8983 |                True           | ROOT
#0.8653 | 0.8596 |                True           | RANDOM
#0.9333 | 0.9203 |                True           | RANDOM5
#0.95   | 0.9276 |                True           | ALL
#0.2957 | 0.3279 |                False          | SELF
#0.5723 | 0.5242 |                False          | ROOT
#0.5364 | 0.5409 |                False          | RANDOM
#0.6361 | 0.6368 |                False          | RANDOM5
#0.672  | 0.6612 |                False          | ALL


#used words strategies:
# ALL = take all words from the tree, compute their representations, and use mean as target.
# ROOT=use root of the tree,
# RANDOM=use random word from the tree,
# RANDOM5 = take 5 random words from tree, and again compute mean of their representations
# SELF=use just the segmeted word itself for computation of representation


"""
Roots from derinet
train  | devel  | WITH_KNOWLEDGE_OF_ROOT_LENGTH | USED_WORDS_STRATEGY | Differences histogram (was our prediction shorter -, or longer + than the correct root)
0.3044 | 0.3313 | False | SELF    | {0: 3349, 2: 2132, 3: 703, 1: 2851, 4: 178, -1: 525, -2: 216, -3: 17, 6: 5, 5: 17, -4: 7}) | {0: 3662, -2: 258, -1: 480, 1: 2495, 2: 1989, 3: 757, -3: 151, 4: 184, 6: 7, 5: 12, -4: 5})
0.5737 | 0.5267 | False | ROOT    | {-1: 1693, 0: 5892, 2: 480, 1: 1142, -2: 729, -3: 38, 3: 26})                              | {0: 5374, -3: 252, -2: 930, -1: 1753, 1: 1158, 3: 136, 2: 397})
0.538  | 0.537  | False | RANDOM  | {1: 1593, -2: 676, 0: 5650, -1: 1437, 2: 524, 4: 9, 3: 67, -3: 39, -4: 5})                 | {1: 1269, -1: 1138, 3: 185, 0: 5729, -2: 710, -3: 329, 2: 617, 4: 6, -4: 14, 5: 3})
0.6351 | 0.6431 | False | RANDOM5 | {-1: 1255, 0: 6508, 1: 1205, 2: 248, -2: 710, 3: 17, -3: 48, 4: 4, -4: 5})                 | {0: 6742, -2: 740, -3: 300, -1: 890, 1: 893, 3: 125, 2: 282, -4: 28})
0.6667 | 0.6612 | False | ALL     | {0: 6814, 2: 218, 1: 1075, -3: 38, -2: 630, -1: 1197, 4: 5, 3: 23})                        | {-4: 39, -3: 200, -2: 799, -1: 778, 0: 6965, 1: 913, 2: 184, 3: 122} 1816 shorter, 6965 ok, 1219 longer.


TODO: 1816 shorter, 6965 ok, 1219 longer => this is not very helpful. If most of errors of our algorithm was too short a root, we could use the predicted roots as a blacklist for changes inside the words (no change within the predicted root),
      and it would not cause any harm....


#TODO: currently evaluated on random sample of words. Look at the results for random sampling of trees

"""



import copy

def experiment2_evaluate_rootdetector3_on_derinet_roots():
    tree_builder=DerinetTreeBuilder.DerinetTreeBuilder(lexicon)
    results=[]
    for WITH_KNOWLEDGE_OF_ROOT_LENGTH in [True, False]:
        for USED_WORDS_STRATEGY in ["SELF","ROOT", "RANDOM", "RANDOM5","ALL"]:
            differences_train=defaultdict(lambda : 0)
            differences_devel=defaultdict(lambda : 0)
            result=[]
            #train set
            data=copy.copy(train_words_with_roots)
            random.shuffle(data)
            data=data[:10000]

            ok_train=0
            cnt_train=0
            for processed_word,root_word,(root, node) in data:
                if(WITH_KNOWLEDGE_OF_ROOT_LENGTH):
                    len_=len(root_word)
                else:
                    len_=None
                print(processed_word)
                best_root,best_distance,best_indices=TripletLossRootDetectors.detect_root3(network,tree_builder, processed_word, len_, used_words_strategy=USED_WORDS_STRATEGY)
                print(best_root)
                if(best_indices[0]==root["Start"] and best_indices[1]==root["End"]):
                    print("OK")
                    ok_train+=1
                cnt_train+=1
                differences_train[(best_indices[1]-best_indices[0])-(root["End"]-root["Start"])]+=1

            result.append(ok_train/cnt_train)
            print(ok_train/cnt_train,WITH_KNOWLEDGE_OF_ROOT_LENGTH,USED_WORDS_STRATEGY)

            #devel set
            data=copy.copy(devel_words_with_roots)
            random.shuffle(data)
            data=data[:10000]
            ok_devel=0
            cnt_devel=0
            for processed_word,root_word,(root, node) in data:
                if(WITH_KNOWLEDGE_OF_ROOT_LENGTH):
                    len_=len(root_word)
                else:
                    len_=None
                print(processed_word)
                best_root,best_distance,best_indices=TripletLossRootDetectors.detect_root3(network,tree_builder, processed_word, len_, used_words_strategy=USED_WORDS_STRATEGY)
                print(best_root)
                if(best_indices[0]==root["Start"] and best_indices[1]==root["End"]):
                    print("OK")
                    ok_devel+=1
                differences_devel[(best_indices[1]-best_indices[0])-(root["End"]-root["Start"])]+=1
                cnt_devel+=1

            result.append(ok_devel/cnt_devel)
            print(ok_devel/cnt_devel,WITH_KNOWLEDGE_OF_ROOT_LENGTH,USED_WORDS_STRATEGY)
            result=result+[WITH_KNOWLEDGE_OF_ROOT_LENGTH,USED_WORDS_STRATEGY, differences_train, differences_devel]
            results.append(result)


    print("Roots from derinet")
    print("train | devel | WITH_KNOWLEDGE_OF_ROOT_LENGTH | USED_WORDS_STRATEGY | Differences histogram")
    for r in results:
        print(" | ".join(list(map(str,r))))

experiment2_evaluate_rootdetector3_on_derinet_roots()

################
#network.compute_representations(network.preprocess_data([a,b]))