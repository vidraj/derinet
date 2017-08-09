#!/usr/bin/env python3

import sys
sys.path.append('../../../../../tools/data-api/derinet-python/')

from derinet_api import DeriNet
import re

derinet = DeriNet('../../../../releases/cs/derinet-1-4.tsv')


#rules = [   { "target": r'\1', "source": r'(\w+)ský'}  ]


rules = [
    { "source_suffix": 'ce', "target_suffix": 'cký'}, # Babice, pozor basnice 
    { "source_suffix": 'c', "target_suffix": 'cký'}, # běžecký
    { "source_suffix": 'k', "target_suffix": 'cký'}, # bonzácký
    { "source_suffix": '', "target_suffix": 'ický'}, # typicky
    { "source_suffix": 'ismus', "target_suffix": 'ický'}, # anachronicky
    { "source_suffix": 'izmus', "target_suffix": 'ický'}, # anachronicky
    { "source_suffix": 'ismus', "target_suffix": 'istický'}, # ekologisticky
    { "source_suffix": 'izmus', "target_suffix": 'istický'}, # ekologisticky    
    { "source_suffix": 'ida', "target_suffix": 'ický'}, # bronchiticky
    { "source_suffix": '', "target_suffix": 'nický'}, # drůbežnický        
    { "source_suffix": 'kum', "target_suffix": 'cký'}, # etnický
    { "source_suffix": 'us', "target_suffix": 'ický'}, # falický
    { "source_suffix": 'os', "target_suffix": 'ický'}, # kosmický        
    { "source_suffix": 'vce', "target_suffix": 'vecký'}, # gánovecký           
    { "source_suffix": 'ýza', "target_suffix": 'ytický'}, # hemolytick7
    { "source_suffix": 'archie', "target_suffix": 'rachický'}, # hemolyticky
    { "source_suffix": 'ie', "target_suffix": 'ický'}, # psychologický
    { "source_suffix": 'ium', "target_suffix": 'ický'}, # kamrický
    { "source_suffix": 'cky', "target_suffix": 'ický'}, # kentucký
    { "source_suffix": 'a', "target_suffix": 'ecký'}, # lhotecký
    { "source_suffix": 'a', "target_suffix": 'atický'}, # prizmatický
    { "source_suffix": 'ca', "target_suffix": 'cký'}, # kremnický        
    { "source_suffix": 'ko', "target_suffix": 'cký'}, # marocký
    { "source_suffix": 'ky', "target_suffix": 'cký'}, # nepomucký?
    { "source_suffix": 'ec', "target_suffix": 'ecký'}, # písmolitelcký
    { "source_suffix": 'ie', "target_suffix": 'ický'}, # ekonomický        

    { "source_suffix": 'sko', "target_suffix": 'ecký'}, # hlinecký
    { "source_suffix": 'k', "target_suffix": 'cký'}, # innsbrucký, měšťácký
    { "source_suffix": 'g', "target_suffix": 'cký'}, # innsbrucký
    { "source_suffix": 'd', "target_suffix": 'cký'}, # peptický          

    { "source_suffix": 'óza', "target_suffix": 'otický'}, # nekrotický
    { "source_suffix": 'áza', "target_suffix": 'atický'}, # nekrotický    
    
    { "source_suffix": 'um', "target_suffix": 'ový'}, # branovy
    { "source_suffix": 't', "target_suffix": 'ťový'}, # celistovy
    { "source_suffix": 'a', "target_suffix": 'ový'}, # guerilovy, nanosekundovy
    { "source_suffix": 'us', "target_suffix": 'ový'}, # meniskovy
    { "source_suffix": 'í', "target_suffix": 'ový'}, # narecovy    
    
]

def report(source_lemma,target_lemma,message):
    print(source_lemma+"\t"+target_lemma+"\t"+message)


for lexeme in derinet._data:
    if not lexeme.parent_id and not lexeme.lemma[0].isupper():
        if re.search(r'cký$', lexeme.lemma):

            success = 0
            for rule in rules:
                
                rule_description = "CHANGE: "+ (rule["source_suffix"] if rule["source_suffix"] else "0") +" --> "+rule["target_suffix"]

                regexp_source = r"\1"+rule["source_suffix"]
                regexp_target = r"(\w+)"+rule["target_suffix"]
                
                parent_candidate = re.sub(regexp_target,regexp_source,lexeme.lemma)

                if parent_candidate != lexeme.lemma:
                 
                    candidate_nodes = derinet.search_lexemes(parent_candidate,pos="N")
                    
                    if len(candidate_nodes)==1:
                        report(lexeme.lemma,parent_candidate,rule_description)
                        success=1
                        break
                        
                    else:
                        parent_candidate = parent_candidate[0].upper() + parent_candidate[1:]
                        candidate_nodes = derinet.search_lexemes(parent_candidate,pos="N")
                        if len(candidate_nodes)==1:
                            report(lexeme.lemma, parent_candidate, rule_description)
                            success=1
                            break

            if not success:
                report(lexeme.lemma,'',"UNRESOLVED")


