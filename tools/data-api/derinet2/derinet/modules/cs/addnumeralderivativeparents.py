from derinet import Block, Format, Lexicon, DerinetMorphError
from derinet.utils import techlemma_to_lemma
import argparse
import logging

import pandas as pd
import numpy as np
import re


logger = logging.getLogger(__name__)


def parse_out_deriv_parent(techlemma):
    lemma = techlemma_to_lemma(techlemma)
    pattern = r"\(\*(\d+)\)"
    match = re.search(pattern, techlemma)

    if match:
        num = int(match.group(1))
        return lemma[:-num]
    else:
        return None

class AddNumeralDerivativeParents(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read dataframe in a tsv of compounds in the form of three columns -
        [lemma, tag, parents].

        The lemma column contains techlemmas from MorfFlex.
        The tag is also from MorfFlex.
        The parents have to be divided by spaces.

        This block assumes that everything in the lemma column is a numeral, and attempts to find the derivational parent of said numerals
        by parsing the lemma using a regular expression.
        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")
        logger.debug(f"Lexicon size: {sum([1 for i in lexicon.iter_lexemes()])}")

        for row in newdf.itertuples():
            techlemma = row.lemma
            lemma = techlemma_to_lemma(techlemma)

            for lexeme in lexicon.get_lexemes(lemma):
                parent_lemma = parse_out_deriv_parent(techlemma)
                parent_lexemes = lexicon.get_lexemes(parent_lemma)

                if parent_lemma and parent_lexemes:
                    parent_lexeme = parent_lexemes[0]
                    logger.info(f"Assigning derivational parent {parent_lexeme} to lemma {lexeme}")
                    lexicon.remove_all_parent_relations(lexeme)
                    lexicon.add_derivation(source=parent_lexeme, target=lexeme)
                else:
                    logger.info(f"No derivational parent found for lemma {lexeme}, skipping.")

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
