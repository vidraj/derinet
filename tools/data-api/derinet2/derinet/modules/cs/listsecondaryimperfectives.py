from derinet import Block, Lexicon
import argparse
import logging

logger = logging.getLogger(__name__)


class ListSecondaryImperfectives(Block):
    """
    List imperfective verbs which are derived by suffixation from
    perfective verbs derived by prefixation from verbs.
    """

    def __init__(self, fname):
        self.fname = fname

    def process(self, lexicon: Lexicon):
        # Fill in the absolute counts.
        with open(self.fname, "wt", encoding="utf-8") as out_f:
            for lexeme in lexicon.iter_lexemes():
                # We test for imperfectives by asking `not Perf`, because many
                #  verbs lack the necessary annotations.
                if (lexeme.pos == "VERB" and lexeme.feats.get("Aspect") != "Perf"
                    and lexeme.parent and lexeme.parent.pos == "VERB"
                    and lexeme.parent.feats.get("Aspect") != "Imp" and
                    lexeme.parent.parent and lexeme.parent.parent.pos == "VERB"):
                    # This might be a secondary imperfective, if the prefixes
                    #  and suffixes are right.
                    lemma = lexeme.lemma
                    plemma = lexeme.parent.lemma
                    pplemma = lexeme.parent.parent.lemma

                    # We can't easily detect if plemma is made by
                    #  prefixation, but we can easily detect some
                    #  suffixation: Chop the final -t, detect substrings.
                    if plemma[:-1].startswith(pplemma[:-1]):
                        logger.info("Detected suffixation in {} -> {}".format(pplemma, plemma))
                        continue

                    # Similarly, we can't easily detect suffixation, but
                    #  we can rule out some prefixations in lemma.
                    if lemma.endswith(plemma):
                        logger.info("Detected prefixation in {} -> {}".format(plemma, lemma))
                        continue

                    count = lexeme.misc["corpus_stats"]["absolute_count"]
                    pcount = lexeme.parent.misc["corpus_stats"]["absolute_count"]
                    ppcount = lexeme.parent.parent.misc["corpus_stats"]["absolute_count"]

                    print(pplemma, ppcount, plemma, pcount, lemma, count, sep="\t", file=out_f)
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

        parser.add_argument("file", help="The file to save the imperfectives to"
                                         " in a TSV format.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
