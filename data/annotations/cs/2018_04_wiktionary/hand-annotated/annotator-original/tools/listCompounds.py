#!usr/bin/env python3
# coding: utf-8

"""Lists compound lemmas."""

import sys


for line in sys.stdin:
    entry = line.rstrip('\r\n').split('\t')

    if len(entry) >= 4:
        if '+' in entry[3]:
            print(entry[1], entry[3], sep='\t')

    if len(entry) >= 5:
        if '+' in entry[4]:
            print(entry[2], entry[4], sep='\t')

    if '(' in entry[0]:
        print(entry[1], entry[2], sep='\t')
