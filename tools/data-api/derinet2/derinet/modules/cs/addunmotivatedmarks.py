from derinet import Block, Format, Lexicon
import argparse
import logging

import os
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddUnmotivatedMarks(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        individual lemmas on each line
        and go through lemmaset and add unmotivated mark to the lemmas."""
        # load lemmas already assigned classes
        assigned = set()
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                line = line.rstrip('\n').split('\t')
                assigned.add(line[0])

        # find lexeme and assign mark
        for lemma in assigned:
            lemma, pos = lemma.split('_')
            nodes = lexicon.get_lexemes(lemma=lemma, pos=pos)

            assigned_nodes, unassigned_nodes = [], []
            for node in nodes:
                if node.parent is None:
                    unassigned_nodes.append(node)
                else:
                    assigned_nodes.append(node)

            if not nodes:
                logger.warning("Lexeme for %s %s not found", lemma, pos)
            elif len(nodes) == 1:
                nodes[0].misc['unmotivated'] = True
            elif len(unassigned_nodes) == 1:
                # Multiple nodes, but all of them have a parent except for one.
                logger.info("Assigning unmotivatedness for ambiguous %s %s to %s, ignoring derived %s", lemma, pos, unassigned_nodes[0], ", ".join(str(n) for n in assigned_nodes))
                unassigned_nodes[0].misc['unmotivated'] = True
            elif not unassigned_nodes:
                # All potential unmotivated lexemes already have an assigned parent.
                logger.warning("Assigning unmotivatedness for ambiguous %s %s randomly to %s, all potential nodes are derived, other options are %s", lemma, pos, nodes[0], ", ".join(str(n) for n in nodes if n is not nodes[0]))
                nodes[0].misc['unmotivated'] = True
            else:
                # Multiple nodes, some are assigned, more than one are unassigned.
                # TODO If the node to mark is a variant, the unmotivatedness should instead be moved to the parent.
                logger.warning("Assigning unmotivatedness for ambiguous %s %s randomly to %s, ignoring %d derived and %d nonderived %s", lemma, pos, unassigned_nodes[0], len(assigned_nodes), len(unassigned_nodes) - 1, ", ".join(str(n) for n in nodes if n is not unassigned_nodes[0]))
                unassigned_nodes[0].misc['unmotivated'] = True


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
