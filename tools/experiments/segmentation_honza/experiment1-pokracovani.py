#the approach of using direct difference has certain issues.
#>>> Segmenter._compute_diff("nachýlit","náchylný")
#[' n', '-a', '+á', ' ch', '+yln', ' ý', '-lit']

#same thing breaks
#>>> Segmenter._compute_diff("zaplácat","zaplacávat")
#[' zapl', '+ac', ' á', '-c', '+v', ' at']


#this time we will try to segment. the words from the derivation tree on the basis of parrent-child relation.

#most words either contain word(s) from their derivational tree as their substrings, or differ by jist a few changes from some other word

###
#load data
import difflib
import editdistance
import importlib



print("Loading data")
import derinet
lexicon=derinet.Lexicon()
lexicon.load("derinet-2-0.tsv")



import segmenteddataset
importlib.reload(segmenteddataset)
train=segmenteddataset.train
devel=segmenteddataset.devel
test=segmenteddataset.test

###

def dprint(f,*args):
    #print(*args)
    out=""
    for x in args:
        out+=str(x)+" "
    out+="\n"
    f.write(out)


def wopen(fname):
    return open(fname,"w",encoding="utf-8",buffering=1024**2)


###
import Segmenters
import DerinetTreeBuilder
importlib.reload(DerinetTreeBuilder)
importlib.reload(Segmenters)
Node=DerinetTreeBuilder.Node


loader=DerinetTreeBuilder.DerinetTreeBuilder(lexicon)

def visualise_segmentation_tree(word, segmentation_class=Segmenters.Segmenter):
    global loader
    root=loader.find_derinettree_root(word)
    tree=DerinetTreeBuilder.DerinetTreeBuilder.build_segmentation_tree(root)
    segmenter=segmentation_class(tree)
    return tree.return_tree() #tree.print_tree(),tree.print_tree2()


for word in ["dar","noha","barva","plesat", "loď", "sníh", "poslouchat", "dynda","stěžeň","pohnout","sníh","výška", "měnit"]:
    vis=visualise_segmentation_tree(word, segmentation_class=Segmenters.Segmenter)
    print(vis)
    print("\n"*3,"-"*6,"\n"*3)
    f=wopen("outputs\\exp1\\segmented_trees\\Segmenter_"+word+".txt")
    f.write(vis)
    f.close()

    vis=visualise_segmentation_tree(word, segmentation_class=Segmenters.ReplacingSegmenter)
    print(vis)
    print("\n"*3,"-"*6,"\n"*3)
    f=wopen("outputs\\exp1\\segmented_trees\\ReplacingSegmenter_"+word+".txt")
    f.write(vis)
    f.close()



#######

import re

def get_class_name(cls):
    return cls.__name__


def findall(word, char):
    i=0
    idx=0
    indices=[]
    while i<len(word):
        if(word[i]==char):
            indices.append(idx)
        else:
            idx+=1
        i+=1
    return indices

segmentation_classes=[Segmenters.Segmenter, Segmenters.PostprocessingSegmenter] #Segmenter, ReplacingSegmenter, PostprocessingSegmenter
segmentation_classes=list(map(lambda x: (get_class_name(x),x), segmentation_classes)) #[("Segmenter",Segmenter),("ReplacingSegmenter",ReplacingSegmenter)...]


cnt=0
ok     ={name:0  for name,cls in segmentation_classes}
nones  =[]
results=[]

#compute splits for all segmentation classes.
for word, correct_segmentation in train:
    cnt+=1
    root=loader.find_derinettree_root(word)
    if(root is None):
        nones.append(word)
        continue

    results.append([])
    for name, segmentation_class in segmentation_classes:
        tree=DerinetTreeBuilder.DerinetTreeBuilder.build_segmentation_tree(root)
        segmenter=segmentation_class(tree)
        segmentation_node=segmenter.segment_word(word)
        if(str(segmentation_node).lower()==correct_segmentation):
            ok[name]+=1
        results[-1].append(segmentation_node)

    correct_segmentation_node=DerinetTreeBuilder.Node(word)
    correct_segmentation_node.segments=set(findall(correct_segmentation, "|"))
    results[-1].append(correct_segmentation_node)

f=wopen("outputs\\exp1\\segmenter_comparison\\predictions_"+segmentation_classes[0][0]+"_"+segmentation_classes[1][0]+".txt")
dprint(f,segmentation_classes)
for x in results:
    dprint(f,x)


dprint(f,"\nCorrect: ", ok,"/",cnt)
f.close()

#

#gets 2 segmentation nodes and the correct predictions
#output e.g.
#de|eskal|ov12á2/v1/a|t12eln|ý

def compare_segmentations(s1,s2,cor):
    out=""
    for i,x in enumerate(s1.word):
        in_s1=i in s1.segments
        in_s2=i in s2.segments
        in_cor=i in cor.segments
        if(in_s1 and in_s2 and in_cor):
            out+="|"
        else:
            if(in_s1):
                out+="1"
            if(in_s2):
                out+="2"
            if(in_cor):
                out+="/"
        out+=x
    return out


f=wopen("outputs\\exp1\\segmenter_comparison\\comparison-of-results_"+segmentation_classes[0][0]+"_"+segmentation_classes[1][0]+".txt")
dprint(f,segmentation_classes)
oversegment_a=0 #how often does a oversegment with regards to the baseline
undersegment_a=0 #how often does a undersegment with regards to the baseline (how often does a omit a true segment)
same_a=0 #number of segments same in a and correct
ok_a=0 #number of segments of correctly segmented words

oversegment_b=0
undersegment_b=0
same_b=0
ok_b=0
a_and_b=0
a_xor_b=0


for a,b,correct in results:
    sega=a.segments
    segb=b.segments
    segcor=correct.segments

    a_and_b+=len(sega.union(segb))
    a_xor_b+=len(sega-segb)+len(segb-sega)
    if(sega==segcor):
        ok_a+=len(sega)
    if(segb==segcor):
        ok_b+=len(segb)

    same_a+=len(a.segments.intersection(correct.segments))
    same_b+=len(b.segments.intersection(correct.segments))
    oversegment_a+=len(a.segments-correct.segments)
    oversegment_b+=len(b.segments-correct.segments)
    undersegment_a+=len(correct.segments-a.segments)
    undersegment_b+=len(correct.segments-b.segments)

    output=compare_segmentations(a,b,correct)
    flags=""
    if(str(a)==str(correct)):
        flags+="1"
    if(str(b)==str(correct)):
        flags+="2"
    tmp=output.replace("12","")
    if("1" in tmp or "2" in tmp): #mark the differently segmentated words
        flags+="D"
    else:
        flags+="S"

    dprint(f,flags," "*(5-len(flags)), output)

