from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class ExtractGenderInflectionPairs(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Lists all pairs of words that have the SemanticLabel set to Female
        (přechylování).
        """
        with open(self.fname, "wt", encoding="utf-8", newline="\n") as f:
            for lexeme in lexicon.iter_lexemes():
                for child_relation in lexeme.child_relations:
                    if child_relation.feats.get("SemanticLabel", "") == "Female":
                        children = child_relation.targets
                        print(lexeme.techlemma,
                              lexeme.pos,
                              ",".join([child.techlemma for child in children]),
                              ",".join([child.pos for child in children]),
                              sep="\t", file=f)

        return lexicon

    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to save the pairs to.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args and **kwargs to __init__ and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
