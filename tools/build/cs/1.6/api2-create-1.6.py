#!/usr/bin/env python3
# coding: utf-8

"""Module for release 1.6."""

# This script loads new manual annotations from the following places
#
# (x) corrections of derinet (deleting/changing incorrect relations)
# ./delete_rel.tsv
#
# (a) nouns derivated by -ace suffix
# ../../../../data/annotations/cs/2017_11_ace_ie_sky_vat/ace_all_final.tsv
#
# (b) nouns derivated by -ie suffix
# ../../../../data/annotations/cs/2017_11_ace_ie_sky_vat/ie_all_final.tsv
#
# (c) adjectives derivated by -ský suffix
# ../../../../data/annotations/cs/2017_11_ace_ie_sky_vat/sky_all_final.tsv
#
# (d) verbs derivated by -vat suffix
# ../../../../data/annotations/cs/2017_11_ace_ie_sky_vat/vat_all_final.tsv
#
# (e) verb-nouns derivations
# ../../../../data/annotations/cs/2018_02_01_nontrivial_v2n/hand-annotated/nontrivial-v2n-merged-magda-jonas.tsv
#
# (f) verb-noun derivations from Turinsky
# ../../../../data/annotations/cs/2018_03_turinsky/turinsky-out.tsv
#
# (g) derivations extracted from wiktionary (cz, en, ge, fr, pl) part 1
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der0001-1000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der1001-2000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der2001-3000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der3001-4000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der4001-5000.tsv
#
# (h) manual observations - add relations, add compounds
# ../../../../data/annotations/cs/2018_08_rels_and_compounds/hand-annotated/relations.tsv
# ../../../../data/annotations/cs/2018_08_rels_and_compounds/hand-annotated/compounds.tsv
#

import sys
from collections import defaultdict

sys.path.append('../../../data-api/derinet2')
import derinet.derinet


der = derinet.DeriNet('derinet-1-5.tsv', version='1.5')


def divideWord(word):
    """Return lemma and pos of word in annotated data.
    Used for ambiguous words. ALT+0150 is separator.
    """
    word = word.split('–')
    lemma = word[0]

    pos = None
    if len(word) > 1:
        if word[1] != 'None':
            pos = word[1]

    return lemma, pos


def searchLexeme(lem, p=None, m=None):
    """Search lemma in DeriNet. Raise warnings for not beeing inside the
    DeriNet and for homonymous lemma.
    """
    candidates = der.search_lexemes(lemma=lem, pos=p, morph=m)
    if len(candidates) == 0:
        print('Warning: Node does not exist for lemma:', lem)
    elif len(candidates) > 1:
        print('Error: Homonymous lemma (return first):', lem, ':', candidates)
        return candidates[0]
    else:
        return candidates[0]
    return None


def checkDerivation(ch_lem, par_lem, ch_pos, par_pos, ch_morph, par_morph):
    """Check if there is NOT relation between two nodes."""
    child = (ch_lem, ch_pos, ch_morph)
    p = der.get_parent(node=ch_lem, pos=ch_pos, morph=ch_morph)
    if p is not None:
        p = (p.lemma, p.pos, p.morph)
        par = (par_lem, par_pos, par_morph)
        if p == par:
            print('Warning: There should not be a relation. Child:', child,
                  'Parent:', parent)


def markCompound(node_lem, node_pos, node_morph):
    """Mark lemma as compound. Add 'C' to its pos."""
    try:
        lem = (node_lem, node_pos, node_morph)

        id = der.get_id(node=node_lem, pos=node_pos, morph=node_morph)
        old_node = der._data[id]

        if 'C' not in old_node.pos:
            new_pos = old_node.pos + 'C'
            new_node = old_node._replace(pos=new_pos)
            der._data[id] = new_node
            print('Done: Lemma was marked as compound. Lemma:',
                  der.show_lexeme(new_node))
        else:
            print('Warning: Lemma is already marked as compound.', 'Lemma:',
                  der.show_lexeme(old_node))

    except derinet.utils.LexemeNotFoundError:
        print('Error: Lemma cannnot be mark as compound because it does not',
              'exist. Lemma:', lem)

    # except derinet.utils.AmbiguousLexemeError:
    #     print('Error: Lemma cannnot be mark as compound because it is',
    #           'ambiguous. Lemma:', lem,
    #           der.search_lexemes(lemma=node_lem, pos=node_pos,
    #                              morph=node_morph))


