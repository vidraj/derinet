from derinet import Block, Format, Lexicon
import argparse
import logging

import os
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddSpellingVariants(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        lemma-representative(_pos) TAB lemma-var_1 TAB ... TAB lemma_var_n
        and add variant relations between the lemmas."""
        # load lemmas already assigned classes
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                variant_nset = line.rstrip('\n').split('\t')
                repre_lem, repre_pos = variant_nset[0].split('_')
                repre = lexicon.get_lexemes(lemma=repre_lem, pos=repre_pos)[0]

                # repre. lemma is connected to non-repre. or their children
                k = [repre.parent.lemma, repre.parent.pos]
                if repre.parent and '_'.join(k) in variant_nset[1:]:
                    repre.parent_relation.remove_from_lexemes()

                for nonrepre in variant_nset[1:]:
                    nonrep_lem, nonrep_pos = nonrepre.split('_')
                    nonrepre = lexicon.get_lexemes(lemma=nonrep_lem,
                                                   pos=nonrep_pos)[0]
                    if repre.parent in list(nonrepre.iter_subtree()):
                        repre.parent_relation.remove_from_lexemes()

                # connect non-repre. lemmas and their subtrees to repre lemma
                for nonrepre in variant_nset[1:]:
                    nonrep_lem, nonrep_pos = nonrepre.split('_')
                    nonrepre = lexicon.get_lexemes(lemma=nonrep_lem,
                                                   pos=nonrep_pos)[0]

                    # delete parent relation of non-repre, if there is any
                    if nonrepre.parent:
                        nonrepre.parent_relation.remove_from_lexemes()

                    # reconnect children of non-repre. lemma to repre lemma
                    for child in nonrepre.children:
                        child.parent_relation.remove_from_lexemes()
                        lexicon.add_derivation(source=repre, target=child)

                    # connect non-repre. lemma to repre lemma
                    lexicon.add_derivation(source=repre, target=nonrepre)
                    nonrepre.parent_relation.feats['SemanticLabel'] = 'Variant'

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
