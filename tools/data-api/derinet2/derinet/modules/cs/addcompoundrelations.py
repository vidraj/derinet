from derinet import Block, Format, Lexicon, DerinetMorphError, DerinetCycleCreationError
import argparse
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def find_first_true(boolean_list):
    for index, value in enumerate(boolean_list):
        if value:
            return index
    return None

class AddCompoundRelations(Block):
    def __init__(self, fname, fname_ambiguity):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname
        self.ambiguity_file = fname_ambiguity

    def process(self, lexicon: Lexicon):

        """
        Read two dataframes.

        1) Compound_parents is a tsv of compounds in the form of two columns -
        [lemma, parents]. The parents have to be divided by spaces.

        2) Compound_ambiguities is a tsv of c in the form of two columns -
        [lemma, parent_lemid]. Each compound lemma may have multiple entries.
        This is a manually annotated list of lemids specifying which lexeme
        out of a group of lemma-sharing lexemes (homonyms) the given compound should be attached to.

        This block does not add any lexemes. It instead adds compound relations to already-existing items
        in DeriNet. If a given parent however does not exist, it is skipped, unless it is a neoclassical
        constituent such as -psych-, in which case a lexeme is created.

        If the compound lemma is ambiguous, all instances get assigned the same set of parents.

        If only one parent is listed in the annotation, a derivational relation is created instead.

        If there are parents with an !exclamation point listed, a univerbisation relation is created.

        If the parent is the same as the lemma in question, all relations are stripped.

        """

        parent_df = pd.read_csv(self.fname, header=0, sep="\t")
        ambiguity_df = pd.read_csv(self.ambiguity_file, header=None, sep="\t")

        logger.debug(f"Lexicon size: {sum([1 for i in lexicon.iter_lexemes()])}")
        lexicon_lemmas = {i.lemma for i in lexicon.iter_lexemes()}

        for row in parent_df.itertuples():
            parentlist = row.parents.strip()
            parentlist = parentlist.replace("  ", " ")
            parentlist = parentlist.split(" ")

            parentnum = len(parentlist)
            lemma = row.lemma

            #This is the list of techlemmas that the compound is to be linked to (as opposed to their homonyms)

            disambiguation = ambiguity_df[ambiguity_df[0] == lemma][1].to_list()

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
                            disambiguation_index = find_first_true([i in disambiguation for i in lemids])

                            logger.info(f"Disconnecting {child_lexeme} from all parents")
                            lexicon.remove_all_parent_relations(child_lexeme)

                            if disambiguation_index is None:
                                parent_lexeme = possible_parent_lexemes[0]
                                lexicon.add_derivation(source=parent_lexeme, target=child_lexeme)
                                logger.warning(
                                            f"Parent {parentlist[0]} from derivative {lemma}"
                                            f" ambiguous, assigning first item from {lemids}.")
                            else:
                                parent_lexeme = possible_parent_lexemes[disambiguation_index]
                                lexicon.add_derivation(source=parent_lexeme, target=child_lexeme)
                                logger.info(
                                    f"Parent {parent_lexeme} from derivative {lemma}"
                                    f" successfully disambiguated from, selecting {lemids[disambiguation_index]}.")
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
                        logger.info(f"Created neocon {lexeme} with lemma {parent}.")
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
                            disambiguation_index = find_first_true([i in disambiguation for i in lemids])
                            if disambiguation_index is None:
                                parent_lexeme = possible_parent_lexemes[0]
                                lex.append(parent_lexeme)
                                logger.warning(
                                    f"Did not find disambiguation; parent {parentlist[0]} from compound/univerbate {lemma}"
                                    f" ambiguous, assigning first item from {lemids}.")
                            else:
                                parent_lexeme = possible_parent_lexemes[disambiguation_index]
                                lex.append(parent_lexeme)
                                logger.info(
                                    f"Parent {parent_lexeme} from compound/univerbate {lemma}"
                                    f" successfully disambiguated from {lemids}, selecting {lemids[disambiguation_index]}.")

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

        parser.add_argument("file", help="The file of compound/parent lemmas to load annotation from.")
        parser.add_argument("ambiguity_file", help="The file of compound lemma/parent techlamm to load.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file
        fname_ambiguity = args.ambiguity_file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname, fname_ambiguity], {}, args.rest
