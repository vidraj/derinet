from DerinetTreeBuilder import Node,DerinetTreeBuilder
import difflib
import editdistance


#sometimes we can use children for better segmentation of their parrent.
#let's build a tree of words, and whenever we find a new segment of a node, we use this information also for segmentation of its children and parrent.



class Segmenter:
    #gets a loaded tree (Node) and segments it.
    def __init__(self,root_node):
        self._tree=root_node
        self._segment(self._tree)
        self._word2node={}
        self._create_word2node_mapping(self._tree)


    def _create_word2node_mapping(self, node):
        self._word2node[node.word.lower()]=node
        for ch in node.children:
            self._create_word2node_mapping(ch)

    def segment_word(self,word):
        node=self._word2node.get(word.lower())
        if(node!=None):
            return(node)
        else:
            return None

    #purely translate segments from one word to another. Useful e.g. in connection with known roots or classifiers.
    @staticmethod
    def _translate_segments(parrent,child,parrent_segments_with_ids):
        diff=Segmenter._compute_diff(parrent.lower(),child.lower())
        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=[] #a|bc => {1}
        parrent_segments_with_ids=sorted(parrent_segments_with_ids, key=lambda x:x[0]) #(SEGMENT_POSITION, SEGMENT_ID)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments_with_ids)!=0 and parrent_segments_with_ids[0][0]<=parrent_i):
                    child_segments.append((parrent_segments_with_ids[0][0]+added_chars-removed_chars, parrent_segments_with_ids[0][1]))
                    del(parrent_segments_with_ids[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_i+=diff_len
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments_with_ids)!=0 and parrent_segments_with_ids[0][0]<=parrent_i):
                    del(parrent_segments_with_ids[0])
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments




    @staticmethod
    def _compute_diff(a,b): #"ammianus","ammianův"
        differ=difflib.Differ();
        dif=list(differ.compare(a,b)) #['  a', '  m', '  m', '  i', '  a', '  n', '- u', '- s', '+ ů', '+ v']
        #let's clean it up a little.
        dif2=[dif[0]]
        for x in dif[1:]:
            if(x[0]==dif2[-1][0]):
                dif2[-1]+=x[1:]
            else:
                dif2.append(x)
        dif3=[]
        for x in dif2:
            dif3.append(x[0]+x[1:].replace(" ",""))
        i=0
        maxi=len(dif3)-1
        while(i<maxi):
            if(dif3[i][0]=="+" and dif3[i+1][0]=="-"): #swap them
                dif3[i],dif3[i+1]=dif3[i+1],dif3[i]
                i+=1
            i+=1
        return dif3

    #do the segmenation of the whole tree.
    @classmethod
    def _segment(cls,node):
        #do the segmentation:
        queue_items=set([node])
        queue_list=[node]

        PROPAGATE_TO_PARRENT=True
        ADD_PARRENT_TO_QUEUE=True
        number_of_iterations=1 #makes only sense if we propagate to parrent and do not add parrent to queue

        #this operates only on parrent-child relations and is sometimes unable to transfer knowledge among relatives further appart.
        #e.g.:
        #  roz|no|ž|i|t
        #    roz|no|ž|ení
        #    roz|no|ž|en|ý

        for x in range(number_of_iterations):
            if(not node in queue_items):
                queue_items.add(node)
                queue_list.append(node)
            while(len(queue_list)!=0):
                me=queue_list[0]
                del(queue_list[0])
                queue_items.remove(me)
                me_old_segments=me.segments
                me_new_segments=set().union(me_old_segments)
                nodes_for_processing=me.children
                if(me.parrent!=None and PROPAGATE_TO_PARRENT ):
                    nodes_for_processing=nodes_for_processing+[me.parrent]
                for it in nodes_for_processing:
                    it_new_segments=cls._detect_and_propagate_segments(me.word.lower(),it.word.lower(),me_new_segments)
                    old_segments=it.segments
                    it_new_segments=it_new_segments.union(it.segments)
                    if(it_new_segments!=it.segments):
                        it.segments=it_new_segments
                        if(not it in queue_items and (it!=me.parrent or ADD_PARRENT_TO_QUEUE)):
                            queue_items.add(it)
                            queue_list.append(it)
                    #if("o|ž|k" in str(it)): #a trick for debugging.
                    #    print(me)
                    #    print(it)
                    #    print(old_segments)
                    #    raise Exception()
        return node



    #we know parrent, child and segmentation of parrent. We want to transfer the knowledge of segments to children and
    #also create some new segments on the basis of the differences.
    @staticmethod
    def _detect_and_propagate_segments(parrent, child, parrent_segments):
        diff=Segmenter._compute_diff(parrent.lower(),child.lower())

        #if in some place there is only +, put segment lines before and after, and shift all the following parrent segments.
        #if in some place there is only -, put segment line on that position, remove all the parrent segments inside the removed interval, and shift all the following parrent segments.
        #if in some place there is -+, then changes outside of the root are easy. Remove all parrent segments inside the interval, put one segment at the beginning and one at the end, and shift all the remaining segments
        #   the problem is, that we add segments also into the root, when it changes.
        #as post processing remove beginning and end of segment at beginning and end of word
        #this method cannot share things between neighbor lemmas


        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=set() #a|bc => {1}
        parrent_segments=sorted(parrent_segments)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    child_segments.add(parrent_segments[0]+added_chars-removed_chars)
                    del(parrent_segments[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_segments.add(child_i)
                child_segments.add(child_i+diff_len)
                child_i+=diff_len
            #elif(diff_type=="-" and next_diff_type=="+"): #not necessary!!
            #    next_diff_len=len(diff[i+1])-1
            #    parrent_i+=diff_len
            #    child_segments.add(child_i)
            #    child_segments.add(child_i+next_diff_len)
            #    child_i+=next_diff_len
            #    added_chars+=next_diff_len
            #    removed_chars+=diff_len
            #    while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
            #        del(parrent_segments[0])
            #    i+=1 #we processed both of them.
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    del(parrent_segments[0])
                child_segments.add(child_i)
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments


#we replace e.g. é->e before computing the difference between words, which means that we ignore this type of changes.
#This trick boosts the number of 100% accuratelly segmented words from 70/500 to 86/500 on the manually segmented dataset,
#but it changes segmentation of half of the words, which is worrying and needs to be examined.

class ReplacingSegmenter(Segmenter):
    def __init__(self,root_node):
        super().__init__(root_node)

    #we know parrent, child and segmentation of parrent. We want to transfer the knowledge of segments to children and
    #also create some new segments on the basis of the differences.

    @staticmethod
    def _detect_and_propagate_segments(parrent, child, parrent_segments):

        def preprocess(w):
            w=w.lower().strip()
            for x,y in ["áa","ée","ěe","íi","ýy","óo","úu","ůu","čc","ďd","ňn","řr","šs","ťt","žz"]: #hubit->zhouba, sníh->sněžný require a more advanced approach
                w=w.replace(x,y)
            return w

        diff=Segmenter._compute_diff(preprocess(parrent),preprocess(child))

        #if in some place there is only +, put segment lines before and after, and shift all the following parrent segments.
        #if in some place there is only -, put segment line on that position, remove all the parrent segments inside the removed interval, and shift all the following parrent segments.
        #if in some place there is -+, then changes outside of the root are easy. Remove all parrent segments inside the interval, put one segment at the beginning and one at the end, and shift all the remaining segments
        #   the problem is, that we add segments also into the root, when it changes.
        #as post processing remove beginning and end of segment at beginning and end of word
        #this method cannot share things between neighbor lemmas

        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=set() #a|bc => {1}
        parrent_segments=sorted(parrent_segments)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    child_segments.add(parrent_segments[0]+added_chars-removed_chars)
                    del(parrent_segments[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_segments.add(child_i)
                child_segments.add(child_i+diff_len)
                child_i+=diff_len
            #elif(diff_type=="-" and next_diff_type=="+"): #not necessary!!
            #    next_diff_len=len(diff[i+1])-1
            #    parrent_i+=diff_len
            #    child_segments.add(child_i)
            #    child_segments.add(child_i+next_diff_len)
            #    child_i+=next_diff_len
            #    added_chars+=next_diff_len
            #    removed_chars+=diff_len
            #    while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
            #        del(parrent_segments[0])
            #    i+=1 #we processed both of them.
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    del(parrent_segments[0])
                child_segments.add(child_i)
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments



class ReplacingSegmenter2(Segmenter):
    def __init__(self,root_node):
        super().__init__(root_node)

    #we know parrent, child and segmentation of parrent. We want to transfer the knowledge of segments to children and
    #also create some new segments on the basis of the differences.

    @staticmethod
    def _detect_and_propagate_segments(parrent, child, parrent_segments):
        def preprocess(w):
            w=w.lower().strip()
            for x,y in ["áa","ée","ěe","íi","ýy","óo","úu","ůu","čc","ďd","ňn","řr","šs","ťt","žz","dt","yi","zs","cs"]: #hubit->zhouba, sníh->sněžný require a more advanced approach #hž->hz
                w=w.replace(x,y)
            return w

        diff=Segmenter._compute_diff(preprocess(parrent),preprocess(child))
        #ignore ou<->u
        #do not split

        #if in some place there is only +, put segment lines before and after, and shift all the following parrent segments.
        #if in some place there is only -, put segment line on that position, remove all the parrent segments inside the removed interval, and shift all the following parrent segments.
        #if in some place there is -+, then changes outside of the root are easy. Remove all parrent segments inside the interval, put one segment at the beginning and one at the end, and shift all the remaining segments
        #   the problem is, that we add segments also into the root, when it changes.
        #as post processing remove beginning and end of segment at beginning and end of word
        #this method cannot share things between neighbor lemmas

        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=set() #a|bc => {1}
        parrent_segments=sorted(parrent_segments)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    child_segments.add(parrent_segments[0]+added_chars-removed_chars)
                    del(parrent_segments[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_segments.add(child_i)
                child_segments.add(child_i+diff_len)
                child_i+=diff_len
            #elif(diff_type=="-" and next_diff_type=="+"): #not necessary!!
            #    next_diff_len=len(diff[i+1])-1
            #    parrent_i+=diff_len
            #    child_segments.add(child_i)
            #    child_segments.add(child_i+next_diff_len)
            #    child_i+=next_diff_len
            #    added_chars+=next_diff_len
            #    removed_chars+=diff_len
            #    while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
            #        del(parrent_segments[0])
            #    i+=1 #we processed both of them.
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    del(parrent_segments[0])
                child_segments.add(child_i)
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments













class ReplacingSegmenter3(Segmenter):
    def __init__(self,root_node):
        super().__init__(root_node)

    #we know parrent, child and segmentation of parrent. We want to transfer the knowledge of segments to children and
    #also create some new segments on the basis of the differences.

    @staticmethod
    def _detect_and_propagate_segments(parrent, child, parrent_segments):

        def preprocess(w):
            w=w.lower().strip()
            for x,y in ["áa","ée","ěe","íi","ýy","óo","úu","ůu","čc","ďd","ňn","řr","šs","ťt","žz"]: #hubit->zhouba, sníh->sněžný require a more advanced approach
                w=w.replace(x,y)
            return w

        diff=Segmenter._compute_diff(preprocess(parrent),preprocess(child))

        #if in some place there is only +, put segment lines before and after, and shift all the following parrent segments.
        #if in some place there is only -, put segment line on that position, remove all the parrent segments inside the removed interval, and shift all the following parrent segments.
        #if in some place there is -+, then changes outside of the root are easy. Remove all parrent segments inside the interval, put one segment at the beginning and one at the end, and shift all the remaining segments
        #   the problem is, that we add segments also into the root, when it changes.
        #as post processing remove beginning and end of segment at beginning and end of word
        #this method cannot share things between neighbor lemmas

        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=set() #a|bc => {1}
        parrent_segments=sorted(parrent_segments)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    child_segments.add(parrent_segments[0]+added_chars-removed_chars)
                    del(parrent_segments[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_segments.add(child_i)
                child_segments.add(child_i+diff_len)
                child_i+=diff_len
            #TODO: DETECT REPLACEMENTS of e.g. ý->ej, and skip them. But be careful,
            #      vymena->vejmena = vej|mena, but dlouhy -> dlouhej = dlouh|ej

            #elif(diff_type=="-" and next_diff_type=="+"): #not necessary!!
            #    next_diff_len=len(diff[i+1])-1
            #    parrent_i+=diff_len
            #    child_segments.add(child_i)
            #    child_segments.add(child_i+next_diff_len)
            #    child_i+=next_diff_len
            #    added_chars+=next_diff_len
            #    removed_chars+=diff_len
            #    while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
            #        del(parrent_segments[0])
            #    i+=1 #we processed both of them.
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    del(parrent_segments[0])
                child_segments.add(child_i)
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments













#TODO: root aware segmenter!




class PostprocessingSegmenter(Segmenter):
    def __init__(self,root_node):
        super().__init__(root_node)

    @staticmethod
    def _detect_and_propagate_segments(parrent, child, parrent_segments):
        diff=Segmenter._compute_diff(parrent.lower(),child.lower())
        #postprocess diff
        i=1
        while i<len(diff)-2:
            #pure replacement inside the word
            if(diff[i][0]=="-" and diff[i+1][0]=="+" and i!=0 and i+1!=len(diff)-2):
                if(len(diff[i])==2 and len(diff[i+1])==2): #replacing one letter with one letter
                    a=diff[i][1]
                    b=diff[i+1][1]
                    for equivalence in ["áa","ée","ěe","íi","ýy","óo","úu","ůu","čc","ďd","ňn","řr","šs","ťt","žz"]:
                        if(a in equivalence and b in equivalence):
                            #print(diff) #print differences before and after postprocessing
                            diff[i-1]=diff[i-1]+a+diff[i+2][1:]
                            del(diff[i+2])
                            del(diff[i+1])
                            del(diff[i])
                            i-=1
                            #print(diff)  #print differences before and after postprocessing
                            break
            i+=1


        i=0
        added_chars=0
        removed_chars=0
        child_i=0
        parrent_i=0
        child_segments=set() #a|bc => {1}
        parrent_segments=sorted(parrent_segments)
        maxi=len(diff)
        while i<maxi:
            diff_type=diff[i][0]
            diff_len=len(diff[i])-1
            next_diff_type=None
            if(i+1<maxi):
                next_diff_type=diff[i+1][0]
            if(diff_type==" "):
                child_i+=diff_len
                parrent_i+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    child_segments.add(parrent_segments[0]+added_chars-removed_chars)
                    del(parrent_segments[0])
            elif(diff_type=="+"):
                added_chars+=diff_len
                child_segments.add(child_i)
                child_segments.add(child_i+diff_len)
                child_i+=diff_len
            elif(diff_type=="-"):
                parrent_i+=diff_len
                removed_chars+=diff_len
                while(len(parrent_segments)!=0 and parrent_segments[0]<=parrent_i):
                    del(parrent_segments[0])
                child_segments.add(child_i)
            i+=1
        if(0 in child_segments):
            child_segments.remove(0)
        if(len(child) in child_segments):
            child_segments.remove(len(child))
        return child_segments

