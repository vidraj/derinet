from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class ChangePosTags(Block):
    """
    Change POS tags to Universal tagset.
    """
    def process(self, lexicon: Lexicon):
        translate_pos = {'N': 'NOUN', 'A': 'ADJ', 'P': 'PRON', 'C': 'NUM', 'V': 'VERB', 'D': 'ADV', 'R': 'ADP'}
        for lexeme in lexicon.iter_lexemes():
            lexeme._pos = translate_pos[lexeme.pos]

        return lexicon
