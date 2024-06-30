from derinet import Block, Lexicon
from derinet.utils import DerinetCycleCreationError
import argparse
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def techlemma_to_lemma(techlemma):
    """Cut off the technical suffixes from the string techlemma and return the raw lemma"""
    shortlemma = re.sub("[_`].+", "", techlemma)
    lemma = re.sub("-\d+$", "", shortlemma)
    return lemma


class RenameAffixoidToNeocon(Block):
    def process(self, lexicon: Lexicon):
        """
        This simple block renames all Affixoid POS to Neocon to avoid annoying Emil Svoboda's dissertation
        reviewers.
        """

        for lexeme in lexicon.iter_lexemes():
            if lexeme.pos == "Affixoid":
                lexeme._pos = "NeoCon"

        return lexicon