#!/usr/bin/env python3

import sys
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description="Correct the annotation file read from STDIN by adding fixes specified in correction files.")
parser.add_argument("corrections", type=argparse.FileType('r'), nargs='+', help="The files to read corrections from")

args = parser.parse_args()

fixups = defaultdict(dict)
seen = defaultdict(dict)

for f in args.corrections:
	for line in f:
		fields = line.rstrip("\r\n").split("\t")
		assert len(fields) == 4
		mark, parent, child, label = fields
		assert (parent not in fixups) or (child not in fixups[parent])
		fixups[parent][child] = (mark, label)


for line in sys.stdin:
	fields = line.rstrip("\r\n").split("\t")
	assert len(fields) == 4
	parent, child, label, prob = fields

	seen[parent][child] = True

	if parent in fixups and child in fixups[parent]:
		if fixups[parent][child][0] == "$" and fixups[parent][child][1] == label:
			# Don't use this label, it is wrong.
			continue
		elif fixups[parent][child][0] == "$":
			# We were told not to use the label in `fixups[parent][child][1]`, but `label` is different.
			print("Fixup for {} {} ignored, labels differ.".format(parent, child), file=sys.stderr)
		elif fixups[parent][child][0] == "+":
			# Use the fixup label instead of the annotated one.
			label = fixups[parent][child][1]
		else:
			assert False, "Unknown annotation mark {}".format(fixups[parent][child][0])

	print(parent, child, label, prob, sep="\t", end="\n")

for parent in fixups.keys() - seen.keys():
	for child in fixups[parent].keys() - seen[parent].keys():
		mark, label = fixups[parent][child]
		if mark == "$":
			print("Fixup for {} {} ignored.".format(parent, child), file=sys.stderr)
		elif mark == "+":
			print(parent, child, label, "NaN", sep="\t", end="\n")
		else:
			assert False, "Unknown annotation mark {}".format(mark)
