from derinet import Block, Lexicon
from derinet.utils import DerinetCycleCreationError
import argparse
import logging


logger = logging.getLogger(__name__)


def divide_word(word):
    """Return lemma and pos of word in annotated data.
    Used for ambiguous words. ALT+0150 is separator.
    """
    word = word.split("–")
    lemma = word[0]

    pos = None
    if len(word) > 1:
        if word[1] != "None":
            # Only return the first char, the rest is e.g. C as a compound marker.
            pos = word[1][0]

    return lemma, pos


def searchLexeme(lexicon, lemma, pos):
    """Search lemma in DeriNet. Log warnings for not being inside the
    DeriNet and for homonymous lemma.
    """
    candidates = lexicon.get_lexemes(lemma, pos)
    if not candidates:
        logger.error("Warning: Node does not exist for %s %s", lemma, pos)
        return None

    if len(candidates) > 1:
        logger.warning("Error: Homonymous lemma (return first): %s: %s", lemma, candidates)

    return candidates[0]

class AddWiktionarySsjcAnnot(Block):

    def __init__(self, fname, *, force_reconnect=False):
        self.fname = fname
        self.force_reconnect = force_reconnect

    def process(self, lexicon: Lexicon):
        r"""
        Add relations and optionally compound marks to lexemes, using a
        rich annotation format from Wiktionary and SSJC annotations from
        v1.7. The format lists candidate relations, which can be added
        as-is, reversed or ignored, and both lexemes can optionally have
        a manually specified actual parent listed.

        Annotation: TSV with 5 columns:
        annotation mark, parent, child, parent mark, child mark.
        Annotation marks:
            (nothing): correct relation,
            §: reversed relation,
            \: not a relation, should be deleted.
        Lexeme marks:
            (nothing): OK
            %: is a compound
            (a word): actual parent of the lexeme
        """
        with open(self.fname, mode="rt", encoding="utf-8") as f:
            for line in f:
                columns = line.rstrip("\n").split("\t")

                if all(clm == "" for clm in columns[:5]):
                    continue

                parent_lem, parent_p = divide_word(columns[1])
                child_lem, child_p = divide_word(columns[2])

                parent = searchLexeme(lexicon, parent_lem, parent_p)
                child = searchLexeme(lexicon, child_lem, child_p)

                # relations
                if child is not None and parent is not None:
                    if columns[0] == "":
                        try:
                            if self.force_reconnect:
                                lexicon.remove_all_parent_relations(child)
                                if child in parent.all_parents:
                                    lexicon.remove_all_parent_relations(parent)

                            if child.parent_relation is None:
                                lexicon.add_derivation(parent, child)
                        except DerinetCycleCreationError as ex:
                            logger.error(ex)
                    elif "§" in columns[0]:
                        try:
                            if self.force_reconnect:
                                lexicon.remove_all_parent_relations(parent)
                                if parent in child.all_parents:
                                    lexicon.remove_all_parent_relations(child)

                            if parent.parent_relation is None:
                                lexicon.add_derivation(child, parent)
                        except DerinetCycleCreationError as ex:
                            logger.error(ex)
                    elif "\\" in columns[0]:
                        if parent in child.all_parents:
                            logger.warning("Incorrect derivation %s -> %s present", parent, child)
                        if child in parent.all_parents:
                            logger.warning("Incorrect derivation %s -> %s present", child, parent)

                # compound
                if columns[3] == "%" and parent is not None:
                    parent.misc["is_compound"] = True
                    pass
                elif columns[4] == "%" and child is not None:
                    child.misc["is_compound"] = True
                    # TODO Perform the necessary checks of compounding marks.
                    pass


                # proposals of relations
                if columns[3] not in ("", "*", "%"):
                    p_parent_lem, p_parent_p = divide_word(columns[3])
                    p_parent = searchLexeme(lexicon, p_parent_lem, p_parent_p)

                    if p_parent is not None and parent is not None:
                        try:
                            if self.force_reconnect:
                                lexicon.remove_all_parent_relations(parent)
                                if parent in p_parent.all_parents:
                                    lexicon.remove_all_parent_relations(p_parent)

                            if parent.parent_relation is None:
                                lexicon.add_derivation(p_parent, parent)
                        except DerinetCycleCreationError as ex:
                            logger.error(ex)

                if columns[4] not in ("", "*", "%"):
                    p_parent_lem, p_parent_p = divide_word(columns[4])
                    p_parent = searchLexeme(lexicon, p_parent_lem, p_parent_p)

                    if p_parent is not None and child is not None:
                        try:
                            if self.force_reconnect:
                                lexicon.remove_all_parent_relations(child)
                                if child in p_parent.all_parents:
                                    lexicon.remove_all_parent_relations(p_parent)

                            if child.parent_relation is None:
                                lexicon.add_derivation(p_parent, child)
                        except DerinetCycleCreationError as ex:
                            logger.error(ex)

        return lexicon

    @classmethod
    def parse_args(cls, args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument("file", help="The file to load annotation from.")
        parser.add_argument("--force-reconnect", action="store_true", help="The file to load annotation from.")

        parser.add_argument("rest", nargs=argparse.REMAINDER,
                            help="A list of other modules and arguments.")
        args = parser.parse_args(args)

        return [args.file], {"force_reconnect": args.force_reconnect}, args.rest
