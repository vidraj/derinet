from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class DeleteUnattestedLeaves(Block):
    """
    Filter the database so that no unattested leaves remain.
    """

    def corpus_count(self, lexeme):
        if "corpus_stats" in lexeme.misc:
            cs = lexeme.misc["corpus_stats"]
            if "absolute_count" in cs:
                return cs["absolute_count"]

        # We can return 0 or not-0, depending on what the default should
        #  be. Let's say that lexemes with missing annotation are
        #  considered to be attested.
        return 1

    def delete_children(self, lexicon, lexeme):
        for child in lexeme.children:
            self.delete_children(lexicon, child)

        if self.corpus_count(lexeme) == 0 and len(lexeme.children) == 0:
            lexicon.delete_lexeme(lexeme, delete_relations=True)

    def process(self, lexicon: Lexicon):
        # Make sure to first build the list to iterate over, then iterate.
        #  Otherwise we modify the iterator while using it, which is not
        #  well defined.
        for lexeme in list(lexicon.iter_trees(sort=False)):
            logger.info("Processing tree {}".format(lexeme))
            self.delete_children(lexicon, lexeme)

        return lexicon
