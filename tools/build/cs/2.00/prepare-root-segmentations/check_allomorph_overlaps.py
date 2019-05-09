#!/usr/bin/env python3

import sys

allomorphsets = []

for line in sys.stdin:
    columns = line.rstrip().split('\t')
    if columns[0] == "STARTOFCLUSTER":
        allomorphsets.append(set(columns[1].split(" ")))


for i1 in range(len(allomorphsets)):
   for i2 in range(i1+1,len(allomorphsets)):
       intersection = allomorphsets[i1].intersection(allomorphsets[i2])
       if len(intersection) > 1:
           print(str(len(intersection))+"\t allomorph set A: "+(" ".join(allomorphsets[i1]))+"\t allomorph set B: "+(" ".join(allomorphsets[i2])))

    
