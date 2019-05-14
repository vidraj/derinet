from derinet import Block, Format, Lexicon
from derinet.utils import techlemma_to_lemma
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class GenerateFakeTagMasks(Block):
    """
    For each lexeme which still has its default tag mask, generate a fake one
    consisting of the lemma, POS and 14 question marks.
    """
    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes():
            if lexeme.lemid == "{}#{}".format(lexeme.lemma, lexeme.pos):
                lexeme._lemid += "??????????????"

        return lexicon
