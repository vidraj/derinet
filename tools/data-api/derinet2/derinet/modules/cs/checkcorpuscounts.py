from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class CheckCorpusCounts(Block):
    """
    Check that the parents of each word have higher corpus counts than the word
    itself, and report all corpus-attested words derived from unattested ones.
    """

    def __init__(self, offset, ratio):
        self.offset = offset
        self.ratio = ratio

    def process(self, lexicon: Lexicon):
        for child in lexicon.iter_lexemes(sort=False):
            ccount = child.misc["corpus_stats"]["absolute_count"]
            for parent in child.all_parents:
                pcount = parent.misc["corpus_stats"]["absolute_count"]
                if self.ratio * (self.offset + pcount) < ccount:
                    score = self.ratio * (self.offset + pcount) / ccount
                    print(parent, pcount, child, ccount, score, sep="\t")

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

        parser.add_argument("--offset", type=float, default=0.0)
        parser.add_argument("--ratio", type=float, default=1.0, help="Only print pairs with ratio * (offset + pc) < cc, where pc is parent's count and cc is child's count.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [args.offset, args.ratio], {}, args.rest
