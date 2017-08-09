#!/usr/bin/env python3

from derinet_api import DeriNet
import sys
import re

derinet = DeriNet('derinet-1-4.tsv')


#rules = [   { "target": r'\1', "source": r'(\w+)ský'}  ]


rules = [
    { "source_suffix": '', "target_suffix": 'ský'},
    { "source_suffix": '', "target_suffix": 'ovský'},
    { "source_suffix": '', "target_suffix": 'onovský'}, # Hamilton
    { "source_suffix": 'ek', "target_suffix": 'vský'}, # Jirásek, Jiránek
    { "source_suffix": 's', "target_suffix": 'siánský'}, # Keynes    
    { "source_suffix": 'y', "target_suffix": 'ský'},
    { "source_suffix": 'sko', "target_suffix": 'ský'},
    { "source_suffix": 'ie', "target_suffix": 'ský'},
    { "source_suffix": 'e', "target_suffix": 'ský'},
    { "source_suffix": 'rk', "target_suffix": 'rský'},
    { "source_suffix": 'rg', "target_suffix": 'rský'},
    { "source_suffix": 'ie', "target_suffix": 'ijský'},
    { "source_suffix": 'ie', "target_suffix": 'ský'}, # syrský
    { "source_suffix": 'h', "target_suffix": 'žský'}, # utažský
    { "source_suffix": 'ch', "target_suffix": 'šský'}, # vojtěšský    
    { "source_suffix": 'a', "target_suffix": 'ský'}, # Bublava
    { "source_suffix": 'a', "target_suffix": 'ovský'}, # Štursa
    { "source_suffix": 'í', "target_suffix": 'ský'}, # Záchlumí, Záporoží
    { "source_suffix": 'go', "target_suffix": 'žský'}, # Záchlumí
    { "source_suffix": 'y', "target_suffix": 'ský'}, # Syrakusy
    { "source_suffix": 'rna', "target_suffix": 'renský'}, # sušárna
    { "source_suffix": 'ce', "target_suffix": 'covský'}, # sušárna
    { "source_suffix": 'es', "target_suffix": 'ovský'}, # Archimédes, Aristoteles
    { "source_suffix": 'a', "target_suffix": 'ářský'}, # kšiltovka
    { "source_suffix": '', "target_suffix": 'ářský'}, # knedlíkářský
    { "source_suffix": 'čka', "target_suffix": 'čkářský'}, # přesmyčkářský
    { "source_suffix": 'ček', "target_suffix": 'čkářský'}, # domečkářský    

    
#    { "source_suffix": 'ka', "target_suffix": 'ský'}    
]

def report(source_lemma,target_lemma,message):
    print(source_lemma+"\t"+target_lemma+"\t"+message)


for lexeme in derinet._data:
    if not lexeme.parent_id and not lexeme.lemma[0].isupper():
        if re.search(r'ský$', lexeme.lemma):

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


