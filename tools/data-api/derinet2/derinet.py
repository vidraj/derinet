#! /usr/bin/env python3


import os
import sys
import locale
import logging
from time import time
from itertools import chain

from . import LexemeNotFoundError, AlreadyHasParentError, CycleCreationError, UnknownFileVersion
from .utils import pretty_lexeme, partial_lexeme_match, lexeme_info, Node, flatten_list

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

locales_full = {
    'cs': 'cs_CZ.utf8',
    'us': 'en_US.utf8',
    'en': 'en_BG.utf8',
    'de': 'de_DE.utf8',
    'pl': 'pl_PL.utf8',
    'it': 'it_IT.utf8',
    'es': 'es_ES.utf8'
}

class DeriNet(object):
    __slots__ = ['_data',  # list of nodes
                 '_index',  # _index[lemma][pos][morph] = lex_id
                 '_fname',  # name of file from which DeriNet was loaded
                 '_ids2internal', # mapping of human-readable ids to internal representation
                 '_ids',
                 '_roots', # list of roots of trees
                 ]

    def __init__(self, fname=None, version="1.4", locales='cs'):
        self._ids2internal = {}
        self._roots = []
        self._ids = []
        if fname is None:
            self._data = []
            self._index = {}
            self._fname = None
        else:
            try:
                self.load(fname, version)
            except UnknownFileVersion:
                logger.error('Unknown file version: %d', version)
        # set locale for correct sorting of entries
        if not locales in locales_full:
            logger.error('Unknown localization settings, the sorting may not work as expected!')
        locales = locales_full[locales]
        try:
            locale.setlocale(locale.LC_ALL, locales)
        except locale.Error:
            logger.error('Error: Czech locale %s is currently not installed\n'
                         'This may result in incorrect sorting of DeriNet entries\n'
                         'It is recommended that you install it by typing\n'
                         '\tsudo apt-get install language-pack-\n'
                         'in your terminal.', locales)


    def _read_nodes_from_file(self, ifile, version):
        data, index = [], {}
        for i, line in enumerate(ifile):
            splitted_line = line.strip('\n').split('\t')
            if version.startswith("1"):
                if len(splitted_line) != 5:
                    logger.warning("Failed to read lexeme on line %d. Invalid line format: get %d field, expected %d_populate_children",
                                  i, len(splitted_line), 5)
                    continue
                else:
                    lex_id, lemma, morph, pos, parent_id = splitted_line
                    data.append(Node(i, lex_id, lemma, morph, pos, tag_mask="",
                                 parent_id=""
                                 if parent_id == ""
                                 else int(parent_id),
                                 composition_parents=[],
                                 misc={},
                                 children=[]))
            elif version.startswith("2"):
                if len(splitted_line) != 8:
                    logger.warning(
                        "Failed to read lexeme on line %d. Invalid line format: get %d field, expected %d",
                        i, len(splitted_line), 8)
                    continue
                else:
                    lex_id, lemma, morph, pos, tag_mask, parent_id, composition_parents, misc = splitted_line
                    data.append(Node(i, lex_id, lemma, morph, pos, tag_mask,
                                 parent_id=""
                                 if parent_id == ""
                                 else int(parent_id),
                                 composition_parents=[edge.split('-') for edge in composition_parents.split(',')],
                                 misc=misc,
                                 children=[]))
            else:
                raise UnknownFileVersion

            if parent_id != "":
                self._roots.append(int(parent_id))
            self._ids2internal[int(lex_id)] = i
            index.setdefault(lemma, {})
            index[lemma].setdefault(pos, {})
            index[lemma][pos][morph] = int(lex_id)
        return data, index

    def _populate_nodes(self, populate_children=True, replace_ids=True):
        """Populate children for all nodes."""
        for node in self._data:
            if node.parent_id == '':
                continue
            parent_id = node.parent_id
            if replace_ids:
                parent_id = self._ids2internal[node.parent_id]
                composition_parents = [(self._ids2internal[p1], self._ids2internal[p2]) for p1, p2 in node.composition_parents]
                self._data[parent_id]._replace(parent_id=parent_id, composition_parents=composition_parents)
            if populate_children:
                self._data[parent_id].children.append(node)

        if replace_ids:
            for i in range(len(self._roots)):
                self._roots[i] = self._ids2internal[self._roots[i]]

    def load(self, fname, version):
        """Load DeriNet from tsv file."""
        if hasattr(fname, "read"):
            ifile = fname
        else:
            if not os.path.exists(fname):
                raise FileNotFoundError('file "{}" not found'.format(fname))
            logger.info('Loading DeriNet (version %s) from "%s" file...', version, fname)
            ifile = open(fname, 'r', encoding='utf-8')
        btime = time()
        self._data, self._index = self._read_nodes_from_file(ifile, version)
        self._populate_nodes()

        if len(self._data) - 1 != self._data[-1].lex_id:
            logger.warning('Lexeme numeration in DeriNet file looks inconsistent:\n'
                           'Discovered %d lexemes total but the last was indexed %d', len(self._data),
                           self._data[-1].lex_id)

        logger.info('Loaded in {:.2f} s.'.format(time() - btime))
        self._fname = fname
        return fname

    def _sort_nodes(self, nodes):
        return nodes.sort(key=lambda x: locale.strxfrm(x.morph.lower()))

    def sort(self):
        """Sort nodes regarding lemmas."""
        logger.info('Sorting DeriNet...')

        btime = time()
        self._sort_nodes(self._data)

        # reindex
        reverse_id = [0] * len(self._data)  # used for parent_ids only
        for i, node in enumerate(self._data):
            reverse_id[node.lex_id] = i
        for i, node in enumerate(self._data):
            self._data[i] = node._replace(lex_id=i,
                                          parent_id=''
                                          if node.parent_id == ''
                                          # TODO: measure if faster than use self._data[node.parent_id].lex_id
                                          else reverse_id[node.parent_id],
                                          children=[])
            self._index[node.lemma][node.pos][node.morph] = i

        # repopulate children
        self._populate_nodes(replace_ids=False)

        logger.info('Sorted in {:.2f} s.'.format(time() - btime))

    def save(self, fname=None, sort=False):
        """
        Save tsv snapshot of current data to fname file.

        If no fname is given, save to the file from which
        the current DeriNet representation was loaded.

        If sort=True, sort nodes by lemma before saving.
        """
        self._ids = {}
        if fname is None:
            fname = self._fname
        if sort:
            self.lex_sort()
        logger.info('Saving snapshot to "%s"', fname)
        btime = time()
        with open(fname, 'w', encoding='utf-8') as ofile:
            for i, root in enumerate(self._roots):
                self.save_tree(i, root, ofile)
        logger.info('Saved in {:.2f} s.'.format(time() - btime))

    def save_tree(self, no, root, ofile):
        try:
            for i, el in enumerate(flatten_list(self.get_subtree_by_id(root))):
                lex_id, pretty_id, lemma, morph, pos, tag_mask, parent_id, composition_parents, misc = el[:-1]
                pretty_id = "{}.{}".format(no, i)
                self._ids[lex_id] = pretty_id
                if parent_id != '':
                    parent_id = self._ids[parent_id]
                    print(parent_id)
                print(pretty_id, lemma, morph, pos, tag_mask,
                      parent_id,  [(self._ids[p1], self._ids[p2]) for p1, p2 in composition_parents], misc,
                      sep="\t", file=ofile)
        except LexemeNotFoundError:
            logger.error('Failed to save tree with root %s', str(root))

    def get_lexeme(self, node, pos=None, morph=None):
        """Get node with lex_id id."""
        lex_id = self.get_id(node, pos=pos, morph=morph)
        if lex_id not in self._data:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))
        return self._data[lex_id]

    def show_lexeme(self, node, pos=None, morph=None):
        """Get represantation of node with lex_id id."""
        lex_id = self.get_id(node, pos=pos, morph=morph)
        if lex_id in self._data:
            return lexeme_info(self._data[lex_id])
        return None

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

    def get_id(self, node, pos=None, morph=None):
        """
        Get lexeme id by lemma and optionally
        by pos and morphological string.
        """
        if isinstance(node, int):
            return node
        if isinstance(node, Node):
            lemma = node.lemma
        else:
            lemma = node
        id_list = self.get_ids(lemma, pos, morph)
        if id_list == []:
            # no such lexeme in the net
            raise LexemeNotFoundError(
                'lexeme not found: {}'.format(
                    pretty_lexeme(lemma, pos, morph)))
        # return first available lexeme
        id_list.sort()
        return id_list[0]

    def get_parent(self, node, pos=None, morph=None):
        """Get parent node of the node with lex_id id."""
        lex_id = self.get_id(node, pos=pos, morph=morph)
        if lex_id in self._data:
            parent_id = self._data[lex_id].parent_id
            if parent_id == '':
                return None
            return self._data[parent_id]
        return None

    def get_root(self, node, pos=None, morph=None):
        """Get root node of the node with lex_id id."""
        lex_id = self.get_id(node, pos=pos, morph=morph)
        if lex_id in self._data:
            parent_id = self._data[lex_id].parent_id
            if parent_id == '':
                return None
            current = self._data[parent_id]
            while current.parent_id != '':
                current = self._data[current.parent_id]
            return current


    def get_children_by_id(self, lex_id):
        """Get list of children of the node with lex_id id."""
        if lex_id in self._data:
            return self._data[lex_id].children
        return None

    def get_subtree_by_id(self, lex_id):
        """
        Recursively build a list representing the tree
        with the node with lex_id id as its root.
        :param lex_id - id of the root of the tree
        :return tree of the form:
            [root, [[ch1, [[ch1.1, ...], [ch1.2, ...], ...]], [ch2, ...]]
        """
        if lex_id in self._data:
            lexeme = self._data[lex_id]
            return [lexeme, [self.get_subtree_by_id(child.lex_id)
                             for child in lexeme.children]]
        raise LexemeNotFoundError('lexeme with id {} not found'.format(lex_id))

    def subtree_as_str_from_root(self, root_id,
                                 form1='',
                                 form2='  ',
                                 form3=''):
        """
        Recursively build a string visualizing the tree
        with the node with id lex_id as its root.
        """
        if root_id in self._data:
            lexeme = self._data[root_id]
            subtree_str = form1 + form3
            subtree_str += '\t'.join(str(item) for item in lexeme[:-1])
            if lexeme.children != []:
                # add all but last children's subtrees
                for child in lexeme.children[:-1]:
                    subtree_str += '\n' + self.subtree_as_str_from_root(
                        child.lex_id,
                        form1=form1 + form2,
                        form2='│ ',
                        form3='└─')
                # add last child's subtree
                # it has slightly different formatting
                subtree_str += '\n' + self.subtree_as_str_from_root(
                    lexeme.children[-1].lex_id,
                    form1=form1 + form2,
                    form2='  ',
                    form3='└─')
            return subtree_str
        raise LexemeNotFoundError('lexeme with id {} not found'.format(root_id))

    def subtree_as_string(self, node, pos=None, morph=None):
        """
        Given lemma and optionally pos and morphological string,
        build a string visualizing the tree with the node as its root.
        """
        lex_id = self.get_id(node, pos=pos, morph=morph)
        root = self.get_root(lex_id)
        if root is None:
            root_id = lex_id
        else:
            root_id = root.lex_id
        return self.subtree_as_str_from_root(root_id)

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

    def add_derivation(self, child, parent, child_pos=None, parent_pos=None, child_morph=None, parent_morph=None,
                       force=False, ignore_if_exists=True):
        """
        Add an edge from the node with lex_id=parent_id
        to the node with lex_id=child_id checking for consistency.

        If force=True, (re)assign parent regardless of the fact
        that the node already has a parent.

        If ignore_if_exists=True, don't raise AlreadyHasParentError
        if the node already has a parent and it is the same as the one
        to be assigned.
        """

        child_id = self.get_id(child, pos=child_pos, morph=child_morph)
        parent_id = self.get_id(parent, pos=parent_pos, morph=parent_morph)
        if child not in self._data:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(child_id))
        if parent_id not in self._data:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(parent_id))
        child = self._data[child_id]
        parent = self._data[parent_id]

        if not force and child.parent_id != '' and child.parent_id is not None:
            actual_parent = self.get_lexeme(self._data[child_id].parent_id)
            parent_lemma = self._data[parent_id].lemma
            child_lemma = self._data[child_id].lemma
            if not ignore_if_exists or not partial_lexeme_match(actual_parent, parent_lemma, parent_pos, parent_morph):
                raise AlreadyHasParentError('node {} already has a parent '
                                            'assigned to it: {}'.format(
                    pretty_lexeme(child_lemma, child_pos, child_morph),
                    pretty_lexeme(actual_parent.lemma, actual_parent.pos, actual_parent.morph)))

        elif not self.exists_loop(parent_id, child_id):
            if self._data[child_id].parent_id != '' and force:
                # remove the child from old parent children
                old_parent = self._data[child.parent_id]
                self._data[child.parent_id] = old_parent._replace(
                    children=[new_child for new_child in old_parent.children if new_child != child])
            if self._data[parent_id].parent_id == child_id and force:
                # turned out we have to reverse the edge
                self._data[parent_id] = self._data[parent_id]._replace(parent_id=self._data[child_id].parent_id)
                child = self._data[child_id]
                self._data[child_id] = child._replace(
                    children=[new_child for new_child in child.children if new_child != parent])
                if self._data[parent_id].lex_id == self._data[parent_id].parent_id:
                    self._data[parent_id] = self._data[parent_id]._replace(parent_id='')
            self._data[child_id] = child._replace(parent_id=parent_id)
            self._data[parent_id].children.append(self._data[child_id])
        else:
            raise CycleCreationError('setting node {} as a parent of node {} '
                                     'would create a cycle'.format(parent_id, child_id))

    def exists_loop(self, parent_id, child_id=None):
        """
        Check if given node is not part of a loop
        :param parent_id: a node to be checked
        :param child_id: if supplied, the (possibly not existing) edge parent->child is considered
        :return:
        """
        nodes_traversed, current, visited = 0, self._data[parent_id], {self._data[child_id].lex_id}
        while current.parent_id != '' and current.lex_id not in visited:
            visited.add(current.lex_id)
            current = self._data[current.parent_id]
            nodes_traversed += 1

        if current.parent_id != '' and nodes_traversed > 0:
            return False
        return True

    def add_derivations(self, edge_list, force=False):
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
            self.add_derivation(child[0], parent[0], child_pos=child[1], parent_pos=parent[1],
                                child_morph=child[2], parent_morph=parent[2],force=force)

    def remove_derivation(self, child, parent, child_pos=None, parent_pos=None,
                           child_morph=None, parent_morph=None):
        """
        Remove an edge from the node with lex_id=parent_id
        to the node with lex_id=child_id checking for consistency.
        """
        child_id = self.get_id(child, pos=child_pos, morph=child_morph)
        parent_id = self.get_id(parent, pos=parent_pos, morph=parent_morph)
        if child_id not in self._data:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(child_id))
        child = self._data[child_id]
        if child.parent_id != parent_id:
            return False
        if parent_id not in self._data:
            raise LexemeNotFoundError('lexeme with id {} not found'.format(parent_id))
        parent = self._data[parent_id]
        new_children = [child
                        for child
                        in self._data[child.parent_id].children
                        if child.lex_id != child_id]
        self._data[child.parent_id] = self._data[child.parent_id]._replace(children=new_children)
        self._data[child_id] = child._replace(parent_id='')
        return True


    def remove_derivations(self, edge_list):
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
            self.remove_derivation(child[0], parent[0], child_pos=child[1], parent_pos=parent[1],
                             child_morph=child[2], parent_morph=parent[2])

    def find_lexeme_pair(self, source_lemma, source_pos, target_lemma, target_pos):
        if source_lemma is None or source_pos is None or target_lemma is None or target_pos is None:
            return None, None

        source_candidates = self._sort_nodes(self.get_ids(source_lemma, source_pos))
        target_candidates = self._sort_nodes(self.get_ids(target_lemma, target_pos))

        # If one of them doesn't exist, we have no clues as to which candidate from the others to choose. Return the first one.
        if (len(source_candidates) == 0 or len(target_candidates) == 0):
            return (source_candidates if len(source_candidates) > 0 else None,
            target_candidates if len(target_candidates) > 0 else None)


        if (len(source_candidates) == 1 and len(target_candidates) == 1):
            return (source_candidates[0], target_candidates[0])


        # Try to find one that is already connected. If it is there, return it.
        for source_candidate in  source_candidates:
            for target_candidate in target_candidates:
                source_candidate = self._data[source_candidate]
                target_candidate = self._data[target_candidate]
                if target_candidate.parent_id != '' and target_candidate.parent_id == source_candidate.lex_id:
                    return (source_candidate, target_candidate)

        # TODO:  Try to find a pair with matching homonym numbers.

        unconnected_targets = [target for target in target_candidates if self._data[target].parent_id == '']

        return (self._data[source_candidates[0]],
                self._data[unconnected_targets[0]] if len(unconnected_targets) == 0 else self._data[target_candidates[0]])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        derinet = DeriNet(sys.argv[1])
        derinet.save("output")
    else:
        derinet = DeriNet('derinet-1-2.tsv')
