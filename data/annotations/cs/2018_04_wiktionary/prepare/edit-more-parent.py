#!usr/bin/env python3
# coding: utf-8

"""Edit list of more-parent for annotation."""

import sys
from collections import defaultdict

ordered_keys = list()
content = defaultdict(list)

# načtení dat
for line in sys.stdin:
    if line == '\n':
        continue

    if line.split('\t')[0] not in content:
        ordered_keys.append(line.split('\t')[0])

    content[line.split('\t')[0]].append(line.strip().split('\t')[1])

# uložení po 500 dětech
n1 = len(ordered_keys) // 500
for i in range(n1):
    name = str(i*500) + '-' + str((i+1)*500)
    with open(sys.argv[1] + 'more-parent-' + name + '.tsv', mode='w',
              encoding='utf-8') as f:
        for key in ordered_keys[i*500:(i+1)*500]:
            for parent in content[key]:
                f.write(parent + '\t' + key + '\n')
            f.write('\n')

# uložení zbytku do posledních 500 dětí
n2 = len(ordered_keys) % 500
if n2 > 0:
    name = str(n1*500) + '-' + str(n2+(n1*500))
    with open(sys.argv[1] + 'more-parent-' + name + '.tsv', mode='w',
              encoding='utf-8') as f:
        for key in ordered_keys[n1*500:n2+(n1*500)]:
            for parent in content[key]:
                f.write(parent + '\t' + key + '\n')
            f.write('\n')
