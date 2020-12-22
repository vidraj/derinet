from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddCompounds2(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Load annotated compounds from a file and add them to the database.
        Format: lemma_pos TAB > TAB lemma + lemma
        The last parent is always considered to be the head of the relation.
        """

        with open(self.fname, mode='rt', encoding='U8') as f:
            for line in f:
                compound, _, lemmas = line.split('\t')
                components = [item.strip() for item in lemmas.split('+')]

                compound, compound_pos = compound.split('_')
                compound_node = lexicon.get_lexemes(lemma=compound,
                                                    pos=compound_pos)

                if len(compound_node) < 1:
                    continue
                compound_node = compound_node[0]

                component_nodes = list()
                for component in components:
                    node = lexicon.get_lexemes(lemma=component)
                    if len(node) > 0:
                        component_nodes.append(node[0])

                if len(component_nodes) < 2:
                    continue

                lexicon.add_composition(component_nodes,
                                        component_nodes[-1],
                                        compound_node)

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