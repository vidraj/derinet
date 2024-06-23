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
        in DeriNet. If a given parent however does not exist, it is skipped, unless it is a neoclassical
        constituent such as -psych-, in which case a lexeme is created.

        If the compound lemma is ambiguous, all instances get assigned the same set of parents.

        If only one parent is listed in the annotation, a derivational relation is created instead.

        If there are parents with an !exclamation point listed, a univerbisation relation is created.

        If the parent is the same as the lemma in question, all relations are stripped.

        """

        newdf = pd.read_csv(self.fname, header=0, sep="\t")
        logger.debug(f"Lexicon size: {sum([1 for i in lexicon.iter_lexemes()])}")
        lexicon_lemmas = {i.lemma for i in lexicon.iter_lexemes()}

        for row in newdf.itertuples():
            parentlist = row.parents.strip()
            parentlist = parentlist.replace("  ", " ")
            parentlist = parentlist.split(" ")

            parentnum = len(parentlist)
            lemma = row.lemma

            #Unmotivated and derivative
            if parentnum == 1:

                #Unmotivated
                if parentlist[0] == lemma:
                    for lexeme in lexicon.get_lexemes(lemma):
                        lexicon.remove_all_parent_relations(lexeme)
                        logger.info(
                            f"{lexeme} annotated as Unmotivated, stripping all relations.")
                    continue
                #

                #Derivative
                else:
                    for child_lexeme in lexicon.get_lexemes(lemma):
                        logger.info(f"{child_lexeme} annotated as Derivation")

                        possible_parent_lexemes = lexicon.get_lexemes(parentlist[0])
                        if len(possible_parent_lexemes) == 0:
                            logger.warning(
                                f"Derivational parent {parentlist[0]} from derivative {lemma} not found, skipping.")
                        elif len(possible_parent_lexemes) == 1:
                            parent_lexeme = possible_parent_lexemes[0]
                            logger.info(f"Disconnecting {child_lexeme} from all parents")
                            lexicon.remove_all_parent_relations(child_lexeme)
                            lexicon.add_derivation(source=parent_lexeme, target=child_lexeme)
                            logger.info(
                                f"Derivational parent {parent_lexeme} attached to derivative {child_lexeme}.")
                        else:
                            lemids = [i.lemid for i in possible_parent_lexemes]
                            parent_lexeme = possible_parent_lexemes[0]
                            logger.info(f"Disconnecting {child_lexeme} from all parents")
                            lexicon.remove_all_parent_relations(child_lexeme)
                            lexicon.add_derivation(source=parent_lexeme, target=child_lexeme)
                            logger.warning(
                                        f"Parent {parentlist[0]} from derivative {lemma}"
                                        f" ambiguous, assigning first item from {lemids}.")
                    continue
                #

            # Compounding and univerbisation
            else:
                #Keep track if compounding or univerbisation
                if parentlist[0][0] == "!":
                    parentlist[0] = parentlist[0].strip("!")
                    wf_type = "univerbate"
                else:
                    wf_type = "compound"

                logger.debug(f"Handling {wf_type} '{lemma}', from '{parentlist}'")

                lex = []
                for parent in parentlist:

                    #Add neocon if not in DeriNet
                    is_neoclassical_constituent = parent[0] == "-" and parent[-1] == "-"
                    if is_neoclassical_constituent and parent not in lexicon_lemmas:
                        lexeme = lexicon.create_lexeme(lemma=parent,
                                                       pos="Affixoid").add_feature(feature="Fictitious",
                                                                                    value="Yes")
                        lexicon_lemmas.add(parent)
                        logger.info(f"Created neocon {lexeme}.")
                    #

                    possible_parent_lexemes = lexicon.get_lexemes(parent)
                    if len(possible_parent_lexemes) == 1:
                        lex.append(possible_parent_lexemes[0])
                    elif len(possible_parent_lexemes) > 1:
                        lemids = [i.lemid for i in possible_parent_lexemes]
                        POSes = [i.split("#")[1][0] for i in lemids]

                        if "C" in POSes:
                            where = np.where(np.array(POSes) == "C")[0].tolist()[0]
                            lex.append(possible_parent_lexemes[where])
                            logger.warning(
                                f"Parent {parent} from compound {lemma} ambiguous, assigning first numeral from {lemids}.")

                        else:
                            lex.append(possible_parent_lexemes[0])
                            logger.warning(
                                f"Parent {parent} from compound {lemma} ambiguous, assigning first item from {lemids}. (no numerals found)")

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
                        logger.info(f"Disconnecting {child} from all parents")
                        try:
                            if wf_type == "compound":
                                lexicon.remove_all_parent_relations(child)
                                lexicon.add_composition(sources=lex, main_source=lex[-1], target=child)
                                logger.info(f"Connecting {wf_type} {child} to parents {parentlist}")
                            elif wf_type == "univerbisation":
                                lexicon.remove_all_parent_relations(child)
                                lexicon.add_univerbisation(sources=lex, main_source=lex[-1], target=child)
                                logger.info(f"Connecting {wf_type} {child} to parents {parentlist}")
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
