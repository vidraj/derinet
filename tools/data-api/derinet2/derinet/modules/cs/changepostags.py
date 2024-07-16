from derinet import Block, Format, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class ChangePosTags(Block):
    """
    Change POS tags to Universal tagset.
    """
    def process(self, lexicon: Lexicon):
        translate_pos = {'N': 'NOUN', 'A': 'ADJ', 'P': 'PRON', 'C': 'NUM', 'V': 'VERB', 'D': 'ADV', 'R': 'ADP'}
        for lexeme in lexicon.iter_lexemes():
            # Note that this breaks the internal datastructures of the
            #  Lexicon, so it might not work at all, and if it does, it's
            #  best to save and reload the database immediately afterwards.
            lexeme._pos = translate_pos[lexeme.pos]

        return lexicon
