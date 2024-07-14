from derinet import Block, Lexicon
from derinet.utils import techlemma_to_lemma
import argparse
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class RenameAffixoidToNeocon(Block):
    def process(self, lexicon: Lexicon):
        """
        This simple block renames all Affixoid POS to Neocon to avoid annoying Emil Svoboda's dissertation
        reviewers.
        """

        for lexeme in lexicon.iter_lexemes():
            # Note that this breaks the internal datastructures of the
            #  Lexicon, so it might not work at all, and if it does, it's
            #  best to save and reload the database immediately afterwards.
            if lexeme.pos == "Affixoid":
                lexeme._pos = "NeoCon"

        return lexicon
