print("Loading data")
import derinet
import time
import numpy as np
import random
lexicon=derinet.Lexicon()
lexicon.load("derinet-2-0.tsv")


###
#extract parent-child pairs

print("Extracting parent-child pairs from trees")
word2nodes={}
def extract_parentchild_pairs(root, report_leaves=False, output_parameter=None):
    if(output_parameter==None):
        output_parameter=[]
    lem=root.lemma.lower().strip()
    if(word2nodes.get(lem) is None):
        word2nodes[lem]=[root]
    else:
        word2nodes[lem].append(root)
    children=root.children
    if(len(children)==0 and report_leaves):
        output_parameter.append((root.lemma, None))
    else:
        for child in children:
            output_parameter.append((root.lemma, child.lemma))
            extract_parentchild_pairs(child, report_leaves, output_parameter)

    return output_parameter


extracted_pairs=[] #contains lists, each of which contains all "(parent lemma, child lemma)" pairs of a given tree
i=1
for tree_root in lexicon.iter_trees():
    if(tree_root.parent!=None):
        print("WTF!!")
    extracted_pairs.append(extract_parentchild_pairs(tree_root))
    i+=1
    if(i%10**4==0):
        print(i)


###
#do the cleanup
print("Cleaning up the data")
def cleanup(word):
    word2=word.strip().lower()
    allowed="qwertyuiopasdfghjklzxcvbnmméěřťžúůíóášďýčň"
    for char in word2:
        #it mostly skips foreign names and places, such as Züngelův or schöneberský,
        #also a few slovak words, and about 40 trees (~120 lemmas) containing "-"
        if(not (char in allowed)):
            #print("skipping "+str(word))
            return None
    return word2

cleaned_pairs=[]
for i in range(len(extracted_pairs)):
    cleaned_pairs.append([])
    for j in range(len(extracted_pairs[i])):
        a,b=extracted_pairs[i][j]
        a2,b2=cleanup(a),cleanup(b)
        if(a2==None or b2==None):
            continue
        cleaned_pairs[-1].append((a2,b2))
    if(len(cleaned_pairs[-1])==0):
        del(cleaned_pairs[-1])
###
#prepair datasets for training
print("Prepairing the datasets for training")
import random
random.seed(42) #the split to train, development, test must be always the same
random.shuffle(cleaned_pairs)
for i in range(len(cleaned_pairs)):
    random.shuffle(cleaned_pairs[i])

num=len(cleaned_pairs)
train_num=int(num/2)
devel_num=int(num/2)+int(num/4)

#[[all pairs of tree i], [all pairs of tree j], ...]
train_pairs=cleaned_pairs[:train_num]
devel_pairs=cleaned_pairs[train_num:devel_num]
test_pairs=cleaned_pairs[devel_num:]


random.seed(time.time())
train_words=[]

#[[words in tree i], [...], ...]
for tree in train_pairs:
    samples=set()
    for item in tree:
        samples.add(item[0])
        samples.add(item[1])
    samples=sorted(samples) #just in case we needed to become repeatable
    random.shuffle(samples)
    train_words.append(samples)

devel_words=[]
for tree in devel_pairs:
    samples=set()
    for item in tree:
        samples.add(item[0])
        samples.add(item[1])
    samples=sorted(samples) #just in case we needed to become repeatable
    random.shuffle(samples)
    devel_words.append(samples)

test_words=[]
for tree in test_pairs:
    samples=set()
    for item in tree:
        samples.add(item[0])
        samples.add(item[1])
    samples=sorted(samples) #just in case we needed to become repeatable
    random.shuffle(samples)
    test_words.append(samples)


train_words_with_roots=[]
for tree in train_words:
    for word in tree:
        node=word2nodes[word][0] #todo: homonymy handling?
        root=None
        for segment in node.segmentation:
            if(segment.get('Type')=='Root'):
                root=segment
                break
        if(root is not None):
            train_words_with_roots.append((node.lemma.lower(), root['Morph'].lower(), (root, node)))


devel_words_with_roots=[]
for tree in devel_words:
    for word in tree:
        node=word2nodes[word][0] #todo: homonymy handling?
        root=None
        for segment in node.segmentation:
            if(segment.get('Type')=='Root'):
                root=segment
                break
        if(root is not None):
            devel_words_with_roots.append((node.lemma.lower(), root['Morph'].lower(), (root, node)))

