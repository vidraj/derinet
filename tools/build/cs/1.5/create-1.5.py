#!/usr/bin/env python3

# This script loads new manual annotations from the following places
#
# (a) adjectives derived by -sky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_sky_bez_kompozit.txt
#
# (b) adjectives derived by -cky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_cky_bez_kompozit.txt
#
# (c) adjectives derived by -ovy suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_ovy_bez_kompozit.txt
#
# (d) other adjectives derived by -ovy and -sky
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/kandidati_ze_sirotku.txt
#
# (e) nouns derived from verbs by -tel
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-E-final.txt
#
# (f) adverbs derived by -avane
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-E-final.txt
#
# (g) adverbs derived by -avatelne
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-E-final.txt
#
# (h) childless compounds
# ../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds
#
# (i) compounds and their derived children (possibly more levels)
# ../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters
#



import sys
sys.path.append('../../../data-api/derinet-python/')

from derinet_api import DeriNet
from derinet_api import Node

import re

derinet = DeriNet('../../../../data/releases/cs/derinet-1-4.tsv')

def find_lexeme_by_lemma(lemma):
    print("Searching for "+lemma)
    candidates = derinet.search_lexemes(lemma)
    print("Pokracovani")
    if len(candidates) > 1:
        print("Warning: homonymous lemma "+lemma)
    return(candidates[0])

def mark_as_compound(node_id):
    old_node = derinet._data[node_id]
    newnode = Node(old_node[0],
                   old_node[1],
                   old_node[2],
                   old_node[3]+"C",
                   old_node[4],
                   old_node[5])
    derinet._data[node_id] = newnode
    

def find_id(lemma,pos):
    candidates=[]
    if pos==None:
        candidates=derinet.get_ids(lemma)
    else:
        candidates=derinet.get_ids(lemma,pos)
    if len(candidates)==0:
        print("Error:No node find for lemma="+lemma)
    elif len(candidates)>1:
        print("Error:Ambiguous lemma="+lemma)
    else:
        return candidates[0]

    
def create_derivation(filename,child_lemma,child_pos,parent_lemma,parent_pos):
#    print("Ladim3")
    try:
#        print("Ladim4")
        child_id = find_id(child_lemma,child_pos)
        parent_id = find_id(parent_lemma,parent_pos)
        derinet.add_edge_by_ids(child_id,parent_id)
        print("Derivation successfully added child="+child_lemma+" parent="+parent_lemma+"\t"+filename)
        
    except:
        print("Error: No edge added for child="+child_lemma+" and parent="+parent_lemma+" , either nonexistent or ambiguous")



# ---------------- part (a) and (c) -------------------
for filename in [
         "../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_sky_bez_kompozit.txt",
         "../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_ovy_bez_kompozit.txt"
        ]:

    fh = open(filename)

    for line in fh:
        columns = line.rstrip('\n').split('\t')
        child_lemma = columns[0]
        parent_lemma = columns[1]

        matchObj = re.search(r' [A-Z]: (\w+)',line) # manual correction
        if matchObj and matchObj.groups:
            parent_lemma = matchObj.group(1)

        if not parent_lemma=="UNRESOLVED" and not parent_lemma=="":
            create_derivation(filename, child_lemma, 'A', parent_lemma, None)


# ---------------- part (b) -------------------
filename = "../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_cky_bez_kompozit.txt"

fh = open(filename)

for line in []: ##########fh:
    if not re.search(r'^[@\?]',line):

        columns = line.lstrip('\t').rstrip('\n').split('\t')
        child_lemma = columns[0]
        parent_lemma = columns[1]

        matchObj = re.search(r' [A-Z]: (\w+)',line) # manual correction
        if matchObj and matchObj.groups:
            parent_lemma = matchObj.group(1)

        if not parent_lemma=="UNRESOLVED" and not parent_lemma=="":
            create_derivation(filename, child_lemma, 'A', parent_lemma, None)



        
# ---------------- part (h) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds'
fh = open(filename)
for shortlemma in []:############# [line.rstrip('\n') for line in fh]:
    try:
        node_ids = derinet.get_ids(shortlemma)
        mark_as_compound(node_ids[0])
    except:
        print("Error: Lemma "+shortlemma+" not found, comes from "+filename)

# ---------------- part (i) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters'
fh = open(filename)
for line in []:########3#fh:
    
    tokens = line.rstrip('\n').split(' ')

#    print(repr(tokens))
    
    node_ids = derinet.get_ids(tokens[0])
    mark_as_compound(node_ids[0])

    last_token = tokens[0]
    stack = []
    for index in range(1,len(tokens)):
        token = tokens[index]
        if token == "(":
            stack.append(last_token)
        elif token == ")":
            stack.pop()
        else:
            print("Child: "+token+"  Parent: "+stack[-1])
            create_derivation(filename,token,None,stack[-1],None)
            last_token = token



        
derinet.save('derinet-1-5.tsv')
