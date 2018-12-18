#!/usr/bin/env python3

"""Module for release 1.5."""

# This script loads new manual annotations from the following places
#
# (x) corrections of derinet (deleting/changing incorrect relations)
# ./delete_rel.tsv
#
# (a) adjectives derived by -sky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_sky_bez_kompozit.txt
#
# (b) adjectives derived by -cky suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_cky_bez_kompozit.txt
#
# (c) adjectives derived by -ovy suffix
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/candidates_ovy_bez_kompozit.txt
#
# (d) other adjectives derived by -ovy and -sky
# ../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/kandidati_ze_sirotku.txt
#
# (e) nouns derived from verbs by -tel
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/VtNtel-E-final.txt
#
# (f) adverbs derived by -avane
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavanyDavane-E-final.txt
#
# (g) adverbs derived by -avatelne
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-C-final.txt
# ../../../../data/annotations/cs/2017_08_tel_avane_avatelne/AavatelnyDavatelne-E-final.txt
#
# (h) childless compounds
# ../../../../data/annotations/cs/2017_08_compounds/all_solitary_compounds
#
# (i) compounds and their derived children (possibly more levels)
# ../../../../data/annotations/cs/2017_08_compounds/all_compound_clusters
#


import re
import sys
from collections import defaultdict

sys.path.append('../../../data-api/derinet-python/')
import derinet_api

derinet = derinet_api.DeriNet('./derinet-1-4.tsv')


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
    """Search lemma in DeriNet.
    Raise warnings for not beeing inside theDeriNet and for homonymous lemma.
    """
    candidates = derinet.search_lexemes(lem, pos=p, morph=m)
    if len(candidates) == 0:
        print('Warning: Node does not exist for lemma:', lem)
    elif len(candidates) > 1:
        print('Error: Homonymous lemma (return first):', lem, ':', candidates)
        return candidates[0]
    else:
        return candidates[0]
    return None


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
        print('Warning: Lemma cannnot be mark as compound because it does not',
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


# ---------------- compound initialize ------------

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

# ---------------- part (a) (b) (c) -------------------

prep = '../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/'
for filename in [
         prep + 'candidates_sky_bez_kompozit.txt',
         prep + 'candidates_ovy_bez_kompozit.txt',
         prep + 'candidates_cky_bez_kompozit.txt']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:
            if line.startswith(('>>', '<<', '==')):
                continue

            columns = line.rstrip('\n').split('\t')

            child = searchLexeme(columns[1], 'A')
            parent_lemma, parent_pos = divideWord(columns[2])
            man_par_lem = ''

            # manual correction of parent
            manual_parent = None
            matchObj = re.search(r' [A-Z]\: (\w+[\-]*\w+[\–]*\w+)', columns[3])
            if matchObj and matchObj.groups:
                man_par_lem, man_par_pos = divideWord(matchObj.group(1))
                manual_parent = searchLexeme(man_par_lem, man_par_pos)

            # incorrect relation
            inc = False
            if parent_lemma != '' and columns[0] in ('@', '?'):
                inc = True
            elif parent_lemma != '' and columns[0] == '' and man_par_lem != '':
                inc = True

            if inc:
                parent = searchLexeme(parent_lemma, parent_pos)
                if child is not None and parent is not None:
                    not_relation[filename].append((child, parent))

            # correct relation with manual parent
            if man_par_lem != '':
                if child is not None and manual_parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=manual_parent[0],
                                     par_pos=manual_parent[1],
                                     par_morph=manual_parent[2])

            # correct relation with automatic parent
            elif (columns[0] not in ('@', '?') and parent_lemma != ''
                  and man_par_lem == ''):
                parent = searchLexeme(parent_lemma, parent_pos)
                if child is not None and parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])

# ---------------- part (d) -------------------

