#!/usr/bin/env python3

from derinet_api import DeriNet
import sys
import re

derinet = DeriNet('derinet-1-4.tsv')

def depth(lexeme):

    if not lexeme.children:
        return 0
    else:
        max_depth = max ([depth(child_lexeme) for child_lexeme in lexeme.children])
        return max_depth+1
    

for lexeme in derinet._data:
    ma_rodice="BEZ_RODICE"
    if lexeme.parent_id:
        ma_rodice="S_RODICEM"

    prvni_pismeno="MALE"
    if lexeme.lemma[0].isupper():
        prvni_pismeno="VELKE"

        
        
    print(lexeme.lemma+"\t" \
          + ma_rodice+"\t" \
          +prvni_pismeno\
          +"\tpos="+lexeme.pos\
          +"\tdelka="+str(len(lexeme.lemma)).rjust(2,"0")
          +"\thloubka="+str(depth(lexeme))
    )
