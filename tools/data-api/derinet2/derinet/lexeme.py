import derinet.relation
from .utils import DerinetError

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
        "_parent_relation",
        "_child_relations",

        # Wild area.
        "misc"
    ]

    def __init__(self, lemma, pos, lemid=None, feats=None, segmentation=None, misc=None):
        assert isinstance(lemma, str)
        assert len(lemma) > 0
        assert isinstance(pos, str)
        assert lemid is None or isinstance(lemid, str)
        assert segmentation is None or isinstance(segmentation, dict)
        assert misc is None or isinstance(misc, dict)

        self._lemid = lemid if lemid is not None else "{}#{}".format(lemma, pos)
        self._lemma = lemma
        self._pos = pos

        # feats == dict
        # reltype == dict
        # segmentation, otherrels = a set of dicts

        self._feats = feats if feats is not None else {}
        self._segmentation = segmentation if segmentation is not None else {}

        self._parent_relation = None
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
        return self._segmentation

    @property
    def parent_relation(self):
        """
        The main parent relation.

        :return: The main parent relation.
        """
        return self._parent_relation

    def _set_parent_relation(self, relation):
        assert isinstance(relation, derinet.relation.Relation)

        if self._parent_relation is not None and self._parent_relation != relation:
            raise DerinetError("A relation was already set for lexeme {}".format(self))

        if relation.main_target is not self:
            raise DerinetError("The parent relation of {} is being changed to a one which doesn't include it as the main target.".format(self))

        self._parent_relation = relation

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
        assert isinstance(relation, derinet.relation.Relation)

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
        # TODO do something with this.
        return None

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