def checkCompoundAnnotation(node):
    """Check and correct annotation of compounds. Final processing."""
    if node.parent_id != '':
        par_node = der._data[int(node.parent_id)]

        c_in_parents = False
        while True:
            if 'C' in par_node.pos:
                c_in_parents = True
                break

            if par_node.parent_id != '':
                par_node = der._data[int(par_node.parent_id)]
            else:
                break

        par_node = der._data[int(node.parent_id)]
        if c_in_parents:
            new_pos = node.pos.replace('C', '')
            new_node = node._replace(pos=new_pos)
            der._data[node.lex_id] = new_node
            print('Warning: Lemma has parent already marked as',
                  'compound, so C was removed from lemma.',
                  'Lemma:', der.show_lexeme(new_node),
                  'Parent:', der.show_lexeme(par_node))
        else:
            if par_node.lemma in node.lemma:
                # der.remove_derivation(child=node.lemma, parent=par_node.lemma,
                #                       child_morph=node.morph,
                #                       parent_morph=par_node.morph)
                print('Erorr: Relation between lemma and parent might be',
                      'removed. Lemma:', der.show_lexeme(node),
                      'Parent:', der.show_lexeme(par_node))
            else:
                new_pos = node.pos.replace('C', '')
                new_node = node._replace(pos=new_pos)
                der._data[node.lex_id] = new_node
                markCompound(par_node.lemma, par_node.pos, par_node.morph)
                print('Warning: Lemma has unmarked (compound) parent. Mark of',
                      'lemma was removed and parent was marked (and checked).',
                      'Lemma:', der.show_lexeme(node), 'Parent:',
                      der.show_lexeme(par_node))
                checkCompoundAnnotation(par_node)
    else:
        print('Done: Lemma marked as compound. OK. Lemma:',
              der.show_lexeme(node))


# def markUnmotivated(node_lem, node_pos, node_morph):
#     """Mark lemma as unmotivated. Add 'U' to its pos."""
#     try:
#         lem = (node_lem, node_pos, node_morph)
#
#         id = der.get_id(node=node_lem, pos=node_pos, morph=node_morph)
#         old_node = derinet._data[id]
#
#         if old_node.parent_id == '':
#             if 'U' not in old_node.pos:
#                 new_pos = old_node.pos + 'U'
#                 new_node = old_node._replace(pos=new_pos)
#                 der._data[id] = new_node
#                 print('Done: Lemma was marked as unmotivated. Lemma:',
#                       der.show_lexeme(new_node))
#             else:
#                 print('Warning: Lemma is already marked as unmotivated.',
#                       'Lemma:', der.show_lexeme(old_node))
#         else:
#             parent = der._data[old_node.parent_id]
#             print('Error: Lemma cannot be marked as unmotivated because it',
#                   'has a parent. Lemma:', derinet_api.lexeme_info(old_node),
#                   'Parent:', der.show_lexeme(parent))
#
#     except derinet.utils.LexemeNotFoundError:
#         print('Error: Lemma cannnot be marked as unmotivated because it',
#               'does not exist. Lemma:', lem)
#
#     except derinet.utils.AmbiguousLexemeError:
#         print('Error: Lemma cannnot be marked as unmotivated because it is',
#               'ambiguous. Lemma:', lem,
#               derinet.search_lexemes(lemma=node_lem, pos=node_pos,
#                                      morph=node_morph))


def createDerivation(ch_lem, par_lem, ch_pos, par_pos, ch_morph, par_morph):
    """Try to create a derivationanl relation between nodes/lemmas.
    If it is not possible, raise error.
    """
    try:
        child = searchLexeme(ch_lem, ch_pos, ch_morph)
        parent = searchLexeme(par_lem, par_pos, par_morph)

        der.add_derivation(child=child.lemma, parent=parent.lemma,
                           child_pos=child.pos,
                           parent_pos=parent.pos, child_morph=child.morph,
                           parent_morph=parent.morph)

        print('Done: Relation was successfully added. Child:',
              der.show_lexeme(child), 'Parent:', der.show_lexeme(parent))

    except derinet.utils.LexemeNotFoundError:
        print('Error: Child does not exist. Lemma:',
              (ch_lem, ch_pos, ch_morph))

    # except derinet.utils.AmbiguousLexemeError:
    #     print('Error: Child is ambiguous. Lemma:', child)

    except derinet.utils.ParentNotFoundError:
        print('Error: Parent does not exist. Lemma:',
              (par_lem, par_pos, par_morph))

    # except derinet.utils.AmbiguousParentError:
    #     print('Error: Parent is ambiguous. Lemma:', parent)

    except derinet.utils.AlreadyHasParentError:
        realParent = der.get_parent(node=child.lemma, pos=child.pos,
                                    morph=child.morph)
        if parent != realParent:
            print('Error: Child already has other parent. Child:',
                  der.show_lexeme(child), 'Proposed parent:',
                  (par_lem, par_pos, par_morph), 'Original parent:',
                  der.show_lexeme(realParent))
        else:
            print('Warning: Child has same parent as proposed parent is.',
                  'Child:', der.show_lexeme(child), 'Proposed parent:',
                  (par_lem, par_pos, par_morph), 'Original parent:',
                  der.show_lexeme(realParent))

    except derinet.utils.CycleCreationError:
        print('Error: Relation would create a cycle. Child:',
              der.show_lexeme(child), 'Proposed parent:',
              der.show_lexeme(parent))

        t = der.subtree_as_string(child.lemma, child.pos, child.morph)
        print('Tree of these lemmas from their root:\n', t)


