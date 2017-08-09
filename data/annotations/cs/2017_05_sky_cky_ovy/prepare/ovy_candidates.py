#!/usr/bin/env python3

from derinet_api import DeriNet
import sys
import re

derinet = DeriNet('derinet-1-4.tsv')


#rules = [   { "target": r'\1', "source": r'(\w+)ský'}  ]


rules = [
    { "source_suffix": '', "target_suffix": 'ový'}, # doletovy 
    { "source_suffix": 'ek', "target_suffix": 'kový'}, # bazenkovy
    { "source_suffix": 'něk', "target_suffix": 'ňkový'}, # doplnkovy
    { "source_suffix": 'eň', "target_suffix": 'ňový'}, # hrusnovy
    { "source_suffix": 'dě', "target_suffix": 'ďový'}, # hyzdovy
    { "source_suffix": 't', "target_suffix": 'ťový'}, # mastovy           
    { "source_suffix": 'ium', "target_suffix": 'iový'},
    { "source_suffix": 'dí', "target_suffix": 'ďový'}, # drozdovy
    { "source_suffix": 'y', "target_suffix": 'ový'}, # dupacky
    { "source_suffix": 'o', "target_suffix": 'ový'}, # banjovy
    { "source_suffix": 'e', "target_suffix": 'ový'}, # fazovy
    { "source_suffix": 'um', "target_suffix": 'ový'}, #
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
        if re.search(r'ový$', lexeme.lemma):

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


