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

import derinet_api

import re

derinet = derinet_api.DeriNet('./derinet-1-4.tsv')

def find_lexeme_by_lemma(lemma):
    print("Searching for "+lemma)
    candidates = derinet.search_lexemes(lemma)
    print("Pokracovani")
    if len(candidates) > 1:
        print("Warning: homonymous lemma "+lemma)
    return(candidates[0])

def mark_as_compound(node_id):
    old_node = derinet._data[node_id]
    new_pos = old_node.pos + "C"
    newnode = old_node._replace(pos=new_pos)
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
        derinet.add_edge_by_lexemes(child_lemma, parent_lemma, child_pos, parent_pos)
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

for line in fh:
    if not re.search(r'^[@\?]',line):

        columns = line.lstrip('\t').rstrip('\n').split('\t')
        child_lemma = columns[0]
        parent_lemma = columns[1]

        matchObj = re.search(r' [A-Z]: (\w+)',line) # manual correction
        if matchObj and matchObj.groups:
            parent_lemma = matchObj.group(1)

        if not parent_lemma=="UNRESOLVED" and not parent_lemma=="":
            create_derivation(filename, child_lemma, 'A', parent_lemma, None)

# ---------------- part (d) -------------------
            
filename = "../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/kandidati_ze_sirotku.txt"

fh = open(filename)

for line in fh:
    if re.search(r'^N ',line):
        line = re.sub(r'^N ','',line)
        columns = line.rstrip('\n').split('\t')
        child_lemma = columns[0]
        parent_lemma = columns[1]

        matchObj = re.search(r' [A-Z]: (\w+)',line) # manual correction
        if matchObj and matchObj.groups:
            parent_lemma = matchObj.group(1)

        if not parent_lemma=="UNRESOLVED" and not parent_lemma=="":
            create_derivation(filename, child_lemma, 'A', parent_lemma, None)



# ---------------- parts (e)+(f)+(g) -------------------

for shortfilename in [
        'AavanyDavane-C-final.txt',
        'AavatelnyDavatelne-C-final.txt',
        'VtNtel-C-final.txt',
        'AavanyDavane-E-final.txt',
        'AavatelnyDavatelne-E-final.txt',
        'VtNtel-E-final.txt'
        ]:

    filename = "../../../../data/annotations/cs/2017_08_tel_avane_avatelne/"+shortfilename

    fh = open(filename)

    for line in fh:
        if not re.search(r'^@',line):
            columns = line.rstrip('\n').split('\t')
            if len(columns)<2:
                print("KRATKE: "+line)
            child_lemma = columns[0]
            parent_lemma = columns[1]
            create_derivation(filename, child_lemma, None, parent_lemma, None)
        
# ---------------- part (h) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds'
fh = open(filename)
for shortlemma in [line.rstrip('\n') for line in fh]:
    try:
        node_ids = derinet.get_ids(shortlemma)
        mark_as_compound(node_ids[0])
    except:
        print("Error: Lemma "+shortlemma+" not found, comes from "+filename)

# ---------------- part (i) -------------------

filename = '../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters'
fh = open(filename)
for line in fh:
    
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
