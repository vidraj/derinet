#!/usr/bin/env python3
# coding: utf-8

"""Module for release 1.4."""

# This script loads new manual annotations from the following places
#
# (a) derivatonal relations within verbs
# ./final_sorted.tsv
#


import re
import sys

sys.path.append('../../../data-api/derinet2')
import derinet.derinet


der = derinet.DeriNet('derinet-1-3.tsv', version='1.3')


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
        o_parent = der.get_parent(parent.lemma, parent.pos, parent.morph)
        if o_parent == child:
            removeDerivation(ch_lem=parent.lemma, ch_pos=parent.pos,
                             ch_morph=parent.morph,
                             par_lem=o_parent.lemma, par_pos=o_parent.pos,
                             par_morph=o_parent.morph)
            createDerivation(ch_lem=child.lemma, ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=parent.lemma, par_pos=parent.pos,
                             par_morph=parent.morph)
        else:
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


# ---------------- part (a) -------------------

filename = 'final_sorted.tsv'

with open(filename, mode='r', encoding='utf-8') as f:

    print('File:', filename)

    for line in f:
        entry = line.rstrip('\n').split('\t')

        child = searchLexeme(entry[1], 'V')
        parent = searchLexeme(re.sub(r"[\-_`].+", '', entry[5]), 'V')

        if child and parent:
            o_parent = der.get_parent(child.lemma, child.pos, child.morph)
            if o_parent:
                removeDerivation(ch_lem=child.lemma, ch_pos=child.pos,
                                 ch_morph=child.morph,
                                 par_lem=o_parent.lemma, par_pos=o_parent.pos,
                                 par_morph=o_parent.morph)

            createDerivation(ch_lem=child.lemma, ch_pos=child.pos,
                             ch_morph=child.morph,
                             par_lem=parent.lemma, par_pos=parent.pos,
                             par_morph=parent.morph)


# ---------------- final processing -------------------

# saving DeriNet release 1.4
with open('api2-derinet-1-4.tsv', 'w', encoding='utf-8') as ofile:
    for lexeme in der._data:
        print(lexeme[0], lexeme[2], lexeme[3], lexeme[4], lexeme[6],
              sep='\t', file=ofile)
print('Complete. Release 1.4 of DeriNet saved.')
