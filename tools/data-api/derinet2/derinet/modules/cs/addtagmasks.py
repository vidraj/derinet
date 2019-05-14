from derinet import Block, Format, Lexicon
from derinet.utils import techlemma_to_lemma
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddTagMasks(Block):
    def __init__(self, fname):
        self.fname = fname

    def process(self, lexicon: Lexicon):
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 2
                techlemma, tag_mask = fields
                lemma = techlemma_to_lemma(techlemma)
                pos = tag_mask[0]

                lexemes = lexicon.get_lexemes(lemma, pos, techlemma)

                if not lexemes:
                    logger.error("Lexeme for '{} {}' not found".format(techlemma, tag_mask))
                elif len(lexemes) > 1:
                    logger.error("Lexeme for '{} {}' ambiguous".format(techlemma, tag_mask))
                else:
                    lexeme = lexemes[0]

                    if lexeme.lemid != "{}#{}".format(lemma, pos):
                        logger.error("Lemid of lexeme {} already set".format(lexeme))
                    else:
                        lexeme._lemid = "{}#{}".format(lemma, tag_mask)

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

        parser.add_argument("file", help="The file to load tag masks from, in a `techlemma TAB tag-mask` format.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
