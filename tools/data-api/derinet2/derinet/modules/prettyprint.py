from derinet import Block, Lexicon
import sys
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class PrettyPrint(Block):
    """
    Print each tree using Unicode line-drawing characters.
    """

    def __init__(self, output=None):
        if output is None:
            self.output = sys.stdout
            self.close_out_at_end = False
        else:
            self.output = open(output, mode="wt", encoding="utf-8", newline="\n")
            self.close_out_at_end = True

    def process(self, lexicon: Lexicon):
        try:
            for root in lexicon.iter_trees(sort=True):
                print(root.pprint_subtree(),
                      file=self.output)
        finally:
            if self.close_out_at_end:
                self.output.close()

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

        parser.add_argument("-o", "--output", help="Where to store the results."
                                                  "If unspecified, prints to STDOUT.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        output = args.output

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [], {"output": output}, args.rest
