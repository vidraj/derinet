#!/usr/bin/env python3

import sys
import re

last3lines = ['\t'*6,'\t'*6,'\t'*6]

last3leading_morphs = ['','','']


for line in sys.stdin:
    last3lines = [last3lines[1],last3lines[2],line]

    leading_morph = re.sub(r'-.+', '', line.rstrip().split('\t')[2])
    last3leading_morphs = [last3leading_morphs[1],last3leading_morphs[2], leading_morph]

    if last3leading_morphs[0] == last3leading_morphs[2] and last3leading_morphs[0] != last3leading_morphs[1]:
        print(''.join(last3lines))
    
    

