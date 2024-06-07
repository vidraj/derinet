#!/usr/bin/env python3

# Count occurences of whole lines in the input.

import sys

h = {}
for line in sys.stdin:
	w = line.rstrip()
	if w in h:
		h[w] += 1
	else:
		h[w] = 1

for w in sorted(h.keys()):
	print(w, h[w], sep="\t", end="\n")
