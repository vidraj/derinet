#!/usr/bin/env python3

import sys

form2pos = {}

sentno = 0

for line in sys.stdin:


    
    columns = line.rstrip().split('\t')


    
    if len(columns) > 1:
        (number,form,lemma,pos) = columns[0:4]

        form = form.lower()

        if not form in form2pos:
            form2pos[form] = {}

        if len(form) > 1 and pos not in ['PUNCT','SYM','PROPN','AUX']:
            form2pos[form][pos] = 1


for form in form2pos:
    if len(form2pos[form])>1:
        print (form+'\t'+' '.join((sorted(list(form2pos[form])))))

        
