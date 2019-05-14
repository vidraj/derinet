from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddSemanticRelationLabels(Block):
    def __init__(self, fname):
        self.fname = fname

    def get_lexemes_for_lemmapos(self, lexicon, lemmapos):
        fields = lemmapos.split("–")
        if len(fields) != 2:
            raise ValueError("Lemma-pos '{}' not parseable".format(lemmapos))
        lemma, pos = fields

        lexemes = lexicon.get_lexemes(lemma, pos)
        if len(lexemes) == 0:
            raise Exception("Lemma-pos '{}' not found".format(lemmapos))
        else:
            return lexemes

    def process(self, lexicon: Lexicon):
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 4
                parent_lemmapos, child_lemmapos, label, prob_str = fields
                label = label.lower()

                try:
                    parent_lexemes = self.get_lexemes_for_lemmapos(lexicon, parent_lemmapos)
                except:
                    logger.error("Error getting parent lexemes '{}':".format(parent_lemmapos), exc_info=True)
                    continue

                try:
                    child_lexemes = self.get_lexemes_for_lemmapos(lexicon, child_lemmapos)
                except:
                    logger.error("Error getting child lexemes '{}':".format(child_lemmapos), exc_info=True)
                    continue

                valid_pairs = []
                for parent_lexeme in parent_lexemes:
                    for child_lexeme in child_lexemes:
                        if child_lexeme.parent is parent_lexeme:
                            valid_pairs.append((parent_lexeme, child_lexeme))

                if not valid_pairs:
                    logger.error("Lexemes '{}' and '{}' are not derived from one another".format(parent_lemmapos, child_lemmapos))
                    continue
                elif len(valid_pairs) > 1:
                    logger.error("Relation '{}' -> '{}' is ambiguous".format(parent_lemmapos, child_lemmapos))
                    continue
                else:
                    parent_lexeme, child_lexeme = valid_pairs[0]
                    child_lexeme.parent_relation.type["semantic-label"] = label

        return lexicon

    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
