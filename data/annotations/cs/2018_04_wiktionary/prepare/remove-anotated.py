# !usr/bin/env python3
# coding: utf-8

import sys

allData = list()
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f: #file with all data for anotating
    for line in f:
        allData.append(line.strip())

with open(file=sys.argv[2], mode='r', encoding='utf-8') as f: #file with already anotated data from all data
    for line in f:
        line = line.strip()
        if not (line == ''):
            try:
                del allData[allData.index(line)]
            except:
                pass

foranotData = [allData[0]]
previous = allData[0]
for entry in allData[1:]:
    if (previous == '') and (entry == ''): pass
    else: foranotData.append(entry)
    previous = entry

for entry in foranotData:
    print(entry)