dprint(f,segmentation_classes[0][0], "oversegments:     ",oversegment_a, "segments. (with regards to baseline)")
dprint(f,segmentation_classes[0][0], "undersegments:    ",undersegment_a, "segments. (with regards to baseline)")
dprint(f,segmentation_classes[0][0], "same as baseline: ",same_a,"segments")

dprint(f,"")
dprint(f,segmentation_classes[1][0], "oversegments:     ",oversegment_b, "segments. (with regards to baseline)")
dprint(f,segmentation_classes[1][0], "undersegments:    ",undersegment_b, "segments. (with regards to baseline)")
dprint(f,segmentation_classes[1][0], "same as baseline: ",same_b,"segments")
dprint(f,"")
dprint(f,segmentation_classes[0][0], "number of segments in completely correct words", ok_a)
dprint(f,segmentation_classes[1][0], "number of segments in completely correct words", ok_b)
dprint(f,"")
dprint(f,"segments in both: ", a_and_b)
dprint(f,"segments in one: ", a_xor_b)
dprint(f,"\n")
dprint(f,"   o   u    s")
dprint(f,segmentation_classes[0][0][0], oversegment_a,undersegment_a,same_a,"....",ok_a)
dprint(f,segmentation_classes[1][0][0], oversegment_b,undersegment_b,same_b,"....",ok_b)
dprint(f,"and",a_and_b,"xor",a_xor_b)
dprint(f,"\nCorrect: ", ok,"/",cnt)
f.close()

