#!/usr/bin/env python3
# coding: utf-8

import gzip
import argparse
from collections import defaultdict


# set initial parameters
parser = argparse.ArgumentParser()
parser.add_argument('--derinet')
parser.add_argument('--input')
parser.add_argument('--output')
args = parser.parse_args()


# load derinet
derinet = defaultdict()
with gzip.open(args.derinet, mode='rb') as derinet_file:
    content_derinet = derinet_file.read().decode('utf-8')
    for line in content_derinet.split('\n'):
        if line.strip() == '':
            continue
        
        line = line.rstrip('\n').split('\t')
        derinet[line[1]] = tuple(line)
print(derinet)

# load input data
input_data = list()
with open(args.input, mode='r', encoding='U8') as input_file:
    for line in input_file:
        input_data.append(line.strip())


# compare data to derinet
