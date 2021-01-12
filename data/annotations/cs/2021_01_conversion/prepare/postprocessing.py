# !/usr/bin/env python3
# coding: utf-8

"""Postprocessed annotations of conversion."""

import argparse


# set argparse
parser = argparse.ArgumentParser()
parser.add_argument('--AnnotInput',
                    action='store',
                    dest='data',
                    required=True)

parser.add_argument('--OutputConversion',
                    action='store',
                    dest='outconversion',
                    required=True)

parser.add_argument('--OutputDeleteLexemes',
                    action='store',
                    dest='outdeletion',
                    required=True)

parser.add_argument('--OutputCreateLexemes',
                    action='store',
                    dest='outcreation',
                    required=True)

par = parser.parse_args()


# load annotations
create = list()
delete = list()
relations = list()
with open(par.data, mode='r', encoding='U8') as f:
    for line in f:
        line = line.strip().split('\t')
        line = [l for l in line if not l.startswith('#')]

        # decide action
        if 'nesouv' in line[0]:
            continue

        elif '-' in line[0]:
            for entry in line[1:]:
                entry = [e for e in entry.split('_') if e != '']
                delete.append(tuple(entry))

        elif any(n in line[0] for n in '0123456789'):
            entry = [e for e in line[int(line[0])].split('_') if e != '']
            delete.append(tuple(entry))

        elif 'M' in line[0]:
            entries = list()
            for entry in line[1:]:
                entry = [e for e in entry.split('_') if e != '']
                entries.append(entry)

            new_lexeme = [entries[0][0]]
            new_lexeme.append('N')
            new_lexeme.append('Masc')

            create.append(tuple(new_lexeme))

            relations.append((entries[0], new_lexeme))
            relations.append((new_lexeme, entries[1]))

        elif 'ok' in line[0]:
            entries = list()
            for entry in line[1:]:
                entry = [e for e in entry.split('_') if e != '']
                entries.append(entry)

            rels = [(entries[i], entries[i+1]) for i in range(len(entries)-1)]
            for rel in rels:
                relations.append(rel)

        elif 'obr' in line[0]:
            entries = list()
            for entry in line[1:]:
                entry = [e for e in entry.split('_') if e != '']
                entries.append(entry)

            relations.append((entries[1], entries[0]))


# save to files
with open(par.outcreation, mode='w', encoding='U8') as f:
    for item in create:
        print(*item, sep='\t', file=f)

with open(par.outdeletion, mode='w', encoding='U8') as f:
    for item in delete:
        print(*item, sep='\t', file=f)

with open(par.outconversion, mode='w', encoding='U8') as f:
    for item in relations:
        print('_'.join(item[0]), '>', '_'.join(item[1]), sep='\t', file=f)
