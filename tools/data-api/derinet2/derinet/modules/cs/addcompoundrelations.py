from derinet import Block, Format, Lexicon, DerinetMorphError, DerinetCycleCreationError
import argparse
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddCompoundRelations(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read dataframe in a tsv of compounds in the form of two columns -
        [lemma, parents]. The parents have to be divided by spaces.

        This block does not add any lexemes. It instead adds compound relations to already-existing items
        in DeriNet. If a given parent however does not exist, a lexeme is created for it, being given an
        'Unknown' POS, and a warning is emitted. If such a parent has -hyphens- on both sides, a lexeme is silently
        created for it with the ROOT part-of-speech.

        If the compound lemma is ambiguous, all instances get assigned the same set of parents.
        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")
        logger.debug(f"Lexicon size: {sum([1 for i in lexicon.iter_lexemes()])}")

        for row in newdf.itertuples():
            parentlist = row.parents.strip().split(" ")
            parentnum = len(parentlist)
            lemma = row.lemma

            if parentnum == 1:
                if parentlist[0] == lemma:
                    logger.debug(
                        f"{lemma} annotated as Unmotivated, skipping.")
                    continue
                else:
                    logger.debug(
                        f"{lemma} annotated as Derivation, skipping.")
                    continue

            logger.debug(f"Compounding '{lemma}' from '{parentlist}'")

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
                        lexicon.create_lexeme(lemma=parent, pos="Affixoid").add_feature(feature="Fictitious", value="Yes")
                    else:
                        logger.warning(f"Parent {parent} from compound {lemma} not found in DeriNet, skipping.")
                        break


            if parentnum != len(lex):
                logger.warning(f"Didn't find enough parents for {lemma}, skipping.")
                continue
            else:
                children = lexicon.get_lexemes(lemma)

                if not children:
                    logger.warning(f"Compound {lemma} not found in DeriNet, skipping.")
                    continue

                for child in children:
                    existing_rels = child.parent_relations
                    for rel in existing_rels:
                        logger.info(f"Disconnecting {lemma} from {rel}")
                        rel.remove_from_lexemes()
                    try:
                        lexicon.add_composition(lex, lex[-1], child)
                    except DerinetCycleCreationError as ex:
                        logger.error(f"Couldn't connect {child} to {', '.join(str(l) for l in lex)}", exc_info=ex)

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
