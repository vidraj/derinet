#!/usr/bin/env python3

import sys
import re

last3lines = ['\t'*6,'\t'*6,'\t'*6]

last3trailing_morphs = ['','','']


for line in sys.stdin:
    last3lines = [last3lines[1],last3lines[2],line]

    trailing_morph = re.sub(r'.+-', '', line.rstrip().split('\t')[2])
    last3trailing_morphs = [last3trailing_morphs[1],last3trailing_morphs[2], trailing_morph]

    if last3trailing_morphs[0] == last3trailing_morphs[2] and last3trailing_morphs[0][0] ==  last3trailing_morphs[1][0] and  last3trailing_morphs[0] != last3trailing_morphs[1]:
        print(''.join(last3lines))
    
    

