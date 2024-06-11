import enum
import json
import logging
import pickle
import re
import typing

from .lexeme import Lexeme
from .relation import DerivationalRelation, CompoundRelation, ConversionRelation, UniverbisationRelation, VariantRelation
from .utils import DerinetError, DerinetCycleCreationError, DerinetFileParseError, DerinetLexemeDeleteError, parse_v1_id, parse_v2_id, format_kwstring, parse_kwstring

logger = logging.getLogger(__name__)

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
    UNIMORPH_V1 = 4


class Lexicon(object):
    __slots__ = [   # If you update __slots__, make sure to also update _load_pickle_v4!
        "_data",   # An array of Lexemes.
        "_index",  # _index[lemma][pos] = [index of Lexeme in _data]
        "_record_changes", # Boolean identifying whether the execution context below is used.
        "_execution_context", # A dict identifying the currently running module when using scenarios.
    ]

    def __init__(self, *, record_changes: bool = False):
        # TODO maybe add a parameter with the database name in it? It could be used for
        #  distinguishing multiple databases from one another.
        self._data = []
        self._index = {}
        self._record_changes = record_changes
        self._execution_context = {"creator": None, "args": None, "kwargs": None, "version": None}

    def load(self, data_source, fmt: Format = Format.DERINET_V2, *, on_err: str = "raise"):
        """
        Load data from data_source and append them to this instance of the lexicon.
        Returns the modified lexicon object for convenience.

        :param data_source: A string containing the file name to open or an object to read data
        from – typically an open file handle or a list of strings.
        :param fmt: The format of the data_source.
        :param on_err: If "raise", will raise an exception, if "continue", will try to recover
        and return partially parsed data.
        :return: The lexicon with the new data in it.
        """
        switch = {
            Format.DERINET_V1: self._load_derinet_v1,
            Format.DERINET_V2: self._load_derinet_v2,
            Format.PICKLE_V4: self._load_pickle_v4,
            Format.UNIMORPH_V1: self._load_unimorph_v1
        }

        if fmt not in switch:
            raise ValueError(
                "Loading from format {} is not supported, format type not recognized.".format(fmt)
            )

        if on_err not in {"raise", "continue"}:
            raise ValueError(
                "Unsupported value '{}' for on_err, should be 'raise' or 'continue'.".format(on_err)
            )

        record_changes = self._record_changes
        try:
            # Don't record relation changes – we don't want to have relations
            #  recorded as being created by “Load”. But remember whether
            #  changes are being recorded and restore the state afterwards.
            self._record_changes = False
            switch[fmt](data_source, on_err)
        except DerinetFileParseError:
            raise
        except DerinetError as exc:
            raise DerinetFileParseError("An error happened while parsing input file.") from exc
        finally:
            self._record_changes = record_changes

        return self

    def _load_derinet_v1(self, data_source, on_err):
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

                misc = {}

                if techlemma:
                    misc["techlemma"] = techlemma

                if len(pos) > 1:
                    extra_pos_bits = pos[1:]
                    pos = pos[0]
                    if "C" in extra_pos_bits:
                        misc["is_compound"] = True
                    if "U" in extra_pos_bits:
                        misc["unmotivated"] = True
                    # TODO Check that extra_pos_bits don't contain anything else.

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

    def _parse_v2_lexeme(self, line_nr, line):
        fields = line.split("\t", maxsplit=9)

        if len(fields) != 10:
            # The line was too short; report an error.
            raise DerinetFileParseError("Line nr. {} '{}' is too short, more data required.".format(line_nr, line))

        lex_id_str, lemid, lemma, pos, feats, segmentation, parent_id_str, reltype, otherrels, misc = fields

        try:
            lex_id = parse_v2_id(lex_id_str)
        except ValueError:
            raise DerinetFileParseError("Unparseable ID '{}' encountered on line nr. {} '{}'.".format(lex_id_str, line_nr, line))

        if not lemma:
            raise DerinetFileParseError("Empty lemma encountered in lexeme ID {} on line {} '{}'".format(lex_id_str, line_nr, line))

        feats_list = parse_kwstring(feats)
        if len(feats_list) == 0:
            feats = {}
        elif len(feats_list) == 1:
            feats = feats_list[0]
        else:
            raise DerinetFileParseError() # TODO Write a proper error message.

        morph_list = parse_kwstring(segmentation)

        reltype_list = parse_kwstring(reltype)
        if len(reltype_list) == 0:
            reltype = {}
        elif len(reltype_list) == 1:
            reltype = reltype_list[0]
        else:
            raise DerinetFileParseError() # TODO Write a proper error message.

        otherrels = parse_kwstring(otherrels)

        try:
            misc = json.loads(misc)
        except json.decoder.JSONDecodeError:
            raise DerinetFileParseError("Couldn't parse the JSON-encoded misc section of lexeme {} at line {} '{}'".format(lex_id_str, line_nr, line))

        lexeme = self.create_lexeme(lemma, pos, lemid=lemid, feats=feats, misc=misc)

        # Add the segmentation.
        self._add_morphs_v2_annot(lexeme, morph_list, line_nr)

        return lexeme, lex_id_str, lex_id, parent_id_str, reltype, otherrels

    def _add_morphs_v2_annot(self, lexeme, morph_list, line_nr):
        for morph in morph_list:
            if "Start" not in morph:
                raise DerinetFileParseError("Morph specification '{}' on line nr. {} doesn't include its start".format(morph, line_nr))
            if "End" not in morph:
                raise DerinetFileParseError("Morph specification '{}' on line nr. {} doesn't include its end".format(morph, line_nr))

            try:
                morph["Start"] = int(morph["Start"])
            except ValueError:
                raise DerinetFileParseError("Morpheme start '{}' on line nr. {} is not integral".format(morph["Start"], line_nr))
            try:
                morph["End"] = int(morph["End"])
            except ValueError:
                raise DerinetFileParseError("Morpheme end '{}' on line nr. {} is not integral".format(morph["End"], line_nr))

            lexeme.add_morph(morph["Start"], morph["End"], morph)

    def _load_derinet_v2(self, data_source, on_err):
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
        deferred_relations = []

        try:
            for line_nr, line in enumerate(data_source, start=1):
                if comment_regex.match(line):
                    # The line is a comment. Ignore it fully.
                    continue

                if not line.endswith("\n"):
                    if on_err == "continue":
                        logger.error("Line nr. {} '{}' doesn't end with a newline, the file was possibly truncated.".format(line_nr, line))
                    else:
                        raise DerinetFileParseError("Line nr. {} '{}' doesn't end with a newline, the file was possibly truncated".format(line_nr, line))

                line = line.rstrip("\n")

                if not line:
                    # The line is empty → block separator.
                    if this_tree is not None:
                        # We've just finished reading a tree. Record it to the set of finished trees.
                        seen_trees.add(this_tree)
                        this_tree = None
                    else:
                        # Two newlines in a row, or an empty line at the start of the file.
                        if on_err == "continue":
                            logger.error("Line nr. {} is empty, but doesn't end a block.".format(line_nr))
                        else:
                            raise DerinetFileParseError("Line nr. {} is empty, but doesn't end a block".format(line_nr))
                    continue

                lexeme, lex_id_str, lex_id, parent_id_str, reltype, otherrels = self._parse_v2_lexeme(line_nr, line)
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

                    if "Type" not in reltype:
                        if on_err == "continue":
                            # Act as if the type was specified to be derivation.
                            logger.error("Unspecified relation type on line nr. %d; assuming derivation.", line_nr)
                            t = "Derivation"
                        else:
                            raise DerinetFileParseError("Unspecified relation type on line nr. {}".format(line_nr))
                    else:
                        t = reltype["Type"]
                        del reltype["Type"]

                    if t == "Derivation":
                        self.add_derivation(parent_lexeme, lexeme, feats=reltype)
                    elif t == "Compounding" or t == "Univerbisation":
                        # This needs to be deferred, as the secondary
                        #  sources may not have been encountered yet.
                        #  But read and parse as much as possible anyway.

                        if "Sources" in reltype:
                            # The compounding relation is well-formed, with extra sources specified.
                            parent_id_strs = reltype["Sources"].split(",")
                            del reltype["Sources"]
                            try:
                                parent_ids = [parse_v2_id(id_str) for id_str in parent_id_strs]
                            except ValueError:
                                raise DerinetFileParseError("Unparseable parent ID encountered on line nr. {}".format(line_nr))

                            deferred_relations.append((line_nr, t, parent_ids, parent_lexeme, lexeme, reltype))
                        elif on_err == "continue":
                            logger.error("%s needs multiple parents, but there are no other Sources on line nr. %d. Adding a derivation instead.", t, line_nr)
                            self.add_derivation(parent_lexeme, lexeme, feats=reltype)
                        else:
                            raise DerinetFileParseError("{} needs multiple parents, but there are no other Sources on line nr. {}.".format(t, line_nr))

                    elif t == "Conversion":
                        self.add_conversion(parent_lexeme, lexeme, feats=reltype)

                    elif t == "Variant":
                        self.add_variant(parent_lexeme, lexeme, feats=reltype)

                    elif on_err == "continue":
                        logger.error("Unknown relation type '%s' on line nr. %d, skipping.", t, line_nr)
                    else:
                        raise DerinetFileParseError("Unknown relation type {} on line nr. {}".format(t, line_nr))

                # TODO Parse secondary relations.
                if otherrels:
                    raise NotImplementedError("Secondary relations are not supported yet.")

            # The whole database is loaded now. Process the deferred relations.
            #  Right now, this only concerns compounds. In the future, more
            #  types may require deferred handling.
            for line_nr, reltype, parent_ids, parent_lexeme, lexeme, feats in deferred_relations:
                parents = []
                for id_str in parent_ids:
                    if id_str in id_map:
                        parents.append(id_map[id_str])
                    else:
                        raise DerinetFileParseError("Lexeme on line nr. {} references unknown parent lexeme ID {}".format(line_nr, id_str))

                if reltype == "Compounding":
                    try:
                        self.add_composition(parents, parent_lexeme, lexeme, feats=feats)
                    except DerinetError as exc:
                        if on_err == "continue":
                            logger.error("Error adding compounding, skipping.", exc_info=exc)
                            continue
                        else:
                            raise
                elif reltype == "Univerbisation":
                    try:
                        self.add_univerbisation(parents, parent_lexeme, lexeme, feats=feats)
                    except DerinetError as exc:
                        if on_err == "continue":
                            logger.error("Error adding univerbisation, skipping.", exc_info=exc)
                            continue
                        else:
                            raise
                else:
                    raise DerinetFileParseError("Unknown relation type {} on line nr. {}".format(reltype, line_nr))

        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

    def _load_pickle_v4(self, data_source, on_err):
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
            self._execution_context = new_lexicon._execution_context  # pylint: disable=protected-access
        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

    def _load_unimorph_v1(self, data_source, on_err):
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

        try:
            for line_nr, line in enumerate(data_source, start=1):
                # Read a new line, get rid of the newline at the end and
                line = line.rstrip("\n")
                fields = line.split("\t")

                if len(fields) != 4:
                    # The line was too short or too long; report an error.
                    raise DerinetFileParseError("Line nr. {} '{}' has {} fields instead of the expected 4.".format(line_nr, line, len(fields)))

                parent_lemma, child_lemma, poses, child_affix = fields

                # Parse out the POSes.
                poses_tuple = poses.split(":")
                known_poses = {"ADJ", "ADV", "J", "N", "U", "V"}
                if len(poses_tuple) != 2 or poses_tuple[0] not in known_poses or poses_tuple[1] not in known_poses:
                    raise DerinetFileParseError("Unparseable POS tuple '{}'".format(poses))

                parent_pos, child_pos = poses_tuple

                if not (parent_lemma and child_lemma and parent_pos and child_pos):
                    raise DerinetFileParseError("Empty field encountered on line nr. {} '{}'".format(line_nr, line))

                # Get or create both lexemes.
                parent_lexemes = self.get_lexemes(parent_lemma, parent_pos) or [self.create_lexeme(parent_lemma, parent_pos)]
                child_lexemes = self.get_lexemes(child_lemma, child_pos) or [self.create_lexeme(child_lemma, child_pos)]
                assert len(parent_lexemes) == 1 and len(child_lexemes) == 1
                parent_lexeme = parent_lexemes[0]
                child_lexeme = child_lexemes[0]

                # Check for reflexivity.
                if (parent_lemma, parent_pos) == (child_lemma, child_pos):
                    if on_err == "continue":
                        logger.error("Reflexive derivation found in {} -> {}".format(parent_lexeme, child_lexeme))
                        continue
                    else:
                        raise DerinetFileParseError("Reflexive derivation found in {} -> {}".format(parent_lexeme, child_lexeme))

                # TODO Include the child_affix in feats.
                # TODO Use the child_affix for segmentation of the child,
                #  and possibly also of the parent.
                try:
                    self.add_derivation(parent_lexeme, child_lexeme)
                except DerinetCycleCreationError as exc:
                    if on_err == "continue":
                        logger.error("Cyclic derivation found in {} -> {}".format(parent_lexeme, child_lexeme), exc_info=exc)
                        continue
                    else:
                        raise
        finally:
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_source.close()

    def save(self, data_sink, fmt: Format = Format.DERINET_V2, *, on_err: str = "raise"):
        switch = {
            Format.DERINET_V1: self._save_derinet_v1,
            Format.DERINET_V2: self._save_derinet_v2,
            Format.PICKLE_V4: self._save_pickle_v4
        }

        if on_err not in {"raise", "continue"}:
            raise ValueError(
                "Unsupported value '{}' for on_err, should be 'raise' or 'continue'.".format(on_err)
            )

        if fmt not in switch:
            raise ValueError(
                "Saving to format {} is not supported, format type not recognized.".format(fmt)
            )

        switch[fmt](data_sink, on_err)

    def _save_derinet_v1(self, data_sink, on_err):
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
            # We're not sorting the items, because that would break identity
            #  of the IDs between input and output files in case the IDs are
            #  consecutive and start from 0. (If there are holes in the
            #  numbering, the IDs won't stay the same anyway – the old format
            #  is only partially supported by this new API.
            # Also, we save the lexemes to a list so that the numbering stays
            #  the same between runs. Today, this is guaranteed anyway, but that
            #  may change in the future.
            lexemes = list(self.iter_lexemes(sort=False))
            lex_id_map = {lexeme: i for i, lexeme in enumerate(lexemes)}
            for i, lexeme in enumerate(lexemes):
                if len(lexeme.all_parents) > 1:
                    if on_err == "continue":
                        logger.warning("Multiple parents encountered in lexeme {}, only saving the main one.".format(lexeme))
                    else:
                        raise DerinetError("Multiple parents encountered in lexeme {}".format(lexeme))

                pos = lexeme.pos
                if lexeme.misc.get("is_compound", False):
                    pos += "C"
                if lexeme.misc.get("unmotivated", False):
                    pos += "U"

                if lexeme.parent is not None:
                    parent_id = str(lex_id_map[lexeme.parent])
                else:
                    parent_id = ""
                print(
                    i,
                    lexeme.lemma,
                    lexeme.techlemma,
                    pos,
                    parent_id,
                    sep="\t", end="\n", file=data_sink
                )
        finally:
            data_sink.flush()
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_sink.close()

    def _format_parent_relation(self, lexeme, rel, id_mapping, include_main_source):
        reltype = {}

        if rel:
            # We need to add features to the reltype, so
            #  copy it to prevent clobbering the original.
            reltype = rel.feats.copy()

            # TODO proper check instead of an assert.
            assert "Type" not in reltype
            reltype["Type"] = rel.type

            if include_main_source:
                assert "MainSource" not in reltype
                reltype["MainSource"] = id_mapping[rel.main_source][0]

            # If there are multiple sources, print all of them
            #  (in order). It is necessary to print them all, even
            #  though the main source is already indicated in
            #  another field, because otherwise it is not clear
            #  where does the main source belong in the list.
            if len(rel.sources) > 1:
                # TODO proper check instead of an assert.
                assert "Sources" not in reltype
                reltype["Sources"] = ",".join([id_mapping[source][0] for source in rel.sources])

        return reltype

    def _save_derinet_v2(self, data_sink, on_err):
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

            # First, make a full mapping of lexeme → ID.
            # This is necessary, because we may need to refer to out-of-tree
            #  lexemes that weren't processed yet – for example in compounds.
            id_mapping = {}

            all_roots = list(self.iter_trees(sort=True))

            for tree_id, root in enumerate(all_roots):
                for lex_in_tree_id, lexeme in enumerate(root.iter_subtree(sort=True)):
                    full_id = "{}.{}".format(tree_id, lex_in_tree_id), tree_id, lex_in_tree_id

                    if lexeme in id_mapping:
                        if on_err == "continue":
                            logger.error("Lexeme {} processed twice; parents: {}".format(lexeme, lexeme.all_parents))
                        else:
                            raise DerinetError("An error occurred while saving data: Lexeme {} processed twice; parents: {}".format(lexeme, lexeme.all_parents))
                    else:
                        id_mapping[lexeme] = full_id

            # After calculating the ID mapping, go over the lexemes again,
            #  printing them.
            for tree_id, root in enumerate(all_roots):
                if tree_id > 0:
                    # Separate unrelated trees by a newline.
                    print("", end="\n", file=data_sink)

                for lexeme in root.iter_subtree(sort=True):
                    formatted_id, tree_id, lex_in_tree_id = id_mapping[lexeme]

                    if lexeme.parent:
                        parent_formatted_id, parent_tree_id, parent_lex_in_tree_id = id_mapping[lexeme.parent]
                        if tree_id != parent_tree_id:
                            if on_err == "continue":
                                logger.error("Lexemes {} and {} should be printed in a single tree, but have different tree IDs.".format(lexeme.parent, lexeme))
                            else:
                                raise DerinetError("Lexemes {} and {} should be printed in a single tree, but have different tree IDs".format(lexeme.parent, lexeme))
                        if lex_in_tree_id <= parent_lex_in_tree_id:
                            if on_err == "continue":
                                logger.error("Lexeme {} is a parent of lexeme {}, but is formatted below it in the tree.".format(lexeme.parent, lexeme))
                            else:
                                raise DerinetError("Lexeme {} is a parent of lexeme {}, but is formatted below it in the tree".format(lexeme.parent, lexeme))
                    else:
                        parent_formatted_id = ""

                    print(
                        formatted_id,
                        lexeme.lemid,
                        lexeme.lemma,
                        lexeme.pos,
                        format_kwstring([lexeme.feats]),
                        format_kwstring([segment for segment in lexeme.segmentation if segment["Type"] != "Implicit"]),
                        parent_formatted_id,
                        format_kwstring([self._format_parent_relation(lexeme, lexeme.parent_relation, id_mapping, False)]),
                        format_kwstring([self._format_parent_relation(lexeme, rel, id_mapping, True) for rel in lexeme.otherrels]),
                        json.dumps(lexeme.misc, ensure_ascii=False, allow_nan=False, indent=None, sort_keys=True),
                        sep="\t", end="\n", file=data_sink
                    )
        finally:
            data_sink.flush()
            # If we are supposed to close the data source, do it now.
            if close_at_end:
                data_sink.close()

    def _save_pickle_v4(self, data_sink, on_err):
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

    def create_lexeme(self, lemma: str, pos: str, lemid: str = None, feats=None, misc: dict = None):
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
        :param misc: Other features not covered elsewhere. You can use this field for storing your own data
                together with the lexemes. Make sure that the contents are serializable to JSON, i.e. strings
                as keys and dicts, lists or primitive types as values.
        :return: The new lexeme.
        """
        lexeme = Lexeme(lemma, pos, lemid, feats, misc)

        # Add the lexeme to the datastore.
        idx = len(self._data)
        self._data.append(lexeme)

        # Add the lexeme idx to the lemma-pos index.
        # This is too slow, do not use: # self._index.setdefault(lexeme.lemma, {}).setdefault(lexeme.pos, []).append(idx)
        if lexeme.lemma not in self._index:
            self._index[lexeme.lemma] = {lexeme.pos: [idx]}
        elif lexeme.pos not in self._index[lexeme.lemma]:
            self._index[lexeme.lemma][lexeme.pos] = [idx]
        else:
            self._index[lexeme.lemma][lexeme.pos].append(idx)

        # TODO add the lexeme to the other indices.

        return lexeme

    def delete_lexeme(self, lexeme, delete_relations=False):
        """
        Delete the specified lexeme from the database.

        If there are any relations incident to the lexeme, the parameter
        `delete_relations` specifies how to treat the situation.
        - When false, the method raises an error.
        - When true, all incident relations are deleted before
          deleting the lexeme itself.

        :param lexeme: The lexeme to delete.
        :param delete_relations: When true, delete incident relations
                before proceeding instead of raising an error.
        """
        # To delete a lexeme, we have to:
        #  1. disconnect it from any relations, both incoming and
        #     outgoing (that is, if the user specifies they want to
        #     autodisconnect any relations – otherwise just raise
        #     an error if there are relations)
        #  2. delete it from the _index (and optionally delete any
        #     resulting empty levels in the index)
        #  3. delete it from _data
        #  - What to do about the resulting empty slot in data?
        #    - We can set it to None and change the iteration and
        #      other functions to ignore empty slots,
        #    - or we can move the last lexeme from _data there and
        #      reindex.
        #      - Do we actually have to reindex anything? It seems
        #        the index in _data is not significant.
        #      - But we probably want to keep the order of lexemes
        #        between loads and stores.

        # TODO verify that the lexeme is in the _data

        if delete_relations:
            self.remove_all_relations(lexeme)

        if lexeme.parent_relations or lexeme.child_relations:
            raise DerinetLexemeDeleteError("The lexeme {} has existing relations, cannot delete it".format(lexeme))

        homonym_index = self._index[lexeme.lemma][lexeme.pos]
        # `idx` is an index of the lexeme in `self._data`.
        # `index_idx` is an index of the `idx` in the homonym list in
        #  `_index`... confusing naming.
        for index_idx, idx in enumerate(homonym_index):
            if self._data[idx] == lexeme:
                break
        else:
            raise ValueError("The lexeme '{}' to delete was not found in the index".format(lexeme))

        # Delete lexeme from the _index. If it's at the last position,
        #  just pop the list. If it's elsewhere, put the last element
        #  in its place and then pop.
        if index_idx < len(homonym_index) - 1:
            homonym_index[index_idx] = homonym_index[-1]
        homonym_index.pop()

        # Similarly, delete lexeme from _data by popping the list.
        assert self._data[idx] == lexeme, "Indexes are wrong, the lexeme to delete is not at the expected place in _data!"
        if idx < len(self._data) - 1:
            # Because we're reordering the _data, we have to reindex
            #  the moved item.
            idx_to_move = len(self._data) - 1
            lexeme_to_move = self._data[idx_to_move]

            # Find out where in the index it is indexed.
            moved_homonym_index = self._index[lexeme_to_move.lemma][lexeme_to_move.pos]
            moved_index_idx = moved_homonym_index.index(idx_to_move)

            # Move it to the index of the removed lexeme.
            moved_homonym_index[moved_index_idx] = idx
            self._data[idx] = lexeme_to_move
        self._data.pop()

    def delete_subtree(self, lexeme):
        raise NotImplementedError()

    def get_lexemes(
            self,
            lemma: str,
            pos: str = None,
            lemid: str = None,
            techlemma: str = None,
            techlemma_match_fuzzy: bool = False
    ) -> typing.List[Lexeme]:
        match_set = self._index.get(lemma, {})

        if pos is not None:
            match_list = match_set.get(pos, [])
        else:
            # Flatten the list of lists into a single list.
            match_list = [lexeme_idx for pos_list in match_set.values() for lexeme_idx in pos_list]

        if lemid is not None:
            match_list = [lexeme_idx for lexeme_idx in match_list if self._data[lexeme_idx].lemid == lemid]

        if techlemma is not None:
            match_list_techlemma = [lexeme_idx for lexeme_idx in match_list if self._data[lexeme_idx].techlemma == techlemma]
            if techlemma_match_fuzzy and not match_list_techlemma:
                # If the user wants to use the techlemmas only as an advice and there is no lexeme matching
                #  the techlemma, fall back to non-techlemmatical matches.
                # TODO also match prefixes – stát-2 matches stát-2_XYZ better than stát-1
                match_list_techlemma = match_list
        else:
            match_list_techlemma = match_list

        return [self._data[lexeme_idx] for lexeme_idx in match_list_techlemma]

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
            if lexeme.parent is None:
                yield lexeme

    def iter_relations(self):
        raise NotImplementedError()

    def lexeme_count(self):
        return len(self._data)

    def set_execution_context(self, creator=None, args=None, kwargs=None, *, version=None):
        if not self._record_changes:
            logger.warn("Asked to set execution context while change recording is disabled.")

        old_context = self._execution_context
        self._execution_context = {
            "creator": creator or old_context["creator"],
            "args": args or old_context["args"],
            "kwargs": kwargs or old_context["kwargs"],
            "version": version or old_context["version"]
        }

    def add_derivation(self, source, target, feats=None):
        rel = DerivationalRelation(source, target, feats=feats)
        rel.add_to_lexemes()
        if self._record_changes:
            rel.main_target.record_parent_relation_change(rel, self._execution_context)

        # TODO should we remember the relation somewhere?

        # TODO should this method return the created link?
        # return rel

    def add_composition(self, sources, main_source, target, feats=None):
        if len(sources) < 2:
            raise DerinetError("Compounding of {} needs at least two sources, given only {}".format(target, sources))

        rel = CompoundRelation(sources, main_source, target, feats=feats)
        rel.add_to_lexemes()
        if self._record_changes:
            rel.main_target.record_parent_relation_change(rel, self._execution_context)

    def add_univerbisation(self, sources, main_source, target, feats=None):
        if len(sources) < 2:
            raise DerinetError("Univerbation of {} needs at least two sources, given only {}".format(target, sources))

        rel = UniverbisationRelation(sources, main_source, target, feats=feats)
        rel.add_to_lexemes()
        if self._record_changes:
            rel.main_target.record_parent_relation_change(rel, self._execution_context)

    def add_conversion(self, source, target, feats=None):
        rel = ConversionRelation(source, target, feats=feats)
        rel.add_to_lexemes()
        if self._record_changes:
            rel.main_target.record_parent_relation_change(rel, self._execution_context)

    def add_variant(self, source, target, feats=None):
        rel = VariantRelation(source, target, feats=feats)
        rel.add_to_lexemes()
        if self._record_changes:
            rel.main_target.record_parent_relation_change(rel, self._execution_context)

    def remove_relation(self, rel):
        """
        Remove the specified relation from all lexemes it's incident to.
        Be aware that since this modifies the relation lists of the
        incident lexemes, you shouldn't call it in a loop like
        `for rel in lexeme.parent_relations`; instead, use a while-loop
        or one of the `remove_all_parent_relations`,
        `remove_all_child_relations` or `remove_all_relations` methods.

        :param rel: The Relation object to remove.
        """
        for lexeme in rel.targets:
            lexeme.record_parent_relation_change(None, self._execution_context)
        rel.remove_from_lexemes()

    def remove_all_parent_relations(self, lexeme):
        # Since the deletion modifies the relation lists, we have
        #  to generate them one-by-one instead of using
        #  `for rel in lexeme.parent_relations`.
        while lexeme.parent_relations:
            self.remove_relation(lexeme.parent_relations[0])

    def remove_all_child_relations(self, lexeme):
        # Since the deletion modifies the relation lists, we have
        #  to generate them one-by-one instead of using
        #  `for rel in lexeme.child_relations`.
        while lexeme.child_relations:
            self.remove_relation(lexeme.child_relations[0])

    def remove_all_relations(self, lexeme):
        self.remove_all_parent_relations(lexeme)
        self.remove_all_child_relations(lexeme)
