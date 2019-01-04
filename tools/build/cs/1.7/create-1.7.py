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

sys.path.append('../../../data-api/derinet-python/')
import derinet_api


derinet = derinet_api.DeriNet('./derinet-1-6.tsv')


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


def searchLexeme(lem, p=None):
    """Search lemma in DeriNet. Raise warnings for not beeing inside the
    DeriNet and for homonymous lemma.
    """
    candidates = derinet.search_lexemes(lem, pos=p)
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
    p = derinet.get_parent_by_lexeme(lemma=ch_lem, pos=ch_pos, morph=ch_morph)
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

        id = derinet.get_id(lemma=node_lem, pos=node_pos, morph=node_morph)
        old_node = derinet._data[id]

        if 'C' not in old_node.pos:
            new_pos = old_node.pos + 'C'
            new_node = old_node._replace(pos=new_pos)
            derinet._data[id] = new_node
            print('Done: Lemma was marked as compound. Lemma:',
                  derinet_api.lexeme_info(new_node))
        else:
            print('Warning: Lemma is already marked as compound.',
                  'Lemma:', derinet_api.lexeme_info(old_node))

    except derinet_api.LexemeNotFoundError:
        print('Error: Lemma cannnot be mark as compound because it does not',
              'exist. Lemma:', lem)

    except derinet_api.AmbiguousLexemeError:
        print('Error: Lemma cannnot be mark as compound because it is',
              'ambiguous. Lemma:', lem,
              derinet.search_lexemes(lemma=node_lem, pos=node_pos,
                                     morph=node_morph))


def checkCompoundAnnotation(node):
    """Check and correct annotation of compounds. Final processing."""
    if node.parent_id != '':
        par_node = derinet._data[int(node.parent_id)]

        c_in_parents = False
        while True:
            if 'C' in par_node.pos:
                c_in_parents = True
                break

            if par_node.parent_id != '':
                par_node = derinet._data[int(par_node.parent_id)]
            else:
                break

        par_node = derinet._data[int(node.parent_id)]
        if c_in_parents:
            new_pos = node.pos.replace('C', '')
            new_node = node._replace(pos=new_pos)
            derinet._data[node.lex_id] = new_node
            print('Warning: Lemma has parent already marked as',
                  'compound, so C was removed from lemma.',
                  'Lemma:', derinet_api.lexeme_info(new_node),
                  'Parent:', derinet_api.lexeme_info(par_node))
        else:
            if par_node.lemma in node.lemma:
                # derinet.remove_edge_by_ids(child_id=node.lex_id,
                #                            parent_id=par_node.lex_id)
                print('Erorr: Relation between lemma and parent might be',
                      'removed. Lemma:', derinet_api.lexeme_info(node),
                      'Parent:', derinet_api.lexeme_info(par_node))
            else:
                new_pos = node.pos.replace('C', '')
                new_node = node._replace(pos=new_pos)
                derinet._data[node.lex_id] = new_node
                markCompound(par_node.lemma, par_node.pos, par_node.morph)
                print('Warning: Lemma has unmarked (compound) parent. Mark of',
                      'lemma was removed and parent was marked (and checked).',
                      'Lemma:', derinet_api.lexeme_info(node), 'Parent:',
                      derinet_api.lexeme_info(par_node))
                checkCompoundAnnotation(par_node)
    else:
        print('Done: Lemma marked as compound. OK. Lemma:',
              derinet_api.lexeme_info(node))


