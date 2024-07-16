from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class DelIncorrectLexemes(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Load list of lexemes and delete them from the database.
        Format: lemma TAB pos TAB gender TAB animacy
        where only lemma is obligatory."""

        with open(self.fname, mode='r', encoding='U8') as f:
            for line in f:
                line = line.strip().split('\t')

                if len(line) == 1:  # only lemma given
                    lemmas = lexicon.get_lexemes(lemma=line[0])

                elif len(line) == 2:  # lemma + pos
                    lemmas = lexicon.get_lexemes(lemma=line[0], pos=line[1])

                elif len(line) == 3:  # lemma + pos + gender
                    lemmas = lexicon.get_lexemes(lemma=line[0], pos=line[1])
                    lemmas = [l for l in lemmas
                              if l.feats.get('Gender', 'x') == line[2]]

                elif len(line) == 4:  # lemma + pos + gender + animacy
                    lemmas = lexicon.get_lexemes(lemma=line[0], pos=line[1])
                    lemmas = [l for l in lemmas
                              if l.feats.get('Gender', '') == line[2]
                              and l.feats.get('Animacy', '') == line[3]]

                elif len(line) > 4:
                    logger.warning('The given line has too many arguments: {}.'
                                   .format(line.strip()))
                    continue

                if len(lemmas) < 1:
                    logger.info('Lexeme {} not found.'.format(line[0]))

                for lemma in lemmas:
                    # delete lexeme
                    lexicon.delete_lexeme(lexeme=lemma, delete_relations=True)
                    logger.info('Lemma: {} was deleted incl. its relations.'
                                .format(lemma))

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
