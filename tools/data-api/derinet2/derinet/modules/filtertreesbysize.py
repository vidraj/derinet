from derinet.modules.block import Block

from derinet.utils import pretty_lexeme
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class FilterTreesBySize(Block):
    def __init__(self, args):
        if "min_size" not in args:
            raise ValueError("Argument 'min_size' must be supplied.")
        else:
            self.min_size = int(args["min_size"])


    def process(self, derinet):
        """Delete all trees which are smaller than min_size."""

        for root_id in derinet.iter_roots():
            root_lexeme = derinet.get_lexeme(root_id)
            root_lexeme_str = pretty_lexeme(root_lexeme.lemma, root_lexeme.pos, root_lexeme.morph)
            size = derinet.get_subtree_size(root_id)
            if size < self.min_size:
                logger.info("The tree under %s is below the limit. Removed.", root_lexeme_str)
                derinet.remove_subtree(root_id)
            else:
                logger.info("The tree under %s is above the limit. Kept.", root_lexeme_str)

        return derinet
