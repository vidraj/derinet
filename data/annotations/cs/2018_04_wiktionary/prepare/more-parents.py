# !usr/bin/env python3
# coding utf-8

import sys
from collections import defaultdict


## načtení dat
relations = defaultdict() # všechny vztahy (které mají pro dítě více jak jednoho potenciálního rodiče)
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    for line in f:
        if line[0] == '#' or line[0] == '\n':
            continue
        line = line.split('\t')
        child = line[0]
        parents = line[1].strip().split('; ')
        if len(parents) > 1:
            relations[child] = parents


## seřazehní do skupin podle co nejdelších suffixálních formantů
# seznamy dětí
children = list(relations) # všechny děti (sirotci) z načtených vztahů

word_pos = list()
for child in children:
    word_pos.append({'word': child.split('_')[0], 'pos': child.split('_')[1]})

# vytvoření 'databáze'/slovníku co-nejdelší-suffixální-format (max 10) a slova-s-takovým-sufixem
n = 10 # na začátku se počítá s maxiálním suffixálním formantem velikosti 10
database = defaultdict(list)

while n > 0:
    cont = list() # úložiště slov k dalšímu zpracování

    # prochází všechny sirotky a ukládá suffixy
    for entry in word_pos:
        child = entry['word']
        pos = entry['pos']
        if len(child) < n:
            cont.append({'word': child, 'pos': pos}) # slovo se pouze určí k dalšímu zpracování
        else:
            database[child[-n:]].append({'word': child, 'pos': pos}) # slovo se uloží se svým suffixálním formantem zkoumané velikosti

    # prochází celou databízi a ukládá suffixy určené ke smazání (ty, které obsahují pouze jeden lexém)
    fordel2 = list() # seznam suffixů určených ke smazání
    for suf, words in database.items():
        if len(words) == 1:
            cont.append(words[0]) # pokud se má suffix smazat, uloží s enejdříve jeho obsah k dalšímu zpracování
            fordel2.append(suf)

    for d in fordel2:
        del database[d]

    # příprava na další cyklus
    word_pos = list() # vymaže se projitý seznam sirotků
    word_pos += cont # seznam sirotků se naplní slovy, která zbývají ke zpracování
    n -= 1 # sníží se velikost zkoumaných suffixálních formantů


## uložení lexémů k anotaci
for suffix, words in database.items():
    for word in words:
        word = word['word'] + '_' + word['pos']
        for parent in relations[word]:
            print(word, parent, sep='\t')
        print()
    print()

for word in cont:
    word = word['word'] + '_' + word['pos']
    for parent in relations[word]:
        print(word, parent, sep='\t')