def createDerivation(ch_lem, par_lem, ch_pos, par_pos, ch_morph, par_morph):
    """Try to create a derivationanl relation between nodes/lemmas.
    If it is not possible, raise error.
    """
    try:
        child = (ch_lem, ch_pos, ch_morph)
        parent = (par_lem, par_pos, par_morph)

        derinet.add_edge_by_lexemes(child_lemma=ch_lem,
                                    parent_lemma=par_lem,
                                    child_pos=ch_pos,
                                    parent_pos=par_pos,
                                    child_morph=ch_morph,
                                    parent_morph=par_morph)
        print('Done: Relation was successfully added. Child:', child,
              'Parent:', parent)

    except derinet_api.LexemeNotFoundError:
        print('Error: Child does not exist. Lemma:', child)

    except derinet_api.AmbiguousLexemeError:
        print('Error: Child is ambiguous. Lemma:', child,
              derinet.search_lexemes(lemma=ch_lem, pos=ch_pos,
                                     morph=ch_morph))

    except derinet_api.ParentNotFoundError:
        print('Error: Parent does not exist. Lemma:', parent)

    except derinet_api.AmbiguousParentError:
        print('Error: Parent is ambiguous. Lemma:', parent,
              derinet.search_lexemes(lemma=par_lem, pos=par_pos,
                                     morph=par_morph))

    except derinet_api.AlreadyHasParentError:
        realParent = derinet.get_parent_by_lexeme(lemma=ch_lem, pos=ch_pos,
                                                  morph=ch_morph)
        r_parent = (realParent.lemma, realParent.pos, realParent.morph)
        if parent != r_parent:
            print('Error: Child already has other parent. Child:', child,
                  'Proposed parent:', parent, 'Original parent:', r_parent)
        else:
            print('Warning: Child has same parent as proposed parent is.',
                  'Child:', child, 'Proposed parent:', parent,
                  'Original parent:', r_parent)

    except derinet_api.CycleCreationError:
        print('Error: Relation would create a cycle. Child:', child,
              'Proposed parent:', parent)

        r = derinet.get_root_by_lexeme(child[0], child[1], child[2])
        t = derinet.subtree_as_str_from_lexeme(child[0], child[1], child[2])
        if r is not None:
            t = derinet.subtree_as_str_from_lexeme(r.lemma, r.pos, r.morph)
        print('Tree of these lemmas from their root:\n', t)


def removeDerivation(ch_lem, par_lem, ch_pos, par_pos, ch_morph, par_morph):
    """Remove a derivational relation between nodes/lemmas."""
    try:
        child = (ch_lem, ch_pos, ch_morph)
        parent = (par_lem, par_pos, par_morph)

        derinet.remove_edge_by_lexemes(child_lemma=ch_lem,
                                       parent_lemma=par_lem,
                                       child_pos=ch_pos,
                                       parent_pos=par_pos,
                                       child_morph=ch_morph,
                                       parent_morph=par_morph)
        print('Done: Relation was successfully removed. Child:', child,
              'Parent:', parent)

    except derinet_api.LexemeNotFoundError:
        print('Error: Child does not exist. Lemma:', child)

    except derinet_api.IsNotParentError:
        print('Error: Parent does not exist. Lemma:', parent)

    except derinet_api.ParentNotFoundError:
        print('Error: Invalid parent in relation. Child:', child,
              'Parent:', parent)


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
            removeDerivation(ch_lem=child[0],
                             ch_pos=child[1],
                             ch_morph=child[2],
                             par_lem=parent[0],
                             par_pos=parent[1],
                             par_morph=parent[2])

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
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])
                elif '§' in columns[0]:
                    createDerivation(ch_lem=parent[0],
                                     ch_pos=parent[1],
                                     ch_morph=parent[2],
                                     par_lem=child[0],
                                     par_pos=child[1],
                                     par_morph=child[2])
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
                    createDerivation(ch_lem=parent[0],
                                     ch_pos=parent[1],
                                     ch_morph=parent[2],
                                     par_lem=p_parent[0],
                                     par_pos=p_parent[1],
                                     par_morph=p_parent[2])

            if columns[4] not in ('', '*', '%'):
                p_parent_lem, p_parent_p = divideWord(columns[4])
                p_parent = searchLexeme(lem=p_parent_lem, p=p_parent_p)

                if p_parent is not None and child is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=p_parent[0],
                                     par_pos=p_parent[1],
                                     par_morph=p_parent[2])


# ---------------- final processing -------------------

# checking if there is not relation
print('\n', 5*'-', 'checking if there is not relation', 5*'-')
for filename, relations in not_relation.items():
    print('File:', filename)
    for rel in relations:
        child = rel[0]
        parent = rel[1]
        checkDerivation(ch_lem=child[0],
                        ch_pos=child[1],
                        ch_morph=child[2],
                        par_lem=parent[0],
                        par_pos=parent[1],
                        par_morph=parent[2])

# marking compounds
print('\n', 5*'-', 'marking compound lemmas', 5*'-')
for filename, lemmas in compounds.items():
    print('File:', filename)
    for lemma in lemmas:
        markCompound(node_lem=lemma[0],
                     node_pos=lemma[1],
                     node_morph=lemma[2])

# checking compound annotation
print('\n', 5*'-', 'checking compound annotation', 5*'-')
all_compounds = list()
for node in derinet._data:
    if 'C' in node.pos:
        all_compounds.append(node)

for node in all_compounds:
    checkCompoundAnnotation(node)

# saving DeriNet release 1.7
derinet.save('derinet-1-7.tsv')
