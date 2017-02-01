#!/usr/bin/env python3

import os
import re

import derinet_api

original_derinet_fname = 'derinet-1-2.tsv'
new_derinet_fname = 'derinet-1-3.tsv'
data_folder = 'data_to_add'
verb_data_folder = os.path.join(data_folder, 'verb_derivations')

dvojiti_rodice_fname = 'dvojiti_rodice_refined.txt'
jk_fname_01 = 'derivace-JK-NO_PARENT_IN_DERINET.csv'
jk_fname_02 = 'derivace-JK-DIFFERENT_PARENT_IN_DERINET.csv'
changed_edge_fname = 'changed-edge-probabilities.csv'

line_re = re.compile(r'^(.*?) ([A-Z]): ([@$]) (.*?) ([A-Z]), ([@$]) (.*?) ([A-Z])$')

def get_info(morpho, pos):
    if '_' in morpho:
        return morpho.replace('-', '_').split('_')[0], pos, morpho
    if '-' in morpho:
        return morpho.split('-')[0], pos, None
    return (morpho, pos, None)

def try_replacing(error, child, parent, position_to_replace):
    assert position_to_replace in {0, 1}
    candidates = derinet.search_lexemes(*((child, parent)[position_to_replace][:2]))
    print(candidates[0].split(' '))
    if len(candidates) == 1:
        print('Warning:', error)
        print('Replaced by the only match "{}"'.format(candidates[0]))
        if position_to_replace == 0:
            derinet.add_edge_by_lexemes(*sum(zip(candidates[0].split(' '), parent), ()))
        elif position_to_replace == 1:
            derinet.add_edge_by_lexemes(*sum(zip(child, candidates[0].split(' ')), ()))
    else:
        print('Error:', error)
        print('Possible candidates:')
        for cand in candidates:
            print(cand)
        print()

def regex_info(regex, line):
    match = regex.match(line)
    if match is not None:
        child = get_info(match.group(1), match.group(2))
        if match.group(3) == '$':
            parent = get_info(match.group(4), match.group(5))
        elif match.group(6) == '$':
            parent = get_info(match.group(7), match.group(8))
        else:
            parent = None
    return child, parent

def get_candidates(derinet, lexeme, suppress_warnings=True):
    """Get possible candidates for lexeme in ."""
    candidates, fallback = derinet.search_lexemes(*lexeme), False
    if len(candidates) == 0:
        fallback = True
        candidates = derinet.search_lexemes(*lexeme[:2])
        if not suppress_warnings:
            print('Warning: full lemma for {} not found'.format(lexeme))
            print('Falling back to short lemma ', end='')
            if len(candidates) == 1:
                print(candidates[0])
            else:
                print()
    return candidates, fallback

def check_and_add(child, parent, suppress_warnings=True):
    """
    Check candidate child and parent lexemes.
    If unambiguous, add the derivation.
    """
    child_candidates, child_fallback = get_candidates(derinet, child, suppress_warnings=suppress_warnings)
    parent_candidates, parent_fallback = get_candidates(derinet, parent, suppress_warnings=suppress_warnings)
    if len(child_candidates) == 1 and len(parent_candidates) == 1:
        try:
            derinet.add_edge_by_lexemes(*sum(zip(child_candidates[0], parent_candidates[0]), ()))
        except (derinet_api.AlreadyHasParentError,
                derinet_api.CycleCreationError) as error:
            if not suppress_warnings:
                print('Warning:', error)
            try:
                derinet.add_edge_by_lexemes(*sum(zip(child_candidates[0], parent_candidates[0]), ()), force=True)
            except derinet_api.CycleCreationError as error:
                print('Error:', error)
                print(derinet._data[derinet.get_id(*child_candidates[0])][:-1])
                print(derinet._data[derinet.get_id(*parent_candidates[0])][:-1])
        except (derinet_api.ParentNotFoundError,
                derinet_api.LexemeNotFoundError,
                derinet_api.AmbiguousParentError,
                derinet_api.AmbiguousLexemeError,
                derinet_api.IsNotParentError) as error:
            print('Error:', error)
        if (child_fallback or parent_fallback) and not suppress_warnings:
            print()
    else:
        if len(child_candidates) != 0 and len(parent_candidates) == 0:
            print('Error: parent missing:', end='')
        elif len(child_candidates) == 0 and len(parent_candidates) != 0:
            print('Error: child missing:', end='')
        elif len(child_candidates) == 0 and len(parent_candidates) == 0:
            print('Error: both missing:', end='')
        elif len(child_candidates) > 1 and len(parent_candidates) <= 1:
            print('Error: child ambiguous:', end='')
        elif len(child_candidates) <= 1 and len(parent_candidates) > 1:
            print('Error: parent ambiguous:', end='')
        elif len(child_candidates) > 1 and len(parent_candidates) > 1:
            print('Error: both ambiguous:', end='')

        print(' {} (child) has '.format(derinet_api.pretty_lexeme(*child)), end='')
        print(['{} {}'.format(child[2], child[1]) for child in child_candidates], end='')
        print(', {} (parent) has '.format(derinet_api.pretty_lexeme(*parent)), end='')
        print(['{} {}'.format(parent[2], parent[1]) for parent in parent_candidates])

