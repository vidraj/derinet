#!/usr/bin/env python3

# This script loads new manual annotations from the following places
#
# (a) childless compounds
# ../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds
#
# (b) compounds and their derived children (possibly more levels)
# ../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters
#
# (c) adjectives derived by -sky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_sky_bez_kompozit.txt
#
# (d) adjectives derived by -cky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_cky_bez_kompozit.txt
#
# (e) adjectives derived by -ovy suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_ovy_bez_kompozit.txt
#
# (f) other adjectives derived by -ovy and -sky
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/kandidati_ze_sirotku.txt
#
# (g) nouns derived from verbs by -tel
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-E-final.txt
#
# (h) adverbs derived by -avane
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-E-final.txt
#
# (i) adverbs derived by -avatelne
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-E-final.txt

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
    

# ---------------- part (a) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds'
fh = open(filename)
for shortlemma in [line.rstrip('\n') for line in fh]:
    try:
        node_ids = derinet.get_ids(shortlemma)
        mark_as_compound(node_ids[0])
    except:
        print("Error: Lemma "+shortlemma+" not found, comes from "+filename)

# ---------------- part (b) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters'
fh = open(filename)
for line in fh:
    
    tokens = line.rstrip('\n').split(' ')

    print(repr(tokens))
    
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
            last_token = token
        
derinet.save('derinet-1-5.tsv')
