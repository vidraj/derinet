#!usr/bin/env python3
# coding: utf-8

import re
import bz2
import argparse


# initial parameters
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str)
parser.add_argument('--output', type=str)
args = parser.parse_args()


# load and find relevant content and store it
word = ''
with bz2.open(args.input, mode='rt', encoding='utf-8') as input_file, \
     open(args.output, mode='w', encoding='U8') as output_file:
    for line in input_file:
        line = str(line.strip())

        if '<title>' in line:
            word = line.replace('/', '').replace('<title>', '')

        if 'compound|cs|' in line:
            if ':' not in word and not (word.startswith('-') or word.endswith('-')):
                print(word, file=output_file)

        if 'affix|cs|' in line:
            item = re.search(r'affix\|cs\|.*?\}', line)
            item = item.group(0)
            item = item.replace('affix|cs|', '').replace('}', '')
            components = list()
            for i in item.split('|'):
                if not i.startswith('-') and not i.endswith('-') and '=' not in i:
                    components.append(i)
            if len(components) >= 2 and len(word) > 2:
                print(word, file=output_file)
