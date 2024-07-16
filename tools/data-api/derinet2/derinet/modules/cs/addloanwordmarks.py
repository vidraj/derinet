from derinet import Block, Format, Lexicon
import argparse
import logging

from collections import defaultdict


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddLoanwordMarks(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        mark-for-changing-label-to-opposite TAB label TAB lemma_pos
        and add loanword labels to the lemmas."""

        # load lemmas already assigned labels
        assigned = defaultdict()
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                line = line.rstrip().split('\t')

                if line == ['']:  # skip empty lines
                    continue

                opos = True if line[0] else False
                label = bool(line[1].replace('False', ''))
                lemma = line[2]

                if opos:
                    assigned[lemma] = not label
                else:
                    assigned[lemma] = label

        # go through lexicon
        for lexeme in lexicon.iter_lexemes():
            label = assigned.get('_'.join([lexeme.lemma, lexeme.pos]), '')
            if label is True or label is False:
                lexeme.feats['Loanword'] = label

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
        parser.add_argument('file', help='The file to load annotation from.')
        # argparse.REMAINDER tells argparse not to be eager and to process
        # only the start of the args.
        parser.add_argument('rest', nargs=argparse.REMAINDER,
                            help='A list of other modules and arguments.')
        args = parser.parse_args(args)
        fname = args.file
        # Return *args to __init__, **kwargs to init and the unprocessed tail
        # of arguments to other modules.
        return [fname], {}, args.rest