def removeDerivation(ch_lem, par_lem, ch_pos, par_pos, ch_morph, par_morph):
    """Remove a derivational relation between nodes/lemmas."""
    try:
        child = searchLexeme(ch_lem, ch_pos, ch_morph)
        parent = searchLexeme(par_lem, par_pos, par_morph)

        der.remove_derivation(child=child.lemma, parent=parent.lemma,
                              child_pos=child.pos, parent_pos=parent.pos,
                              child_morph=child.morph,
                              parent_morph=parent.morph)

        print('Done: Relation was successfully removed. Child:',
              der.show_lexeme(child), 'Parent:', der.show_lexeme(parent))

    except derinet.utils.LexemeNotFoundError:
        print('Error: Child does not exist. Lemma:',
              der.show_lexeme(child))

    # except derinet.utils.IsNotParentError:
    #     print('Error: Parent does not exist. Lemma:',
    #           der.show_lexeme(parent))

    except derinet.utils.ParentNotFoundError:
        print('Error: Invalid parent in relation. Child:',
              der.show_lexeme(child), 'Parent:', der.show_lexeme(parent))


# ---------------- initializing for final processing -------------------

not_relation = defaultdict(list)
compounds = defaultdict(list)
# unmotivated = defaultdict(list)

# ---------------- part (x) -------------------

filename = './delete_rel.tsv'

with open(filename, mode='r', encoding='utf-8') as f:

    print('File:', filename)

    for line in f:

        if line.startswith('#'):
            continue

        line = line.rstrip('\n').split('\t')

        parent_lemma, parent_pos = divideWord(line[0])
        child_lemma, child_pos = divideWord(line[1])

        parent = searchLexeme(parent_lemma, parent_pos)
        child = searchLexeme(child_lemma, child_pos)

        # relations to remove
        if child is not None and parent is not None:
            removeDerivation(ch_lem=child.lemma,
                             ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=parent.lemma,
                             par_pos=parent.pos,
                             par_morph=parent.morph)

# ---------------- parts (a) (b) (c) (d) -------------------

prep = '../../../../data/annotations/cs/'
for filename in [
        prep + '2017_11_ace_ie_sky_vat/ace_all_final.tsv',
        prep + '2017_11_ace_ie_sky_vat/ie_all_final.tsv',
        prep + '2017_11_ace_ie_sky_vat/sky_all_final.tsv',
        prep + '2017_11_ace_ie_sky_vat/vat_all_final.tsv']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:

            columns = line.rstrip('\n').split('\t')

            child_lemma = columns[1]
            child_pos = columns[3]

            parent_lemma = ''
            parent_pos = None

            if columns[5] != '':
                parent_lemma = columns[5]
            elif columns[4] != '':
                parent_lemma = columns[4]
                for rep in ['<<<?>>>', '<<<preklep>>>', '<<<', '>>>']:
                    parent_lemma = parent_lemma.replace(rep, '')

            if parent_lemma == '':
                continue

            parent_lemma, parent_pos = divideWord(parent_lemma)

            child = searchLexeme(child_lemma, child_pos)
            parent = searchLexeme(parent_lemma, p=parent_pos)

            # relations
            if child is not None and parent is not None:
                createDerivation(ch_lem=child.lemma,
                                 ch_pos=child.pos,
                                 ch_morph=child.morph,
                                 par_lem=parent.lemma,
                                 par_pos=parent.pos,
                                 par_morph=parent.morph)

