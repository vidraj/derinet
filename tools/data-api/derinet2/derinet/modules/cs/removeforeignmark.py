from derinet import Block, Lexicon
import logging


logger = logging.getLogger(__name__)


class RemoveForeignMark(Block):
    """
    Remove Foreign mark because it is joint with Loanword label.
    """
    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes():
            if lexeme.feats.get('Foreign', False):
                lexeme.feats.pop('Foreign', None)
                logger.info('Foreign mark deleted from {}.'.format(lexeme))

        return lexicon
