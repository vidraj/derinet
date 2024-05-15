from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging
import pandas as pd
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def techlemma_to_lemma(techlemma):
    """Cut off the technical suffixes from the string techlemma and return the raw lemma"""
    shortlemma = re.sub("[_`].+", "", techlemma)
    lemma = re.sub("-\d+$", "", shortlemma)
    return lemma

class AddCompoundRelations(Block):
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

        This block assumes that everything in the lemma column is a numeral, and adds everything therein
        with the NUM tag into DeriNet. It then attempts to find the parents of said numerals
        by going through the parents column. It only assigns those parents which it can find in DeriNet.
        (by that point, the numerals from the lemma column are already in DeriNet).

        At present, the block *DOES NOT* use the information contained in the lemma to find derivational or conversional
        ancestors or orthographical variants. It only parses out the lemma.
        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")

        for row in newdf.itertuples():
            techlemma = row.lemma
            lemma = techlemma_to_lemma(techlemma)
            tag = row.tag

            if lexicon.get_lexemes(lemma, pos="NUM"):
                logger.warning(f"Numeral {lemma} already exists in DeriNet, skipping.")
                continue

            logger.debug(f"Adding numeral '{lemma}'")

            lexicon.create_lexeme(lemma=lemma,
                                  lemid=lemma + "#" + tag,
                                  pos="NUM",
                                  misc={'techlemma': techlemma})

        for row in newdf.itertuples():
            parentlist = row.parents.split(" ")
            parentnum = len(parentlist)
            lemma = techlemma_to_lemma(row.lemma)

            logger.debug(f"Adding parents '{parentlist}' for numeral '{lemma}'")

            lex = []
            for parent in parentlist:
                lst = lexicon.get_lexemes(parent)
                if len(lst) == 1:
                    lex.append(lst[0])
                if len(lst) > 1:
                    lex.append(lst[0])
                    logger.warning(
                        f"Parent {lst[0].lemma} from compound {lemma} ambiguous, assigning first item from {[i.lemid for i in lst]}.")
                else:
                    is_neoclassical_constituent = parent[0] == "-" and parent[-1] == "-"
                    if is_neoclassical_constituent:
                        lexicon.create_lexeme(lemma=parent, pos="Affixoid").add_feature(feature="Fictitious",
                                                                                        value="Yes")
                    else:
                        logger.warning(f"Parent {lst[0].lemma} from compound {lemma} not found in DeriNet, skipping.")
                        continue

            if parentnum < len(lex):
                continue
            else:
                children = lexicon.get_lexemes(lemma, pos="NUM")
                if children == []:
                    logger.warning(f"Child numeral {lemma} not found in DeriNet, skipping. Bug in previous loop, should have been added!")
                    continue

                for child in children:
                    lexicon.add_composition(lex, lex[-1], child)

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

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
