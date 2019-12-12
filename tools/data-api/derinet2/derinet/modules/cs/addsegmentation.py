from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddSegmentation(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Example processing method. Assumes that the opened file contains a list of morphs separated by spaces on each line.
        """
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()
                morphs = line.split(" ")
                lemma = "".join(morphs)

                lexemes = lexicon.get_lexemes(lemma)
                if len(lexemes) == 1:
                    # Happy path, add the segmentation.
                    lexeme = lexemes[0]

                    start = 0
                    end = 0
                    for i, morph in enumerate(morphs):
                        start = end
                        end = start + len(morph)

                        # Just an example, don't actually do this! The type must be something sensible, else leave it undefined.
                        if len(morphs) == 1:
                            type = "root"
                        elif i == 0:
                            type = "prefix"
                        elif i == len(morphs) - 1:
                            type = "suffix"
                        else:
                            type = "root"

                        lexeme.add_morph(start, end, {"type": type})

                elif len(lexemes) == 0:
                    logger.warning("Lexeme for lemma {} not found".format(lemma))
                else:
                    logger.warning("Lemma {} ambiguous".format(lemma))

        return lexicon

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

        # Return *args and **kwargs to __init__ and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
