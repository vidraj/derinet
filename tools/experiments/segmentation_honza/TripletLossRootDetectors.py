import numpy as np
import math
import random
import tensorflow as tf

def compute_root_likelihood(network, word):
    alf="qwertyuiopasdfghjklzxcvbnm"
    dsts=[]
    for i in range(0, len(word)):
        dist_sum=0.0
        for j in range(len(alf)-1):
            word2=list(word)
            word2[i]=alf[j]
            word2="".join(word2)
            dist_sum+=measure("^"+word+"$","^"+word2+"$")
        dsts.append(dist_sum/len(alf))
    return dsts

def detect_root(network,word,threshold=None, likelihoods=None):
    THRESHOLD=0.5
    if(threshold!=None):
        THRESHOLD=threshold
    if(likelihoods is None):
        likelihoods=compute_root_likelihood(network, word)
    bitmap=[]
    for x in likelihoods:
        if(x>=THRESHOLD):
            bitmap.append(1)
        else:
            bitmap.append(0)
    bitmap2=[bitmap[0]]
    for x in bitmap[1:]:
        if(x==0):
            bitmap2.append(0)
        else:
            bitmap2.append(bitmap2[-1]+1)
    max_=bitmap2[0]
    max_i=0
    for i,x in enumerate(bitmap2):
        if(x>max_):
            max_=x
            max_i=i
    root=""
    i=max_i-max_+1
    while i<=max_i:
        root+=word[i]
        i+=1
    return likelihoods, root

#let's imagine that we have an oracle, which magically tells us the root length of the word
#this is just another evaluation method. If it work's we know that the network has a good idea about the position of root,
#and we may think about how to find out the length or how to pick the correct root from group of a few possible roots of different lengths.
#TODO: maybe it can help to detect root changes in experiment1.
def detect_root2(network,word,root_length):
    min_root=word[:root_length]
    min_dist=measure(word,min_root)
    i=1
    while i<len(word)-root_length:
        root=word[i:i+root_length]
        dist=measure("^"+word+"$", "^"+root+"$")
        if(dist<min_dist):
            min_root=root
            min_dist=dist
        i+=1
    return min_root,min_dist

dist=lambda x:np.mean((x[0]-x[1])**2)
measure=lambda a,b: dist(network.compute_representations(network.preprocess_data([a,b])))

def detect_root2b(network,word,root_length):
    words_to_predict=["^"+word+"$"]
    i=0
    while i<=len(word)-root_length:
        words_to_predict.append("^"+word[i:i+root_length]+"$")
        i+=1
    representations=network.compute_representations(network.preprocess_data(words_to_predict))
    w=representations[0]
    others=representations[1:]
    dists=np.sum(  (others-np.reshape(w, (1,-1) ))**2, axis=1)
    min_idx=np.argmin(dists)
    return word[min_idx:min_idx+root_length], dists[min_idx]



"""
>>> [ detect_root2b_group(network,["rozeštvaný","poštvat"],x) for x in range(1,1+len("rozeštvaný"))]
[('', 51.327637), ('št', 46.82035), ('štv', 41.111275), ('štva', 33.680782), ('eštva', 32.182407), ('štvaný', 17.975319), ('eštvaný', 16.600533), ('eštvaný', 16.600533), ('zeštvaný', 17.18243), ('rozeštvaný', 12.975147)]

>>> [ detect_root2b_group(network,["poštvat"],x) for x in range(1,1+len("rozeštvaný"))]
[('t', 67.69275), ('po', 57.36358), ('poš', 51.20939), ('pošt', 38.043495), ('poštv', 18.71543), ('poštva', 12.660403), ('poštvat', 0.0), ('poštvat', 0.0), ('poštvat', 0.0), ('poštvat', 0.0)]

>>> [ detect_root2b_group(network,["rozeštvat"],x) for x in range(1,1+len("rozeštvaný"))]
[('e', 60.517555), ('št', 51.76041), ('ešt', 46.65281), ('zešt', 39.77413), ('štvat', 32.89485), ('eštvat', 22.314434), ('zeštvat', 14.992233), ('ozeštvat', 13.243563), ('rozeštvat', 0.0), ('rozeštvat', 0.0)]
"""



def detect_root2b_group(network,words,root_length):
    main_word=words[0]
    words_to_predict=list(map(lambda x: "^"+x+"$", words))
    i=0
    while i<=len(word)-root_length:
        words_to_predict.append("^"+main_word[i:i+root_length]+"$")
        i+=1
    representations=network.compute_representations(network.preprocess_data(words_to_predict))
    len_=len(words)
    w=representations[:len_]
    w=np.mean(w, axis=0)
    others=representations[len_:]
    dists=np.sum(  (others-np.reshape(w, (1,-1) ))**2, axis=1)
    min_idx=np.argmin(dists)
    return main_word[min_idx:min_idx+root_length], dists[min_idx]






