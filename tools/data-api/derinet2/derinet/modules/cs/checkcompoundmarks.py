from derinet import Block, Lexicon
from derinet.utils import DerinetCycleCreationError
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def check_compound_mark(node):
    """Check and correct annotation of compounds."""
    if node.parent is not None:
        c_in_parents = False
        par_node = node
        while par_node.parent is not None:
            par_node = par_node.parent
            if "is_compound" in par_node.misc and par_node.misc["is_compound"]:
                c_in_parents = True
                break

        par_node = node.parent
        if c_in_parents:
            node.misc["is_compound"] = False
            logger.warning('Lemma has parent already marked as'
                  ' compound, so C was removed from lemma.'
                  ' Lemma: {} Parent: {}'.format(node, par_node))
        else:
            if par_node.lemma in node.lemma:
                logger.error('Relation between lemma and parent might be'
                      ' removed. Lemma: {} Parent: {}'.format(node, par_node))
            else:
                node.misc["is_compound"] = False
                par_node.misc["is_compound"] = True
                logger.warning('Lemma has unmarked (compound) parent. Mark of'
                      ' lemma was removed and parent was marked (and checked).'
                      ' Lemma: {} Parent: {}'.format(node, par_node))
                check_compound_mark(par_node)
    else:
        logger.info('Lemma marked as compound. OK. Lemma: {}'.format(node))



class CheckCompoundMarks(Block):
    def process(self, lexicon: Lexicon):
        """
        Check that compounds are roots of trees. If not, move the compound
        mark higher up the tree or warn about suspicious relations.
        """
        for lexeme in lexicon.iter_lexemes(sort=False):
            if "is_compound" in lexeme.misc and lexeme.misc["is_compound"]:
                check_compound_mark(lexeme)

        return lexicon
