from derinet import Block, Format, Lexicon
import argparse
import logging

import os
import sys
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddConjugationClasses(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        tagmask TAB lemma TAB conjug-class
        and add conjugation classes to the lemmas."""
        # load lemmas already assigned classes
        assigned = defaultdict()
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                line = line.rstrip('\n').split('\t')
                assigned[line[0]] = line[2]

        # go through lexicon
        for lexeme in lexicon.iter_lexemes():
            if lexeme.pos != 'V':
                continue
            # known lemma (is in 'assigned' dict)
            if assigned.get(lexeme.lemid, False):
                conjug = assigned[lexeme.lemid]
                # lemmas with assigned classes
                if conjug != '#':
                    # conjug = conjug.replace('#', '|')
                    lexeme.feats['ConjugClass'] = conjug

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
