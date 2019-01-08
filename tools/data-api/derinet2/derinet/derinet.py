#! /usr/bin/env python3


import os
import sys
import locale
import logging
from time import time
from itertools import chain

from .utils import pretty_lexeme, partial_lexeme_match, Node, flatten_list, no_parent, \
    LexemeNotFoundError, ParentNotFoundError, AlreadyHasParentError, CycleCreationError, \
    LexemeAlreadyExistsError, UnknownFileVersion


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
                 '_execution_context' # Signature of the currently-running module, if we launch DeriNet from the scenario manager.
                 ]

    def __init__(self, fname=None, version="1.4", locales='cs'):
        self._ids2internal = {}
        self._roots = set()
        self._ids = []
        self._execution_context = None
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
            split_line = line.strip('\n').split('\t')
            if version.startswith("1"):
                if len(split_line) != 5:
                    logger.warning("Failed to read lexeme on line %d. Invalid line format: get %d field, expected %d",
                                  i, len(split_line), 5)
                    continue
                else:
                    lex_id, lemma, morph, pos, parent_id = split_line
                    data.append(Node(i, lex_id, lemma, morph, pos, tag_mask="",
                                 parent_id=""
                                 if no_parent(parent_id)
                                 else int(parent_id),
                                 composition_parents=[],
                                 misc={},
                                 children=[]))
            elif version.startswith("2"):
                if len(split_line) != 8:
                    logger.warning(
                        "Failed to read lexeme on line %d. Invalid line format: get %d field, expected %d",
                        i, len(split_line), 8)
                    continue
                else:
                    lex_id, lemma, morph, pos, tag_mask, parent_id, composition_parents, misc = split_line
                    data.append(Node(i, lex_id, lemma, morph, pos, tag_mask,
                                 parent_id=""
                                 if no_parent(parent_id)
                                 else self._ids2internal[parent_id],
                                 composition_parents=[edge.split('-') for edge in composition_parents.split(',')],
                                 misc=misc,
                                 children=[]))
            else:
                raise UnknownFileVersion

            if no_parent(parent_id):
                    self._roots.add(i)
            if version.startswith("2"):
                self._ids2internal[lex_id] = i
            else:
                self._ids2internal[int(lex_id)] = i
            index.setdefault(lemma, {})
            index[lemma].setdefault(pos, {})
            index[lemma][pos][morph] = i
        return data, index

    def _populate_nodes(self, populate_children=True, replace_ids=True):
        """Populate children for all nodes."""
        for node_id, node in enumerate(self._data):
            if no_parent(node):
                continue
            parent_id = node.parent_id
            if replace_ids:
                if node.parent_id not in self._ids2internal:
                    continue
                parent_id = self._ids2internal[node.parent_id]

                composition_parents = [(self._ids2internal[p1], self._ids2internal[p2]) for p1, p2 in node.composition_parents]
                self._data[node_id] = node._replace(parent_id=parent_id, composition_parents=composition_parents)
            if populate_children:
                self._data[parent_id].children.append(node.lex_id)

        if replace_ids:
            new_roots = set()
            for root in self._roots:
                if root not in self._ids2internal:
                    new_roots.add(root)
                else:
                    new_roots.add(self._ids2internal[root])
            self._roots = new_roots

    def _valid_lex_id_or_raise(self, lex_id, exc_cls=LexemeNotFoundError):
        if lex_id < 0 or lex_id > len(self._data):
            raise exc_cls('Lexeme with id "{}" not found'.format(lex_id))

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
        if len(self._data) > 0 and len(self._data) - 1 != self._data[-1].lex_id:
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
                                          if no_parent(node)
                                          # TODO: measure if faster than use self._data[node.parent_id].lex_id
                                          else reverse_id[node.parent_id],
                                          children=[])
            self._index[node.lemma][node.pos][node.morph] = i

        # repopulate children
        self._populate_nodes(replace_ids=False)
        new_roots = set()
        for root in self._roots:
            new_roots.add(reverse_id[root])
        self._roots = new_roots

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
            self.sort()
        logger.info('Saving snapshot to "%s"', fname)
        btime = time()
        with open(fname, 'w', encoding='utf-8') as ofile:
            for i, root in enumerate(sorted(self._roots)):
                self.save_tree(i, root, ofile)
        logger.info('Saved in {:.2f} s.'.format(time() - btime))

    def save_tree(self, no, root, ofile):
        try:
            for i, el in enumerate(flatten_list(self.get_subtree(root))):
                lex_id, pretty_id, lemma, morph, pos, tag_mask, parent_id, composition_parents, misc = el[:-1]
                pretty_id = "{}.{}".format(no, i)
                self._ids[lex_id] = pretty_id
                if parent_id != '':
                    parent_id = self._ids[parent_id]
                print(pretty_id, lemma, morph, pos, tag_mask,
                      parent_id,  [(self._ids[p1], self._ids[p2]) for p1, p2 in composition_parents], misc,
                      sep="\t", file=ofile)
        except LexemeNotFoundError:
            logger.error('Failed to save tree with root %s', str(root))

    def add_lexeme(self, node):
        """
        Add a new node to the database.

        Doesn't add any derivations, you have to take care of these yourself.
        In fact, the node mustn't contain any outstanding derivational links,
        otherwise an assertion is violated.
        """

        # Check that node is not present yet.
        if self.lexeme_exists(node):
            raise LexemeAlreadyExistsError("lexeme {} already exists in the database".format(pretty_lexeme(node.lemma, node.pos, node.morph)))

        # Find the position to insert the node to. This also becomes its internal ID.
        current_index = len(self._data)


        # Check that the necessary fields are filled in properly.
        # TODO check types of fields – most should be strings, some ints, some arrays/dicts.

        # Check that the internal ID is not set and set it to the future node position in the data array.
        assert node.lex_id is None, "Node %s has filled lex_id. That field is internal, do not set it yourself" % (pretty_lexeme(node.lemma, node.pos, node.morph))
        node = node._replace(lex_id=current_index)

        # If the node doesn't have an external ID, set it. This may be required somewhere. TODO check whether and where.
        if node.pretty_id is None:
            node = node._replace(pretty_id="")

        # Check that at least the basic node information is set.
        assert node.lemma is not None
        assert node.pos is not None
        if node.morph is None:
            # If there is no m-layer Hajič's morphology information (which, apart from Czech,
            #  there isn't), set it to the lemma.
            # This might be actually not the best way of handling things, but whatever.
            #  Maybe we'd rather like to leave the field blank in that case.
            node = node._replace(morph=node.lemma)

        # Check that the node doesn't contain any derivational information and stands completely on its own.
        assert no_parent(node), "The newly added node '%s' must not have any parents set" % (pretty_lexeme(node.lemma, node.pos, node.morph))
        assert node.composition_parents is None or node.composition_parents == [], "The newly added node '%s' must not have any parents set" % (pretty_lexeme(node.lemma, node.pos, node.morph))
        assert node.children is None or node.children == [], "The newly added node '%s' must not have any children set" % (pretty_lexeme(node.lemma, node.pos, node.morph))

        if node.tag_mask is None:
            node = node._replace(tag_mask="")
        if node.misc is None:
            node = node._replace(misc={})

        # Add it.

        self._data.append(node)

        # The new node is always a root, so record it as such.
        self._roots.add(node.lex_id)

        if node.pretty_id:
            if node.pretty_id in self._ids2internal:
                raise LexemeAlreadyExistsError("lexeme id {} already exists in the database".format(node.pretty_id))
            self._ids2internal[node.pretty_id] = current_index
        else:
            # Not having a pretty_id is not a problem, self._ids2internal is not actually read anywhere.
            logger.info("Lexeme %s doesn't have an ID" % pretty_lexeme(node.lemma, node.pos, node.morph))

        self._index.setdefault(node.lemma, {})
        self._index[node.lemma].setdefault(node.pos, {})
        self._index[node.lemma][node.pos][node.morph] = node.lex_id

    def lexeme_exists(self, node):
        """Return a boolean indicating whether the node is already in the database.

        The method checks node.lemma, node.pos and node.morph for equality with any lexeme in the database.
        If node has a truthy pretty_id, it is checked as well, otherwise it is ignored."""

        similar_lexemes = self.search_lexemes(node.lemma, node.pos, node.morph)
        if similar_lexemes and not node.pretty_id: # FIXME what exactly is the pretty_id? Can it be an int? If so, fix this for the case when pretty_id == 0.
            # The candidate matches in lemma, pos and morph and there is no ID to check.
            return True
        else:
            # We have to check the ID for a match.
            for candidate in similar_lexemes:
                if candidate.pretty_id == node.pretty_id:
                    return True
        return False

    def get_lexeme(self, node, pos=None, morph=None):
        """
            Get instance of the specified node
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity
            :return: instance of the parent node
        """
        lex_id = self.get_id(node, pos=pos, morph=morph)
        self._valid_lex_id_or_raise(lex_id)
        return self._data[lex_id]

    def show_lexeme(self, node, pos=None, morph=None):
        """
            Get representation of the specified node
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity
            :return: instance of the parent node
        """
        lexeme = self.get_lexeme(node, pos, morph)
        return (lexeme.lemma, lexeme.pos, lexeme.morph)

    def search_lexemes(self, lemma, pos=None, morph=None, allow_fallback=False):
        """
        Search for all lexemes that satisfy given lemma, pos and morph,
        and return their representations. If allow_fallback is set, also
        search for lemma and pos only, disregarding morph.
        """
        lexeme_ids = self.get_ids(lemma, pos=pos, morph=morph)
        if len(lexeme_ids) == 0 and allow_fallback and morph is not None:
            lexeme_ids = self.get_ids(lemma, pos=pos, morph=None)
            if lexeme_ids:
                logger.warning("Used fallback to search for {} {}, found {}".format(morph, pos, ", ".join([self._data[lexeme_id].morph for lexeme_id in lexeme_ids])))
        return [self._data[lexeme_id] for lexeme_id in lexeme_ids]

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
        assert node is not None
        if isinstance(node, int):
            return node
        if isinstance(node, Node):
            # FIXME the code should be really restructured, so that we don't
            #  need to search for fully specified nodes by lemma, pos and morph.
            # It should be possible to search by ID.
            assert pos is None and morph is None
            lemma = node.lemma
            pos = node.pos
            morph = node.morph
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
        """
            Get parent of the specified node
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity
            :return: instance of the parent node
        """
        lex_id = self.get_id(node, pos=pos, morph=morph)
        self._valid_lex_id_or_raise(lex_id)
        parent_id = self._data[lex_id].parent_id
        if no_parent(parent_id) or parent_id > len(self._data):
            return None
        return self._data[parent_id]

    def get_root(self, node, pos=None, morph=None):
        """
            Get root  of the specified node's tree
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity
            :return: instance of the respective tree's root
        """
        lex_id = self.get_id(node, pos=pos, morph=morph)
        self._valid_lex_id_or_raise(lex_id)
        parent_id = self._data[lex_id].parent_id
        if no_parent(parent_id):
            return self._data[lex_id]
        current = self._data[parent_id]
        while current.parent_id != '':
            current = self._data[current.parent_id]
        return current

    def get_children(self, node, pos=None, morph=None):
        """
            Get children of the specified node
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity
            :return: list of found children
        """
        lexeme = self.get_lexeme(node, pos=pos, morph=morph)
        return [self._data[child_id] for child_id in lexeme.children]

    def get_subtree(self, node, pos=None, morph=None):
        """
            Recursively build a list representing the tree
            with the specified node as its root.
            :param node: identification of the node (instance, lemma or id)
            :param pos: POS tag to resolve ambiguity
            :param morph: morph string to resolve ambiguity

            :return tree of the form:
                [root, [[ch1, [[ch1.1, ...], [ch1.2, ...], ...]], [ch2, ...]]
        """
        lexeme = self.get_lexeme(node, pos=pos, morph=morph)
        return [lexeme, [self.get_subtree(child)
                         for child in lexeme.children]]

    def subtree_as_str_from_root(self, root, pos=Node, morph=None,
                                 form1='',
                                 form2='  ',
                                 form3=''):
        """
        Recursively build a string visualizing the tree
        with the specified node as its root.
        """
        lexeme = self.get_lexeme(root, pos=pos, morph=morph)
        subtree_str = form1 + form3
        subtree_str += '\t'.join(str(item) for item in lexeme[:-1])
        if lexeme.children != []:
            # add all but last children's subtrees
            for child in lexeme.children[:-1]:
                subtree_str += '\n' + self.subtree_as_str_from_root(
                    child, pos=pos, morph=morph,
                    form1=form1 + form2,
                    form2='│ ',
                    form3='└─')
            # add last child's subtree
            # it has slightly different formatting
            subtree_str += '\n' + self.subtree_as_str_from_root(
                lexeme.children[-1], pos, morph,
                form1=form1 + form2,
                form2='  ',
                form3='└─')
        return subtree_str

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

    def iter_lexemes(self):
        """
        Iterate through all lexemes in the database in an unspecified order,
        visiting each one exactly once. The method is guaranteed to work even
        if new lexemes are added (they will be visited) or removed (lexemes
        removed before being visited will not be visited) while iterating.
        """

        # Use a while-cycle to ensure correctness even with concurrent changes
        #  of the datastore.
        i = 0
        while i < len(self._data):
            lexeme = self._data[i]

            assert isinstance(lexeme, Node)
            yield lexeme

            i += 1

    def iter_roots(self):
        """
        Iterate through all roots of all trees. Concurrent edits are not visible,
        therefore newly added roots are not visited and removed roots will be
        visited anyway.
        """
        roots = sorted(self._roots)
        for root_id in roots:
            root = self._data[root_id]
            assert isinstance(root, Node)
            assert root.parent_id == "", "Node {} is cached as a root, but has a parent".format(pretty_lexeme(root.lemma, root.pos, root.morph))
            yield root

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
        Add an edge from the node specified by 'parent'
        to the node specified by 'child' checking for consistency.

        If force=True, (re)assign parent regardless of the fact
        that the node already has a parent.

        If ignore_if_exists=True, don't raise AlreadyHasParentError
        if the node already has a parent and it is the same as the one
        to be assigned.
        """

        child_id = self.get_id(child, pos=child_pos, morph=child_morph)
        parent_id = self.get_id(parent, pos=parent_pos, morph=parent_morph)
        self._valid_lex_id_or_raise(child_id)
        self._valid_lex_id_or_raise(parent_id, ParentNotFoundError)
        child = self._data[child_id]
        parent = self._data[parent_id]

        if not force and child.parent_id != '' and child.parent_id is not None:
            actual_parent = self.get_lexeme(child.parent_id)
            parent_lemma = parent.lemma
            child_lemma = child.lemma
            if not ignore_if_exists or not partial_lexeme_match(actual_parent, parent_lemma, parent_pos, parent_morph):
                raise AlreadyHasParentError('node {} already has a parent '
                                            'assigned to it: {}'.format(
                    pretty_lexeme(child_lemma, child_pos, child_morph),
                    pretty_lexeme(actual_parent.lemma, actual_parent.pos, actual_parent.morph)))

        elif not self.exists_loop(parent_id, child_id):
            if child.parent_id != '' and force:
                # remove the child from old parent children
                old_parent = self._data[child.parent_id]
                self._data[child.parent_id] = old_parent._replace(
                    children = [new_child for new_child in old_parent.children if new_child != child.lex_id]
                )
                parent = self._data[parent_id]
            if parent.parent_id == child_id and force:
                # turned out we have to reverse the edge
                self._data[parent_id] = parent._replace(parent_id=child.parent_id)
                parent = self._data[parent_id]
                child = self._data[child_id]
                self._data[child_id] = child._replace(
                    children=[new_child for new_child in child.children if new_child != parent.lex_id]
                )
                if parent.lex_id == parent.parent_id:
                    self._data[parent_id] = parent._replace(parent_id='')

            if self.get_root(child_id).lex_id == child_id:
                # the new children was actually a root node
                self._roots.remove(child_id)
            self._data[child_id] = child._replace(parent_id=parent_id)
            self._data[parent_id].children.append(child_id)
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
        current_id = self._data[parent_id].lex_id # ID of the node we're about to visit.
        visited = set() # A set of already visited node IDs.

        if child_id is not None:
            visited.add(self._data[child_id].lex_id)

        while self.get_parent(current_id) and current_id not in visited:
            visited.add(current_id)
            current_id = self.get_parent(current_id).lex_id

        if current_id in visited:
            return True
        else:
            return False

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
                                child_morph=child[2], parent_morph=parent[2], force=force)

    def remove_derivation(self, child, parent, child_pos=None, parent_pos=None,
                           child_morph=None, parent_morph=None):
        """
        Remove an edge from the node specified by 'parent'
        to the node specified by 'child' checking for consistency.
        """
        child_id = self.get_id(child, pos=child_pos, morph=child_morph)
        parent_id = self.get_id(parent, pos=parent_pos, morph=parent_morph)
        self._valid_lex_id_or_raise(child_id)
        child = self._data[child_id]
        if child.parent_id != parent_id:
            return False
        self._valid_lex_id_or_raise(parent_id, ParentNotFoundError)
        parent = self._data[parent_id]
        new_children = [ch for ch in self._data[child.parent_id].children
                        if ch != child_id]
        self._data[child.parent_id] = self._data[child.parent_id]._replace(children=new_children)
        self._data[child_id] = child._replace(parent_id='')
        self._roots.add(child_id)
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
        for source_candidate in source_candidates:
            for target_candidate in target_candidates:
                source_candidate = self._data[source_candidate]
                target_candidate = self._data[target_candidate]
                if target_candidate.parent_id != '' and target_candidate.parent_id == source_candidate.lex_id:
                    return (source_candidate, target_candidate)

        # TODO:  Try to find a pair with matching homonym numbers.

        unconnected_targets = [target for target in target_candidates if no_parent(self._data[target])]

        return (self._data[source_candidates[0]],
                self._data[unconnected_targets[0]] if len(unconnected_targets) == 0 else self._data[target_candidates[0]])

    def set_execution_context(self, context):
        self._execution_context = context


if __name__ == "__main__":
    if len(sys.argv) == 2:
        derinet = DeriNet(sys.argv[1])
        derinet.save("output")
    else:
        derinet = DeriNet('derinet-1-2.tsv')