"""
[('Segmenter', <class '__main__.Segmenter'>), ('PostprocessingSegmenter', <class '__main__.PostprocessingSegmenter'>)]

Segmenter oversegments:      581 segments. (with regards to baseline)
Segmenter undersegments:     631 segments. (with regards to baseline)
Segmenter same as baseline:  1197 segments
Correctwords: 70

PostprocessingSegmenter oversegments:      532 segments. (with regards to baseline)
PostprocessingSegmenter undersegments:     632 segments. (with regards to baseline)
PostprocessingSegmenter same as baseline:  1196 segments
Correct words:73


ReplacingSegmenter oversegments:      392 segments. (with regards to baseline)
ReplacingSegmenter undersegments:     642 segments. (with regards to baseline)
ReplacingSegmenter same as baseline:  1186 segments
Correct words: 86

Segmenter number of segments in completely correct words 74
PostprocessingSegmenter number of segments in completely correct words 81
ReplacingSegmenter number of segments in completely correct words 118



   o   u    s
S 581 631 1197 .... 74
P 532 632 1196 .... 81
R 392 642 1186 .... 118

S and P 1778
S xor P 50

P and R 1870 #segments in P and R
P xor R 434



we can see, that over- and under- segmentation are equally big issue. We also see, that PostprocessingSegmenter was able to
precisely address the issue it was expected to solve. It made 50 changes in segmentation - 49 were correct removals of segments,
1 was an incorrect removal of segment. But beware. This does not necessarilly mean that we were so successful in every given segmentation step.
This is result of the whole iterative algorithm, not of a single step..

In the second case, we compared PostprocessingSegmenter wiht ReplacingSegmenter. We can conclude, that ReplacementSegmenter removes LOTS of wrong segments, with just a few
unnecessary removals.





[Segmenter, ReplacingSegmenter]

S    Dynd|a
S    Pedici/a       #tree with 1 word only
S    Štiav/n/i/čk/a #tree with 1 word only
D    šperk|ovni1č2/k/a #->šperkovnice
D    k1a1no|ist|k|a   #-> kánoe
S    trul/a         #tree with 1 word only
S    poly/valen12c/e #-> polyvalen|tní
S    z|re/vok|ov12a|vš/í                  #revokace->revok|ov|at (insertion of "ov")
....

#automatic segmentation: lout|k|a|ř,  correct: loutk|ař, wrong segments come from lout|eč|ka






the differences between the version which does not use the replacement ě->e, á->a,.. , and the one that does.
This difference improves the results from 70/500 to 86/500, but it affects half of the training set.

('šperk|ovni|čka', 'šperk|ovnič|ka', 'šperk|ovnič|k|a') #šperkovnice
('k|a|no|ist|k|a', 'kano|ist|k|a', 'kano|ist|k|a')   #kánoe?
('lepš|ová', 'lepš|ov|á', 'lepš|ov|á') #WTF?????
('islan|d', 'island', 'island')        #islanďan
('s|e|t|n|i|ce', 's|e|t|ni|c|e', 'set|ni|c|e')
('za|chr|áp|a|n|ě', 'za|chráp|a|n|ě', 'za|chráp|a|n|ě')
('ve|chv|át|a|n|ě', 've|chvát|a|n|ě', 've|chvát|a|n|ě') #chvat
('na|žble|p|t|áv|a|n|ě', 'na|žble|p|t|á|va|n|ě', 'na|žblept|á|v|a|n|ě')
('z|kr|v|á|c|ov|áv|a|n|ě', 'z|kr|vác|ová|va|n|ě', 'z|krv|ác|ová|v|a|n|ě')
('po|sv|ě|c|ov|áv|a|n|ě', 'po|sv|ě|c|ová|va|n|ě', 'po|svěc|ová|v|a|n|ě')
('z|galvan|ov|áv|a|n|ě', 'z|galvan|ová|va|n|ě', 'z|galvan|ová|v|a|n|ě')
('z|bar|v|ov|áv|a|n|ě', 'z|bar|v|ová|va|n|ě', 'z|barv|ová|v|a|n|ě')
('v|kl|uz|o|v|áv|a|n|ě', 'v|kl|uz|o|vá|va|n|ě', 'v|kluz|ová|v|a|n|ě')
('pro|st|oh|ov|a|n|ě', 'pro|st|oh|ova|n|ě', 'pro|stoh|ova|n|ě')
('roz|po|sl|o|u|ch|áv|a|t|eln|ě', 'roz|po|sl|o|u|ch|á|va|t|eln|ě', 'roz|po|slouch|á|v|a|teln|ě')
('u|zdv|i|h|áv|a|t|eln|ě', 'u|zdvi|h|á|va|t|eln|ě', 'u|zdvih|á|v|a|teln|ě')
('z|led|ov|áv|a|t|eln|ě', 'z|led|ová|va|t|eln|ě', 'z|led|ová|v|a|teln|ě')
('po|s|i|l|ov|áv|a|t|eln|ě', 'po|sil|ov|á|va|t|eln|ě', 'po|sil|ová|v|a|teln|ě')
('galvan|ov|áv|a|t|eln|ě', 'galvan|ová|va|t|eln|ě', 'galvan|ová|v|a|teln|ě')
('za|šp|á|r|o|v|áv|a|t|eln|ě', 'za|šp|á|r|o|vá|va|t|eln|ě', 'za|špár|ová|v|a|teln|ě')
('tábo|ř|ív|a|t|eln|ě', 'táboř|í|va|t|eln|ě', 'táboř|í|v|a|teln|ě')
('vys|í|l|a|čk|ov|ě', 'vys|í|la|čk|ov|ě', 'vy|síl|ač|k|ov|ě')
('ti|sk|a|cí', 'tis|k|a|cí', 'tisk|a|c|í')
('o|cejch|ov|áv|a|cí', 'o|cejch|ová|va|cí', 'o|cejch|ová|v|a|c|í')           #ová
('u|k|o|j|ov|áv|a|cí', 'u|k|o|j|ová|va|cí', 'u|koj|ová|v|a|c|í')
('se|s|a|z|ov|áv|a|cí', 'se|sa|z|ová|va|cí', 'se|saz|ová|v|a|c|í')
('do|o|pl|o|z|ov|áv|a|cí', 'do|o|pl|o|z|ová|va|cí', 'do|o|ploz|ová|v|a|c|í')
('třeš|t|ív|a|cí', 'třeš|t|í|va|cí', 'třešt|í|v|a|c|í')
('pl|á|c|a|jící', 'plác|a|jící', 'plác|aj|íc|í')
('obsíl|a|jící', 'obsíla|jící', 'ob|síl|aj|íc|í')
('štrajk|ov|áv|a|jící', 'štrajk|ová|va|jící', 'štrajk|ová|v|aj|íc|í')
('u|smy|k|o|v|áv|a|jící', 'u|smy|k|o|vá|va|jící', 'u|smyk|ová|v|aj|íc|í')
('za|trén|ov|áv|a|jící', 'za|trén|ová|va|jící', 'za|trén|ová|v|aj|íc|í')
('při|k|up|ov|áv|a|jící', 'při|k|up|ová|va|jící', 'při|kup|ová|v|aj|íc|í')
('koment|ov|áv|a|jící', 'koment|ov|á|va|jící', 'koment|ová|v|aj|íc|í')
('při|no|ž|ov|áv|a|jící', 'při|no|ž|ová|va|jící', 'při|nož|ová|v|aj|íc|í')
('flast|r|ující', 'flastr|ující', 'flastr|uj|íc|í')
('na|pajc|ov|áv|ání', 'na|pajc|ová|vá|ní', 'na|pajc|ová|v|á|n|í')
('pře|p|u|t|o|v|áv|ání', 'pře|p|ut|ov|á|vá|ní', 'pře|put|ová|v|á|n|í')
('při|krč|ov|ání', 'při|krč|ová|ní', 'při|krč|ová|n|í')
('do|štrik|ov|ání', 'do|štrik|ová|ní', 'do|štrik|ová|n|í')
('p|í|sk|o|v|ání', 'písk|o|vá|ní', 'písk|ová|n|í')
('zprůchod|ň|ov|ání', 'zprůchodň|ová|ní', 'z|prů|chod|ň|ová|n|í')
('do|t|ě|s|ňov|ání', 'do|t|ě|s|ň|ová|ní', 'do|těsň|ová|n|í')
('za|konzerv|ov|ání', 'za|konzerv|ov|á|ní', 'za|konzerv|ová|n|í')
('na|proud|ění', 'na|proud|ěn|í', 'na|proud|ě|n|í')
('do|n|a|stř|e|l|ov|a|vší', 'do|na|stř|e|l|ova|vší', 'do|na|střel|ova|vš|í')
('za|štup|ov|a|vší', 'za|štup|ova|vší', 'za|štup|ova|vš|í')
('z|p|é|k|a|t', 'z|p|é|ka|t', 'z|pék|a|t')
('roz|cmrnd|áv|a|t', 'roz|cmrnd|á|va|t', 'roz|cmrnd|á|v|a|t')
('roz|chy|t|áv|a|t', 'roz|chy|t|á|va|t', 'roz|chyt|á|v|a|t')
('karb|ov|áv|a|t', 'karb|ová|va|t', 'karb|ová|v|a|t')
('sh|y|b|o|v|áv|a|t', 'shyb|o|vá|va|t', 's|hyb|ová|v|a|t')
('vy|ce|ň|ov|áv|a|t', 'vy|ceň|ová|va|t', 'vy|ceň|ová|v|a|t')
('od|rap|ov|áv|a|t', 'od|rap|ová|va|t', 'od|rap|ová|v|a|t')
('rychlonabíj|ív|a|t', 'rychlonabíj|íva|t', 'rychl|o|na|bíj|í|v|a|t')
('zanepr|a|zd|ň|ov|a|t', 'zaneprazdň|ova|t', 'za|ne|prazdň|ova|t')
('vy|stres|ov|a|t', 'vy|stres|ova|t', 'vy|stres|ova|t')
('zmythologisov|a|t', 'zmythologisova|t', 'z|myth|o|log|isova|t')
('vhečm|a|n|ost', 'vhečma|n|ost', 'v|hečm|a|n|ost')
('roz|kolís|a|n|ost', 'roz|kolísa|n|ost', 'roz|kolís|a|n|ost')
('u|jeb|áv|a|n|ost', 'u|jeb|á|va|n|ost', 'u|jeb|á|v|a|n|ost')
('vy|l|e|h|áv|a|n|ost', 'vy|l|e|h|á|va|n|ost', 'vy|leh|á|v|a|n|ost')
('o|šuk|áv|a|n|ost', 'o|šuk|á|va|n|ost', 'o|šuk|á|v|a|n|ost')
('zaž|í|r|áv|a|n|ost', 'zaž|í|rá|va|n|ost', 'za|žír|á|v|a|n|ost')
('vy|zpyt|áv|a|n|ost', 'vy|zpytá|va|n|ost', 'vy|zpyt|á|v|a|n|ost')
('za|čachr|ov|áv|a|n|ost', 'za|čachr|ová|va|n|ost', 'za|čachr|ová|v|a|n|ost')
('o|cenzur|ov|áv|a|n|ost', 'o|cenzur|ov|á|va|n|ost', 'o|cenzur|ová|v|a|n|ost')
('sabráž|ov|áv|a|n|ost', 'sabráž|ová|va|n|ost', 'sabráž|ová|v|a|n|ost')
('antagoni|z|ov|áv|a|n|ost', 'antagoni|z|ová|va|n|ost', 'anta|gon|izová|v|a|n|ost')
('plejtv|áv|a|n|ost', 'plejtvá|va|n|ost', 'plejtv|á|v|a|n|ost')
('roz|porc|ov|a|n|ost', 'roz|porc|ova|n|ost', 'roz|porc|ova|n|ost')
('o|štrik|ov|a|n|ost', 'o|štrik|ova|n|ost', 'o|štrik|ova|n|ost')
('od|ch|y|l|ov|a|n|ost', 'od|chyl|ova|n|ost', 'od|chyl|ova|n|ost')
('zhangr|ov|a|n|ost', 'zhangr|ova|n|ost', 'z|hangr|ova|n|ost')
('o|s|u|š|ov|a|n|ost', 'o|s|u|š|ova|n|ost', 'o|suš|ova|n|ost')
('o|č|i|ch|áv|a|t|eln|ost', 'o|č|i|ch|á|va|t|eln|ost', 'o|čich|á|v|a|teln|ost')
('dočmuch|áv|a|t|eln|ost', 'dočmuchá|va|t|eln|ost', 'do|čmuch|á|v|a|teln|ost')
('čm|á|r|áv|a|t|eln|ost', 'čmár|á|va|t|eln|ost', 'čmár|á|v|a|teln|ost')
('vy|č|u|r|áv|a|t|eln|ost', 'vy|čur|á|va|t|eln|ost', 'vy|čur|á|v|a|teln|ost')
('do|r|ach|t|áv|a|t|eln|ost', 'do|rach|t|á|va|t|eln|ost', 'do|racht|á|v|a|teln|ost')
('do|patrol|ov|áv|a|t|eln|ost', 'do|patrol|ov|á|va|t|eln|ost', 'do|patrol|ová|v|a|teln|ost')
('z|konsum|ov|áv|a|t|eln|ost', 'z|konsum|ová|va|t|eln|ost', 'z|konsum|ová|v|a|teln|ost')
('po|s|un|o|v|áv|a|t|eln|ost', 'po|s|un|o|vá|va|t|eln|ost', 'po|sun|ová|v|a|teln|ost')
('u|let|ov|áv|a|t|eln|ost', 'u|let|ová|va|t|eln|ost', 'u|let|ová|v|a|teln|ost')
('pře|šluk|o|v|a|t|eln|ost', 'pře|šluk|o|va|t|eln|ost', 'pře|šluk|ova|teln|ost')
('z|mrv|ov|a|t|eln|ost', 'z|mrv|ova|t|eln|ost', 'z|mrv|ova|teln|ost')
('vy|zdv|í|h|áv|a|n|ý', 'vy|zdví|h|á|va|n|ý', 'vy|zdvíh|á|v|a|n|ý')
('vecp|áv|a|n|ý', 'vecpá|va|n|ý', 've|cp|á|v|a|n|ý')
('do|z|pr|a|c|ov|áv|a|n|ý', 'do|z|prac|ov|á|va|n|ý', 'do|z|prac|ová|v|a|n|ý')
('od|št|ě|p|ov|áv|a|n|ý', 'od|št|ě|p|ová|va|n|ý', 'od|štěp|ová|v|a|n|ý')
('od|test|ov|áv|a|n|ý', 'od|test|ov|á|va|n|ý', 'od|test|ová|v|a|n|ý')
('pře|košt|o|v|áv|a|n|ý', 'pře|košt|o|vá|va|n|ý', 'pře|košt|ová|v|a|n|ý')
('švenk|o|v|a|n|ý', 'švenk|o|va|n|ý', 'švenk|ova|n|ý')
('po|zele|ň|ov|a|n|ý', 'po|zeleň|ova|n|ý', 'po|zeleň|ova|n|ý')
('roz|s|a|zen|ý', 'roz|sa|zen|ý', 'roz|saz|en|ý')
('o|šol|i|ch|áv|a|t|eln|ý', 'o|šolichá|va|t|eln|ý', 'o|šolich|á|v|a|teln|ý')
('podestýl|áv|a|t|eln|ý', 'podestýl|á|va|t|eln|ý', 'pode|stýl|á|v|a|teln|ý')
('pro|po|č|í|t|áv|a|t|eln|ý', 'pro|po|č|í|t|á|va|t|eln|ý', 'pro|po|čít|á|v|a|teln|ý')
('u|mil|ov|áv|a|t|eln|ý', 'u|mil|ov|á|va|t|eln|ý', 'u|mil|ová|v|a|teln|ý')
('konstru|ov|áv|a|t|eln|ý', 'konstru|ová|va|t|eln|ý', 'kon|stru|ová|v|a|teln|ý')
('gauč|ov|a|t|eln|ý', 'gauč|ova|t|eln|ý', 'gauč|ova|teln|ý')
('pro|kl|uz|o|v|a|t|eln|ý', 'pro|kl|uz|o|va|t|eln|ý', 'pro|kluz|ova|teln|ý')
('za|dř|í|m|l|e', 'za|dřím|l|e', 'za|dřím|l|e')
('pře|deklar|ov|áv|a|n|ě', 'pře|deklar|ov|á|va|n|ě', 'pře|de|klar|ová|v|a|n|ě')
('ob|r|á|b|ív|a|n|ě', 'ob|r|á|b|íva|n|ě', 'ob|ráb|í|v|a|n|ě')
('za|sk|l|í|v|a|n|ě', 'za|sk|l|í|va|n|ě', 'za|skl|í|v|a|n|ě')
('u|v|á|l|c|ov|a|n|ě', 'u|vál|c|ov|a|n|ě', 'u|vál|c|ova|n|ě')
('stra|ch|ov|a|n|ě', 'stra|ch|ova|n|ě', 'strach|ova|n|ě')
('kad|m|i|ov|a|n|ě', 'kad|m|i|ova|n|ě', 'kadmi|ova|n|ě')
('v|m|ěš|ov|a|n|ě', 'v|m|ě|š|ova|n|ě', 'v|měš|ova|n|ě')
('obl|e|t|o|v|a|n|ě', 'oblet|o|va|n|ě', 'ob|let|ova|n|ě')
('o|hr|a|ž|ov|a|n|ě', 'o|hra|ž|ova|n|ě', 'o|hraž|ova|n|ě')
('z|utra|kv|i|z|ov|a|n|ě', 'z|utra|kv|i|z|ova|n|ě', 'z|utrakv|izova|n|ě')
('loku|čn|ě', 'lokuč|n|ě', 'lokuč|n|ě')
('br|a|t|ř|en|ě', 'bra|tř|en|ě', 'bratř|en|ě')
('do|d|iv|en|ě', 'do|d|i|v|en|ě', 'do|div|en|ě')
('po|v|o|žen|ě', 'po|v|o|ž|en|ě', 'po|vož|en|ě')
('šmrdl|a|t|eln|ě', 'šmrdla|t|eln|ě', 'šmrdl|a|teln|ě')
('o|k|o|us|áv|a|t|eln|ě', 'o|k|o|us|á|va|t|eln|ě', 'o|kous|á|v|a|teln|ě')
('pře|s|év|áv|a|t|eln|ě', 'pře|s|évá|va|t|eln|ě', 'pře|s|é|v|á|v|a|teln|ě')
('zakademič|ť|ov|áv|a|t|eln|ě', 'zakademičť|ová|va|t|eln|ě', 'z|akadem|ič|ť|ová|v|a|teln|ě')
('za|o|č|k|o|v|a|t|eln|ě', 'za|o|č|k|o|va|t|eln|ě', 'za|oč|k|ova|teln|ě')
('vy|handrk|ov|a|t|eln|ě', 'vy|handrk|ova|t|eln|ě', 'vy|handrk|ova|teln|ě')
('oflitrov|a|t|eln|ě', 'oflitrova|t|eln|ě', 'o|flitr|ova|teln|ě')
('od|kmot|r|ov|a|t|eln|ě', 'od|kmotr|ova|t|eln|ě', 'od|kmotr|ova|teln|ě')
('kř|á|p|n|u|t|eln|ě', 'křáp|n|u|t|eln|ě', 'křáp|nu|teln|ě')
('v|y|j|ížďk|ov|ě', 'vy|j|ížďk|ov|ě', 'vy|jížď|k|ov|ě')
('same|t|ov|ě', 'samet|ov|ě', 'samet|ov|ě')
('zů|st|áv|a|cí', 'zů|st|á|va|cí', 'zůst|áv|a|c|í')
('ze|škare|ď|ov|áv|a|cí', 'ze|škareď|ová|va|cí', 'ze|škareď|ová|v|a|c|í')
('za|hajduch|ov|áv|a|cí', 'za|hajduch|ová|va|cí', 'za|hajduch|ová|v|a|c|í')
('v|y|ch|o|v|áv|a|cí', 'vy|ch|o|v|á|va|cí', 'vy|chov|á|v|a|c|í')
('za|řemes|l|o|v|áv|a|cí', 'za|řemes|l|o|vá|va|cí', 'za|řemes|l|ová|v|a|c|í')
('senziti|z|o|v|áv|a|cí', 'senziti|z|o|v|á|va|cí', 'senz|it|izová|v|a|c|í')
('od|há|č|k|ov|a|cí', 'od|há|č|k|ova|cí', 'od|háč|k|ova|c|í')
('besemer|ov|a|cí', 'besemer|ova|cí', 'besemer|ova|c|í')
('pro|kšeft|ov|a|cí', 'pro|kšeft|ova|cí', 'pro|kšeft|ova|c|í')
('při|sn|ěž|ov|a|cí', 'při|sn|ěž|ova|cí', 'při|sněž|ova|c|í')
('p|á|r|k|ov|áv|a|jící', 'pár|k|ová|va|jící', 'pár|k|ová|v|aj|íc|í')
('trošt|ov|áv|a|jící', 'trošt|ová|va|jící', 'trošt|ová|v|a|j|íc|í')
('za|v|áz|ív|a|jící', 'za|vá|z|íva|jící', 'za|váz|í|v|aj|íc|í')
('na|n|a|ř|í|k|ání', 'na|na|ř|í|k|á|ní', 'na|na|řík|á|n|í')
('vy|p|ej|k|ání', 'vy|p|e|j|ká|ní', 'vy|pejk|á|n|í')
('za|dudl|ání', 'za|dudl|á|ní', 'za|dudl|á|n|í')
('vmít|ání', 'vmítá|ní', 'v|mít|á|n|í')
('zacupot|ání', 'zacupotá|ní', 'za|cup|ot|á|n|í')
('zachropot|áv|ání', 'zachropotá|vá|ní', 'za|chrop|ot|á|v|á|n|í')
('re|emigr|ov|áv|ání', 're|emigr|ov|á|vá|ní', 're|e|migr|ová|v|á|n|í')
('komuni|z|ov|áv|ání', 'komuni|z|ov|á|vá|ní', 'komun|izová|v|á|n|í')
('zagajdov|ání', 'zagajdová|ní', 'za|gajd|ová|n|í')
('fábor|k|ov|ání', 'fábor|k|ová|ní', 'fábor|k|ová|n|í')
('rela|tiv|iz|ov|ání', 'rela|tiv|i|z|ov|á|ní', 'relat|iv|izová|n|í')
('za|ha|šení', 'za|haš|en|í', 'za|haš|en|í')
('za|štiřik|a|vší', 'za|štiřika|vší', 'za|štiřik|a|vš|í')
('pro|kormid|l|o|v|a|vší', 'pro|kormid|l|o|va|vší', 'pro|kormidl|ova|vš|í')
('za|lažír|ov|a|vší', 'za|lažír|ova|vší', 'za|lažír|ova|vš|í')
('za|kant|o|r|ov|a|vší', 'za|kant|o|r|ova|vší', 'za|kant|or|ova|vš|í')
('od|syst|e|m|ati|z|ov|a|vší', 'od|system|ati|z|ov|a|vší', 'od|systém|at|izova|vš|í')
('v|ě|d|m|ák', 'v|ě|d|m|á|k', 'věd|m|ák')
('konvenčn|ík', 'konvenční|k', 'kon|venč|ník')
('zmatk|á|ř', 'zmatkář', 'z|mat|k|ář')
('vy|v|st|áv|a|t', 'vy|v|st|á|va|t', 'vy|v|st|á|v|a|t')
('ag|ov|áv|a|t', 'ag|ová|va|t', 'agov|á|v|a|t')
('ordin|ov|áv|a|t', 'ordin|ov|á|va|t', 'ordin|ová|v|a|t')
('na|var|ov|áv|a|t', 'na|var|ov|á|va|t', 'na|var|ová|v|a|t')
('o|kategori|z|ov|áv|a|t', 'o|kategori|z|ov|á|va|t', 'o|kategor|izová|v|a|t')
('t|k|a|l|c|ov|a|t', 't|ka|l|c|ova|t', 'tka|lc|ova|t')
('zageneralisov|a|t', 'zageneralisova|t', 'za|general|isova|t')
('debit|ov|a|t', 'debit|ova|t', 'debit|ova|t')
('vy|hlad|ov|ov|a|t', 'vy|hlad|ov|ova|t', 'vy|hlad|ov|ova|t')
('o|pl|ác|e|t', 'o|plá|c|e|t', 'o|plác|e|t')
('s|m|y|s|l|i|t', 's|m|y|sl|i|t', 's|mysl|i|t')
('zamykl|a|n|ost', 'zamykla|n|ost', 'za|mykl|a|n|ost')
('céd|áv|a|n|ost', 'cédá|va|n|ost', 'cé|dá|v|a|n|ost')
('z|p|a|l|i|č|k|ov|áv|a|n|ost', 'z|pal|i|č|k|ov|á|va|n|ost', 'z|pal|ič|k|ová|v|a|n|ost')
('acidifik|ov|áv|a|n|ost', 'acidifik|ová|va|n|ost', 'acid|i|fik|ová|v|a|n|ost')
('popo|str|k|ov|áv|a|n|ost', 'popo|str|k|ová|va|n|ost', 'po|po|strk|ová|v|a|n|ost')
('z|kypř|ov|áv|a|n|ost', 'z|kypř|ová|va|n|ost', 'z|kypř|ová|v|a|n|ost')
('zimav|ív|a|n|ost', 'zimav|íva|n|ost', 'zimavív|a|n|ost')
('transkri|b|ov|a|n|ost', 'transkri|b|ova|n|ost', 'tran|skrib|ova|n|ost')
('skot|ač|en|ost', 'skot|a|č|en|ost', 'skotač|en|ost')
('vy|chr|á|n|ěn|ost', 'vy|chrán|ěn|ost', 'vy|chrán|ěn|ost')
('za|m|a|k|a|t|eln|ost', 'za|mak|a|t|eln|ost', 'za|mak|a|teln|ost')
('zaplít|a|t|eln|ost', 'zaplíta|t|eln|ost', 'za|plít|a|teln|ost')
('subvenc|ov|áv|a|t|eln|ost', 'subvenc|ová|va|t|eln|ost', 'sub|ven|c|ová|v|a|teln|ost')
('pro|s|chv|a|l|ov|áv|a|t|eln|ost', 'pro|s|chval|ová|va|t|eln|ost', 'pro|s|chval|ová|v|a|teln|ost')
('po|žel|atin|ov|áv|a|t|eln|ost', 'po|žel|atin|ov|á|va|t|eln|ost', 'po|žel|atin|ová|v|a|teln|ost')
('roz|po|č|t|ov|áv|a|t|eln|ost', 'roz|po|č|t|ová|va|t|eln|ost', 'roz|po|čt|ová|v|a|teln|ost')
('atom|i|z|ov|áv|a|t|eln|ost', 'atom|i|z|ov|á|va|t|eln|ost', 'atom|izová|v|a|teln|ost')
('upovšech|ň|ov|a|t|eln|ost', 'upovšechň|ova|t|eln|ost', 'u|po|vše|ch|ň|ova|teln|ost')
('zmalát|ň|ov|a|t|eln|ost', 'zmalátň|ova|t|eln|ost', 'z|malát|ň|ova|teln|ost')
('n|a|hr|a|d|i|t|eln|ost', 'na|hra|d|i|t|eln|ost', 'na|hrad|i|teln|ost')
('pro|kl|á|d|k|ov|ost', 'pro|klá|d|k|ov|ost', 'pro|klád|k|ov|ost')
('v|y|b|í|r|a|č|ův', 'vy|b|í|r|a|č|ův', 'vy|bír|ač|ův')
('alfr|é|d|ův', 'alfréd|ův', 'alfréd|ův')
('vinohr|a|d|n|í|k|ův', 'vinohrad|ní|k|ův', 'vin|o|hrad|ník|ův')
('kř|í|ž|ov|n|í|k|ův', 'kříž|ov|ní|k|ův', 'kříž|ovník|ův')
('pohl|c|ov|a|t|el|ův', 'pohl|c|ova|t|el|ův', 'po|hlc|ova|tel|ův')
('verb|a|l|is|t|ův', 'verb|al|i|s|t|ův', 'verb|al|ist|ův')
('ř|e|z|n|i|c|k|y', 'ř|e|z|ni|c|k|y', 'řez|nic|k|y')
('o|chr|a|n|i|t|el|s|k|y', 'o|chran|i|t|el|s|k|y', 'o|chran|i|tel|sk|y')
('pro|cvik|a|n|ý', 'pro|cvika|n|ý', 'pro|cvik|a|n|ý')
('za|sál|a|n|ý', 'za|sála|n|ý', 'za|sál|a|n|ý')
('sebeuzavír|a|n|ý', 'sebeuzavíra|n|ý', 'seb|e|u|za|vír|a|n|ý')
('z|aproxim|ov|áv|a|n|ý', 'z|aproxim|ov|á|va|n|ý', 'z|a|proxim|ová|v|a|n|ý')
('z|kap|a|l|ň|ov|áv|a|n|ý', 'z|kap|a|l|ň|ová|va|n|ý', 'z|kap|a|l|ň|ová|v|a|n|ý')
('ze|sn|o|v|áv|a|n|ý', 'ze|sn|o|v|á|va|n|ý', 'ze|snov|á|v|a|n|ý')
('spíj|ív|a|n|ý', 'spíj|íva|n|ý', 's|píj|í|v|a|n|ý')
('blouzn|ív|a|n|ý', 'blouzn|í|va|n|ý', 'blouzn|í|v|a|n|ý')
('zmultiplicírov|a|n|ý', 'zmultiplicírova|n|ý', 'z|multi|plic|ír|ova|n|ý')
('po|ch|u|t|n|a|t|eln|ý', 'po|ch|ut|n|a|t|eln|ý', 'po|chut|n|a|teln|ý')
('po|z|í|r|áv|a|t|eln|ý', 'po|z|í|r|á|va|t|eln|ý', 'po|zír|á|v|a|teln|ý')
('de|eskal|ov|áv|a|t|eln|ý', 'de|eskal|ov|á|va|t|eln|ý', 'de|eskal|ová|v|a|teln|ý')
('hra|n|ív|a|t|eln|ý', 'hran|í|va|t|eln|ý', 'hran|í|v|a|teln|ý')
('jas|n|ív|a|t|eln|ý', 'jas|n|í|va|t|eln|ý', 'jas|n|í|v|a|teln|ý')
('velrybař|ív|a|t|eln|ý', 'velrybař|í|va|t|eln|ý', 'vel|ryb|ař|í|v|a|teln|ý')
('ž|i|l|n|a|t|ív|a|t|eln|ý', 'žil|n|a|t|íva|t|eln|ý', 'žil|n|atí|v|a|teln|ý')
('čtvr|t|ív|a|t|eln|ý', 'čtvr|t|í|va|t|eln|ý', 'čtvrt|í|v|a|teln|ý')
('s|kv|ív|a|t|eln|ý', 's|kv|íva|t|eln|ý', 'skv|í|v|a|teln|ý')
('dat|um|ov|a|t|eln|ý', 'dat|um|ova|t|eln|ý', 'dat|um|ova|teln|ý')
('strip|ov|a|t|eln|ý', 'strip|ova|t|eln|ý', 'strip|ova|teln|ý')
('roz|kompres|ov|a|t|eln|ý', 'roz|kompres|ova|t|eln|ý', 'roz|kom|pres|ova|teln|ý')
('ú|ž|i|t|eln|ý', 'úž|i|t|eln|ý', 'úž|i|teln|ý')
('z|tl|á|p|n|u|t|eln|ý', 'z|tláp|n|u|t|eln|ý', 'z|tláp|nu|teln|ý')
('super|špi|č|k|ov|ý', 'super|špič|k|ov|ý', 'super|špič|k|ov|ý')













dar
  darovat - [' dar', '+ovat'] dar|ovat
    dárce - [' d', '-a', '+á', ' r', '-ovat', '+ce'] d|á|r|ce
      dárcovský - [' dárc', '-e', '+ovský'] d|á|r|c|ovský
        dárcovskost - [' dárcovsk', '-ý', '+ost'] d|á|r|c|ovsk|ost
        dárcovsky - [' dárcovsk', '-ý', '+y'] d|á|r|c|ovsk|y
        dárcovství - [' dárcovs', '-ký', '+tví'] d|á|r|c|ovs|tví
      dárcův - [' dárc', '-e', '+ův'] d|á|r|c|ův
      dárkyně - [' dár', '-ce', '+kyně'] d|á|r|kyně
        dárkynin - [' dárkyn', '-ě', '+in'] d|á|r|kyn|in
      službodárce - ['+službo', ' dárce'] službo|d|á|r|ce
        službodárcův - [' službodárc', '-e', '+ův'] službo|d|á|r|c|ův
        službodárkyně - [' službodár', '-ce', '+kyně'] službo|d|á|r|kyně
          službodárkynin - [' službodárkyn', '-ě', '+in'] službo|d|á|r|kyn|in
    darovací - [' darova', '-t', '+cí'] dar|ova|cí
    darování - [' darov', '-at', '+ání'] dar|ov|ání
    darovaný - [' darova', '-t', '+ný'] dar|ova|ný
      darovaně - [' darovan', '-ý', '+ě'] dar|ova|n|ě
      darovanost - [' darovan', '-ý', '+ost'] dar|ova|n|ost
    darovatel - [' darovat', '+el'] dar|ovat|el
      darovatelka - [' darovatel', '+ka'] dar|ovat|el|ka
        darovatelčin - [' darovatel', '-ka', '+čin'] dar|ovat|el|čin
      darovatelův - [' darovatel', '+ův'] dar|ovat|el|ův
    darovatelný - [' darovat', '+elný'] dar|ovat|elný
      darovatelně - [' darovateln', '-ý', '+ě'] dar|ovat|eln|ě
      darovatelnost - [' darovateln', '-ý', '+ost'] dar|ovat|eln|ost
    darovávat - [' darov', '+áv', ' at'] dar|ov|áv|at
      darovávací - [' darováva', '-t', '+cí'] dar|ov|áv|a|cí
      darovávající - [' darováva', '-t', '+jící'] dar|ov|áv|a|jící
      darovávání - [' darováv', '-at', '+ání'] dar|ov|áv|ání
      darovávaný - [' darováva', '-t', '+ný'] dar|ov|áv|a|ný
        darovávaně - [' darovávan', '-ý', '+ě'] dar|ov|áv|a|n|ě
        darovávanost - [' darovávan', '-ý', '+ost'] dar|ov|áv|a|n|ost
      darovávatelný - [' darovávat', '+elný'] dar|ov|áv|at|elný
        darovávatelně - [' darovávateln', '-ý', '+ě'] dar|ov|áv|at|eln|ě
        darovávatelnost - [' darovávateln', '-ý', '+ost'] dar|ov|áv|at|eln|ost
    darovavší - [' darova', '-t', '+vší'] dar|ova|vší
    darující - [' dar', '-ovat', '+ující'] dar|ující
    obdarovat - ['+ob', ' darovat'] ob|dar|ovat
      obdarovací - [' obdarova', '-t', '+cí'] ob|dar|ova|cí
      obdarování - [' obdarov', '-at', '+ání'] ob|dar|ov|ání
      obdarovaný - [' obdarova', '-t', '+ný'] ob|dar|ova|ný
        obdarovaně - [' obdarovan', '-ý', '+ě'] ob|dar|ova|n|ě
        obdarovanost - [' obdarovan', '-ý', '+ost'] ob|dar|ova|n|ost
      obdarovatel - [' obdarovat', '+el'] ob|dar|ovat|el
        obdarovatelka - [' obdarovatel', '+ka'] ob|dar|ovat|el|ka
          obdarovatelčin - [' obdarovatel', '-ka', '+čin'] ob|dar|ovat|el|čin
        obdarovatelův - [' obdarovatel', '+ův'] ob|dar|ovat|el|ův
      obdarovatelný - [' obdarovat', '+elný'] ob|dar|ovat|elný
        obdarovatelně - [' obdarovateln', '-ý', '+ě'] ob|dar|ovat|eln|ě
        obdarovatelnost - [' obdarovateln', '-ý', '+ost'] ob|dar|ovat|eln|ost
      obdarovávat - [' obdarov', '+áv', ' at'] ob|dar|ov|áv|at
        obdarovávací - [' obdarováva', '-t', '+cí'] ob|dar|ov|áv|a|cí
        obdarovávající - [' obdarováva', '-t', '+jící'] ob|dar|ov|áv|a|jící
        obdarovávání - [' obdarováv', '-at', '+ání'] ob|dar|ov|áv|ání
        obdarovávaný - [' obdarováva', '-t', '+ný'] ob|dar|ov|áv|a|ný
          obdarovávaně - [' obdarovávan', '-ý', '+ě'] ob|dar|ov|áv|a|n|ě
          obdarovávanost - [' obdarovávan', '-ý', '+ost'] ob|dar|ov|áv|a|n|ost
        obdarovávatel - [' obdarovávat', '+el'] ob|dar|ov|áv|at|el
          obdarovávatelka - [' obdarovávatel', '+ka'] ob|dar|ov|áv|at|el|ka
            obdarovávatelčin - [' obdarovávatel', '-ka', '+čin'] ob|dar|ov|áv|at|el|čin
          obdarovávatelův - [' obdarovávatel', '+ův'] ob|dar|ov|áv|at|el|ův
        obdarovávatelný - [' obdarovávat', '+elný'] ob|dar|ov|áv|at|elný
          obdarovávatelně - [' obdarovávateln', '-ý', '+ě'] ob|dar|ov|áv|at|eln|ě
          obdarovávatelnost - [' obdarovávateln', '-ý', '+ost'] ob|dar|ov|áv|at|eln|ost
      obdarovavší - [' obdarova', '-t', '+vší'] ob|dar|ova|vší
    podarovat - ['+po', ' darovat'] po|dar|ovat
      podarovací - [' podarova', '-t', '+cí'] po|dar|ova|cí
      podarování - [' podarov', '-at', '+ání'] po|dar|ov|ání
      podarovaný - [' podarova', '-t', '+ný'] po|dar|ova|ný
        podarovaně - [' podarovan', '-ý', '+ě'] po|dar|ova|n|ě
        podarovanost - [' podarovan', '-ý', '+ost'] po|dar|ova|n|ost
      podarovatelný - [' podarovat', '+elný'] po|dar|ovat|elný
        podarovatelně - [' podarovateln', '-ý', '+ě'] po|dar|ovat|eln|ě
        podarovatelnost - [' podarovateln', '-ý', '+ost'] po|dar|ovat|eln|ost
      podarovávat - [' podarov', '+áv', ' at'] po|dar|ov|áv|at                        #todo: otázka je, zda tu nemá být po|dar|ov|áv|a!t
        podarovávací - [' podarováva', '-t', '+cí'] po|dar|ov|áv|a|cí
        podarovávající - [' podarováva', '-t', '+jící'] po|dar|ov|áv|a|jící
        podarovávání - [' podarováv', '-at', '+ání'] po|dar|ov|áv|ání
        podarovávaný - [' podarováva', '-t', '+ný'] po|dar|ov|áv|a|ný
          podarovávaně - [' podarovávan', '-ý', '+ě'] po|dar|ov|áv|a|n|ě
          podarovávanost - [' podarovávan', '-ý', '+ost'] po|dar|ov|áv|a|n|ost
        podarovávatelný - [' podarovávat', '+elný'] po|dar|ov|áv|at|elný
          podarovávatelně - [' podarovávateln', '-ý', '+ě'] po|dar|ov|áv|at|eln|ě
          podarovávatelnost - [' podarovávateln', '-ý', '+ost'] po|dar|ov|áv|at|eln|ost
      podarovavší - [' podarova', '-t', '+vší'] po|dar|ova|vší
  dárek - [' d', '-a', '+á', ' r', '+ek'] d|á|r|ek                                                       #todo: třeba tady se velice spolehlivě rozbije na změně písmene v kořeni. proto je tam to d|á|r
    dáreček - [' dáre', '+če', ' k'] d|á|r|e|če|k
    dárkový - [' dár', '-e', ' k', '+ový'] d|á|r|k|ový
      dárkově - [' dárkov', '-ý', '+ě'] d|á|r|k|ov|ě
      dárkovost - [' dárkov', '-ý', '+ost'] d|á|r|k|ov|ost
    superdárek - ['+super', ' dárek'] super|d|á|r|ek
    radiodárek - ['+radio', ' dárek'] radio|d|á|r|ek
"""
