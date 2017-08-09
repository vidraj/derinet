#! /usr/bin/env python3

import os
import sys
import locale
from time import time
from itertools import chain
from collections import namedtuple


# set Czech locale for correct sorting of entries
try:
    locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
except locale.Error:
    print('Error: Czech locale cs_CZ.utf8 is currently not installed\n'
          'This may result in incorrect sorting of DeriNet entries\n'
          'It is recommended that you install it by typing\n'
          '\tsudo apt-get install language-pack-cs\n'
          'in your terminal.', file=sys.stderr)


# user-defined error classes
class LexemeNotFoundError(Exception):
    pass

class AmbiguousLexemeError(Exception):
    pass

class AmbiguousParentError(Exception):
    pass

class ParentNotFoundError(Exception):
    pass

class AlreadyHasParentError(Exception):
    pass

class IsNotParentError(Exception):
    pass

class CycleCreationError(Exception):
    pass

def safe_str(line):
    if line is None:
        return ''
    return line

def pretty_lexeme(lemma, pos, morph):
    items = [lemma]
    for item in (pos, morph):
        if item is not None:
            items.extend([' ', item])
    return '"{}"'.format(''.join(items))

def partial_lexeme_match(node, lemma, pos, morph):
    return all(item is None or node[field] == item 
                for field, item in (
                    (1, lemma),
                    (3, pos),
                    (2, morph)
                    ))

# a simple structure to represent a node
Node = namedtuple('Node', 
                  ['lex_id',
                   'lemma',
                   'morph',
                   'pos',
                   'parent_id',
                   'children', # these are actual children nodes, not ids
                   ])

def lexeme_info(lexeme):
    assert type(lexeme) == Node
    return (lexeme.lemma, lexeme.pos, lexeme.morph)


