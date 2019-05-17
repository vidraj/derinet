#!/usr/bin/env python3

import sys
import re
from collections import Counter
import operator


lemma_to_root = {}

with open(sys.argv[1]) as f:
    for lineno, line in enumerate(f, 1):
        line = line.rstrip()
        raw_morphs = line.split()

        # The input contains roots annotated by enclosing them in parentheses.
        # Find the root morph (in parens), strip the parens and remember its position.
        morphs = []
        root_positions = []
        for i, morph in enumerate(raw_morphs):
            extracted_root = re.match(r"^\((.*)\)$", morph)
            if extracted_root is not None:
                # The morph is a root. Remember its position and save
                #  only what's inside the parentheses.
                #print("Root found in {}".format(morph), file=sys.stderr)
                root_positions.append(i)
                morphs.append(extracted_root.group(1))
            else:
                # The morph is not tagged as a root. Just save it.
                #print("No root found in {}".format(morph), file=sys.stderr)
                morphs.append(morph)

        #root_positions = set(root_positions)
        roots = set([morphs[i] for i in root_positions])

        lemma = "".join(morphs)

        #assert len(root_positions) == 1, "Multiple root positions given for {}: {}.".format(" ".join(raw_morphs), ", ".join([str(pos) for pos in root_positions]))
        if len(roots) < 1:
            print("No root found in lemma {} ({}) on line {}.".format(lemma, line, lineno), file=sys.stderr)

        if lemma in lemma_to_root:
            #print("Multiple segmentations given for {}.".format(lemma), file=sys.stderr)
            lemma_to_root[lemma].update(roots)
        else:
            lemma_to_root[lemma] = roots


blocks = set() # A set of (ident, size, text, roots)

last_block_id = 0
size = 0
text = ""
roots = Counter()
ident = None
for line in sys.stdin:
    lex_id, lemma, techlemma, pos, *rest = line.rstrip().split("\t")
    block_id, lex_in_block_id = lex_id.split(".")

    block_id = int(block_id)
    lex_in_block_id = int(lex_in_block_id)

    if block_id != last_block_id:
        # Start a new block.
        blocks.add((ident, size, text, tuple(root for root, count in roots.most_common())))

        last_block_id = block_id
        size = 0
        text = ""
        roots = Counter()
        ident = None

    if ident is None:
        ident = "{}#{}".format(lemma, pos)

    if lemma in lemma_to_root:
        #print("Roots of {} in block {} were {}, adding {}.".format(lemma, block_id, roots, lemma_to_root[lemma]), file=sys.stderr)
        roots.update(lemma_to_root[lemma])
    else:
        print("No segmentation given for lemma {}.".format(lemma), file=sys.stderr)

    # Continue the current block.
    size += 1
    text += "\t".join((lemma, techlemma, pos)) + "\n"
else:
    blocks.add((ident, size, text, tuple(root for root, count in roots.most_common())))
    last_block_id = block_id
    size = 0
    text = ""
    roots = Counter()
    ident = None

print("Read {} blocks.".format(len(blocks)), file=sys.stderr)

#blocks.sort(key=lambda block: block[1], reverse=True)

for ident, size, text, roots in sorted(blocks, key=operator.itemgetter(1, 0, 3), reverse=True):
    #print("Automatic roots: {}".format(" ".join(sorted(sorted(roots), key=lambda root: len(root)))))
    print("# Automatic roots for {}:\t{}".format(ident, " ".join(roots)))
    print("# Manual roots for {}:\t".format(ident))
    #print("\n")
    print(text, end="")
    print("\n")
