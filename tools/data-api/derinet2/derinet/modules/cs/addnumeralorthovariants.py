from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging

import pandas as pd
import numpy as np
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

def parse_out_deriv_parent(techlemma):
    lemma = techlemma_to_lemma(techlemma)
    pattern = "\(\*(\d+)\)"
    match = re.search(pattern, techlemma)

    if match:
        num = int(match.group(1))
        return lemma[:-num]
    else:
        return None

def parse_out_orthovariant(techlemma):
    lemma = techlemma_to_lemma(techlemma)
    pattern = "\(\^GC\*\*([a-Ž]*)\)"
    match = re.search(pattern, techlemma)

    if match:
        return match.group(1)
    else:
        return None


class AddNumeralCompoundParents(Block):
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

        This block assumes that everything in the lemma column is a numeral, and attempts to find the parents of said numerals
        by parsing the MorfFlex lemma.
        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")
        logger.debug(f"Lexicon size: {sum([1 for i in lexicon.iter_lexemes()])}")

        for row in newdf.itertuples():
            parentlist = row.parents.split(" ")
            parentnum = len(parentlist)
            if parentnum < 2:
                continue

            lemma = techlemma_to_lemma(row.lemma)

            if parentnum == 1:
                if parentlist[0] == lemma:
                    logger.debug(
                        f"{lemma} annotated as unmotivated, skipping.")
                    continue


            logger.debug(f"Adding parents '{parentlist}' for numeral '{lemma}'")



            lex = []
            for parent in parentlist:
                lst = lexicon.get_lexemes(parent)
                if len(lst) == 1:
                    lex.append(lst[0])
                elif len(lst) > 1:
                    lemids = [i.lemid for i in lst]
                    POSes = [i.split("#")[1][0] for i in lemids]

                    if "C" in POSes:
                        where = np.where(np.array(POSes) == "C")[0].tolist()[0]
                        lex.append(lst[where])
                        logger.warning(
                            f"Parent {parent} from compound {lemma} ambiguous, assigning first numeral from {lemids}.")

                    else:
                        lex.append(lst[0])
                        logger.warning(
                            f"Parent {parent} from compound {lemma} ambiguous, assigning first item from {lemids}. (no numerals found)")

                else:
                    is_neoclassical_constituent = parent[0] == "-" and parent[-1] == "-"
                    if is_neoclassical_constituent:
                        lexicon.create_lexeme(lemma=parent, pos="Affixoid").add_feature(feature="Fictitious",
                                                                                                  value="Yes")
                    else:
                        logger.warning(f"Parent {parent} from compound {lemma} not found in DeriNet, skipping.")
                        break

            if parentnum != len(lex):
                logger.warning(f"Didn't find enough parents for {lemma}, skipping.")
                continue

            else:
                children = lexicon.get_lexemes(lemma, pos="NUM")
                if children == []:
                    logger.warning(f"Child numeral {lemma} not found in DeriNet, skipping. Bug in previous loop, should have been added!")
                    continue

                for child in children:
                    lexicon.remove_all_parent_relations(child)
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
