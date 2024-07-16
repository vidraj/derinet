from derinet import Block, Format, Lexicon
import argparse
import logging

from collections import defaultdict


logger = logging.getLogger(__name__)


class AddConjugationClasses(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        tagmask TAB lemma TAB conjug-class
        and add conjugation classes to the lemmas."""
        # load lemmas already assigned classes
        deferred = defaultdict(list)
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                lemid, lemma, conjug = line.rstrip('\n').split('\t')

                if conjug == "#":
                    # Unassigned.
                    continue

                lexemes = lexicon.get_lexemes(lemma, "V", lemid=lemid)

                if not lexemes:
                    # Ignore the lemid, it has changed between versions.
                    lexemes = lexicon.get_lexemes(lemma, "V")

                if not lexemes:
                    logger.warning("Lexeme for lemma '{}' not found".format(lemma))
                    continue
                elif len(lexemes) > 1:
                    # Try to solve homonymy later.
                    deferred[lemma].append(conjug)
                    continue
                else:
                    lexeme = lexemes[0]
                    # conjug = conjug.replace('#', '|')
                    lexeme.feats['ConjugClass'] = conjug

        for lemma, conjugs in deferred.items():
            if len(set(conjugs)) == 1:
                # All the lexemes have the same class.
                lexemes = lexicon.get_lexemes(lemma, "V")
                for lexeme in lexemes:
                    lexeme.feats['ConjugClass'] = conjugs[0]
            else:
                logger.warning("Lemma '{}' is ambiguous, different homonyms have different classes: {}".format(lemma, conjugs))


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
