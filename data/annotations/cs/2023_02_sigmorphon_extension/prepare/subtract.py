#!/usr/bin/env python3

import sys

fd = open(sys.argv[1])

listed = {}

for line in fd:
    listed[line.rstrip().lower()] = 1

for line in sys.stdin:
    line = line.rstrip().lower()

    if line not in listed:
        print(line)

        