prep = '../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/'
filename = prep + 'kandidati_ze_sirotku.txt'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as f:
    for line in f:
        columns = line.rstrip('\n').split('\t')

        # ignore lemma/relation
        if '?' in columns[0]:
            continue

        child = searchLexeme(columns[1], 'A')
        parent_lemma, parent_pos = divideWord(columns[2])
        man_par_lem = ''

        # manual correction of parent
        manual_parent = None
        matchObj = re.search(r' [A-Z]\:(\w+[\-]*\w+[\–]*\w+)', columns[3])
        if matchObj and matchObj.groups:
            man_par_lem, man_par_pos = divideWord(matchObj.group(1))
            manual_parent = searchLexeme(man_par_lem, man_par_pos)

        # incorrect relation
        if man_par_lem != '' and parent_lemma != '':
            parent = searchLexeme(parent_lemma, parent_pos)
            if child is not None and parent is not None:
                not_relation[filename].append((child, parent))

        # correct relation with compound mark
        if 'N' not in columns[0]:
            if man_par_lem != '':
                if child is not None and manual_parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=manual_parent[0],
                                     par_pos=manual_parent[1],
                                     par_morph=manual_parent[2])
                    compounds[filename].append(manual_parent)
            elif parent_lemma != '':
                parent = searchLexeme(parent_lemma, parent_pos)
                if child is not None and parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])
                    compounds[filename].append(parent)
            if child is not None:
                compounds[filename].append(child)

        # correct relation without compound mark
        if 'N' in columns[0]:
            if man_par_lem != '':
                if child is not None and manual_parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=manual_parent[0],
                                     par_pos=manual_parent[1],
                                     par_morph=manual_parent[2])
            elif parent_lemma != '':
                parent = searchLexeme(parent_lemma, parent_pos)
                if child is not None and parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])

# ---------------- parts (e) (f) (g) -------------------

prep = '../../../../data/annotations/cs/2017_08_tel_avane_avatelne/'
for filename in [
        prep + 'AavanyDavane-C-final.txt',
        prep + 'AavatelnyDavatelne-C-final.txt',
        prep + 'VtNtel-C-final.txt',
        prep + 'AavanyDavane-E-final.txt',
        prep + 'AavatelnyDavatelne-E-final.txt',
        prep + 'VtNtel-E-final.txt']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as f:
        for line in f:

            # incorect relation
            if re.search(r'^@', line):
                columns = line.rstrip('\n').split('\t')

                child_lemma, child_pos = divideWord(columns[1])
                parent_lemma, parent_pos = divideWord(columns[2])
                child = searchLexeme(child_lemma, child_pos)
                parent = searchLexeme(parent_lemma, parent_pos)

                if child is not None and parent is not None:
                    not_relation[filename].append((child, parent))

            # correct relation
            if not re.search(r'^@', line):
                columns = line.rstrip('\n').split('\t')

                child_lemma, child_pos = divideWord(columns[0])
                parent_lemma, parent_pos = divideWord(columns[1])
                child = searchLexeme(child_lemma, child_pos)
                parent = searchLexeme(parent_lemma, parent_pos)

                if child is not None and parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])

# ---------------- part (h) -------------------

prep = '../../../../data/annotations/cs/2017_08_compounds/'
filename = prep + 'all_solitary_compounds'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as f:
    for line in f:
        columns = line.rstrip('\n').split('\t')

        # correct compound
        if '@' not in columns[0]:
            lemma_lemma, lemma_pos = divideWord(columns[1])
            lemma = searchLexeme(lemma_lemma, lemma_pos)
            if lemma is not None:
                compounds[filename].append(lemma)

# ---------------- part (i) -------------------

prep = '../../../../data/annotations/cs/2017_08_compounds/'
filename = prep + 'all_compound_clusters'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n').split('\t')
        tokens = None

        # incorect relation
        if '@' in line[0]:
            if len(line) == 3:
                tokens = line[2].split(' ')
            else:
                continue

        # correct relation
        if '@' not in line[0]:
            tokens = line[1].split(' ')

        lemma_lemma, lemma_pos = divideWord(tokens[0])
        lemma = searchLexeme(lemma_lemma, lemma_pos)

        # correct compound
        if lemma is not None and '$' not in line[0]:
            compounds[filename].append(lemma)

        last_token = tokens[0]
        stack = []
        for index in range(1, len(tokens)):
            token = tokens[index]
            if token == '(':
                stack.append(last_token)
            elif token == ')':
                stack.pop()
            else:
                child_lemma, child_pos = divideWord(token)
                parent_lemma, parent_pos = divideWord(stack[-1])
                child = searchLexeme(child_lemma, child_pos)
                parent = searchLexeme(parent_lemma, parent_pos)

                if child is not None and parent is not None:
                    createDerivation(ch_lem=child[0],
                                     ch_pos=child[1],
                                     ch_morph=child[2],
                                     par_lem=parent[0],
                                     par_pos=parent[1],
                                     par_morph=parent[2])
                last_token = token

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
for filename, compound_list in compounds.items():
    print('File:', filename)
    for lemma in compound_list:
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

# saving DeriNet release 1.5
derinet.save('derinet-1-5.tsv')
