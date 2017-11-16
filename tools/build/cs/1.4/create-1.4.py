#!/usr/bin/env python3

import sys
import re
sys.path.append('../../../data-api/derinet-python/')
from derinet_api import DeriNet

derinet = DeriNet('derinet-1-3.tsv')

def homoindex_from_long_lemma(long_lemma):
    if "-" in long_lemma:
        m = re.search("^[^`_-]+-(\d+)", long_lemma)
        return m.group(1)
    else:
        return ""

def long_to_short(long_lemma):
    return re.sub(r"[\-_`].+",'',long_lemma)

def choose_lexeme(long_lemma, pos):

#    print("Searching for lexeme\t"+long_lemma)
    
    short_lemma = long_to_short(long_lemma)
    candidates = derinet.search_lexemes(short_lemma,pos=pos)

    if len(candidates) == 0:
        print("XXX: nenalezen zadny lexem\t"+long_lemma)
        return None
    
    elif len(candidates) == 1:
#        print("XXX: nalezen prave jeden lexem\t"+long_lemma)
        return candidates[0]
    
    else:
        given_homoindex = homoindex_from_long_lemma(long_lemma)
        for candidate in candidates:
            candidate_long_lemma = candidate[2]
            candidate_homoindex = homoindex_from_long_lemma(candidate_long_lemma)
            if candidate_homoindex == given_homoindex:
#                print("XXX: nalezeno vic kandidatu, vybran jeden\t"+long_lemma+" -> "+candidate_long_lemma)
                return candidate

        print("XXX: nalezeno vic kandidatu, ale zadny nesedi cislickem\t%s\t[%s]" % (long_lemma, ", ".join([c[2] for c in candidates])))
        return None
    
with open('final_sorted') as f:
    for line in f.readlines():
        target_id,target_short_lemma,target_long_lemma,pos,\
            source_id,source_long_lemma =  line.strip().split()

        best_source_lexeme = choose_lexeme(source_long_lemma, "V")
        best_target_lexeme = choose_lexeme(target_long_lemma, pos)

        if best_source_lexeme and best_target_lexeme:
            print("adding edge "+best_source_lexeme[2]+" -> "+best_target_lexeme[2] )
            source_id = derinet.get_id(best_source_lexeme[0], pos=best_source_lexeme[1], morph=best_source_lexeme[2])
            target_id = derinet.get_id(best_target_lexeme[0], pos=best_target_lexeme[1], morph=best_target_lexeme[2])
            print ("IDs: "+str(source_id)+" -> "+str(target_id))

#            print("orig_parent_id: "+best_target_lexeme[4])

            old_source_lexeme = derinet.get_parent_by_id(target_id)
            
            if old_source_lexeme:
                print("Old source lemma: "+old_source_lexeme[1])
                print("New source lemma: "+best_source_lexeme[0])
                if old_source_lexeme[1] == best_source_lexeme[0]:
                    print("Warning: same parent as before:\t"+best_source_lexeme[2]+" -> "+best_target_lexeme[2])
                else:
                    print("Warning: parent lemma changed:\t NEWPARENT: "+best_source_lexeme[2]+" -> "+best_target_lexeme[2]+ "  OLD: "+old_source_lexeme[2])
            
            derinet.add_edge_by_ids(target_id,source_id,force=True)
        

derinet.save('derinet-1-4.tsv')
