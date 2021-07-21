from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddChunks(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read annotation in the form of a simple list of words separated by \n
        The script assumes chunks are marked as -chunk-, it skips over words not thus marked
        """

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()
                mark, chunk = line.split("\t")

                if mark == "+" and chunk.startswith("-") and chunk.endswith("-"):
                    lexicon.create_lexeme(chunk, pos="Affixoid").add_feature(feature="Fictitious", value="Yes")

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
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
