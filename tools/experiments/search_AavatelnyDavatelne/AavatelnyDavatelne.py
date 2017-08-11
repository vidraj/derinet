#!/usr/bin/env python3

import sys

sys.path.append('../../data-api/derinet-python/')

from derinet_api import DeriNet

import re

derinet = DeriNet('../../../data/releases/cs/derinet-1-4.tsv')

with open('log.txt','w') as logfile:

    for child in derinet._data:

        if child.pos=='D' and re.search(r'ávatelně$', child.lemma):   #  POS ditete a pripona ditete
         
            parent_candidate_lemma = re.sub(r'ávatelně',r'ávatelný',child.lemma) # hadani rodicovskeho lemmatu zamenou pripony
            parent_candidate_nodes = derinet.search_lexemes(parent_candidate_lemma,pos='A') # dejme tomu, ze rodic ma byt sloveso

            logfile.write(child.lemma+'\t'+parent_candidate_lemma+'\t')

            current_parent = None

            if child.parent_id:
                current_parent = derinet.get_lexeme_by_id(child.parent_id)
            
            if not parent_candidate_nodes:
                if current_parent:
                    logfile.write('(A) CANDIDATE NONEXISTENT, CURRENT PARENT=\t'+current_parent.lemma+'\n')
                else:
                    logfile.write('(B) CANDIDATE NONEXISTENT, CURRENTLY PARENTLESS\n')

            else:
                
                for candidate in parent_candidate_nodes:
                  
                    if not current_parent:
                        logfile.write('(C) NO PARENT BEFORE\n')

                    elif current_parent[1] == candidate[0]:
                        logfile.write('(D) PARENT SAME AS BEFORE\n')

                    else:
                        logfile.write('(E) PARENT DIFFERENT, CURRENT PARENT=\t'+current_parent.lemma+'\n')
                        


