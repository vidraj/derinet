#!/usr/bin/env python3

import sys
import glob
import re

for filename in glob.glob("candi*.txt"):
    print("Processing "+filename)
    fh = open(filename)
    for line in fh:
        line = re.sub('^\s+',"",line)
        columns = line.split("\t")
#        print(columns[0])
        matchObj = re.search(r'Z: (\w+)',line)
        if matchObj and matchObj.groups:
            zz_lemma = matchObj.group(1)
            if not zz_lemma[:2].lower() == columns[0][:2].lower():
                print(filename+" Different beginnings: "+columns[0]+" Z: "+zz_lemma)
 
