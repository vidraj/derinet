from derinet.modules.block import Block

from derinet.utils import pretty_lexeme, techlemma_to_lemma
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def remove_subtree(derinet, root):
    """
    Remove all lexemes from the subtree of root.
    """
    lexeme = derinet.get_lexeme(root)
    for child in derinet.get_children(lexeme):
        remove_subtree(derinet, child)

    #assert not derinet.get_children(lexeme), "All children were removed from {}, yet some remain? Error!".format(pretty_lexeme(lexeme))

    #logger.info("Removing lexeme %s", pretty_lexeme(lexeme))
    derinet.remove_lexeme(lexeme)


class DeleteSubtrees(Block):
    def __init__(self, args):
        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.file = args["file"]

    def process(self, derinet):
        """Delete all subtrees with roots in file."""

        with open(self.file, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                techlemma, pos = line.split("\t")

                if not techlemma or not pos:
                    logger.error("Malformed line '%s' in file '%s'. Skipping.", line, self.file)
                    continue

                lemma = techlemma_to_lemma(techlemma)
                lexemes = derinet.search_lexemes(lemma, pos, techlemma, allow_fallback=True)

                if not lexemes:
                    logger.warning("Lexeme %s not found", pretty_lexeme(lemma, pos, techlemma))
                    continue
                elif len(lexemes) > 1:
                    logger.warning("Ambiguous lexeme %s, skipping", pretty_lexeme(lemma, pos, techlemma))
                    continue

                logger.info("Removing subtree of %s", pretty_lexeme(lemma, pos, techlemma))

                lexeme = lexemes[0]
                remove_subtree(derinet, lexeme)

        return derinet
