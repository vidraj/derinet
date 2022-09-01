#!/usr/bin/env python3

import sys

for line in sys.stdin:
    columns = line.rstrip().split('\t')

    if len(columns)>3 and len(columns[2])>0 and len(columns[3])>0:
        if columns[3].lower() == columns[2].replace("+"," ").lower():
            columns.append("CMP:SAME")
        else:
            columns.append("CMP:DIFFERENT")

    print ("\t".join(columns))


