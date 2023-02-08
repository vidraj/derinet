#!/usr/bin/env python3

import sys

for line in sys.stdin:
    line = line.rstrip()
    columns = line.split("\t")
    print("\t".join( [columns[0],columns[0][::-1] ]+columns[1:] ))
