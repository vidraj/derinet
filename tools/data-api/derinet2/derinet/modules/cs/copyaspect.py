from derinet import Block, Lexicon, Format, DerinetError
from derinet.utils import techlemma_to_lemma
import re
import argparse
import logging

logger = logging.getLogger(__name__)


class CopyAspect(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        """

        # Load the source of aspectual information.
        old_lexicon = Lexicon().load(self.fname, fmt=Format.DERINET_V2)

        for lexeme in lexicon.iter_lexemes(sort=False):
            if lexeme.pos == "V":
                linked_lexemes = old_lexicon.get_lexemes(lexeme.lemma, lexeme.pos, lemid=lexeme.lemid)

                if not linked_lexemes:
                    # Try again without the lemid specification.
                    linked_lexemes = old_lexicon.get_lexemes(lexeme.lemma, lexeme.pos)

                # Don't try to unify lexemes based on techlemmas – they
                #  won't match. If they matched, they would either both
                #  contain the aspectual information, or they would both
                #  lack it. In either case, there is no processing to be
                #  done.

                if not linked_lexemes:
                    logger.warning("Lexeme {} not found in the old DB".format(lexeme))
                    continue
                elif len(linked_lexemes) == 1:
                    aspect = linked_lexemes[0].feats.get("Aspect")
                elif len(linked_lexemes) > 1:
                    aspects = [l.feats.get("Aspect") for l in linked_lexemes if "Aspect" in l.feats]
                    aspect = aspects[0] if aspects else None
                    if len(set(aspects)) > 1:
                        logger.info("Lexeme {} ambiguous, possible aspects {}, picking {}".format(lexeme, aspects, aspect))

                if aspect is None:
                    # The old lexeme doesn't have aspect, skip it.
                    if "Aspect" not in lexeme.feats:
                        # Warn only in case the new lexeme has no aspect either.
                        logger.warning("Lexeme {} has no aspect even in the old DB".format(lexeme))
                    continue

                if "Aspect" in lexeme.feats and lexeme.feats["Aspect"] != aspect:
                        # Both lexemes have aspect and they don't match.
                        logger.warning("Lexeme {} already has aspect filled {} different from linked {}, overwriting".format(lexeme, lexeme.feats["Aspect"], aspect))

                #logger.debug("Setting aspect of {} to {}".format(lexeme, aspect))
                lexeme.feats["Aspect"] = aspect

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

        parser.add_argument("file", help="The DeriNet V2 database to copy aspect from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
