#!/usr/bin/env python3

import sys

allomorphsets = []

#shortlemmas = []
longlemmas = []

def set2string (allomorphset):
    return "{"+(",".join(allomorphset))+"}"


ignore_cluster = 0;

current_batch = 0;
batch_of_cluster = []

for line in sys.stdin:
    columns = line.rstrip().split('\t')

    current_batch = columns[0]
    columns.pop(0)
    
    if columns[0] == "STARTOFCLUSTER":
            if len(columns) == 1 or len(columns[1])<1:  # A WARNING SHOULD BE ISSUED HERE
                ignore_cluster = 1
            else:
                ignore_cluster = 0
                allomorphsets.append(set(columns[1].split(" ")))
                longlemmas.append("UNKNOWN")
                batch_of_cluster.append(current_batch)

    if columns[0] == "ROOTNODE" and not ignore_cluster:
        longlemmas[-1] = columns[2]
#        shortlemmas.append(columns[3])

sys.stderr.write("Celkem allomorfickych mnozin: "+str(len(allomorphsets)))
sys.stderr.write("Celkem lemmat korenu: "+str(len(longlemmas)))

for i1 in range(len(allomorphsets)):
   for i2 in range(i1+1,len(allomorphsets)):
#       print ("i1/i2 " + str(i1) + " " + str(i2))
       intersection = allomorphsets[i1].intersection(allomorphsets[i2])
       if len(intersection) > 0:
            if batch_of_cluster[i1] != "3" and batch_of_cluster[i2] == "3":
#           if  batch_of_cluster[i2] == 3:
               print(str(len(intersection))+"\t"+
                     set2string(allomorphsets[i1].intersection(allomorphsets[i2])) + "\t" +
                     set2string(allomorphsets[i1]) + "\t" + set2string(allomorphsets[i2]) + "\t" +
                     longlemmas[i1] + " (batch "+batch_of_cluster[i1]+")\t" + longlemmas[i2]  + " (batch "+batch_of_cluster[i2] + ")\tSOLUTION:\tCOMMENT:")

#                 {"+(",".join(allomorphsets[i1]))+"\t allomorph set B: "+(" ".join(allomorphsets[i2])))

    
