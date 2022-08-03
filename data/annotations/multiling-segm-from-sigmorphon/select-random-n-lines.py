#!/usr/bin/env python3

import sys
import random

infile = sys.argv[1]
howmanylines = int(sys.argv[2])

sys.stderr.write("Randomly selecting "+str(howmanylines)+" from "+infile + "\n")

random.seed(0)

with open(infile) as f:
    lines = random.sample(f.readlines(),howmanylines)
    print(*lines,sep='')
