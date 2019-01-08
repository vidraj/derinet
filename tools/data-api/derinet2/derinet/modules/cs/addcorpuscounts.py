from derinet.modules.block import Block

from derinet.utils import techlemma_to_lemma
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class AddCorpusCounts(Block):
    def __init__(self, args):
        if "file" not in args or "name" not in args:
            raise ValueError("Arguments 'file' and 'name' must be supplied.")
        else:
            self.fname = args["file"]
            self.name = args["name"]


    def process(self, derinet):
        """Read a file with corpus count statistics and store them into the misc section."""

        with open(self.fname, "rt") as f:
            for line in f:
                line = line.rstrip()
                count, techlemma, pos = line.split()
                count = int(count)
                lemma = techlemma_to_lemma(techlemma)

                # TODO perform the count-to-lemma matching twice. First, go over
                #  the whole database without a fallback, and then do it once again
                #  with fallback, filling only the lexemes which were not matched
                #  the first time.
                lexemes = derinet.search_lexemes(lemma, pos, techlemma, allow_fallback=True)

                # TODO do not fill all at once, first fill only exact matches and
                #  fill the rest in a second pass.
                for lexeme in lexemes:
                    if "corpus" not in lexeme.misc:
                        lexeme.misc["corpus"] = {}
                    if self.name not in lexeme.misc["corpus"]:
                        lexeme.misc["corpus"][self.name] = {}
                    if "count" not in lexeme.misc["corpus"][self.name]:
                        lexeme.misc["corpus"][self.name]["count"] = count

        return derinet
