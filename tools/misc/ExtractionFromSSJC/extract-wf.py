# !usr/bin/env python3
# coding: utf-8

import re
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-s', action='store', dest='s', required=True, help='the SSJČ data')
par = parser.parse_args()

derivates = defaultdict(set)

def clean_tokenize(text, deleteSign):
    # čištění
    for sign in deleteSign:
        text = text.replace(sign, '')
    text = text.replace(';', ',')
    text = re.sub(r'\s[XV]*I*[XV]*[\s\,\;]', '', text)
    text = re.sub(r'\,\s*\-\s*\w+', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\-{2,}', '', text)
    text = re.sub(r'[0-9]*', '', text)

    text = text.replace('(', '')
    text = text.replace(')', '')

    # tokenizace
    text = text.split(',')
    text = [word.strip() for word in text]
    text = [re.sub(r'\sl*', '', word) for word in text]

    if ('' in text): del text[text.index('')]

    text = list(set(text))

    return text

def setRoot(text):
    # čištění a tokenizace
    deleteSign = ['*', 'zast. ', 'podst.', 'přísl.', 'l.', '.', ' si', ' se', ':', ',- ', '/']
    text = clean_tokenize(text, deleteSign)

    # volba kořene (nejkratší z nabízených)
    root = None
    for word in sorted(text, key=len):
        if not ('-' in word):
            root = word
            del text[text.index(word)]
            break
    if (root is None):
        root = text[0]
        del text[0]

    # ostatní nabízené vložit do vztahu derivace
    for word in text: derivates[word].add(root)
    return root

def setDer(text, root):
    # čištění a tokenizace
    deleteSign = ['*', 'zast. ', 'podst.', 'přísl.', 'l.', '.', ' si', ' se', ':', ',- ', '/']
    text = clean_tokenize(text, deleteSign)

    # předpony sloves
    out = list()
    for word in text:

        if (word == root): continue

        if (word.endswith('-')):
            if (root.startswith('-')): out.append(word[:-1] + root[1:])
            else: out.append(word[:-1] + root)

        elif (word.startswith('-')):
            if (root.startswith('-')): out.append(word)
            else:
                index = None
                i = 2
                lock = False
                while not lock:
                    try:
                        index = root.index(word[1:i])
                        i += 1
                        if (i == 10): lock = True
                    except:
                        out.append(root[:index] + word[1:])
                        lock = True

        else: out.append(word)

    return out

# Extrakce
with open(file=par.s, mode='r', encoding='utf-8') as f:
    root = None
    previousLine = ''
    for line in f:
        # kořen
        if ('<root>' in line):
            root = re.search(r'\<root\>\<h\>(.*?)\<\/h\>', line).group(1)
            root = setRoot(root)

        # vzory bez kontextu
        # <arial> </arial>
        if ('<arial>' in line):
            der = re.search(r'\<arial\>(.*?)\<\/arial\>', line).group(1)
            for word in setDer(der, root):
                derivates[word].add(root)
        # <h2> </h2>
        if ('<h2>' in line):
            der = re.search(r'\<h2\>(.*?)\<\/h2\>', line).group(1)
            for word in setDer(der, root):
                derivates[word].add(root)
        # <ital> k </ital>
        if ('<ital>k ' in line) or ('<ital>ke ' in line):
            der = re.search(r'\<ital\>[(k)|(ke)]*\s*(.*?)[\s\:\<]', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[root].add(word)
        # <ital> zdrob. k </ital>
        if ('<ital>zdrob. ' in line):
            der = re.search(r'\<ital\>zdrob\. [(k)|(ke)]*\s*(.*?)[\s\:\<]', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[root].add(word)
        # <ital> sloužící k </ital>
        if ('<ital>sloužící ' in line):
            der = re.search(r'\<ital\>sloužící [(k)|(ke)]*\s*(.*?)[\s\:\<]', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[root].add(word)
        # <norm> zast. </norm>
        if ('<norm>zast. ' in line):
            der = re.search(r'\<norm\>zast. (.*?)[\s\:\<]', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[word].add(root)

        # vzory s kontextem
        # <small> příd. (expr.) </small> \n <ital> velmi(, nadmíru) </ital>
        if ((previousLine.strip() == '<small>příd. </small>') or (previousLine.strip() == '<small>příd. expr. </small>')) and (line.startswith('<ital>velmi')):
            der = re.search(r'\<ital\>velmi[(\, )|(nadmíru)|(přespříliš)|(mile)|(nadmíru)|(zcela)|(pěkně)|(příjemně)|(hezky)|(n\.)]* (\w+)', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[root].add(word)
        # <small> řidč. </small> \n <ital> </ital>
        if (previousLine.strip() == '<small>řidč. </small>') and not (re.search(r'\w+\:', line) is None):
            der = re.search(r'(\w+)\:', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[word].add(root)
        # <small>předp. </small>\n<norm>
        if (previousLine.strip() == '<small>předp. </small>') and ('<norm>' in line):
            der = re.search(r'\<norm\>(.*?)\<\/norm\>', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[word].add(root)
        # </arial> \n <norm> (zast.
        if ('</arial>' in previousLine) and ('<norm>(zast.' in line):
            der = re.search(r'\<norm\>\(zast\. ([\-]*\w+[\-]*)', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[word].add(root)
        # <small> v. (též) </small> \n <norm>
        if ((re.search(r'\<small>\s*v\.\s(též\s)*\<\/small\>', previousLine)) and ('<norm>' in line)):
            der = re.search(r'\<norm\>([\-]*\w+[\-]*)', line).group(1)
            for word in setDer(der, root):
                if not (word == ''): derivates[root].add(word)

        previousLine = line # kontext

# Ukládání dat (závěrečné čištění od chyb)
vovels = {'a', 'e', 'i', 'y', 'o', 'u', 'ě', 'ý', 'á', 'í', 'é', 'ó', 'ů', 'ú'}
with open('ssjc-wf.tsv', mode='w', encoding='utf-8') as f:
    for child,parents in derivates.items():
        if (('-' in child) or (child == '')): continue
        for parent in parents:
            if not ('-' in parent):
                ch = child
                p = parent

                # odstranění samohlásek
                for rep in vovels:
                    if not (ch.replace(rep, '') == ''): ch = ch.replace(rep, '')
                    if not (p.replace(rep, '') == ''): p = p.replace(rep, '')
                ch = ch.lower()
                p = p.lower()

                # bigramy
                childBigr = set()
                first = ch[0]
                for second in ch[1:]:
                    childBigr.add(first+second)
                    first = second

                parentBigr = set()
                first = p[0]
                for second in p[1:]:
                    parentBigr.add(first+second)
                    first = second

                # chyby
                before = len(childBigr) + len(parentBigr)
                after = len(childBigr.union(parentBigr))
                if not (after < before): pass
                else: f.write(child + '_None' + '\t' + parent + '_None' + '\n')