def correct_changed_edge_probabilities(import_fname, suppress_warnings=True, almost_silent=True):
    """1st dataset"""
    print('\nAdding {}'.format(import_fname))
    with open(os.path.join(data_folder, import_fname), 'r', encoding='utf-8') as import_file:
        for line in import_file:
            child, parent = regex_info(line_re, line)
            match = line_re.match(line)
            if parent is not None:
                if not almost_silent:
                    print('Setting {} <- {}'.format(child, parent))
                check_and_add(child, parent, suppress_warnings=suppress_warnings)

def add_jk(import_fnames, suppress_warnings=True, almost_silent=True):
    """2nd and 3rd datasets"""
    for import_fname in import_fnames:
        print('\nAdding {}'.format(import_fname))
        with open(os.path.join(data_folder, import_fname), 'r', encoding='utf-8') as import_file:
            for line in import_file:
                mark, id, child, parent, action = line.strip().split(',')[:5]
                try:
                    if '_' in parent: # have a technical lemma
                        tech, parent = parent, parent.replace('-', '_').split('_')[0]
                    else:
                        tech = None
                    if action == 'NO_PARENT_IN_DERINET' and mark != '-':
                        candidate_parents = [candidate for candidate in derinet.search_lexemes(parent) if candidate[1] in {'N', 'V'}]
                        if len(candidate_parents) == 1:
                            if not almost_silent:
                                print('Setting {} <- {}'.format(child, parent))
                            args = (child, candidate_parents[0][0], None, candidate_parents[0][1])
                            derinet.add_edge_by_lexemes(*args)
                        else:
                            if tech is not None:
                                derinet.add_edge_by_lexemes(*sum(zip((child, None, None), (parent, None, tech)), ()))
                            else:
                                print('Error: parent ambiguous, choice from: ', end='')
                                print([candidate[2] for candidate in candidate_parents])

                    elif action == 'DIFFERENT_PARENT_IN_DERINET' and mark == '+':
                        if not almost_silent:
                            print('Setting {} <- {}'.format(child, parent))
                        args = (child, parent)
                        derinet.add_edge_by_lexemes(*args)
                except (derinet_api.AlreadyHasParentError, derinet_api.CycleCreationError) as error:
                    if not suppress_warnings:
                        print('Warning:', error)
                    try:
                        derinet.add_edge_by_lexemes(*args, force=True)
                    except derinet_api.CycleCreationError as error:
                        print('Error:', error)
                except derinet_api.AmbiguousLexemeError as error:
                    # this part is correct ONLY for this dataset
                    # because there only two cases with ambiguous child
                    # and both are to be resolved this way 
                    print('Warning: child ambiguous, adding both: '.format(error), end='')
                    candidate_children = [candidate for candidate in derinet.search_lexemes(child) if candidate[1] in {'N', 'V'}]
                    print([candidate[2] for candidate in candidate_children])
                    for candidate_child in candidate_children:
                        derinet.add_edge_by_lexemes(*sum(zip(candidate_child, (parent, None, None)), ()))
                    
                except derinet_api.ParentNotFoundError as error:
                    print('Error: parent missing:', error)
                except derinet_api.LexemeNotFoundError as error:
                    print('Error: child missing:', error)
                except derinet_api.IsNotParentError as error:
                    print('Error:', error)

def add_changed_edge_probabilities(import_fname, suppress_warnings=True, almost_silent=True):
    """ 4th dataset """
    print('\nAdding {}'.format(import_fname))
    with open(os.path.join(data_folder, import_fname), 'r', encoding='utf-8') as import_file:
        for line in import_file:
            mark, child, prob, new_parent, old_parent = line.rstrip('\n').split('\t')
            if mark == '+':
                child = get_info(*child.split(' '))
                parent = get_info(*new_parent.replace('NEW: ', '').split(' '))
                if not almost_silent:
                    print('Setting {} <- {}'.format(child, parent))
                check_and_add(child, parent, suppress_warnings=suppress_warnings)

def add_verb_deriv(data_folder, suppress_warnings=True, almost_silent=True):
    """Verb derivation dataset."""
    for fname in sorted(filter(lambda x: x.endswith('_final_populated.tsv') and not x.startswith('aspect'), os.listdir(data_folder))):
        print('\nAdding {}'.format(fname))
        with open(os.path.join(data_folder, fname), 'r', encoding='utf-8') as import_file:
            for line in import_file:
                line_parts = line.strip().split('\t')
                child = get_info(line_parts[2].strip('"'), 'V')
                parent = get_info(line_parts[5].strip('"'), 'V')
                if not almost_silent:
                    print('Setting {} <- {}'.format(child, parent))
                check_and_add(child, parent, suppress_warnings=suppress_warnings)

if __name__ == "__main__":
    derinet = derinet_api.DeriNet(original_derinet_fname)
    add_changed_edge_probabilities(changed_edge_fname)
    correct_changed_edge_probabilities(dvojiti_rodice_fname)
    add_jk((jk_fname_01, jk_fname_02))
    #add_verb_deriv(verb_data_folder)

    derinet.save(fname=new_derinet_fname, sort=True)
