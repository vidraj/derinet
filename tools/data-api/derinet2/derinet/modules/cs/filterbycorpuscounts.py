from derinet.modules.block import Block

from derinet.utils import pretty_lexeme
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def remove_fully_true_subtrees(derinet, root, condition):
    """
    Remove all lexemes from the subtree of root, where condition evaluates to a truthy value for all descendants.
    Condition is a function of two arguments: DeriNet and Node.
    """
    lexeme = derinet.get_lexeme(root)
    for child in derinet.get_children(lexeme):
        remove_fully_true_subtrees(derinet, child, condition)

    if len(derinet.get_children(lexeme)) == 0 and condition(derinet, lexeme):
        logger.info("Removing lexeme %s", pretty_lexeme(lexeme.lemma, lexeme.pos, lexeme.morph))
        derinet.remove_lexeme(lexeme)
    else:
        logger.info("Keeping lexeme %s", pretty_lexeme(lexeme.lemma, lexeme.pos, lexeme.morph))

class FilterByCorpusCounts(Block):
    def __init__(self, args):
        if "min-count" not in args or "name" not in args:
            raise ValueError("Arguments 'min-count' and 'name' must be supplied.")
        else:
            self.min_count = int(args["min-count"])
            self.name = args["name"]

    def process(self, derinet):
        """Read a file with corpus count statistics and store them into the misc section."""

        for root in derinet.iter_roots():
            remove_fully_true_subtrees(derinet,
                                       root,
                                       lambda derinet, lexeme: not ("corpus" in lexeme.misc
                                                                    and self.name in lexeme.misc["corpus"]
                                                                    and "count" in lexeme.misc["corpus"][self.name]
                                                                    and lexeme.misc["corpus"][self.name]["count"] >= self.min_count))

        return derinet
