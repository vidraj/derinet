from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def read_etym_data(filename: str) -> dict[str, list[str]]:
    '''
    Parses a tsv file containing words and their etymological information.

    Parameters:
    - filename (str): The path to the tsv file containing data.

    Returns:
    - dict[str, list[str]]: A dictionary where each key is a word and each value 
    is a list of abbreviations of countries from which the word came to czech.
    '''
    etym_data = {}
    with open(filename, 'r') as etym_file:
        for line in etym_file.readlines():
            line = line.split('\t')
            word = line[0].strip()
            etymology = line[1].split(',')
            etym_data[word] = etymology
    return etym_data


class AddEtymology(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        '''
        Writes etymological information to root lexeme
        to new feature Etymology as a list of abbreviations
        of countries.
        '''
        data = read_etym_data(self.fname)
        for word, etymology in data.items():
            lexemes = lexicon.get_lexemes(lemma=word)
            for lexeme in lexemes:
                root_lexeme = lexeme.get_tree_root()
                if 'Etymology' not in root_lexeme.feats:
                    root_lexeme.add_feature('Etymology', etymology)

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