# ---------------- part (e) -------------------

filename = '../../../../data/annotations/cs/2018_02_01_nontrivial_v2n/' \
           'hand-annotated/nontrivial-v2n-merged-magda-jonas.tsv'

with open(filename, mode='r', encoding='utf-8') as f:

    print('File:', filename)

    for line in f:
        columns = line.rstrip('\n').split('\t')

        child_lemma = columns[1]
        child_pos = None

        parent_lemma = columns[2]
        parent_pos = None

        parent_lemma, parent_pos = divideWord(parent_lemma)
        child_lemma, child_pos = divideWord(child_lemma)

        parent = searchLexeme(lem=parent_lemma, p=parent_pos)
        child = searchLexeme(lem=child_lemma, p=child_pos)

        if child is None or parent is None:
            continue

        # relations
        if columns[0] == '@':
            not_relation[filename].append((child, parent))
        elif columns[0] == '>':
            createDerivation(ch_lem=parent.lemma,
                             ch_pos=parent.pos,
                             ch_morph=parent.morph,
                             par_lem=child.lemma,
                             par_pos=child.pos,
                             par_morph=child.morph)
        elif columns[0] in ('*', '%', '&', '$'):
            createDerivation(ch_lem=child.lemma,
                             ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=parent.lemma,
                             par_pos=parent.pos,
                             par_morph=parent.morph)
        elif columns[0] == '#':
            not_relation[filename].append((child, parent))
            compounds[filename].append(child)

# ---------------- part (f) -------------------

filename = '../../../../data/annotations/cs/2018_03_turinsky/turinsky-out.tsv'

with open(filename, mode='r', encoding='utf-8') as f:

    print('File:', filename)

    for line in f:
        columns = line.rstrip('\n').split('\t')

        child_lem = columns[1]
        child_p = None

        parent_lem = columns[2]
        parent_p = None

        c_parent_lem = columns[3]
        c_parent_p = None

        parent_lem, parent_p = divideWord(parent_lem)
        child_lem, child_p = divideWord(child_lem)
        c_parent_lem, c_parent_p = divideWord(c_parent_lem)

        parent = searchLexeme(lem=parent_lem, p=parent_p)
        child = searchLexeme(lem=child_lem, p=child_p)
        c_parent = None
        if c_parent_lem != '':
            c_parent = searchLexeme(lem=c_parent_lem, p=c_parent_p)

        if child is None:
            continue

        # relations
        if columns[0] == '*' and parent is not None:
            createDerivation(ch_lem=child.lemma,
                             ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=parent.lemma,
                             par_pos=parent.pos,
                             par_morph=parent.morph)
        elif columns[0] == '%' and c_parent is not None:
            createDerivation(ch_lem=child.lemma,
                             ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=c_parent.lemma,
                             par_pos=c_parent.pos,
                             par_morph=c_parent.morph)
        elif columns[0] == '§' and child is not None and parent is not None:
            not_relation[filename].append((child, parent))

# ---------------- part (g) -------------------

prep = '../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/'
for filename in [
        prep + 'der0001-1000.tsv',
        prep + 'der1001-2000.tsv',
        prep + 'der2001-3000.tsv',
        prep + 'der3001-4000.tsv',
        prep + 'der4001-5000.tsv']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:
            columns = line.rstrip('\n').split('\t')

            if all(clm == '' for clm in columns[:5]):
                continue

            parent_lem, parent_p = divideWord(columns[1])
            child_lem, child_p = divideWord(columns[2])

            parent = searchLexeme(lem=parent_lem, p=parent_p)
            child = searchLexeme(lem=child_lem, p=child_p)

            # relations
            if child is not None and parent is not None:
                if columns[0] == '':
                    createDerivation(ch_lem=child.lemma,
                                     ch_pos=child.pos,
                                     ch_morph=child.morph,
                                     par_lem=parent.lemma,
                                     par_pos=parent.pos,
                                     par_morph=parent.morph)
                elif '§' in columns[0]:
                    createDerivation(ch_lem=parent.lemma,
                                     ch_pos=parent.pos,
                                     ch_morph=parent.morph,
                                     par_lem=child.lemma,
                                     par_pos=child.pos,
                                     par_morph=child.morph)
                elif '\\' in columns[0]:
                    not_relation[filename].append((child, parent))

            # # unmotivated
            # if columns[3] == '*' and parent is not None:
            #     unmotivated[filename].append(parent)
            # elif columns[4] == '*' and child is not None:
            #     unmotivated[filename].append(child)

            # compound
            if columns[3] == '%' and parent is not None:
                compounds[filename].append(parent)
            elif columns[4] == '%' and child is not None:
                compounds[filename].append(child)

            # proposals of relations
            if columns[3] not in ('', '*', '%'):
                p_parent_lem, p_parent_p = divideWord(columns[3])
                p_parent = searchLexeme(lem=p_parent_lem, p=p_parent_p)

                if p_parent is not None and parent is not None:
                    createDerivation(ch_lem=parent.lemma,
                                     ch_pos=parent.pos,
                                     ch_morph=parent.morph,
                                     par_lem=p_parent.lemma,
                                     par_pos=p_parent.pos,
                                     par_morph=p_parent.morph)

            if columns[4] not in ('', '*', '%'):
                p_parent_lem, p_parent_p = divideWord(columns[4])
                p_parent = searchLexeme(lem=p_parent_lem, p=p_parent_p)

                if p_parent is not None and child is not None:
                    createDerivation(ch_lem=child.lemma,
                                     ch_pos=child.pos,
                                     ch_morph=child.morph,
                                     par_lem=p_parent.lemma,
                                     par_pos=p_parent.pos,
                                     par_morph=p_parent.morph)

