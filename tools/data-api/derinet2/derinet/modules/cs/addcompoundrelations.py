from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging
import pandas as pd

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

        for row in newdf.itertuples():
            parentlist = row.parents.split(" ")
            parentnum = len(parentlist)
            word = row.lemma

            logger.debug(f"Compounding '{word}' from '{parentlist}'")

            lex = []
            for parent in parentlist:
                lst = lexicon.get_lexemes(parent)
                if len(lst) == 1:
                    lex.append(lst[0])
                if len(lst) > 1:
                    lex.append(lst[0])
                    logger.warning(f"Parent {lst[0].lemma} from compound {word} ambiguous, assigning first item from {[i.lemid for i in lst]}.")
                else:
                    is_neoclassical_constituent = parent[0] == "-" and parent[-1] == "-"
                    if is_neoclassical_constituent:
                        lexicon.create_lexeme(lemma=parent, pos="Affixoid").add_feature(feature="Fictitious", value="Yes")
                    else:
                        logger.warning(f"Parent {lst[0].lemma} from compound {word} not found in DeriNet, skipping.")
                        continue


            if parentnum < len(lex):
                continue
            else:
                children = lexicon.get_lexemes(word)

                if not children:
                    logger.warning(f"Compound {word} not found in DeriNet, skipping.")
                    continue

                for child in children:
                    existing_rels = child.parent_relations
                    for rel in existing_rels:
                        logger.info(f"Disconnecting {word} from {rel}")
                        rel.remove_from_lexemes()
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
