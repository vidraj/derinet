#!/usr/bin/env python3
# coding: utf-8

"""Postprocess data with derivatives."""

import argparse


# initial parameters
parser = argparse.ArgumentParser()
parser.add_argument('--data', action='store', type=str)
parser.add_argument('--output', action='store', type=str)


# main code
def main(args):
    with open(args.data, mode='r', encoding='U8') as f, \
         open(args.output, mode='w', encoding='U8') as g:
        for line in f:
            if line.startswith(','):
                continue

            line = line.rstrip('\n').split(',')
            derivative = line[2]
            base = line[13]

            print(base, '>', derivative, sep='\t', file=g)


# run main
if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
