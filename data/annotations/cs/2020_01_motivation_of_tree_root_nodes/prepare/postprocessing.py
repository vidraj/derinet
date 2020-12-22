#!/usr/bin/env python3
# coding: utf-8

"""Extract: derivational and compounding relations, labels of unmotivatedness,
and compounds, spelling variants."""

import sys
import csv

# arguments:
# (1) input file
# (2) output for derivational relations (ders, [order: child, parent])
# (3) output for compounding relations (comp, [order: child, parents])
# (4) output for labels of unmotivatedness (unmo)
# (5) output for labels of compounding (lcom)
# (5) output for spelling variants (vari)


# go through input data and extract annotations
ders = list()
comp = list()
unmo = list()
lcom = list()
vari = list()
with open(sys.argv[1], mode='r', encoding='U8') as f:
    data = csv.reader(f, delimiter=';')
    for line in data:
        line_backup = line[:]
        line += ['']*10
        # extract labels of unmotivated lexemes
        if ''.join(line[2:]) == '':
            unmo.append('_'.join(line[:2]))
            continue

        # extract labels of compounding
        if (line[2] in ('C', '%C') or '+' in line[2]) and \
           ''.join(line[3:]) == '':
            lcom.append('_'.join(line[:2]))

            # extract compounding relations
            if '+' in line[2] and ''.join(line[3:]) == '':
                line[2] = line[2].replace(' + ', '+')
                parents = ['phantom:' + p.replace('_', '')
                           if p.startswith('_') or p.endswith('_')
                           else p
                           for p in line[2].split('+')]
                comp.append(('_'.join(line[:2]), tuple(parents)))
            continue

        # extract derivational relations
        if not any(i in line[2] for i in '%?') and line[2] not in ('C', 'H') \
           and ''.join(line[3:]) == '':
            line[2] = line[2].replace(' (', '_').replace(')', '')
            if line[2].startswith('_') or line[2].endswith('_'):
                line[2] = 'phantom:' + line[2].replace('_', '')
            ders.append(('_'.join(line[:2]), line[2]))
            continue

        # extract pieces of annotations from mistakes
        if line[3] == 'MISSEDBYSARKA':
            if ''.join(line[5:]) == '' or line[5] == 'ZZ: viz Rejzek':
                line[4] = line[4].replace('ZZ: ', '')
                ders.append(('_'.join(line[:2]), line[4]))
                continue
            if 'ZZ: VARIANT' in line[5]:
                line[5] = line[5].replace('ZZ: VARIANT ', '')
                vari.append(('_'.join(line[:2]), line[5]))
                continue

        # extract conversion
        if line[3] == 'CONVERS':
            line[2] = line[2].replace(' (', '_').replace(')', '')
            ders.append(('_'.join(line[:2]), line[2]))
            continue

        # extract variants
        if 'VARIANT' in line[3]:
            if not line[4]:
                if line[3] == 'VARIANT' and line[2]:
                    vari.append(('_'.join(line[:2]), line[2]))
                    continue
                else:
                    line[3] = line[3].replace('VARIANT', '').replace('k ', '')
                    line[3] = line[3].strip()
                    if line[3] and '?' not in line[3]:
                        vari.append(('_'.join(line[:2]), line[3]))
                        continue
            elif line[4] and '?' not in line[4]:
                line[4] = line[4].replace('ZZ: ', '')
                vari.append(('_'.join(line[:2]), line[4]))
                continue

        # extract others
        if line[3] == 'OTHER':
            if 'ZZ: VARIANT ' in line[4]:
                line[4] = line[4].replace('ZZ: VARIANT ', '')
                vari.append(('_'.join(line[:2]), line[4]))
                continue
            elif 'ZZ: DER ' in line[4]:
                line[4] = line[4].replace('ZZ: DER ', '')
                ders.append(('_'.join(line[:2]), line[4]))
                continue
            elif 'ZZ: C' in line[4]:
                line[4] = line[4].replace('ZZ: C ', '')
                lcom.append('_'.join(line[:2]))
                continue

        # extract colloq
        if 'COLLOQ' in line[3]:
            if 'ZZ: VARIANT ' in line[4]:
                line[4] = line[4].replace('ZZ: VARIANT ', '')
                vari.append(('_'.join(line[:2]), line[4]))
                continue
            elif line[3] == 'COLLOQ' and line[2]:
                vari.append(('_'.join(line[:2]), line[2]))
                continue

        # extract compar
        if line[3] == 'COMPAR':
            line[4] = line[4].replace('ZZ: ', '')
            ders.append(('_'.join(line[:2]), line[4]))
            continue

        # extract sarkawrong
        if line[3] == 'SARKAWRONG':
            if 'ZZ: DER ' in line[4]:
                line[4] = line[4].replace('ZZ: DER ', '')
                ders.append(('_'.join(line[:2]), line[4]))
                continue

        # negation
        if 'NEG' in line[3]:
            if line[0].startswith('ne'):
                ders.append(('_'.join(line[:2]), line[0][2:]))
                continue
            else:
                ders.append(('_'.join(line[:2]), line[2]))
                continue

        # univerbisation
        if line[3] == 'UNIVERB':
            if '+' not in line[2] and line[2]:
                ders.append(('_'.join(line[:2]), line[2]))
                continue
            elif '+' in line[2]:
                lcom.append('_'.join(line[:2]))
                # extract compounding relations
                if '+' in line[2]:
                    line[2] = line[2].replace(' + ', '+')
                    parents = ['phantom:' + p.replace('_', '')
                               if p.startswith('_') or p.endswith('_')
                               else p
                               for p in line[2].split('+')]
                    comp.append(('_'.join(line[:2]), tuple(parents)))
                continue

        # phantom
        if 'PHANTOM' in line[3]:
            if line[2]:
                line[2] = 'phantom:' + line[2].replace('_', '')
                ders.append(('_'.join(line[:2]), line[2]))
            else:
                line[3] = line[3].replace('PHANTOM', '').replace('?', '')
                line[3] = line[3].strip()
                if line[3]:
                    line[3] = 'phantom:' + line[3].replace('_', '')
                    ders.append(('_'.join(line[:2]), line[3]))
            continue

        # the rest to manually postprocess
        if 'PARENT' in line[3] or 'NAME' in line[3] or '%jmeno' in line[2]:
            continue

        # the rest for manual postprocessing
        print('\t'.join(line_backup))


