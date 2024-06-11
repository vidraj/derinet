from derinet import Block, Lexicon
from derinet.utils import DerinetCycleCreationError
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%a, %d %b %Y %H:%M:%S")

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


class DeleteDerivations(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Delete relations using the file format for deleting derivations
        from 1.7: parentlemma–parentpos TAB childlemma–childpos
        """
        with open(self.fname, mode="rt", encoding="utf-8") as f:
            for line in f:
                if not line or line.startswith("#"):
                    continue

                columns = line.rstrip("\n").split("\t")
                assert len(columns) == 2

                plemma, ppos = divide_word(columns[0])
                clemma, cpos = divide_word(columns[1])

                children = lexicon.get_lexemes(clemma, cpos)

                rels_to_remove = []

                for child in children:
                    for rel in child.parent_relations:
                        for parent in rel.sources:
                            if parent.lemma == plemma and parent.pos == ppos:
                                rels_to_remove.append(rel)

                if rels_to_remove:
                    for rel in rels_to_remove:
                        lexicon.remove_relation(rel)
                else:
                    logger.info("Relation {} -> {} does not exist.".format(columns[0], columns[1]))

        return lexicon

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process
        # only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER,
                            help="A list of other modules and arguments.")
        args = parser.parse_args(args)
        fname = args.file
        # Return *args to __init__, **kwargs to init and the unprocessed tail
        # of arguments to other modules.
        return [fname], {}, args.rest
