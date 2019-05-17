#!/usr/bin/env python3

import sys


def read_block(f):
    # Read and consume empty lines at the beginning.
    for line in f:
        # Read until the line contains something else than the newline at the end.
        if line.rstrip():
            break

    # line now contains the first line of the block.
    block = line

    # Read the body of the block.
    for line in f:
        if line.rstrip():
            # The line contains some characters -> it is part of the block.
            block += line
        else:
            # The line is empty -> end of the block.
            break

    return block


first_block = True
def write_block(f, block):
    global first_block

    if first_block:
        first_block = False
    else:
        f.write("\n\n")

    f.write(block)



count = int(sys.argv[1])

for i in range(count):
    block = read_block(sys.stdin)
    write_block(sys.stdout, block)
