from derinet import Block, Lexicon
from derinet.utils import techlemma_to_lemma
import argparse
import re
import logging


logger = logging.getLogger(__name__)


class AddCompounds(Block):
    lemma_pos_regex = re.compile(r"^(.*)#(.)$")

    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def split_lemma_pos(self, lemma_pos):
        match = self.lemma_pos_regex.fullmatch(lemma_pos)
        if match is None:
            raise ValueError("Lemma#pos string '{}' not parseable.".format(lemma_pos))
        else:
            lemma, pos = match.groups()
            return lemma, pos

    def find_lemma_pos(self, lexicon, lemma_pos):
        techlemma, pos = self.split_lemma_pos(lemma_pos)
        lemma = techlemma_to_lemma(techlemma)
        lexemes = lexicon.get_lexemes(lemma, pos, techlemma=techlemma, techlemma_match_fuzzy=True)

        if len(lexemes) == 0:
            logger.warning("Lemma#pos '{}' not found".format(lemma_pos))
            return None
        elif len(lexemes) == 1:
            return lexemes[0]
        else:
            logger.warning("Lemma#pos '{}' ambiguous".format(lemma_pos))
            return None


    def process(self, lexicon: Lexicon):
        """
        Load annotated compounds from a file and add the confirmed ones to the
        database.

        Format: mark compound tab first-parent tab second-parent
        where mark is nothing for confirmed compounds or exclamation mark
        for rejected compounds.

        The second parent is always considered to be the head of the relation.
        """


        with open(self.fname, "rt", encoding="utf-8", newline="\n") as in_file:
            for line_nr, line in enumerate(in_file):
                fields = line.rstrip("\n").split("\t")
                if len(fields) != 3:
                    logger.error("Line nr. {} is corrupt, has wrong number of fields.".format(line_nr))
                    continue

                marked_compound_lemma_pos, first_parent_lemma_pos, second_parent_lemma_pos = fields

                if marked_compound_lemma_pos.startswith("!"):
                    # Negative example, ignore.
                    continue

                compound = self.find_lemma_pos(lexicon, marked_compound_lemma_pos)
                first_parent = self.find_lemma_pos(lexicon, first_parent_lemma_pos)
                second_parent = self.find_lemma_pos(lexicon, second_parent_lemma_pos)

                if compound is not None and first_parent is not None and second_parent is not None:
                    if compound.parent is not None:
                        logger.warning("Disconnecting lexeme {} from {}, attaching it to {} instead".format(compound, compound.parent_relation.sources, [first_parent, second_parent]))
                        lexicon.remove_relation(compound.parent_relation)
                    lexicon.add_composition([first_parent, second_parent], second_parent, compound)

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