test_words_with_roots=[]
for tree in test_words:
    for word in tree:
        node=word2nodes[word][0] #todo: homonymy handling?
        root=None
        for segment in node.segmentation:
            if(segment.get('Type')=='Root'):
                root=segment
                break
        if(root is not None):
            test_words_with_roots.append((node.lemma.lower(), root['Morph'].lower(), (root, node)))

#[all pairs taken from all trees]. (word1,word2, tree_id)
train_all_pairs=[]
for tree_id,tree in enumerate(train_pairs):
    for pair in tree:
        train_all_pairs.append((pair[0],pair[1], tree_id))

devel_all_pairs=[]
for tree_id,tree in enumerate(devel_pairs):
    for pair in tree:
        devel_all_pairs.append((pair[0],pair[1], tree_id))

test_all_pairs=[]
for tree_id,tree in enumerate(test_pairs):
    for pair in tree:
        test_all_pairs.append((pair[0],pair[1], tree_id))


#todo: what shall we do with the 19 trees, which have a thousand of lemmas?




###Triplets generators

#random.seed(42)
#train2=select_samples(train)) #(pos,neg,centr)
#devel2=select_samples(devel)
#test2 =select_samples(test )



def generate_standard_triplets(train_pairs):
    pos=[]
    cen=[]
    neg=[]
    for i,x in enumerate(train_pairs):
        k=random.randint(0,1)
        r=random.randint(0, len(x)-1)
        pos.append("^"+x[r][k]+"$")
        cen.append("^"+x[r][1-k]+"$")
        r=random.randint(0, len(train_pairs)-2)
        if(i==r):
            r=len(train_pairs)-1
        r2=random.randint(0,len(train_pairs[r])-1)
        neg.append("^"+train_pairs[r][r2][random.randint(0,1)]+"$")
    return (pos,neg,cen)

#ignore the parrent-child relationship
def generate_standard_triplets_from_whole_trees(train_words):
    pos=[]
    cen=[]
    neg=[]
    for i,x in enumerate(train_words):
        len_=len(x)
        if(len_<2):
            continue
        a=random.randint(0,len_-1)
        if(len_!=2):
            b=random.randint(0,len_-2)
            if(a==b):
                b=len_-1
        else:
            b=1-a
        pos.append("^"+x[a]+"$")
        cen.append("^"+x[b]+"$")
        r=random.randint(0, len(train_words)-2)
        if(i==r):
            r=len(train_words)-1
        r2=random.randint(0,len(train_words[r])-1)
        neg.append("^"+train_words[r][r2]+"$")
    return (pos,neg,cen)


#ignore the parrent-child relationship
def generate_standard_triplets_from_whole_big_trees(train_words):
    pos=[]
    cen=[]
    neg=[]
    cnt=0
    for i,x in enumerate(train_words):
        len_=len(x)
        if(len_<10):
            continue
        else:
            cnt+=1
        if(len_<2):
            continue
        a=random.randint(0,len_-1)
        if(len_!=2):
            b=random.randint(0,len_-2)
            if(a==b):
                b=len_-1
        else:
            b=1-a
        pos.append("^"+x[a]+"$")
        cen.append("^"+x[b]+"$")
        r=random.randint(0, len(train_words)-2)
        if(i==r):
            r=len(train_words)-1
        r2=random.randint(0,len(train_words[r])-1)
        neg.append("^"+train_words[r][r2]+"$")
    print(cnt)
    return (pos,neg,cen)



#randomly samples the pairs
def generate_standard_triplets_from_all_pairs(all_pairs):
    pos=[]
    cen=[]
    neg=[]
    for pair in all_pairs:
        rnd=random.randint(0,1)
        cen.append("^"+pair[rnd]+"$")
        pos.append("^"+pair[1-rnd]+"$")
        tree_id=pair[2]

        rnd2=random.randint(0,len(all_pairs)-1)
        while all_pairs[rnd2][2]==tree_id:
            rnd2=random.randint(0,len(all_pairs)-1)

        rnd=random.randint(0,1)
        neg.append("^"+all_pairs[rnd2][rnd]+"$")
    return (pos,neg,cen)

#pos,neg,cen=generate_standard_triplets(train)