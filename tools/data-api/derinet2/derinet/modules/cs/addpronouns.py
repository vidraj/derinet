from derinet import Block, Format, Lexicon, DerinetMorphError
from derinet.utils import techlemma_to_lemma
import argparse
import logging
import pandas as pd
import re


logger = logging.getLogger(__name__)


class AddPronouns(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read dataframe in a tsv of compounds in the form of two columns -
        [lemma, tag].

        The lemma column contains techlemmas from MorfFlex.
        The tag is also from MorfFlex.

        This block assumes that everything in the lemma column is a pronoun, and adds everything therein
        with the PRON tag into DeriNet.

        At present, the block *DOES NOT* use the information contained in the lemma to find derivational or conversional
        ancestors or orthographical variants. It only parses out the lemma. It however does use the original
        MorfFlex lemma and stores it as the techlemma. It also uses the MorfFlex tag to the store the lemid.
        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")

        for row in newdf.itertuples():
            techlemma = row.lemma
            lemma = techlemma_to_lemma(techlemma)
            tag = row.tag

            if lexicon.get_lexemes(lemma, pos="PRON"):
                logger.warning(f"Pronoun {lemma} already exists in DeriNet, skipping.")
                continue

            logger.debug(f"Adding pronoun '{lemma}'")

            lexicon.create_lexeme(lemma=lemma,
                                  lemid=lemma + "#" + tag,
                                  pos="PRON",
                                  misc={'techlemma': techlemma})

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
