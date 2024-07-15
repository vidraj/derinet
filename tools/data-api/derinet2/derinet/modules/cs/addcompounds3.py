from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddCompounds3(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read dataframe in tsv of compounds in the form of three columns - compounds, pos, parents
        parents have to be divided.by.dots
        Add compound relations, if the given parent does not exist, a lexeme is created for it, being given an
        'Unknown' POS
        """

        newdf = pd.read_csv(self.fname, header=None, names=['compounds', 'poses', 'parents'], sep="\t")

        for row in newdf.itertuples():
            parentlist = row.parents.split(".")
            word = row.compounds
            pos = row.poses

            logger.debug("Compounding '{}' from '{}'".format(word, "', '".join(parentlist)))

            lex = []
            for parent in parentlist:
                lst = lexicon.get_lexemes(parent)
                if lst:
                    lex.append(lst[0])
                else:
                    logger.warning("Lexeme for lemma '{}' not found, skipping.".format(parent))
                    #lex.append(lexicon.create_lexeme(parent, 'Unknown'))
                    lex = None
                    break

            if lex is None:
                # Some parent lexemes were not found.
                continue

            child = lexicon.get_lexemes(word, pos=pos)[0]

            lexicon.remove_all_parent_relations(child)

            lexicon.add_composition(lex, lex[-1], child)

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

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
