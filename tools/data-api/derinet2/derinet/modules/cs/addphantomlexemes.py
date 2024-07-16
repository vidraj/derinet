from derinet import Block, Format, Lexicon, DerinetMorphError
import argparse
import logging


logger = logging.getLogger(__name__)


class AddPhantomLexemes(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Read annotation in the form of
        mark child-lemma TAB parent-lemma
        and if mark == +, annotate parent as fictitious and add a derivation
        from parent to child.
        """

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()

                if line.startswith("+"):
                    columns = line[1:].split("\t")
                    assert len(columns) == 2
                    child_lemma, parent_lemma = columns

                    parent_lexemes = lexicon.get_lexemes(parent_lemma)
                    child_lexemes = lexicon.get_lexemes(child_lemma)

                    if len(parent_lexemes) == 1 and len(child_lexemes) == 1:
                        parent_lexeme = parent_lexemes[0]
                        child_lexeme = child_lexemes[0]

                        # Add the "Fictitious" mark to the parent.
                        parent_lexeme.add_feature("Fictitious", "Yes")

                        # Add the derivation.
                        lexicon.add_derivation(parent_lexeme, child_lexeme)
                    else:
                        if not parent_lexemes:
                            logger.error("Lexeme for lemma {} not found".format(parent_lemma))
                        if not child_lexemes:
                            logger.error("Lexeme for lemma {} not found".format(child_lemma))
                        if len(parent_lexemes) > 1:
                            logger.warning("Lexeme for lemma {} ambiguous, skipping".format(parent_lemma))
                        if len(child_lexemes) > 1:
                            logger.error("Lexeme for lemma {} ambiguous, skipping".format(child_lemma))

        return lexicon

    @classmethod
    def parse_args(cls, args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
