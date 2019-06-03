from derinet import Block, Lexicon, DerinetError
from derinet.utils import techlemma_to_lemma
import re
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddDerivationsFromAllomorphOverlap(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read an allomorph overlap annotation file, parse out the resolution
        column and add all derivations specified therein.
        """

        solution_regex = re.compile(r"^SOLUTION:\s*([^ ]+)\s*>\s*([^ ]+)\s*$")

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()
                columns = line.split("\t")
                assert len(columns) == 8
                solution = columns[6]

                match = solution_regex.fullmatch(solution)
                if match is not None:
                    parent_techlemma, child_techlemma = match.groups()
                    parent_lemma = techlemma_to_lemma(parent_techlemma)
                    child_lemma = techlemma_to_lemma(child_techlemma)
                    parents = lexicon.get_lexemes(parent_lemma, techlemma=parent_techlemma, techlemma_match_fuzzy=True)
                    children = lexicon.get_lexemes(child_lemma, techlemma=child_techlemma, techlemma_match_fuzzy=True)

                    if not parents:
                        logger.error("Lexeme for lemma '{}' not found".format(parent_lemma))
                    elif not children:
                        logger.error("Lexeme for lemma '{}' not found".format(child_lemma))
                    elif len(parents) > 1:
                        logger.warning("Lexeme for lemma '{}' ambiguous, skipping".format(parent_lemma))
                    elif len(children) > 1:
                        logger.warning("Lexeme for lemma '{}' ambiguous, skipping".format(child_lemma))
                    else:
                        parent = parents[0]
                        child = children[0]
                        try:
                            lexicon.add_derivation(parent, child)
                        except DerinetError as e:
                            logger.error("Derivation {} → {} not added".format(parent, child), exc_info=e)
                elif solution == "SOLUTION:":
                    pass
                else:
                    logger.info("Solution '{}' not parseable".format(solution))

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
