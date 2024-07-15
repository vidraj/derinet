from derinet import Block, Lexicon, DerinetCycleCreationError
import argparse
import logging

import os
import sys
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def similarity(a, b):
    """
    Return the string-wise similarity between `a` and `b`.
    Currently, we approximate it with the length of the longest common
    prefix.
    """
    for i in range(len(a) - 1):
        if not b.startswith(a[:i + 1]):
            return i
    return len(a)

def most_similar(clexemes, plexeme):
    """
    Return the lexeme from clexemes which is most similar to plexeme.
    """
    return max([(similarity(lexeme.lemma, plexeme.lemma), lexeme) for lexeme in clexemes], key=lambda l: l[0])[1]

class AddUniverbisation(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        lemma [dash parents]
        and add the univerbisation relations."""

        with open(self.fname, mode="rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip("\n")
                items = line.split("-")
                if len(items) < 2:
                    logger.error("Unparseable univerbisation at line '{}'".format(line))
                    continue

                plemma = items[0]
                plexemes = lexicon.get_lexemes(plemma)

                if not plexemes:
                    logger.warning("Lexeme for lemma '{}' not found, skipping".format(plemma))
                    continue
                elif len(plexemes) > 1:
                    logger.warning("Lemma '{}' ambiguous, picking random one".format(plemma))
                plexeme = plexemes[0]

                for clemmas in items[1:]:
                    clemmas = clemmas.split(" ")
                    clexemes = []
                    fail = False

                    for clemma in clemmas:
                        cl = lexicon.get_lexemes(clemma)

                        if not cl:
                            logger.warning("Lexeme for lemma '{}' not found, skipping".format(clemma))
                            fail = True
                            break
                        elif len(cl) > 1:
                            logger.warning("Lemma '{}' ambiguous, picking random one".format(clemma))
                        clexemes.append(cl[0])

                    if fail:
                        continue
                    else:
                        existing_rels = plexeme.parent_relations
                        lexicon.remove_all_parent_relations(plexeme)

                        try:
                            main_clexeme = most_similar(clexemes, plexeme)
                            if main_clexeme is not clexemes[0]:
                                logger.info("Choosing a different lexeme for {}: {} instead of {}".format(plexeme, main_clexeme, clexemes[0]))
                            lexicon.add_univerbisation(clexemes, main_clexeme, plexeme)
                        except DerinetCycleCreationError as e:
                            logger.error("Error adding univerbisation for lemma '{}'".format(plemma), exc_info=e)
                        # We've added one relation, that is enough. Skip the other ones.
                        break

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
        parser.add_argument('file', help='The file to load annotation from.')
        # argparse.REMAINDER tells argparse not to be eager and to process
        # only the start of the args.
        parser.add_argument('rest', nargs=argparse.REMAINDER,
                            help='A list of other modules and arguments.')
        args = parser.parse_args(args)
        fname = args.file
        # Return *args to __init__, **kwargs to init and the unprocessed tail
        # of arguments to other modules.
        return [fname], {}, args.rest
