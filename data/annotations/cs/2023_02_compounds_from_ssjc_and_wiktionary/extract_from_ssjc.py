#!usr/bin/env python3
# coding: utf-8

import re
import argparse


# initial parameters
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str)
parser.add_argument('--output', type=str)
args = parser.parse_args()


# load
content = ''
with open(file=args.input, mode='r', encoding='utf-8') as f:
    content = f.read()


# take only content with relevant labels
relevant = list()
for cont in content.split('\n\n'):
    if 'první část' in cont or 'druhá část' in cont:
        relevant.append(cont)


# extract compounds
with open(args.output, mode='w', encoding='U8') as output_file:
    for cont in relevant:
        cont = cont.replace('\n', '')

        query = re.findall(r'\<norm\>\(.*?\<\/norm\>', cont)
        if query:  # in brackets
            for item in query:
                for i in ('spisovatel', 'popis přírody', 'jazýček', 'list javoru', 'list babyky', 'výlet pořádáte'):
                    item = item.replace(i, '')
                item = item.replace('<norm>(', '').replace('</norm>', '')
                item = item.replace('ap.', '').replace('atd.', '').replace('aj.', '').replace('atp.', '')
                item = item.replace(')', '').replace(';', ',').replace(' ', '').replace('?', '')
                for item in item.split(','):
                    if '*' not in item and 'zast.' not in item and item != '' and item[-1] != '-' and len(item) > 2:
                        if item not in (
                            'sedlákožníchbylrád', 'žedostaliznáméhozloděje(napráci', 'kyselinametafosforečná', 'ortofosforečnákyselina',
                            'spisobsahujez-yčeskéhojazyka', 'město', 'vněmžpověstmojebeřez.', 'p-tuamobile', 'p-tuumobile'
                        ):
                            print(item, file=output_file)

        else:  # not in brackets
            query = re.findall(r'\<norm\>.*?\<\/norm\>', cont)
            if query and any(i in query[0] for i in ('-dku', '-tku', '-y', '-í', '-na', '-ty-', 'lithos', '-u', '-ám', 'k-é', '-zo-', 't-á', 'u.', '-e', '-u', 'v.', )):
                continue
            for item in query:
                for i in ('kyselina', 'muž', 'úmysl', 'strom', 'drát'):
                    item = item.replace(i, '')
                item = item.replace('<norm>', '').replace('</norm>', '')
                item = item.replace('ap.', '').replace('atd.', '').replace('aj.', '').replace('atp.', '')
                item = item.replace(')', '').replace(';', ',').replace(' ', '').replace('?', '').replace('...', '').replace('[', '').replace(']', '')
                item = re.sub(r'.*\(', '', item)
                for item in item.split(','):
                    if '*' not in item and 'zast.' not in item and 'G.' not in item and item != '' and not (item.endswith('-') or item.startswith('-')) and len(item) > 2:
                        if item not in (
                            'dvě', 'dvojí', 'gram', 'chval', 'oba', 'obě', 'obojí', 'monstre', 'quasioriginálníjenzdánlivělogický', 'originální', 'recte', 'ikdybyutíkalsebevíc',
                            'sebeméněseneuchýlit', 'nedoběhne', 'supra', 'tři', 'trojí'
                        ):
                            print(item, file=output_file)            
