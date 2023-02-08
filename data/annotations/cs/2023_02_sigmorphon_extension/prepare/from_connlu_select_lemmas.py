#!/usr/bin/env python3

import sys

fd = open(sys.argv[1])

listed = {}

for line in fd:
    listed[line.rstrip().lower()] = 1

sys.stderr.write("Loaded "+str(len(listed.keys()))+" items from "+sys.argv[1]+"\n")
    
for line in sys.stdin:
    columns = line.rstrip().split('\t')
#    if len(columns) > 3:
#        print(columns[2])
    if len(columns) > 3 and columns[2].lower() in listed:
        print(line.rstrip().lower())
        del listed[columns[2].lower()] # at most one example per listed lemma

        
