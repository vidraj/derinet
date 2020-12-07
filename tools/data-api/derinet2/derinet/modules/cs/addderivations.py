from derinet import Block, Format, Lexicon
import argparse
import logging

import os
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddDerivations(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        lemma-parent(_pos) TAB > TAB lemma-child(_pos)
        and add derivational relations between the lemmas."""
        # load lemmas already assigned classes
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                parent, _, child = line.rstrip('\n').split('\t')

                # preprocess lexeme
                if '_' in parent:
                    p_lemma, p_pos = parent.split('_')
                else:
                    p_lemma, p_pos = parent, None

                if '_' in child:
                    c_lemma, c_pos = child.split('_')
                else:
                    c_lemma, c_pos = child, None

                # find lexeme
                c_node = lexicon.get_lexemes(lemma=c_lemma, pos=c_pos)
                p_node = lexicon.get_lexemes(lemma=p_lemma, pos=p_pos)

                # add derivational relation
                if c_node and p_node:
                    c_node, p_node = c_node[0], p_node[0]
                    # skip if they are the same
                    if c_node == p_node:
                        continue

                    # disconnect child from its parent
                    if c_node.parent_relation:
                        c_node.parent_relation.remove_from_lexemes()

                    # disconnect cycles
                    for node in c_node.get_tree_root().iter_subtree():
                        if node == p_node and p_node.parent:
                            p_node.parent_relation.remove_from_lexemes()

                    # add derivational relation
                    lexicon.add_derivation(source=p_node, target=c_node)

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
