#!/usr/bin/env python3
# coding: utf-8

"""Module for release 1.7."""

# This script loads new manual annotations from the following places
#
# (x) corrections of derinet (deleting/changing incorrect relations)
# ./delete_rel.tsv
#
# (a) rest of derivations extracted from wiktionary (cz, en, ge, fr, pl) part 2
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der5001-6000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der6001-7000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der7001-8036.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der0001-0500.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der0501-1000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der1001-1500.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der1501-2000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der2001-2500.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der2501-3000.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der3001-3500.tsv
# ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der3501-3728.tsv
#
# (b) derivations extracted from SSJC
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der0001-1000.tsv
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der1001-2000.tsv
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der2001-3000.tsv
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der3001-4000.tsv
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der4001-4616.tsv
# ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-more-der0001-0500.tsv
#

import sys
from collections import defaultdict

sys.path.append('../../../data-api/derinet2')
import derinet.derinet


der = derinet.DeriNet('derinet-1-6.tsv', version='1.6')


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
            print('Warning: There should not be a relation. Child:',
                  der.show_lexeme(child), 'Parent:', der.show_lexeme(parent))


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

# ---------------- parts (a) and (b) -------------------

preps = ['../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/',
         '../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/']
for filename in [
        preps[0] + 'der5001-6000.tsv',
        preps[0] + 'der6001-7000.tsv',
        preps[0] + 'der7001-8036.tsv',
        preps[0] + 'more-der-0001-0500.tsv',
        preps[0] + 'more-der-0501-1000.tsv',
        preps[0] + 'more-der-1001-1500.tsv',
        preps[0] + 'more-der-1501-2000.tsv',
        preps[0] + 'more-der-2001-2500.tsv',
        preps[0] + 'more-der-2501-3000.tsv',
        preps[0] + 'more-der-3001-3500.tsv',
        preps[0] + 'more-der-3501-3728.tsv',
        preps[1] + 'ssjc-one-der-0001-1000.tsv',
        preps[1] + 'ssjc-one-der-1001-2000.tsv',
        preps[1] + 'ssjc-one-der-2001-3000.tsv',
        preps[1] + 'ssjc-one-der-3001-4000.tsv',
        preps[1] + 'ssjc-one-der-4001-4616.tsv',
        preps[1] + 'ssjc-more-der-0001-0500.tsv']:

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

# saving DeriNet release 1.7
with open('api2-derinet-1-7.tsv', 'w', encoding='utf-8') as ofile:
    for lexeme in der._data:
        print(lexeme[0], lexeme[2], lexeme[3], lexeme[4], lexeme[6],
              sep='\t', file=ofile)
print('Complete. Release 1.7 of DeriNet saved.')