#Can use more words from one tree to improve the predictions
def detect_root3(network,tree_builder, processed_word,root_length=None, used_words_strategy="ALL"):
    root=tree_builder.find_derinettree_root(processed_word)
    tree=tree_builder.build_segmentation_tree(root)
    if(used_words_strategy=="ALL"):
        words_from_tree=tree.get_tree_words()
    elif(used_words_strategy=="ROOT"):
        words_from_tree=[tree.word]
    elif(used_words_strategy=="SELF"):
        words_from_tree=[processed_word]
    elif(used_words_strategy=="RANDOM"):
        words_from_tree=tree.get_tree_words()
        words_from_tree=[words_from_tree[random.randint(0,len(words_from_tree)-1)]]
    elif(used_words_strategy=="RANDOM5"):
        words_from_tree=tree.get_tree_words()
        random.shuffle(words_from_tree)
        words_from_tree=words_from_tree[:5]
    else:
        raise NotImplementedError("Unknown used_words_strategy")

    potentional_roots=[]
    indices_of_potentional_roots=[]
    if(root_length is None):
        for i in range(0,len(processed_word)):
            for j in range(i+2,len(processed_word)+1):
                potentional_roots.append(processed_word[i:j])
                indices_of_potentional_roots.append((i,j))
    else:
        for i in range(0,len(processed_word)-root_length+1):
            j=i+root_length
            potentional_roots.append(processed_word[i:j])
            indices_of_potentional_roots.append((i,j))

    input_words=words_from_tree+potentional_roots
    input_words=list(map(lambda word: "^"+word.lower()+"$", input_words))

    representations=network.compute_representations(network.preprocess_data(input_words))
    representations_words_from_tree=representations[:len(words_from_tree)]
    target=np.mean(representations_words_from_tree, axis=0)
    representations_roots=representations[len(words_from_tree):]
    distances=np.mean((representations_roots-target)**2, axis=1)
    best_roots={}
    for i,root in enumerate(potentional_roots):
        distance=distances[i] #those distances are ok for comparison of absolute values, not for rations
        #distance=np.mean((representations_roots[i]-representations_words_from_tree)**2)
        length=len(root)
        current_best=best_roots.get(length)
        if(current_best is None or current_best[1]>distance):
            best_roots[length]=(root,distance, indices_of_potentional_roots[i])




    #print(best_roots)
    if(root_length is not None):
        return best_roots[root_length]

    else:
        best_roots=sorted(best_roots.values(),key=lambda x: len(x[0]))
        best_root,best_distance,best_indices=best_roots[0]
        for r,dist,indices in best_roots[1:]:
            #The numbers show that there is still some reserve, because we were able to get to 73% on segmented derinet words with knowledge of root length.
            if(dist<=best_distance-0.07*(len(r)-len(best_root))): #197/497 correct.
            #if(dist/best_distance<=0.8**(len(r)-len(best_root))): #140/497 correct with standard distances, 168 with the better ones
                best_root=r
                best_distance=dist
                best_indices=indices

        return best_root,best_distance,best_indices




#Evaluation functions:


def eval_detect_root2_groups(network):
    print("evalroot2b")
    start=time.time()
    all_train=0
    ok_train=0
    random.shuffle(train_words_with_roots)
    random.shuffle(devel_words_with_roots)
    for w,root, _ in train_words_with_roots[:5000]:
        root_prediction, _ = detect_root2b(network, w, len(root))
        if(root_prediction==root):
            ok_train+=1
        all_train+=1
    all_devel=0
    ok_devel=0
    for w,root, _ in devel_words_with_roots[:5000]:
        root_prediction, _ = detect_root2b(network, w, len(root))
        if(root_prediction==root):
            ok_devel+=1
        all_devel+=1
    with network.summary_writer.as_default():
        tf.summary.scalar("StandardTraining/evalroot2b",ok_train/all_train , step=network.global_step)
        tf.summary.scalar("StandardDevelopment/evalroot2b",ok_devel/all_devel , step=network.global_step)
    end=time.time()
    print(end-start)


def eval_detect_root2(network):
    print("evalroot2")
    start=time.time()
    all_train=0
    ok_train=0
    random.shuffle(train_words_with_roots)
    random.shuffle(devel_words_with_roots)
    for w,root, _ in train_words_with_roots[:5000]:
        root_prediction, _ = detect_root2b(network, w, len(root))
        if(root_prediction==root):
            ok_train+=1
        all_train+=1
    all_devel=0
    ok_devel=0
    for w,root, _ in devel_words_with_roots[:5000]:
        root_prediction, _ = detect_root2b(network, w, len(root))
        if(root_prediction==root):
            ok_devel+=1
        all_devel+=1
    with network.summary_writer.as_default():
        tf.summary.scalar("StandardTraining/evalroot2",ok_train/all_train , step=network.global_step)
        tf.summary.scalar("StandardDevelopment/evalroot2",ok_devel/all_devel , step=network.global_step)
    end=time.time()
    print(end-start)




##TODO: stats about how often the tripplet loss over- and under- estimates the root length