# ---------------- part (h) -------------------

prep = '../../../../data/annotations/cs/2018_08_rels_and_compounds/'

for filename in [prep + 'hand-annotated/relations.tsv',
                 prep + 'hand-annotated/compounds.tsv']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:

            if line.startswith('#'):
                continue

            line = line.rstrip('\n').split('\t')

            if line[0] == '':
                continue

            # relations
            if '§' in line[0]:
                parent_lemma, parent_pos = divideWord(line[1])
                parent = searchLexeme(parent_lemma, parent_pos)

                child_lemma, child_pos = divideWord(line[2])
                child = searchLexeme(child_lemma, child_pos)

                if child is not None and parent is not None:
                    createDerivation(ch_lem=child.lemma,
                                     ch_pos=child.pos,
                                     ch_morph=child.morph,
                                     par_lem=parent.lemma,
                                     par_pos=parent.pos,
                                     par_morph=parent.morph)
            # compounds
            if '%' in line[0]:
                lem, p = divideWord(line[1])
                lemma = searchLexeme(lem, p)
                if lemma is not None:
                    compounds[filename].append(lemma)

# ---------------- final processing -------------------

# checking if there is not relation
print('\n', 5*'-', 'checking if there is not relation', 5*'-')
for filename, relations in not_relation.items():
    print('File:', filename)
    for rel in relations:
        child = rel[0]
        parent = rel[1]
        checkDerivation(ch_lem=child.lemma,
                        ch_pos=child.pos,
                        ch_morph=child.morph,
                        par_lem=parent.lemma,
                        par_pos=parent.pos,
                        par_morph=parent.morph)

# marking compounds
print('\n', 5*'-', 'marking compound lemmas', 5*'-')
for filename, lemmas in compounds.items():
    print('File:', filename)
    for lemma in lemmas:
        markCompound(node_lem=lemma.lemma,
                     node_pos=lemma.pos,
                     node_morph=lemma.morph)

# checking compound annotation
print('\n', 5*'-', 'checking compound annotation', 5*'-')
all_compounds = list()
for node in der._data:
    if 'C' in node.pos:
        all_compounds.append(node)

for node in all_compounds:
    checkCompoundAnnotation(node)


# # marking unmotivated lemmas
# print('\n', 5*'-', 'marking unmotivated lemmas', 5*'-')
# for filename, lemmas in unmotivated.items():
#     print('File:', filename)
#     for lemma in lemmas:
#         markUnmotivated(node_lem=lemma[0],
#                         node_pos=lemma[1],
#                         node_morph=lemma[2])
#
# # checking compound-unmotivated collisions
# print('\n', 5*'-', 'checking compound-unmotivated annotation', 5*'-')
# for node in der._data:
#     if 'U' in node.pos and 'C' in node.pos:
#         print('Error: Lemma is marked as coumpound and also as unmotivated.',
#               'Lemma:', derinet_api.lexeme_info(node))

# saving DeriNet release 1.6
with open('api2-derinet-1-6.tsv', 'w', encoding='utf-8') as ofile:
    for lexeme in der._data:
        print(lexeme[0], lexeme[2], lexeme[3], lexeme[4], lexeme[6],
              sep='\t', file=ofile)
print('Complete. Release 1.6 of DeriNet saved.')
