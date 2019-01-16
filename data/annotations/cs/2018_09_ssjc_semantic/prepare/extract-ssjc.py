#!usr/bin/env python3
# coding: utf-8

"""Extraction of semantic labels from SSJČ."""

import re
import sys

sys.path.append('../../../../../tools/data-api/derinet-python/')
import derinet_api


# load DeriNet (for finding if extracted lemmas exist)
derinet = derinet_api.DeriNet(sys.argv[2])


def clean_parents(text):
    """Return cleaned parents from given text."""
    deleteSign = ('*', 'zast. ', '.', '"')
    for sign in deleteSign:
        text = text.replace(sign, '')

    text = re.sub(r' s[ei][\s\,\:\;]', '', text)
    text = re.sub(r'\s[XV]*I*[XV]*[\s\,\;l]', ',', text)
    text = re.sub(r'[0-9]*', '', text)
    text = re.sub(r'\(.*?\)', '', text)

    text = text.replace(', ', ';')
    text = text.replace(',', ';')

    text = re.sub(r'\sl*', '', text)
    text = re.sub(r'[a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ]*-[a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ]*', '', text)
    text = re.sub(r'\;$', '', text)

    text = re.sub(r'ti\;', 't;', text)  # old verb ending
    text = re.sub(r'ti$', 't', text)  # old verb ending

    parents = [par for par in text.split(';') if par]

    return parents


def clean_childrens(text):
    """Return cleaned parents from given text."""
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\".*?\"', '', text)
    text = re.sub(r'\w\w*\..*', '', text)
    text = re.sub(r' k .*', '', text)
    text = re.sub(r' s[ei][\s\,\:\;]', '', text)
    text = re.sub(r' bez ', '', text)
    text = re.sub(r'[0-9]*', '', text)
    text = re.sub(r'\s[XV]*I*[XV]*\s', '', text)
    text = re.sub(r'\s[XV]*I*[XV]*$', '', text)
    text = re.sub(r'[a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ]*-[a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ]*', '', text)

    deleteSign = ('*', 'v.', 't.', 'm.', 'ž.', '(', ')', '[', ']')
    for sign in deleteSign:
        text = text.replace(sign, '')

    text = text.replace(' ', ',')

    text = re.sub(r'ti\,', 't,', text)  # old verb ending
    text = re.sub(r'ti$', 't', text)  # old verb ending

    children = [child for child in text.split(',') if child]
    children = [child for child in children if len(child) > 2]

    return list(set(children))


def searchLexeme(lem, p=None):
    """Search lemma in DeriNet. Return None if lemma is not in DeriNet."""
    def divideWord(word):
        """Return lemma and pos of word in annotated data (sep=ALT+0150)."""
        word = word.split('–')
        lemma = word[0]

        pos = None
        if len(word) > 1:
            if word[1] != 'None':
                pos = word[1]

        return lemma, pos

    if p is None:
        lem, p = divideWord(lem)

    candidates = derinet.search_lexemes(lem, pos=p)
    if len(candidates) == 0:  # not in
        return None
    else:  # homonymous and OK
        return candidates[0]


# load
content = ''
with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
    content = f.read()

# take only content with relevant labels
relevant = list()
for cont in content.split('\n\n'):
    for label in ('expr.', 'zdrob.', 'zpodst.', 'nás.', 'dok.', 'ned.',
                  'm. </small><h2>('):
        if label in cont:
            relevant.append(cont)
            break

# clean xml tags, extract relations and labels
data = set()  # format: {(parent, child, label), (parent, child, label), ...}
for cont in relevant:
    old_cont = cont
    # clean xml tags
    cont = cont.replace('<h>', '{h}')
    cont = cont.replace('</h>', '{/h}')
    cont = re.sub(r'\<.*?\>', '', cont)
    cont = cont.replace('\n', '')

    # extract relations and labels
    parents = clean_parents(re.search(r'\{h\}(.*)?\{\/h\}', cont).group(1))

    if parents == []:
        continue

    if 'expr. zdrob.' in cont:  # expresive and diminutive
        children = re.search(r'expr\. zdrob\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'zdrob.'))

        children = re.search(r'expr\. zdrob\. k[e]* ([0-9][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zdrob.'))

        children = re.search(r'expr\. zdrob\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zdrob.'))

        cont = cont.replace('expr. zdrob.', '')

    if 'zdrob. expr.' in cont:  # diminutive and expresive
        children = re.search(r'zdrob\. expr\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zdrob.'))

        cont = cont.replace('zdrob. expr.', '')

    if 'zdrob.' in cont:  # diminutive
        children = re.search(r'zdrob\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'zdrob.'))

        children = re.search(r'zdrob\. k[e]* ([0-9][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zdrob.'))

        children = re.search(r'zdrob\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zdrob.'))

        cont = cont.replace('zdrob.', '')

    if 'zpodst.' in cont:  # conversion, substantivization
        children = re.search(r'zpodst\. k[e]* ([0-9][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zpodst.'))

        children = re.search(r'zpodst\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'zpodst.'))

        cont = cont.replace('zpodst.', '')

    if 'podst.' in cont:  # substantivization
        children = re.search(r'podst\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'podst.'))

        children = re.search(r'podst\. k[e]* ([0-9][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'podst.'))

        children = re.search(r'podst\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'podst.'))

        cont = cont.replace('podst.', '')

    if 'nás.' in cont:  # multiplication
        children = re.search(r'nás\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'nás.'))

        children = re.search(r'nás\. k[e]* ([0-9][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'nás.'))

        children = re.search(r'nás\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'nás.'))

        cont = cont.replace('nás.', '')

    if 'ned. i dok.' in cont:  # perfective and also imperfective
        cont = cont.replace('ned. i dok.', '')

    if 'dok.' in cont:  # perfective (aspect)
        children = re.search(r'dok\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'dok.'))

        children = re.search(r'dok\.(?! k[e]*) ([^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'dok.'))

        cont = cont.replace('dok.', '')

    if 'ned.' in cont:  # imperfective (aspect)
        children = re.search(r'ned\. k[e]* ([a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ][^\;\:]*)', cont)
        if children:
            children = clean_childrens(children.group(1))  # reversed P and CH
            if children != []:
                for child in children:
                    for par in parents:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((child, par, 'ned.'))

        cont = cont.replace('ned.', '')

    if 'm. </small><h2>(' in old_cont:  # formation of feminines
        children = re.search(r'm\. \(([\*|a-zěščřžýáíéóúůňďť|A-ZĚŠČŘŽÝÁÍÉÓÚŮŇĎŤ]*[^\,\)])', cont)
        if children:
            children = clean_childrens(children.group(1))
            if children != []:
                for par in parents:
                    for child in children:
                        # check if lemmas exist in DeriNet and take POS
                        check_ch = searchLexeme(child)
                        check_pr = searchLexeme(par)
                        if check_ch and check_pr:
                            if '–' not in child:
                                child = child + '–' + check_ch[1]
                            if '–' not in par:
                                par = par + '–' + check_pr[1]
                            data.add((par, child, 'přech.'))

# save extracted relations and labels
for entry in data:
    print(*entry, sep='\t')
