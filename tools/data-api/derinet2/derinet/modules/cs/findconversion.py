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
            for rel in lexeme.parent_relations:
                if len(rel.sources) == 1 and lexeme.lemma == rel.main_source.lemma:
                    parent_lexeme = rel.main_source
                    lexicon.remove_relation(rel)
                    lexicon.add_conversion(parent_lexeme, lexeme)

        return lexicon
