#!/usr/bin/env python3

import sys

fd = open(argv[1])

listed = {}

for line in fd:
    listed[line.rstrip()] = 1

for line in sys.stdin:
    columns = line.rstrip().split('\t')
    if len(columns) > 3 and columns[2] in listed:
        pass
    else:
        print(line)
        
