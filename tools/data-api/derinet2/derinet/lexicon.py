import enum
import json
import pickle
import re

from .lexeme import Lexeme
from .relation import DerivationalRelation
from .utils import DerinetError, DerinetFileParseError, parse_v1_id, parse_v2_id, format_kwstring, parse_kwstring


# The main database.
# Has a list of Lexemes and some caches of their properties for fast lookup.
# Must support:
# add lexeme (without any links),
# remove lexeme (what about the links? Delete, reconnect, raise an error?)
# add link (n-to-n; labelled as derivation, compounding, …; tagged by a semantic label or whatever)
# remove link (keeping all the endpoints)
# iterate over lexemes
# get all roots (what is the definition of a root?)


# FIXME: lexemes and links should be created solely through the Network object.

# Konstruktor – možná parametr se jménem databáze (pro rozličení různých DB)
# load(filename, pickle=False)
# save(filename, pickle=False)
# create_lexeme(…)
# remove_lexeme(…), remove_subtree(…)

# search_lexemes(…)
# iter_lexemes, iter_roots (?), iter_relations

# add_derivation, add_composition, … – create new relations
# remove_derivation, … – delete relations.
#  TODO Should the signature be (source, target), or (relation)?
#        If the latter, does a single remove_relation() suffice?
# TODO Where should we check for cycles? In Relation, in Lexeme or in Lexicon?
#       An argument for checking in the Lexicon is, that we can check in both directions at once
#       and only assign anything once the checks are done. If we checked in Lexeme.…parent… and
#       Lexeme.…child…, we would have to undo setting one of them if the other one failed.
#           But maybe we could check when creating the Relation itself? But perhaps that class should
#       be kept as simple as possible and all the complexity should be concentrated in the Lexicon.
# FIXME I've made my mind. The checks should be done in Relation. When creating a new Relation,
#        it should check for cycles and update the records in all endpoints. When deleting it,
#        the Relation itself in its destructor should remove itself from the Lexemes. That way
#        everything should stay as simple as possible.
#        TODO write tests for that, and then the code.

@enum.unique
class Format(enum.Enum):
    DERINET_V1 = 1
    DERINET_V2 = 2
    PICKLE_V4 = 3


