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
        "_type"  # TODO Document what the type is and actually use it somewhere.
    ]

    @abstractmethod
    def __init__(self, sources, main_source, targets, main_target):
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

        # Check that the related lexemes are actually lexemes.
        assert isinstance(main_source, derinet.lexeme.Lexeme)
        assert isinstance(main_target, derinet.lexeme.Lexeme)
        for p in sources:
            assert isinstance(p, derinet.lexeme.Lexeme)
        for p in targets:
            assert isinstance(p, derinet.lexeme.Lexeme)

        # Store the relation data.
        self._main_source = main_source
        self._sources = tuple(sources)
        self._main_target = main_target
        self._targets = tuple(targets)
        self._type = {}  # TODO Add this field to the constructor and use it.

    def add_to_lexemes(self):
        # Add this relation to the lexemes.

        # Check for acyclicity.
        to_check = [self.main_source]
        while to_check:
            lexeme_to_check = to_check.pop()
            if lexeme_to_check == self.main_target:
                raise DerinetCycleCreationError("Cyclic relation detected between {} and {}".format(self.main_source, lexeme_to_check))
            if lexeme_to_check.parent_relation is not None:
                to_check.extend(lexeme_to_check.parent_relation.sources)

        # TODO test that they haven't been set already
        # noinspection PyProtectedMember
        self.main_source._add_child_relation(self)  # pylint: disable=protected-access
        # noinspection PyProtectedMember
        self.main_target._set_parent_relation(self)  # pylint: disable=protected-access

    def remove_from_lexemes(self):
        # Remove this relation from the lexemes.
        # TODO
        raise NotImplementedError()

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
    def type(self):
        return self._type

    def __eq__(self, other):
        object_types_equal = type(self) is type(other)
        main_lexemes_equal = self.main_source is other.main_source and self.main_target is other.main_target
        sources_equal = len(self.sources) == len(other.sources) and all([src_self is src_other for src_self, src_other in zip(self.sources, other.sources)])
        targets_equal = len(self.targets) == len(other.targets) and all([tgt_self is tgt_other for tgt_self, tgt_other in zip(self.targets, other.targets)])
        # FIXME compare the types properly (I wrote this before defining how they are stored and used).
        relation_types_equal = self.type == other.type

        return object_types_equal and main_lexemes_equal and sources_equal and targets_equal and relation_types_equal

    def __hash__(self):
        # self._type is not used to determine the hash, because it is mutable and of an unhashable type.
        #  This doesn't matter, as the Python data model only requires that __eq__ ⇒ same __hash__, not vice versa.
        return hash((self._sources, self._main_source, self._targets, self._main_target))


class DerivationalRelation(Relation):
    """
    A 1-to-1 relation used for affixation and (depending on your taste also) conversion.
    """
    __slots__ = ()

    def __init__(self, source, target):
        super().__init__((source,), source, (target,), target)


class CompoundRelation(Relation):
    """
    A many-to-1 relation for compounding.
    """
    __slots__ = ()

    def __init__(self, sources, main_source, target):
        super().__init__(sources, main_source, (target,), target)
