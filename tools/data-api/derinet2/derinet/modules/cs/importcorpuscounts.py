from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class ImportCorpusCounts(Block):
    """
    Add corpus counts into the misc section of lexemes.
    """

    def __init__(self, fname):
        self.fname = fname

    def process(self, lexicon: Lexicon):
        corpus_total = 0

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 3
                lemma, pos, count = fields
                count = int(count)

                corpus_total += count

                lexemes = lexicon.get_lexemes(lemma, pos)

                if not lexemes:
                    logger.info("Lexeme for '{} {}' not found".format(lemma, pos))
                    continue

                if len(lexemes) > 1:
                    logger.warning("Lexeme for '{} {}' ambiguous, filling the count to all of them".format(lemma, pos))

                for lexeme in lexemes:
                    if "CorpusCount" in lexeme.misc:
                        logger.warning("Lexeme {} already has corpus count filled"
                                       "with value {}, will overwrite".format(
                            lexeme,
                            lexeme.misc["CorpusCount"]
                        ))

                    lexeme.misc["CorpusCount"] = count

        # Initialize all unseen lexemes to 0.
        for lexeme in lexicon.iter_lexemes():
            if "CorpusCount" not in lexeme.misc:
                lexeme.misc["CorpusCount"] = 0

        return lexicon

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load the corpus counts from,"
                                         "in a `lemma TAB pos TAB count` format."
                                         "In case of homonyms, the same count is"
                                         "added to all of them.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
