#!/usr/bin/env python3

"""Module for release 1.5."""

# This script loads new manual annotations from the following places
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

sys.path.append('../../../data-api/derinet-python/')
import derinet_api

derinet = derinet_api.DeriNet('./derinet-1-4.tsv')


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
                derinet.remove_edge_by_ids(child_id=node.lex_id,
                                           parent_id=par_node.lex_id)
                print('Warning: Relation between lemma and parent was',
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


def createDerivation(ch_lem, par_lem, ch_pos, par_pos):
    """Try to create a derivationanl relation between nodes/lemmas.
    If it is not possible, raise error.
    """
    try:
        child = (ch_lem, ch_pos)
        parent = (par_lem, par_pos)

        derinet.add_edge_by_lexemes(child_lemma=ch_lem,
                                    parent_lemma=par_lem,
                                    child_pos=ch_pos,
                                    parent_pos=par_pos)
        print('Done: Relation was successfully added. Child:', child,
              'Parent:', parent)

    except derinet_api.LexemeNotFoundError:
        print('Error: Child does not exist. Lemma:', child)

    except derinet_api.AmbiguousLexemeError:
        print('Error: Child is ambiguous. Lemma:', child,
              derinet.search_lexemes(lemma=ch_lem, pos=ch_pos))

    except derinet_api.ParentNotFoundError:
        print('Error: Parent does not exist. Lemma:', parent)

    except derinet_api.AmbiguousParentError:
        print('Error: Parent is ambiguous. Lemma:', parent,
              derinet.search_lexemes(lemma=par_lem, pos=par_pos))

    except derinet_api.AlreadyHasParentError:
        realParent = derinet.get_parent_by_lexeme(lemma=ch_lem, pos=ch_pos)
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

        r = derinet.get_root_by_lexeme(child[0], child[1])
        t = derinet.subtree_as_str_from_lexeme(child[0], child[1])
        if r is not None:
            t = derinet.subtree_as_str_from_lexeme(r.lemma, r.pos, r.morph)
        print('Tree of these lemmas from their root:\n', t)


# ---------------- compound initialize ------------

compounds = list()

# ---------------- part (a) (c) -------------------

prep = '../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/'
for filename in [
         prep + 'candidates_sky_bez_kompozit.txt',
         prep + 'candidates_ovy_bez_kompozit.txt',
         prep + 'candidates_cky_bez_kompozit.txt']:

    print('File:', filename)

    with open(filename, mode='r', encoding='utf-8') as fh:
        for line in fh:
            if line.startswith(('>>', '<<', '==')):
                continue

            columns = line.rstrip('\n').split('\t')
            child_lemma = columns[0]
            parent_lemma = columns[1]

            matchObj = re.search(r' [A-Z]: (\w+)', line)  # manual correction
            if matchObj and matchObj.groups:
                parent_lemma = matchObj.group(1)

            if not (parent_lemma == 'UNRESOLVED' or parent_lemma == ''
                    or child_lemma.startswith('?')):
                createDerivation(child_lemma, parent_lemma, 'A', None)

# ---------------- part (b) -------------------

prep = '../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/'
filename = prep + 'candidates_cky_bez_kompozit.txt'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as fh:
    for line in fh:
        if not re.search(r'^[@\?]', line):
            columns = line.lstrip('\t').rstrip('\n').split('\t')
            child_lemma = columns[0]
            parent_lemma = columns[1]

            matchObj = re.search(r' [A-Z]: (\w+)', line)  # manual correction
            if matchObj and matchObj.groups:
                parent_lemma = matchObj.group(1)

            if not (parent_lemma == 'UNRESOLVED' or parent_lemma == ''):
                createDerivation(child_lemma, parent_lemma, 'A', None)

# ---------------- part (d) -------------------

prep = '../../../../data/annotations/cs/2017_05_sky_cky_ovy/hand-annotated/'
filename = prep + 'kandidati_ze_sirotku.txt'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as fh:
    for line in fh:
        if re.search(r'^N ', line):
            line = re.sub(r'^N ', '', line)
            columns = line.rstrip('\n').split('\t')
            child_lemma = columns[0]
            parent_lemma = columns[1]

            matchObj = re.search(r' [A-Z]: (\w+)', line)  # manual correction
            if matchObj and matchObj.groups:
                parent_lemma = matchObj.group(1)

            if not (parent_lemma == 'UNRESOLVED' or parent_lemma == ''):
                createDerivation(child_lemma, parent_lemma, 'A', None)

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

    with open(filename, mode='r', encoding='utf-8') as fh:
        for line in fh:
            if not re.search(r'^@', line):
                columns = line.rstrip('\n').split('\t')
                child_lemma = columns[0]
                parent_lemma = columns[1]

                createDerivation(child_lemma, parent_lemma, None, None)

# ---------------- part (h) -------------------

prep = '../../../../data/annotations/cs/2017_08_compounds/'
filename = prep + 'all_solitary_compounds'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as fh:
    for line in fh:
        entry = line.rstrip('\n').split('\t')

        mark = entry[0]
        lemma = entry[1]

        if '@' not in mark:
            lemma = searchLexeme(lemma)
            if lemma is not None:
                compounds.append(lemma)

# ---------------- part (i) -------------------

prep = '../../../../data/annotations/cs/2017_08_compounds/'
filename = prep + 'all_compound_clusters'

print('File:', filename)

with open(filename, mode='r', encoding='utf-8') as fh:
    for line in fh:
        tokens = line.rstrip('\n').split(' ')

        lemma = searchLexeme(tokens[0])
        if lemma is not None:
            compounds.append(lemma)

        last_token = tokens[0]
        stack = []
        for index in range(1, len(tokens)):
            token = tokens[index]
            if token == '(':
                stack.append(last_token)
            elif token == ')':
                stack.pop()
            else:
                createDerivation(token, stack[-1], None, None)
                last_token = token

# ---------------- final processing -------------------

# marking compounds
print('\n', 5*'-', 'marking compound lemmas', 5*'-')
for lemma in compounds:
    markCompound(node_lem=lemma[0],
                 node_pos=lemma[1],
                 node_morph=lemma[2])

# checking compound annotation
all_compounds = list()
for node in derinet._data:
    if 'C' in node.pos:
        all_compounds.append(node)

for node in all_compounds:
    checkCompoundAnnotation(node)

# saving DeriNet release 1.5
derinet.save('derinet-1-5.tsv')
