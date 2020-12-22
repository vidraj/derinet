from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class FindConversion(Block):
    """
    Find relations of conversion and change their type to Conversion.
    """
    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes():
            if lexeme.parent:
                parent_node = lexeme.parent
                if lexeme.lemma == parent_node.lemma:
                    lexeme.parent_relation.remove_from_lexemes()
                    lexicon.add_conversion(parent_node, lexeme)

        return lexicon
