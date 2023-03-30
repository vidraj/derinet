#!/usr/bin/env python3

import sys

for line in sys.stdin:
    columns = line.rstrip().split("\t")

    source = columns[0]
    origword = columns[1]
    inverted = columns[2]
    segmented = columns[3] 

    # in some files, manual segmentation followed in the 5th columns (if different from automatic segmentation in 4th column)
    if len(columns) > 4 and columns[4] != "" and columns[4].replace(" ","") == origword:
        segmented = columns[4]

    print("\t".join([origword,inverted,segmented,source]))
        
        
    

    
    
    