class DeriNet(object):

    __slots__ = ['_data',  # list of nodes
                 '_index', # _index[lemma][pos][morph] = lex_id
                 '_fname', # name of file from which DeriNet was loaded
                ]

    def __init__(self, fname=None):
        if fname is None:
            self._data = []
            self._index = {}
            self._fname = None
        else:
            self.load(fname)

    def _read_nodes_from_file(self, fname):
        data, index = [], {}
        with open(fname, 'r', encoding='utf-8') as ifile:
            for i, line in enumerate(ifile):
                line = line.strip('\n')
                lex_id, lemma, morph, pos, parent_id = line.split('\t')
                data.append(Node(int(lex_id), lemma, morph, pos, 
                                 parent_id=''
                                     if parent_id == ''
                                     else int(parent_id),
                                 children=[]))
                index.setdefault(lemma, {})
                index[lemma].setdefault(pos, {})
                index[lemma][pos][morph] = int(lex_id)
        return data, index

    def _populate_children(self):
        """Populate children for all nodes."""
        for node in self._data:
            if node.parent_id != '':
                self._data[node.parent_id].children.append(node)

    def load(self, fname):
        """Load DeriNet from tsv file."""
        if not os.path.exists(fname):
            raise FileNotFoundError('file "{}" not found'.format(fname))

        print('Loading DeriNet from "{}" file...'.format(fname), file=sys.stderr)
        btime = time()

        self._data, self._index = self._read_nodes_from_file(fname)

        if len(self._data) - 1 != self._data[-1].lex_id:
            print('Warning: lexeme numeration in DeriNet file looks inconsistent:\n'
                  'Discovered {} lexemes total but the last was indexed {}'
                  ''.format(len(self._data), i), file=sys.stderr)

        self._populate_children()

        print('Loaded in {:.2f} s.'.format(time() - btime), file=sys.stderr)
        self._fname = fname
        return fname

    def lex_sort(self):
        """Sort nodes regarding lemmas."""
        print('Sorting DeriNet...', file=sys.stderr)
        btime = time()
        # sort
        self._data.sort(key=lambda x: locale.strxfrm(x.morph.lower()))

        # reindex
        reverse_id = [0] * len(self._data) # used for parent_ids only
        for i, node in enumerate(self._data):
            reverse_id[node.lex_id] = i
        for i, node in enumerate(self._data):
            self._data[i] = node._replace(lex_id=i,
                                          parent_id=''
                                              if node.parent_id == ''
                                              else reverse_id[node.parent_id],
                                          children=[])
            self._index[node.lemma][node.pos][node.morph] = i

        # repopulate children
        self._populate_children()

        print('Sorted in {:.2f} s.'.format(time() - btime), file=sys.stderr)

    def save(self, fname=None, sort=False):
        """
        Save tsv snapshot of current data to fname file.

        If no fname is given, save to the file from which
        the current DeriNet representation was loaded.

        If sort=True, sort nodes by lemma before saving.
        """
        if fname is None:
            fname = self._fname
        if sort:
            self.lex_sort()
        print('Saving snapshot to "{}"'.format(fname), file=sys.stderr)
        btime = time()
        with open(fname, 'w', encoding='utf-8') as ofile:
            for lexeme in self._data:
                print(*lexeme[:-1], sep='\t', file=ofile)
        print('Saved in {:.2f} s.'.format(time() - btime), file=sys.stderr)

    def get_lexeme_by_id(self, lex_id):
        """Get node with lex_id id."""
        try:
            return self._data[lex_id]
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))

    def show_lexeme_by_id(self, lex_id):
        """Get represantation of node with lex_id id."""
        try:
            return lexeme_info(self._data[lex_id])
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))

    def search_lexemes(self, lemma, pos=None, morph=None, allow_fallback=False):
        """
        Search for all lexemes that satisfy given lemma, pos and morph,
        and return their representations.
        """
        lexeme_ids = self.get_ids(lemma, pos=pos, morph=morph)
        if len(lexeme_ids) == 0 and allow_fallback and morph is not None:
            lexeme_ids = self.get_ids(lemma, pos=pos, morph=None)
        return [lexeme_info(self._data[lexeme_id])
                    for lexeme_id in lexeme_ids]

    def get_ids(self, lemma, pos=None, morph=None):
        """
        Get a list of node ids given lemma and optionally 
        pos and morphological string.
        """
        if lemma not in self._index:
            return []
        lemma_index = self._index[lemma]
        if pos is None:
            if morph is None:
                return list(chain.from_iterable(list(morph_index.values())
                                for morph_index 
                                    in lemma_index.values()))
            else:
                all_pos_index = dict(list(chain.from_iterable(list(morph_index.items())
                                        for morph_index 
                                            in lemma_index.values())))
                if morph in all_pos_index:
                    return [all_pos_index[morph]]
                return []
        else:
            if pos not in lemma_index:
                return []
            lemma_pos_index = lemma_index[pos]
            if morph is None:
                return list(lemma_pos_index.values())
            else:
                if morph in lemma_pos_index:
                    return [lemma_pos_index[morph]]
                return []
        return []

    def get_id(self, lemma, pos=None, morph=None):
        """
        Get lexeme id by lemma and optionally 
        by pos and morphological string.

        Raise exception if no lexeme was found
        or lexeme was ambiguous.
        """
        id_list = self.get_ids(lemma, pos, morph)
        if id_list == []:
            # no such lexeme in the net
            raise LexemeNotFoundError(
                    'lexeme not found: {}'.format(
                    pretty_lexeme(lemma, pos, morph)))
        if len(id_list) > 1:
            # ambiguous lexeme
            raise AmbiguousLexemeError(
                    'ambiguous lexeme: {}'.format(
                    pretty_lexeme(lemma, pos, morph)))
        # lexeme ok
        return id_list[0]

    def get_parent_by_id(self, lex_id):
        """Get parent node of the node with lex_id id."""
        try:
            parent_id = self._data[lex_id].parent_id
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))
        if parent_id == '':
            return None
        return self._data[parent_id]

    def get_parent_by_lexeme(self, lemma, pos=None, morph=None):
        """
        Get parent node of the node given its lemma
        and optionally pos and morphological string.
        """
        lex_id = self.get_id(lemma, pos=pos, morph=morph)
        return self.get_parent_by_id(lex_id)

    def get_root_by_id(self, lex_id):
        """Get root node of the node with lex_id id."""
        try:
            parent_id = self._data[lex_id].parent_id
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))
        if parent_id == '':
            return None
        current = self._data[parent_id]
        while current.parent_id != '':
            current = self._data[current.parent_id]
        return current

    def get_root_by_lexeme(self, lemma, pos=None, morph=None):
        """
        Get root node of the node given its lemma
        and optionally pos and morphological string.
        """
        lex_id = self.get_id(lemma, pos=pos, morph=morph)
        return self.get_root_by_id(lex_id)

    def get_children_by_id(self, lex_id):
        """Get list of children of the node with lex_id id."""
        try:
            return self._data[lex_id].children
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))

    def get_subtree_by_id(self, lex_id):
        """
        Recursively build a list representing the tree
        with the node with lex_id id as its root.
        """
        try:
            lexeme = self._data[lex_id]
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))
        return [lexeme, [self.get_subtree_by_id(child.lex_id)
                            for child in lexeme.children]]

    def subtree_as_str_from_id(self, lex_id, 
                               form1='',
                               form2='  ',
                               form3=''):
        """
        Recursively build a string visualizing the tree
        with the node with id lex_id as its root.
        """
        try:
            lexeme = self._data[lex_id]
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))
        subtree_str = form1 + form3
        subtree_str += '\t'.join(str(item) for item in lexeme[:-1])
        if lexeme.children != []:
            # add all but last children's subtrees
            for child in lexeme.children[:-1]:
                subtree_str += '\n' + self.subtree_as_str_from_id(
                                        child.lex_id,
                                        form1=form1+form2,
                                        form2='│ ',
                                        form3='└─')
            # add last child's subtree
            # it has slightly different formatting
            subtree_str += '\n' + self.subtree_as_str_from_id(
                                    lexeme.children[-1].lex_id,
                                    form1=form1+form2,
                                    form2='  ',
                                    form3='└─')
        return subtree_str

    def subtree_as_str_from_lexeme(self, lemma, pos=None, morph=None):
        """
        Given lemma and optionally pos and morphological string,
        build a string visualizing the tree with the node as its root.
        """
        lex_id = self.get_id(lemma, pos=pos, morph=morph)
        return self.subtree_as_str_from_id(lex_id)

    def subtree_as_str_with_id(self, lex_id, 
                               form1='',
                               form2='  ',
                               form3=''):
        """
        Recursively build a string visualizing the tree
        containing the node with id lex_id.
        """
        root = self.get_root_by_id(lex_id)
        if root is None:
            root_id = lex_id
        else:
            root_id = root.lex_id
        return self.subtree_as_str_from_id(root_id)

    def subtree_as_str_with_lexeme(self, lemma, pos=None, morph=None):
        """
        Given lemma and optionally pos and morphological string,
        build a string visualizing the tree containing the node.
        """
        lex_id = self.get_id(lemma, pos=pos, morph=morph)
        return self.subtree_as_str_with_id(lex_id)

    def list_ambiguous_lemmas(self):
        """
        Return a dictionary with all ambiguous lemmas.
        """
        ambig_dict = {}
        for lemma, lemma_index in self._index.items():
            if len(lemma_index) > 1:
                ambig_dict[lemma] = lemma_index
        return ambig_dict

    def list_ambiguous_lemmas_pos(self):
        """
        Return a dictionary with all ambiguous pairs (lemma, pos).
        """
        ambig_dict = {}
        for lemma, lemma_index in self._index.items():
            for pos, lemma_pos_index in lemma_index.items():
                if len(lemma_pos_index) > 1:
                    ambig_dict[(lemma, pos)] = lemma_pos_index
        return ambig_dict

    def add_edge_by_ids(self, child_id, parent_id, force=False):
        """
        Add an edge from the node with lex_id=parent_id
        to the node with lex_id=child_id checking for consistency.

        If force=True, (re)assign parent regardless of the fact
        that the node already has a parent.
        """
        try:
            child = self._data[child_id]
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(child_id))
        try:
            parent = self._data[parent_id]
        except IndexError:
            raise ParentNotFoundError('invalid parent id {} for node {}: '
                                      "parent doesn't exist".format(parent_id, child_id))
        if not force and child.parent_id != '' and child.parent_id is not None:
            raise AlreadyHasParentError('node {} already has a parent '
                                        'assigned to it: {}'.format(child_id, parent_id))
        else:
            try:
                if self._data[child_id].parent_id != '' and force:
                    # remove the child from old parent children
                    old_parent = self._data[child.parent_id]
                    self._data[child.parent_id] = old_parent._replace(children=[new_child for new_child in old_parent.children if new_child != child])
                if self._data[parent_id].parent_id == child_id and force:
                    # turned out we have to reverse the edge
                    self._data[parent_id] = self._data[parent_id]._replace(parent_id=self._data[child_id].parent_id)
                    child = self._data[child_id]
                    self._data[child_id] = child._replace(children=[new_child for new_child in child.children if new_child != parent])
                    if self._data[parent_id].lex_id == self._data[parent_id].parent_id:
                        self._data[parent_id] = self._data[parent_id]._replace(parent_id='')
                self._data[child_id] = child._replace(parent_id=parent_id)
                self._data[parent_id].children.append(self._data[child_id])

                # check for possible cycle creation
                cycle_count, current, visited = 0, self._data[parent_id], {self._data[child_id].lex_id}
                while current.parent_id != '' and current.lex_id not in visited:
                    visited.add(current.lex_id)
                    current = self._data[current.parent_id]
                    cycle_count += 1

                if current.parent_id != '' and cycle_count > 0:
                    raise CycleCreationError('setting node {} as a parent of node {} '
                                             'would create a cycle'.format(parent_id, child_id))
            except CycleCreationError:
                    raise CycleCreationError('setting node {} as a parent of node {} '
                                             'would create a cycle'.format(parent_id, child_id))

    def add_edge_by_lexemes(self, 
                            child_lemma, parent_lemma, 
                            child_pos=None, parent_pos=None,
                            child_morph=None, parent_morph=None,
                            force=False, ignore_if_exists=True):
        """
        Given lemmas and optionally pos and morphological strings,
        add an edge from parent to child checking for consistency.

        If force=True, (re)assign parent regardless of the fact
        that the node already has a parent.

        If ignore_if_exists=True, don't raise AlreadyHasParentError
        if the node already has a parent and it is the same as the one
        to be assigned.
        """
        try:
            child_id = self.get_id(child_lemma, pos=child_pos, morph=child_morph)
        except LexemeNotFoundError:
            raise LexemeNotFoundError('lexeme {} not found'.format(
                                      pretty_lexeme(child_lemma, child_pos, child_morph)))
        except AmbiguousLexemeError:
            raise AmbiguousLexemeError('lexeme {} is ambiguous'.format(
                                       pretty_lexeme(child_lemma, child_pos, child_morph)))
        try:
            parent_id = self.get_id(parent_lemma, pos=parent_pos, morph=parent_morph)
        except LexemeNotFoundError:
            raise ParentNotFoundError('invalid parent {} '
                                      'for node {}: '
                                      "parent doesn't exist".format(
                                      pretty_lexeme(parent_lemma, parent_pos, parent_morph),
                                      pretty_lexeme(child_lemma, child_pos, child_morph)))
        except AmbiguousLexemeError:
            raise AmbiguousParentError('invalid parent {} '
                                       'for node {}: '
                                       "parent is ambiguous".format(
                                       pretty_lexeme(parent_lemma, parent_pos, parent_morph),
                                       pretty_lexeme(child_lemma, child_pos, child_morph)))
        try:
            self.add_edge_by_ids(child_id, parent_id, force=force)
        except AlreadyHasParentError:
            actual_parent = self.get_lexeme_by_id(self._data[child_id].parent_id)
            if not ignore_if_exists:
                raise AlreadyHasParentError('node {} already has a parent '
                                            'assigned to it: {}'.format(
                                            pretty_lexeme(child_lemma, child_pos, child_morph),
                                            pretty_lexeme(actual_parent.lemma, actual_parent.pos, actual_parent.morph)))
            else:
                if partial_lexeme_match(actual_parent, parent_lemma, parent_pos, parent_morph):
                    pass
                else:
                    raise AlreadyHasParentError('node {} already has a parent '
                                                'assigned to it: {}'.format(
                                                pretty_lexeme(child_lemma, child_pos, child_morph),
                                                pretty_lexeme(actual_parent.lemma, actual_parent.pos, actual_parent.morph)))              

        except CycleCreationError:
            raise CycleCreationError('setting node {} as a parent of node {} '
                             'would create a cycle'.format(
                             pretty_lexeme(parent_lemma, parent_pos, parent_morph),
                             pretty_lexeme(child_lemma, child_pos, child_morph)))

    def add_edges_by_lexemes(self, edge_list, force=False):
        """
        Given a list of edges denoted by child and parent lemmas
        and optionally pos and morphological strings,
        add edges from parent to child checking for consistency.

        If force=True, assign parent regardless of the fact
        that the node already has a parent.
        
        Each element in edge_list must be in the following format:
        
        ((child_lemma, child_pos, child_morph), (parent_lemma, parent_pos, parent_morph))

        If any of child_pos, child_morph, parent_pos, parent_morph are to be omitted,
        pass None in its place, e.g.:

        (('divadelník', None, None), ('divadlo', None, None))
        """
        for child, parent in edge_list:
            self.add_edge_by_lexemes(child[0], parent[0],
                                     child_pos=child[1], parent_pos=parent[1],
                                     child_morph=child[2], parent_morph=parent[2],
                                     force=force)

    def remove_edge_by_ids(self, child_id, parent_id):
        """
        Remove an edge from the node with lex_id=parent_id
        to the node with lex_id=child_id checking for consistency.
        """
        try:
            child = self._data[child_id]
        except IndexError:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(child_id))
        if child.parent_id != parent_id:
            raise IsNotParentError('node {} is not a parent '
                                   'of node {}'.format(parent_id, child_id))
        try:
            parent = self._data[parent_id]
        except IndexError:
            raise ParentNotFoundError("invalid parent id {} for node {}: "
                                      "parent doesn't exist".format(parent_id, child_id))
        new_children = [child 
                            for child
                                in self._data[child.parent_id].children
                                    if child.lex_id != child_id]
        self._data[child.parent_id] = self._data[child.parent_id]._replace(children=new_children)
        self._data[child_id] = child._replace(parent_id='')

    def remove_edge_by_lexemes(self, 
                            child_lemma, parent_lemma, 
                            child_pos=None, parent_pos=None,
                            child_morph=None, parent_morph=None):
        """
        Given lemmas and optionally pos and morphological strings,
        remove an edge from parent to child.
        """
        child_id = self.get_id(child_lemma, pos=child_pos, morph=child_morph)
        parent_id = self.get_id(parent_lemma, pos=parent_pos, morph=parent_morph)
        try:
            self.remove_edge_by_ids(child_id, parent_id)
        except IsNotParentError:
            raise IsNotParentError('node {} is not a parent '
                                   'of node {}'.format(
                                   pretty_lexeme(parent_lemma, parent_pos, parent_morph),
                                   pretty_lexeme(child_lemma, child_pos, child_morph)))

    def remove_edges_by_lexemes(self, edge_list, force=True):
        """
        Given a list of edges denoted by child and parent lemmas
        and optionally pos and morphological strings,
        remove edges from parent to child.
        
        Each element in edge_list must be in the following format:
        
        ((child_lemma, child_pos, child_morph), (parent_lemma, parent_pos, parent_morph))

        If any of child_pos, child_morph, parent_pos, parent_morph are to be omitted,
        pass None in its place, e.g.:

        (('divadelník', None, None), ('divadlo', None, None))
        """
        for child, parent in edge_list:
            self.remove_edge_by_lexemes(child[0], parent[0],
                                        child_pos=child[1], parent_pos=parent[1],
                                        child_morph=child[2], parent_morph=parent[2],
                                        force=force)
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        derinet = DeriNet(sys.argv[1])
    else:
        derinet = DeriNet('derinet-1-2.tsv')
