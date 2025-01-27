from derinet import Block, Format, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class AddCompoundMarks(Block):
    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """Read annotation in the form of
        individual lemmas on each line
        and go through lemmaset and add compound mark to the lemmas."""
        # load lemmas already assigned classes
        assigned = set()
        with open(self.fname, mode='rt', encoding='U8', newline='\n') as f:
            for line in f:
                line = line.rstrip('\n').split('\t')
                assigned.add(line[0])

        # find lexeme and assign mark
        for lemma in assigned:
            lemma, pos = lemma.split('_')
            node = lexicon.get_lexemes(lemma=lemma, pos=pos)

            if node and not node[0].parent:
                node[0].misc['is_compound'] = True

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