class Lexicon(object):
    __slots__ = [   # If you update __slots__, make sure to also update _load_pickle_v4!
        "_data",   # An array of Lexemes.
        "_index",  # _index[lemma][pos] = [Lexeme]
    ]

    def __init__(self):
        # TODO maybe add a parameter with the database name in it? It could be used for
        #  distinguishing multiple databases from one another.
        self._data = []
        self._index = {}

    def load(self, data_source, fmt: Format = Format.DERINET_V2):
        """
        Load data from data_source and append them to this instance of the lexicon.
        Returns the modified lexicon object for convenience.

        :param data_source: A string containing the file name to open or an object to read data
        from – typically an open file handle or a list of strings.
        :param fmt: The format of the data_source.
        :return: The lexicon with the new data in it.
        """
        switch = {
            Format.DERINET_V1: self._load_derinet_v1,
            Format.DERINET_V2: self._load_derinet_v2,
            Format.PICKLE_V4: self._load_pickle_v4
        }

        if fmt not in switch:
            raise ValueError(
                "Loading from format {} is not supported, format type not recognized.".format(fmt)
            )

        try:
            switch[fmt](data_source)
        except DerinetFileParseError:
            raise
        except DerinetError:
            raise DerinetFileParseError("An error happened while parsing input file.")

        return self

    def _load_derinet_v1(self, data_source):
        close_at_end = False
        if isinstance(data_source, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_source = open(
                data_source,
                "rt",
                buffering=16384,
                encoding="utf-8",
                errors="strict",
                newline="\n"
            )

        id_map = {}
        parent_map = {}

        try:
            for line_nr, line in enumerate(data_source, start=1):
                # Read a new line, get rid of the newline at the end and
                line = line.rstrip("\n")
                fields = line.split("\t")

                if len(fields) != 5:
                    # The line was too short or too long; report an error.
                    raise DerinetFileParseError("Line nr. {} '{}' has {} fields instead of the expected 5.".format(line_nr, line, len(fields)))

                this_id_str, lemma, techlemma, pos, parent_id_str = fields

                # Parse out the lexeme ID.
                try:
                    this_id = parse_v1_id(this_id_str)
                except ValueError:
                    raise DerinetFileParseError("Unparseable ID '{}' encountered on line nr. {} '{}'.".format(this_id_str, line_nr, line))

                # Check that a lexeme with an identical ID doesn't exist yet.
                if this_id in id_map:
                    raise DerinetFileParseError("Lexeme with ID {} defined a second time on line nr. {} '{}'.".format(this_id, line_nr, line))

                if not lemma:
                    raise DerinetFileParseError("Empty lemma encountered in lexeme ID {} on line {} '{}'".format(this_id_str, line_nr, line))

                misc = {"techlemma": techlemma}

                if len(pos) > 1:
                    extra_pos_bits = pos[1:]
                    pos = pos[0]
                    if "C" in extra_pos_bits:
                        misc["is_compound"] = True
                    if "U" in extra_pos_bits:
                        misc["is_nonderived"] = True

                # Create the lexeme itself, without any links.
                lexeme = self.create_lexeme(lemma, pos, misc=misc)

                # Record the lexeme ID for creating the links in the future.
                id_map[this_id] = lexeme

                if parent_id_str:
                    # This lexeme has a parent.
                    # We'll have to create a link to the parent. Record this fact.
                    try:
                        parent_map[this_id] = parse_v1_id(parent_id_str)
                    except ValueError:
                        raise DerinetFileParseError("Unparseable parent ID '{}' encountered on line nr. {} '{}'.".format(parent_id_str, line_nr, line))
        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

        # Now that all lexemes have been loaded, create the links.
        for child_id, parent_id in parent_map.items():
            child_lexeme = id_map[child_id]
            if parent_id in id_map:
                parent_lexeme = id_map[parent_id]
            else:
                raise DerinetFileParseError("Lexeme with ID {} not found but referenced by ID {}".format(parent_id, child_id))

            self.add_derivation(parent_lexeme, child_lexeme)

    def _load_derinet_v2(self, data_source):
        close_at_end = False
        if isinstance(data_source, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_source = open(
                data_source,
                "rt",
                buffering=16384,
                encoding="utf-8",
                errors="strict",
                newline="\n"
            )

        comment_regex = re.compile(r"^\s*#")
        id_map = {}
        seen_trees = set()
        this_tree = None

        try:
            for line_nr, line in enumerate(data_source, start=1):
                if comment_regex.match(line):
                    # The line is a comment. Ignore it fully.
                    continue

                line = line.rstrip("\n")

                if not line:
                    # The line is empty → block separator.
                    if this_tree is not None:
                        # We've just finished reading a tree. Record it to the set of finished trees.
                        seen_trees.add(this_tree)
                        this_tree = None
                    continue

                fields = line.split("\t", maxsplit=9)

                if len(fields) != 10:
                    # The line was too short; report an error.
                    raise DerinetFileParseError("Line nr. {} '{}' is too short, more data required.".format(line_nr, line))

                lex_id_str, lemid, lemma, pos, feats, segmentation, parent_id_str, reltype, otherrels, misc = fields

                try:
                    lex_id = parse_v2_id(lex_id_str)
                except ValueError:
                    raise DerinetFileParseError("Unparseable ID '{}' encountered on line nr. {} '{}'.".format(lex_id_str, line_nr, line))
                tree_id, lex_in_tree_id = lex_id

                # If the ID was used already, raise an error.
                if lex_id in id_map:
                    raise DerinetFileParseError("ID {} defined a second time at line nr. {}".format(lex_id_str, line_nr))

                if this_tree is None:
                    # We've just started reading this tree.
                    # Check that the tree_id was not seen before.
                    # If it was, raise an error.
                    if tree_id in seen_trees:
                        raise DerinetFileParseError("Tree with ID {} encountered in a second block at line nr. {}".format(tree_id, line_nr))
                    else:
                        this_tree = tree_id
                else:
                    if tree_id != this_tree:
                        # Tree ID mismatch.
                        raise DerinetFileParseError("Lexeme with tree ID {} found in a block of tree ID {} at line nr. {}".format(tree_id, this_tree, line_nr))

                # TODO Check that the block ID is constant in a block and not seen
                #  in other blocks, and that the lexeme-in-block ID is unique in a block.

                if not lemma:
                    raise DerinetFileParseError("Empty lemma encountered in lexeme ID {} on line {} '{}'".format(lex_id_str, line_nr, line))

                feats_list = parse_kwstring(feats)
                if len(feats_list) == 0:
                    feats = {}
                elif len(feats_list) == 1:
                    feats = feats_list[0]
                else:
                    raise DerinetFileParseError() # TODO Write a proper error message.

                segmentation = parse_kwstring(segmentation)

                reltype_list = parse_kwstring(reltype)
                if len(reltype_list) == 0:
                    reltype = {}
                elif len(reltype_list) == 1:
                    reltype = feats_list[0]
                else:
                    raise DerinetFileParseError() # TODO Write a proper error message.

                otherrels = parse_kwstring(otherrels)

                try:
                    misc = json.loads(misc)
                except json.decoder.JSONDecodeError:
                    raise DerinetFileParseError("Couldn't parse the JSON-encoded misc section of lexeme {} at line {} '{}'".format(lex_id_str, line_nr, line))

                lexeme = self.create_lexeme(lemma, pos, lemid=lemid, feats=feats, segmentation=segmentation, misc=misc)

                # We already know that the ID wasn't encountered previously.
                id_map[lex_id] = lexeme

                if parent_id_str != "":
                    try:
                        parent_id = parse_v2_id(parent_id_str)
                    except ValueError:
                        raise DerinetFileParseError("Unparseable parent ID '{}' encountered on line nr. {} '{}'.".format(parent_id_str, line_nr, line))

                    parent_tree_id, parent_lex_in_tree_id = parent_id

                    # Check that the the main reference does not cross trees.
                    if parent_tree_id != this_tree:
                        raise DerinetFileParseError("Lexeme with ID {} on line nr. {} refers to an out-of-tree lexeme ID {}".format(lex_id_str, line_nr, parent_id_str))

                    # The file structure guarantees that the primary parent was encountered before all its children.
                    # Check that this holds.
                    if parent_id in id_map:
                        parent_lexeme = id_map[parent_id]
                    else:
                        raise DerinetFileParseError("Lexeme with ID {} on line nr. {} refers to an in-tree lexeme ID {}, which was not encountered yet.".format(lex_id_str, line_nr, parent_id_str))

                    # TODO Check that reltype is derivation.
                    self.add_derivation(parent_lexeme, lexeme)

                # TODO Parse secondary relations.
        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

    def _load_pickle_v4(self, data_source):
        close_at_end = False
        if isinstance(data_source, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_source = open(data_source, "rb")
        try:
            # We can't unpickle self, so load the lexicon slots individually.
            new_lexicon = pickle.load(data_source)

            if not isinstance(new_lexicon, Lexicon):
                raise DerinetFileParseError("The pickled stream does not contain a Lexicon")

            self._data = new_lexicon._data  # pylint: disable=protected-access
            self._index = new_lexicon._index  # pylint: disable=protected-access
        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

    def save(self, data_sink, fmt: Format = Format.DERINET_V2):
        switch = {
            Format.DERINET_V1: self._save_derinet_v1,
            Format.DERINET_V2: self._save_derinet_v2,
            Format.PICKLE_V4: self._save_pickle_v4
        }

        if fmt not in switch:
            raise ValueError(
                "Saving to format {} is not supported, format type not recognized.".format(fmt)
            )

        switch[fmt](data_sink)

    def _save_derinet_v1(self, data_sink):
        """Serialize the database as a DeriNet-1.X TSV file.

        Be aware that since this new API doesn't use IDs internally, they are not preserved when saving.
        This means that loading a database from 1.X TSV and storing it again may rename the IDs."""

        close_at_end = False
        if isinstance(data_sink, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_sink = open(
                data_sink,
                "wt",
                encoding="utf-8",
                errors="strict",
                newline="\n"
            )

        try:
            lex_id_map = {lexeme: i for i, lexeme in enumerate(self.iter_lexemes())}
            for lexeme, i in lex_id_map.items():
                if lexeme.parent is not None:
                    parent_id = str(lex_id_map[lexeme.parent])
                else:
                    parent_id = ""
                print(
                    i,
                    lexeme.lemma,
                    lexeme.techlemma,
                    lexeme.pos,
                    parent_id,
                    sep="\t", end="\n", file=data_sink
                )
        finally:
            data_sink.flush()
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_sink.close()

    def _save_derinet_v2(self, data_sink):
        close_at_end = False
        if isinstance(data_sink, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_sink = open(
                data_sink,
                "wt",
                encoding="utf-8",
                errors="strict",
                newline="\n"
            )

        try:
            id_mapping = {}

            for tree_id, root in enumerate(self.iter_trees(sort=True)):
                if tree_id > 0:
                    # Separate unrelated trees by a newline.
                    print("", end="\n", file=data_sink)

                for lex_in_tree_id, lexeme in enumerate(root.iter_subtree(sort=True)):
                    full_id = "{}.{}".format(tree_id, lex_in_tree_id)

                    if lexeme in id_mapping:
                        raise Exception("An error occurred while saving data: Lexeme {} processed twice".format(lexeme))
                    else:
                        id_mapping[lexeme] = full_id

                    if lexeme.parent:
                        if lexeme.parent in id_mapping:
                            parent_id = id_mapping[lexeme.parent]
                        else:
                            raise Exception("An error occurred while saving data: Lexeme {} processed before its parent".format(lexeme))
                    else:
                        parent_id = ""

                    reltype = {}
                    if lexeme.parent_relation:
                        reltype = lexeme.parent_relation.type

                    print(
                        full_id,
                        lexeme.lemid,
                        lexeme.lemma,
                        lexeme.pos,
                        format_kwstring([lexeme.feats]),
                        format_kwstring([segment for segment in lexeme.segmentation if segment["type"] != "implicit"]),
                        parent_id,
                        format_kwstring([reltype]),
                        format_kwstring(lexeme.otherrels),
                        json.dumps(lexeme.misc, ensure_ascii=False, allow_nan=False, indent=None, sort_keys=True),
                        sep="\t", end="\n", file=data_sink
                    )
        finally:
            data_sink.flush()
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_sink.close()

    def _save_pickle_v4(self, data_sink):
        close_at_end = False
        if isinstance(data_sink, str):
            # Act as if data_source is a filename to open.
            # Since we opened the file ourselves, we must close it later.
            close_at_end = True
            data_sink = open(data_sink, "wb")

        try:
            pickle.dump(self, data_sink, protocol=4)
        finally:
            data_sink.flush()
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_sink.close()

    def create_lexeme(self, lemma: str, pos: str, lemid: str = None, feats=None, segmentation=None, misc: dict = None):
        """
        Create a new Lexeme and add it to the database as a root of a new tree.

        :param lemma: The lemma of the lexeme, preferably recognizable both by speakers of the language
                and by language processing tools. If the lemmas for those two uses differ, specify
                the machine-readable form as the "techlemma" key in `misc`.
        :param pos: The part-of-speech tag of the lexeme, preferably one of the Universal POS tags;
                see https://universaldependencies.org/u/pos/
        :param lemid: An universal identifier of the lexeme for distinguishing homonyms from one another.
        :param feats: Morphological features of the lexeme other than the part-of-speech tag, preferably
                from the set of Universal features; see https://universaldependencies.org/u/feat/index.html
                TODO specify the format.
        :param segmentation: Specification of the internal morphological (morphematical) structure of the word.
                TODO specify the format.
        :param misc: Other features not covered elsewhere. You can use this field for storing your own data
                together with the lexemes. Make sure that the contents are serializable to JSON, i.e. strings
                as keys and dicts, lists or primitive types as values.
        :return: The new lexeme.
        """
        lexeme = Lexeme(lemma, pos, lemid, feats, segmentation, misc)

        # Add the lexeme to the datastore.
        self._data.append(lexeme)

        # Add the lexeme to the lemma-pos index.
        # This is too slow, do not use: # self._index.setdefault(lexeme.lemma, {}).setdefault(lexeme.pos, []).append(lexeme)
        if lexeme.lemma not in self._index:
            self._index[lexeme.lemma] = {lexeme.pos: [lexeme]}
        elif lexeme.pos not in self._index[lexeme.lemma]:
            self._index[lexeme.lemma][lexeme.pos] = [lexeme]
        else:
            self._index[lexeme.lemma][lexeme.pos].append(lexeme)

        # TODO add the lexeme to the other indices.

        return lexeme

    def delete_lexeme(self, lexeme):
        raise NotImplementedError()

    def delete_subtree(self, lexeme):
        raise NotImplementedError()

    def get_lexemes(
            self,
            lemma: str,
            pos: str = None,
            techlemma: str = None,
            techlemma_match_fuzzy: bool = False
    ):
        match_set = self._index.get(lemma, {})

        if pos is not None:
            match_list = match_set.get(pos, [])
        else:
            # Flatten the list of lists into a single list.
            match_list = [lexeme for pos_list in match_set.values() for lexeme in pos_list]

        if techlemma is not None:
            match_list_techlemma = [lexeme for lexeme in match_list if lexeme.techlemma == techlemma]
            if techlemma_match_fuzzy and not match_list_techlemma:
                # If the user wants to use the techlemmas only as an advice and there is no lexeme matching
                #  the techlemma, fall back to non-techlemmatical matches.
                match_list_techlemma = match_list
        else:
            match_list_techlemma = match_list

        return match_list_techlemma

    def iter_lexemes(self, sort=False):
        """
        Iterate through all lexemes in the database in an unspecified order, visiting each one exactly once.

        The method is not guaranteed to work with concurrent changes to the datastore while iterating.
        """

        if sort:
            data = sorted(self._data)
        else:
            # TODO maybe copy the data to ensure concurrent changes won't do weird things?
            data = self._data

        for lexeme in data:
            # if lexeme is not None:
            assert isinstance(lexeme, Lexeme)
            yield lexeme

    def iter_trees(self, sort=False):
        # TODO cache the roots so that we don't have to recompute them every time.
        for lexeme in self.iter_lexemes(sort=sort):
            if lexeme.parent_relation is None:
                yield lexeme

    def iter_relations(self):
        raise NotImplementedError()

    def add_derivation(self, source, target):
        rel = DerivationalRelation(source, target)
        rel.add_to_lexemes()

        # TODO should we remember the relation somewhere?

        # TODO should this method return the created link?
        # return rel

    def add_composition(self, sources, main_source, target):
        raise NotImplementedError()
