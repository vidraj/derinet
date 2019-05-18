#!/usr/bin/env python3

import sys

allomorphsets = []

shortlemmas = []
longlemmas = []

def set2string (allomorphset):
    return "{"+(",".join(allomorphset))+"}"


for line in sys.stdin:
    columns = line.rstrip().split('\t')
    if columns[0] == "STARTOFCLUSTER":
        allomorphsets.append(set(columns[1].split(" ")))

    if columns[0] == "ROOTNODE":
        longlemmas.append(columns[2])        
        shortlemmas.append(columns[3])

for i1 in range(len(allomorphsets)):
   for i2 in range(i1+1,len(allomorphsets)):
       intersection = allomorphsets[i1].intersection(allomorphsets[i2])
       if len(intersection) > 0:
           print(str(len(intersection))+"\t"+
              set2string(allomorphsets[i1].intersection(allomorphsets[i2])) + "\t" +
                 set2string(allomorphsets[i1]) + "\t" + set2string(allomorphsets[i2]) + "\t" +
                   longlemmas[i1] + "\t" + longlemmas[i2] + "\tSOLUTION:\tCOMMENT:")

#                 {"+(",".join(allomorphsets[i1]))+"\t allomorph set B: "+(" ".join(allomorphsets[i2])))

    
