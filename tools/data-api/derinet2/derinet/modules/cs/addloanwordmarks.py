from derinet import Block, Format, Lexicon
import argparse
import logging

import os
import sys
sys.path.append(os.path.realpath('../../../../data/annotations/cs/2020_03_loanwords/'))
from recogFW import recog_foreign_word

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddLoanwordMarks(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Go through lemmaset and add loanword mark."""
        for lexeme in lexicon.iter_lexemes():

            foreign = lexeme.feats.get('Foreign', False)
            if foreign:
                lexeme.feats['Loanword'] = True
                continue

            loan = recog_foreign_word(word=lexeme.lemma, pos=lexeme.pos)
            if loan and lexeme.lemma[0].islower():
                lexeme.feats['Loanword'] = loan

        return lexicon

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('rest', nargs=argparse.REMAINDER,
                            help='A list of other modules and arguments.')
        args = parser.parse_args(args)
        # Return *args to __init__, **kwargs to init and
        # the unprocessed tail of arguments to other modules.
        return [None], {}, args.rest
