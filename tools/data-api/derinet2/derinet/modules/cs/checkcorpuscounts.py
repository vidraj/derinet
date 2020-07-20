from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class CheckCorpusCounts(Block):
    """
    Check that the parents of each word have higher corpus counts than the word
    itself, and report all corpus-attested words derived from unattested ones.
    """

    def process(self, lexicon: Lexicon):
        for child in lexicon.iter_lexemes(sort=False):
            ccount = child.misc["corpus_stats"]["absolute_count"]
            for parent in child.all_parents:
                pcount = parent.misc["corpus_stats"]["absolute_count"]
                if pcount < ccount:
                    print(parent, pcount, child, ccount, sep="\t")

        return lexicon
