#!/usr/bin/env python3

import sys

for line in sys.stdin:
    print(line.rstrip() + "\t" + line.rstrip()[::-1])
