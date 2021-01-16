from abc import ABCMeta, abstractmethod
import derinet.lexeme
from .utils import DerinetCycleCreationError


class Relation(object, metaclass=ABCMeta):  # Defining it as Relation(ABC) doesn't mix well with slots usage – it doesn't prevent __dict__ from forming.
    """
    A base class for all network relations. A relation is a graph multiedge pointing from the word-formational
    parent (antecedent) to the word-formation child (descendant). It may have multiple parents (compounding) and,
    at the time, just a single child. But if there is a case for multiple children, we will add that as well.

    Do not instantiate this class directly, use its subclasses.

    In the 2.0 version of the DeriNet API, relations are explicit objects. However, they don't get an ID
    (nor does anything else) and they are not explicitly stored anywhere – they are only accessible from
    their incident lexemes. A reference to the relation is stored in all parents.
    """

    __slots__ = [
        "_sources",
        "_main_source",
        "_targets",
        "_main_target",
        "_feats"  # TODO Document what the type is and actually use it somewhere.
    ]

    @abstractmethod
    def __init__(self, sources, main_source, targets, main_target, feats=None):
        # Check that the main main_source is one of the sources.
        if main_source not in sources:
            raise ValueError("The specified main main_source {} was not found in the list of sources [{}]".format(
                main_source,
                ", ".join((str(p) for p in sources))
            ))

        # Similarly for the targets.
        if main_target not in targets:
            raise ValueError("The specified main main_target {} was not found in the list of targets [{}]".format(
                main_target,
                ", ".join((str(p) for p in targets))
            ))

        # Check that the sources and targets don't overlap.
        if not set(sources).isdisjoint(targets):
            raise DerinetCycleCreationError("The sets of sources [{}] and targets [{}] are not disjoint".format(
                ", ".join((str(p) for p in sources)),
                ", ".join((str(p) for p in targets))
            ))

        # Check that the related lexemes are actually lexemes.
        assert isinstance(main_source, derinet.lexeme.Lexeme)
        assert isinstance(main_target, derinet.lexeme.Lexeme)
        for p in sources:
            assert isinstance(p, derinet.lexeme.Lexeme)
        for p in targets:
            assert isinstance(p, derinet.lexeme.Lexeme)

        # Fill in the default value for type if the user didn't specify anything.
        if feats is None:
            feats = {}

        # Store the relation data.
        self._main_source = main_source
        self._sources = tuple(sources)
        self._main_target = main_target
        self._targets = tuple(targets)
        self._feats = feats

    def add_to_lexemes(self):
        # Add this relation to the lexemes.

        # Check that the exact same relation doesn't exist yet.
        if self.main_target.parent_relation == self:
            return

        # Check for acyclicity.
        to_check = [self.main_source]
        while to_check:
            lexeme_to_check = to_check.pop()
            if lexeme_to_check == self.main_target:
                raise DerinetCycleCreationError("Cyclic relation detected between {} and {}".format(self.main_source, lexeme_to_check))
            if lexeme_to_check.parent_relation is not None:
                to_check.extend(lexeme_to_check.parent_relation.sources)

        # TODO test that they haven't been set already
        # The set() below does basically that – in cases of reduplication,
        #  a single lexeme may be in the sources or targets multiple times,
        #  but we have to add the relation just once.
        # First try to add the relation to the parent, because that one may fail.
        #  Adding it to the children shouldn't.
        for target in set(self.targets):
            # noinspection PyProtectedMember
            target._add_parent_relation(self)  # pylint: disable=protected-access
        for source in set(self.sources):
            # noinspection PyProtectedMember
            source._add_child_relation(self)  # pylint: disable=protected-access

    def remove_from_lexemes(self):
        # Remove this relation from the lexemes.
        for target in set(self.targets):
            target._del_parent_relation(self)  # pylint: disable=protected-access
        for source in set(self.sources):
            source._del_child_relation(self)  # pylint: disable=protected-access

    @property
    def main_source(self):
        return self._main_source

    @property
    def sources(self):
        return self._sources

    @property
    def other_sources(self):
        return tuple(s for s in self.sources if s is not self.main_source)

    @property
    def main_target(self):
        return self._main_target

    @property
    def targets(self):
        return self._targets

    @property
    def other_targets(self):
        return tuple(t for t in self.targets if t is not self.main_target)

    @property
    def feats(self):
        return self._feats

    @property
    @abstractmethod
    def type(self):
        return None

    def __eq__(self, other):
        if other is None:
            # Other may be None
            return self is None

        object_types_equal = type(self) is type(other)
        main_lexemes_equal = self.main_source is other.main_source and self.main_target is other.main_target
        sources_equal = len(self.sources) == len(other.sources) and all([src_self is src_other for src_self, src_other in zip(self.sources, other.sources)])
        targets_equal = len(self.targets) == len(other.targets) and all([tgt_self is tgt_other for tgt_self, tgt_other in zip(self.targets, other.targets)])
        # FIXME compare the types properly (I wrote this before defining how they are stored and used).
        relation_feats_equal = self.feats == other.feats

        return object_types_equal and main_lexemes_equal and sources_equal and targets_equal and relation_feats_equal

    def __hash__(self):
        # self._type is not used to determine the hash, because it is mutable and of an unhashable type.
        #  This doesn't matter, as the Python data model only requires that __eq__ ⇒ same __hash__, not vice versa.
        return hash((self._sources, self._main_source, self._targets, self._main_target))


class DerivationalRelation(Relation):
    """
    A 1-to-1 relation used for affixation.
    """
    __slots__ = ()

    def __init__(self, source, target, feats=None):
        super().__init__((source,), source, (target,), target, feats=feats)

    @property
    def type(self):
        return "Derivation"


class CompoundRelation(Relation):
    """
    A many-to-1 relation for compounding.
    """
    __slots__ = ()

    def __init__(self, sources, main_source, target, feats=None):
        super().__init__(sources, main_source, (target,), target, feats=feats)

    @property
    def type(self):
        return "Compounding"


class ConversionRelation(Relation):
    """
    A 1-to-1 relation used for conversion.

    It doesn't check anywhere that the relation is actually a conversion, i.e.
    that the lemmas of the source and target are identical and the POSes are
    different. TODO maybe we want to do that?
    """
    __slots__ = ()

    def __init__(self, source, target, feats=None):
        super().__init__((source,), source, (target,), target, feats=feats)

    @property
    def type(self):
        return "Conversion"


class VariantRelation(Relation):
    """
    A 1-to-1 relation used for spelling variants.
    """
    __slots__ = ()

    def __init__(self, source, target, feats=None):
        super().__init__((source,), source, (target,), target, feats=feats)

    @property
    def type(self):
        return "Variant"
