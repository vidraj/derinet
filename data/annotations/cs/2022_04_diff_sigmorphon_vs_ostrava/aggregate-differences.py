#!/usr/bin/env python3

import sys
import re
import glob
from collections import Counter

diff2examples = {}

freq_of_diff = Counter()



for line in sys.stdin:
    columns = line.rstrip().split('\t')
    (unsegmented, retro, ostrava, praha) = columns[:4]

    ostrava_remainder = ostrava
    praha_remainder = praha

    while (ostrava_remainder[0] == praha_remainder[0]):
        ostrava_remainder = ostrava_remainder[1:]
        praha_remainder = praha_remainder[1:]        

    diff = ostrava_remainder + " --> " + praha_remainder
    freq_of_diff.update([diff])

    example = ostrava + " --> " + praha
    
    if diff in diff2examples:
        diff2examples[diff].append(example)
    else:
        diff2examples[diff] = [example]

for (diff, freq) in freq_of_diff.most_common():
    print (str(freq) + "\t" + diff + "\t" + ", ".join(diff2examples[diff]) + "\n")
    
