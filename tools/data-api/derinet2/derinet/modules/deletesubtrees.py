from derinet import Block, Lexicon
from derinet.utils import techlemma_to_lemma
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class DeleteSubtrees(Block):
    """
    Delete all subtrees of lexemes listed in a file.
    """

    def __init__(self, file, lemma_type):
        self.file = file
        self.lemma_type = lemma_type

    def remove_subtree(self, lexicon, root):
        """
        Remove all lexemes from the subtree of the lexeme `root`,
        including the root.
        """
        for child in root.children:
            self.remove_subtree(lexicon, child)
        lexicon.delete_lexeme(root, delete_relations=True)

    def remove_homonym_subtrees(self, lexicon, techlemma, pos):
        """
        Delete all lexemes from subtrees of all lexemes with the specified
        techlemma (matched fuzzily) and pos, including the root.
        """
        if self.lemma_type == "lemma":
            lexemes = lexicon.get_lexemes(techlemma, pos=pos)
            warn_techlemma_match = False
        elif self.lemma_type == "techlemma":
            lemma = techlemma_to_lemma(techlemma)
            lexemes = lexicon.get_lexemes(lemma, pos=pos, techlemma=techlemma, techlemma_match_fuzzy=False)
            warn_techlemma_match = False
        elif self.lemma_type == "fuzzy-techlemma":
            # Note: the fuzzy techlemma matching may produce different
            #  results based on the order of records in the input file.
            lemma = techlemma_to_lemma(techlemma)
            lexemes = lexicon.get_lexemes(lemma, pos=pos, techlemma=techlemma, techlemma_match_fuzzy=True)
            warn_techlemma_match = True
        else:
            raise ValueError("Unknown lemma_type {}".format(self.lemma_type))

        if not lexemes:
            logger.warning("No lexemes to delete found for '{}#{}'.".format(techlemma, pos))
        elif warn_techlemma_match and lexemes[0].techlemma != techlemma:
            logger.warning("Fuzzily matched techlemma when deleting '{}#{}', got '{}' ({})".format(techlemma, pos, lexemes[0].techlemma, lexemes[0]))
            if len(lexemes) > 1:
                logger.warning("... and got multiple fuzzy matches for ^^^!")
        elif len(lexemes) > 1:
            logger.warning("Found multiple lexemes for '{}#{}', deleting all.".format(techlemma, pos))

        # Delete all subtrees of all matched lexemes.
        for lexeme in lexemes:
            self.remove_subtree(lexicon, lexeme)

    def process(self, lexicon: Lexicon):
        for line in self.file:
            line = line.rstrip("\n")
            fields = line.split("\t")

            assert len(fields) == 2
            techlemma, pos = fields

            self.remove_homonym_subtrees(lexicon, techlemma, pos)

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

        parser.add_argument("--lemma-type", choices=["lemma", "techlemma", "fuzzy-techlemma"], default="lemma", help="Use the first column as a plain lemma, a strictly-matched (Czech) techlemma or a fuzzily-matched techlemma.")
        parser.add_argument("file", type=argparse.FileType("rt"), help="The file to load, in TSV format `(tech)lemma TAB pos-tag`.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [args.file, args.lemma_type], {}, args.rest
