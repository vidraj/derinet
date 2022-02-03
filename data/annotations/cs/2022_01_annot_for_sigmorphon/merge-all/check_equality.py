#!/usr/bin/env python3

import sys

for line in sys.stdin:
    columns = line.rstrip().split('\t')
    orig = columns[0]
    segmented = columns[2]

    if orig != segmented.replace('-','') and segmented != '"':
        print(line.rstrip()+"\t"+"#NON-EQUAL")

    else:
#        print(line.rstrip())
        pass