# save annotations
with open(sys.argv[2].replace('.tsv', '-classic.tsv'),
          mode='w', encoding='U8') as f, \
     open(sys.argv[2].replace('.tsv', '-phantom.tsv'),
          mode='w', encoding='U8') as g:
    for entry in ders:
        if ':' in entry[1]:
            phantom = entry[1].replace('phantom:', '')
            g.write('+' + '\t'.join([entry[0][:-2], phantom]) + '\n')
        else:
            f.write('\t'.join([entry[1], '>', entry[0]]) + '\n')

with open(sys.argv[3].replace('.tsv', '-classic.tsv'),
          mode='w', encoding='U8') as f, \
     open(sys.argv[3].replace('.tsv', '-phantom.tsv'),
          mode='w', encoding='U8') as g:
    for entry in comp:
        if ':' in ''.join(entry[1]):
            g.write('\t'.join([entry[0], '>', ' + '.join(entry[1])]) + '\n')
        else:
            f.write('\t'.join([entry[0], '>', ' + '.join(entry[1])]) + '\n')

with open(sys.argv[4], mode='w', encoding='U8') as f:
    for entry in lcom:
        f.write('\t'.join([entry, 'mark as Compound']) + '\n')

with open(sys.argv[5], mode='w', encoding='U8') as f:
    for entry in unmo:
        f.write('\t'.join([entry, 'mark as Unmotivated']) + '\n')

with open(sys.argv[6], mode='w', encoding='U8') as f:
    for entry in vari:
        f.write('\t'.join([entry[1], entry[0]]) + '\n')
