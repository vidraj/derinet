#todo: persistence of my nodes and trees? Or do it in iterative manner? (one tree at a time)
class Node:
    def __init__(self, word_=None, parrent_=None, children_=[]):
        self.word=word_
        self.parrent=None
        self.children=[]
        self.segments=set()
        self.classifier_segments=None #segmentation from classifier - indices plus likelihoods
        self.classifier_segments_from_neighbors=None
        self.triplet_loss_root=None  #indices of likely root from triplet loss
        self.derinet_root=None
        self.derinet_segments=[] #all derinet segments including root


        if(parrent_!=None):
            self.add_parrent(parrent_)

        for x in children_:
            self.add_child(x)

    def add_child(self, child):
        self.children.append(child)
        child.parrent=self

    def add_parrent(self, parrent_):
        self.parrent=parrent_
        parrent_.children.append(self)

    def __repr__(self):
        out=""
        for i,x in enumerate(self.word):
            if(i in self.segments):
                out+="|"
            out+=x
        return out


    def print_tree(self, level=0):
        print(level*"  "+str(self))
        for ch in self.children:
            ch.print_tree(level+1)


    def return_tree(self, level=0, output_var=None):
        if(output_var is None):
            output_var=[""]
        output_var[0]+=(level*"  "+str(self))+"\n"
        for ch in self.children:
            ch.return_tree(level+1,output_var)
        return output_var[0]

    def print_tree2(self,parrent_node=None, level=0):
        diff=""
        if(parrent_node is not None):
            diff=Segmenter._compute_diff(parrent_node.word.lower(), self.word.lower())
        print(level*"  ",self.word,"-",diff,self," ",sorted(self.segments))
        for ch in self.children:
            ch.print_tree2(self,level+1)

    def return_tree_segmentations(self, output_list=None):
        if(output_list is None):
            output_list=[]
        output_list.append((self.word, self.segments))
        for ch in self.children:
            ch.return_tree_segmentation(output_list)
        return output_list

    def get_tree_words(self, output_list=None):
        if(output_list is None):
            output_list=[]
        output_list.append(self.word)
        for ch in self.children:
            ch.get_tree_words(output_list)
        return output_list

    def subtree_map(self, function): #standard map() for trees.
        function(self)
        for ch in self.children:
            ch.subtree_map(function)









class DerinetTreeBuilder:
    def __init__(self, lexicon):
        self._lexicon=lexicon
        self._word2root={}
        self._create_word2root_mapping()

    #creates my tree from the derinet tree, for given root.
    @staticmethod
    def build_segmentation_tree(current_derinet_node, parrent_node=None, parrent_segments=None):
        if(parrent_segments is None):
            parrent_segments=set()
        current_mynode=Node(current_derinet_node.lemma, parrent_node)

        for segment in current_derinet_node.segmentation:
            current_mynode.derinet_segments.append((segment["Start"],segment["End"],segment))
            if(segment["Type"]=="Root"):
                if(current_mynode.derinet_root is not None):
                    print("Derinet has 2 roots for word "+current_derinet_node.word)
                current_mynode.derinet_root=(segment["Start"],segment["End"],segment)


        for child in current_derinet_node.children:
            child_segments=set()
            childnode=DerinetTreeBuilder.build_segmentation_tree(child, current_mynode, child_segments)
            childnode.segments=child_segments
        return current_mynode


    def _create_word2root_mapping(self, node=None, root=None):
        if(root==None): #the first call.
            for tree_root in self._lexicon.iter_trees():
                self._create_word2root_mapping(tree_root, root=tree_root)
        else:
            lemma=node.lemma.lower()
            ptr=self._word2root.get(lemma)
            if(ptr is None):
                self._word2root[lemma]=[root]
            else:
                ptr.append(root)

            for ch in node.children:
                self._create_word2root_mapping(ch,root)


    def find_derinettree_root(self, word):
        results=self._word2root.get(word.lower())
        if(results!=None):
            return results[0]
        else:
            return None

