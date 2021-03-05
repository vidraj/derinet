from derinet import Block, Lexicon
import argparse
import logging
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class DeleteUnattestedLeaves(Block):
    """
    Filter the database so that no unattested leaves remain.
    """

    def delete_children(self, lexicon, lexeme):
        for child in lexeme.children:
            self.delete_children(lexicon, child)

        if lexeme.misc["corpus_stats"]["absolute_count"] == 0 and len(lexeme.children) == 0:
            lexicon.delete_lexeme(lexeme, delete_relations=True)

    def process(self, lexicon: Lexicon):
        # Make sure to first build the list to iterate over, then iterate.
        #  Otherwise we modify the iterator while using it, which is not
        #  well defined.
        for lexeme in list(lexicon.iter_trees(sort=False)):
            logger.info("Processing tree {}".format(lexeme))
            self.delete_children(lexicon, lexeme)

        return lexicon
