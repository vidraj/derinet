#!/usr/bin/env python3

import sys

if len(sys.argv) != 2:
    sys.stderr.write("Usage:  ./first_n_sentences.py N < file.conllu\n")
    quit()

max_sentences = int(sys.argv[1])

processed_sentences = 0

for line in sys.stdin:

    line = line.rstrip()
    
    if len(line)==0:
        processed_sentences += 1
        if processed_sentences == max_sentences:
            break
        print()
#        print("SENTNO = "+str(processed_sentences))

    else:
        print(line)

        
