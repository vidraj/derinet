#!usr/bin/env python3
# coding: utf-8

"""Lists unmotivated lemmas."""

import sys


for line in sys.stdin:
    entry = line.rstrip('\r\n').split('\t')

    if len(entry) >= 4:
        if '*' in entry[3]:
            print(entry[1])

    if len(entry) >= 5:
        if '*' in entry[4]:
            print(entry[2])
