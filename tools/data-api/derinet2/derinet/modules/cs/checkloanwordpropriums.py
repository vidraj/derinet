from derinet import Block, Lexicon
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class CheckLoanwordPropriums(Block):
    """
    Find propriums and their subtrees and delete label Loanwords from them.
    """
    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes():
            if lexeme.lemma[0].isupper():
                for node in lexeme.iter_subtree():
                    node.feats.pop('Loanword', None)
                    logger.info('Loanword mark deleted from {}.'.format(node))

        return lexicon
