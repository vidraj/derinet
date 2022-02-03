#!/usr/bin/env python3

import sys
import re

words = {}

for line in sys.stdin:
    word = line.rstrip()

    if re.search(r'\w{3}',word) and not re.search(r'\d',word):
#        print("IGNORED "+word)
#    else:
#        if word not in words:
            words[word.lower()] = 1


reverted_words = [word[::-1] for word in  words]
            
#for word in [a[::-1] for a in  [word[::-1] for word in  words].sort()] :
for word in  [word[::-1] for word in sorted(reverted_words)]:    
    print(word)
