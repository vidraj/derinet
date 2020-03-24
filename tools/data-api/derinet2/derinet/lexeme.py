from .relation import Relation
from .utils import DerinetError, DerinetMorphError, range_overlaps

# The lexeme class
# Must have all the fields from the DeriNet 2.0 documentation.
# Do we want the base fields (lemma, techlemma, POS, …) to be modifiable?
#  Probably not.
# The other fields should have proper getters and setters.
# We want to store full history of changes – especially reconnections.
#  This can be done as in Perl, by storing a list of former relations for each lexeme. Do we store it in parents as well, or only in the children?
#  Another way is to make the lexeme immutable and store history as references to older versions of the lexeme.
#   This probably requires that relations store an array offset, not a pointer, so that they always point to the newest version.
#    This prevents us from reconstructing the whole state of the network at a given point in time, but the Perl solution
#    didn't allow this anyway and it was good enough.
#   And it is hard to serialize to the textual format, so no no no, we won't be doing this.


# Metody:
# parent, children – lexémy na druhých koncích čistě hlavních hran
# rels_in, rels_out – relations, všechno jsou to pole (nebo iterátory) Relations

class Lexeme(object):
    """
    A class for lexemes, i.e. nodes of the derivational network. Do not create lexemes yourself,
    use Lexicon.create_lexeme() to create and insert them into the network in a single operation.
    """

    __slots__ = [
        # Immutable properties identifying the lexeme.
        "_lemid",
        "_lemma",
        "_pos",

        # Mutable properties of the lexeme.
        "_feats",
        "_segmentation",

        # Mutable relations with other lexemes.
        # The parent relation list is unique in that it is not conceptually
        #  flat. The first member is special and e.g. checked for acyclicity.
        "_parent_relations",
        "_child_relations",

        # Wild area.
        "misc"
    ]

    def __init__(self, lemma, pos, lemid=None, feats=None, misc=None):
        assert isinstance(lemma, str)
        assert len(lemma) > 0
        assert isinstance(pos, str)
        assert lemid is None or isinstance(lemid, str)
        assert misc is None or isinstance(misc, dict)

        self._lemid = lemid if lemid is not None else "{}#{}".format(lemma, pos)
        self._lemma = lemma
        self._pos = pos

        # feats == dict
        # reltype == dict
        # segmentation, otherrels = a set of dicts

        self._feats = feats if feats is not None else {}
        self._segmentation = {
            "boundaries": {},
            "morphs": [{
                "Type": "Implicit",
                "Start": 0,
                "End": len(lemma),
                "Morph": lemma
            }]
        }

        self._parent_relations = []
        self._child_relations = []

        self.misc = misc if misc is not None else {}

    def __repr__(self):
        return "Lexeme(lemma={lemma!r}, pos={pos!r}, lemid={lemid!r}, feats={feats!r}, segmentation={segmentation!r}, misc={misc!r})".format(
            # TODO id – will it be present?
            lemma=self.lemma,
            pos=self.pos,
            lemid=self.lemid,
            feats=self.feats,
            segmentation=self.segmentation,
            # TODO parentid
            # TODO reltype
            # TODO otherrels
            misc=self.misc
        )

    def __str__(self):
        return "{}#{}".format(self.techlemma, self.pos)

    def __lt__(self, other):
        assert isinstance(other, Lexeme)
        return (self.lemma, self.pos, self.lemid, self.techlemma) < (other.lemma, other.pos, other.lemid, other.techlemma)

    @property
    def lemid(self):
        """
        An unique, permanent, cross-database identification of this lexeme.

        Previously known as permalemma, in Czech it contains the tag mask.
        """
        return self._lemid

    @property
    def lemma(self):
        """
        The lemma of this lexeme. Immutable.
        """
        return self._lemma

    @property
    def pos(self):
        """
        The part-of-speech tag of this lexeme. Immutable.
        """
        return self._pos

    @property
    def techlemma(self):
        """
        Returns a disambiguated representation of the lemma. Should be immutable, but actually reads the mutable
        "techlemma" property from misc. If "techlemma" was not provided in misc, returns the lemma.

        In Czech, this attribute is used for storing the m-lemma from the MorfFlex dictionary.

        If you want to know whether an actual techlemma was set, look into misc.
        """
        if "techlemma" in self.misc:
            return self.misc["techlemma"]
        else:
            return self.lemma

    @property
    def feats(self):
        # TODO write this
        return self._feats

    @property
    def segmentation(self):
        return self._segmentation["morphs"]

    @property
    def parent_relation(self) -> Relation:
        """
        The main parent relation.

        :return: The main parent relation.
        """
        if len(self._parent_relations) >= 1:
            return self._parent_relations[0]
        else:
            return None

    @property
    def parent_relations(self):
        """
        The relations to parent lexemes, including all the otherrels.

        :return: A list of relations to parent lexemes.
        """
        return self._parent_relations

    def _add_parent_relation(self, relation):
        assert isinstance(relation, Relation)

        self._parent_relations.append(relation)

    @property
    def parent(self):
        """
        The main parent lexeme from the main relation – the only one in case of derivation,
        the main one in case of compounding.

        The edges obtained by mapping this function over a set of lexemes are guaranteed to form a forest.
        """
        if self.parent_relation is not None:
            return self.parent_relation.main_source
        else:
            return None

    @property
    def all_parents(self):
        """
        All immediate parents of the lexeme from all parent relations.
        """
        parents = []
        for rel in self.parent_relations:
            parents.extend(rel.sources)
        return parents

    @property
    def child_relations(self):
        return self._child_relations

    @property
    def children(self):
        """
        Return a list of lexemes which have this lexeme as their parent; i.e. whose main relation has this
        lexeme as its main starting point.
        """
        # FIXME what is the exact meaning of self.child_relations? If it only lists the main ones,
        #  then the filter is not necessary.
        return [child_relation.main_target for child_relation in self.child_relations if child_relation.main_source is self]

    def _add_child_relation(self, relation):
        assert isinstance(relation, Relation)

        self._child_relations.append(relation)

        # if relation in self.child_relations:
        #     # FIXME do we want to signal an error in this case? Why shouldn't it be allowed to create the same relation multiple times?
        #     # FIXME can it actually happen? Since the parent can only have one such relation set, it can't possibly have two links to this place.
        #     raise DerinetError("The relation already exists.")
        # else:
        #     self._child_relations.append(relation)
        #     # TODO do we need to ensure uniqueness of the target lexemes as well?
        #     #  The uniqueness of the relation itself doesn't guarantee this.

    @property
    def otherrels(self):
        return self.parent_relations[1:]

    def get_tree_root(self):
        lexeme = self
        while lexeme.parent is not None:
            lexeme = lexeme.parent
        return lexeme

    def iter_subtree(self, sort=False):
        yield self

        if sort:
            children = sorted(self.children)
        else:
            children = self.children

        for child in children:
            yield from child.iter_subtree()

    def add_morph(self, start: int, end: int, annot=None):
        """
        Identify a new morph in the lexeme's lemma, starting with character
        index `start` in the lemma and containing all characters up to index
        `end` exclusive. The parameter `annot` identifies properties of the
        morph. The morph may not be further subdivided. Raise DerinetMorphError
        if the morph is not compatible with other segmentation already present.

        :param start: index of the first character in the morph
        :param end: index just after the last character in the morph
        :param annot: a map of features of the morph
        :return: None
        """

        # Check that the morph may be safely added.
        # Check start and end bounds.
        if start < 0:
            raise ValueError("Morph start position {} is out-of-bounds in lexeme {}".format(start, self))
        if end > len(self.lemma):
            raise ValueError("Morph end position {} is out-of-bounds in lexeme {}".format(end, self))
        if start >= end:
            raise ValueError("Starting position {} not smaller than end position {} in lexeme {}".format(start, end, self))

        # The string form of the morph.
        morph = self.lemma[start:end]

        if annot is None:
            annot = {}
        else:
            # Check that annot doesn't contain any forbidden keys.
            if "Start" in annot:
                if annot["Start"] != start:
                    raise ValueError("'Start' specified in annot {} doesn't match given start {}".format(annot["Start"], start))
            if "End" in annot:
                if annot["End"] != end:
                    raise ValueError("'end' specified in annot {} doesn't match given end {}".format(annot["End"], end))
            if "Morph" in annot:
                if annot["Morph"] != morph:
                    raise ValueError("'morph' specified in annot {} doesn't match actual morph {}".format(annot["Morph"], morph))

        # Make sure that annot contains the required "Type" key.
        if "Type" not in annot:
            annot["Type"] = "Unknown"

        # Check that making a new boundary is allowed at start and end.
        if not (self.is_boundary_allowed(start) and self.is_boundary_allowed(end)):
            raise DerinetMorphError("Creating a new boundary is not allowed at positions {} or {} in lexeme {}".format(start, end, self))

        # Check that any morphs overlapping this one are implicit only.
        for segment in self._segmentation["morphs"]:
            if range_overlaps((start, end), (segment["Start"], segment["End"])) and segment["Type"] != "Implicit":
                # The morphs overlap and the recorded one is an actual, user-specified morph.
                raise DerinetMorphError(
                    "Morph {} overlaps existing morph {} in lexeme {}".format(
                        (start, end),
                        (segment["Start"], segment["End"]),
                        self)
                )

        # Record constraints for future morphs.
        # Explicitly allow boundaries at start and end.
        self.add_boundary(start, True)
        self.add_boundary(end, True)

        # Disallow boundaries in between.
        for position in range(start + 1, end):
            self.add_boundary(position, False)

        # Add the morph.
        annot["Start"] = start
        annot["End"] = end
        annot["Morph"] = morph

        new_morphs = []
        for segment in self._segmentation["morphs"]:
            if range_overlaps((start, end), (segment["Start"], segment["End"])):
                if (start, end) == (segment["Start"], segment["End"]):
                    assert segment["Type"] == "Implicit", "We already checked for this above!"
                    # The morphs are exactly in the same spot.
                    new_morphs.append(annot)
                else:
                    raise Exception("Adding a boundary did not subdivide a morph.")
            else:
                # Copy the other ones over as they are.
                new_morphs.append(segment)

        self._segmentation["morphs"] = new_morphs

    def add_boundary(self, position: int, allowed: bool):
        """
        Annotate a place in lemma as either a morph boundary or morph-internal
        place where placing a boundary is prohibited. Raise DerinetMorphError
        if the place is already annotated with a non-compatible annotation.

        :param position: the index in lemma to add the boundary to
        :param allowed: whether the boundary is a split or a forbidden split
        :return: None
        """
        # Check that the boundary is in bounds.
        if position < 0 or position > len(self.lemma):
            raise ValueError("Position {} out-of-bounds in lexeme {}".format(position, self))

        # See whether the position already exists.
        if position in self._segmentation["boundaries"]:
            # The boundary at this position was already recorded.
            if self._segmentation["boundaries"][position] != allowed:
                # The present boundary has opposite allowedness. Raise an error.
                current_state = "allowed" if self._segmentation["boundaries"][position] else "disallowed"
                new_state = "allow" if allowed else "disallow"
                raise DerinetMorphError("Boundary at position {} in {} already {}, cannot {} it".format(position, self, current_state, new_state))
            else:
                # The present boundary is the same as the new one. Nothing to do.
                return

        # The boundary was not recorded yet.
        # Check that it can be allowed / disallowed. These checks should be unnecessary, but let's do them anyway.

        if allowed:
            # Subdivide the appropriate segment in self.segmentation.
            new_morphs = []
            for segment in self._segmentation["morphs"]:
                if segment["Start"] <= position and segment["End"] >= position:
                    # This is the appropriate morph to subdivide.
                    if segment["Type"] != "Implicit" or segment.keys() != {"Type", "Start", "End", "Morph"}:
                        # But the segment is not a "rest" type, it is an actual user-specified morph!
                        # Raise an error.
                        raise Exception("Attempted to subdivide morpheme {} in {} at position {}."
                                        " Curiously, its internals were not forbidden!".format(segment, self, position))

                    if segment["Start"] < position:
                        left_segment = {
                            "Type": "Implicit",
                            "Start": segment["Start"],
                            "End": position,
                            "Morph": segment["Morph"][:position - segment["Start"]]
                        }
                        new_morphs.append(left_segment)

                    if segment["End"] > position:
                        right_segment = {
                            "Type": "Implicit",
                            "Start": position,
                            "End": segment["End"],
                            "Morph": segment["Morph"][position - segment["Start"]:]
                        }
                        new_morphs.append(right_segment)
                else:
                    # Do not subdivide this, just copy.
                    new_morphs.append(segment)

            # Store the edited morph list.
            self._segmentation["morphs"] = new_morphs
        else:
            # Make sure there is not a boundary there.
            for segment in self._segmentation["morphs"]:
                if position == segment["Start"] or position == segment["End"]:
                    raise DerinetMorphError("Cannot forbid position {} in {};"
                                            " segment {} already has a boundary there".format(position, self, segment))

        # Record the actual boundary.
        self._segmentation["boundaries"][position] = allowed

        return

    def is_boundary_allowed(self, position: int, default=True):
        """
        Check whether it is allowed to add a morpheme boundary at `position` in lemma.
        Out-of-bounds positions evaluate to False, unknown positions default to `default`.
        Set `default` to False if you want to query for explicitly allowed boundaries.

        :param position: The index in lemma to query
        :param default: The value to return when the position was not annotated
        :return: A boolean specifying whether the boundary at `position` is allowed
        """
        if position < 0 or position > len(self.lemma):
            # The position is out-of-bounds.
            return False

        if position in self._segmentation["boundaries"]:
            # The position is recorded. Return what the record says.
            return self._segmentation["boundaries"][position]
        else:
            # The position was not recorded yet. Return the default.
            return default

    def add_feature(self, feature, value):
        if value is None:
            if feature in self._feats:
                self._feats.pop(feature)
            return

        if feature in self._feats:
            if self._feats[feature] == value:
                return
            else:
                raise DerinetError("The feature '{}' is already present in lexeme {}".format(feature, self))
        else:
            self._feats[feature] = value
