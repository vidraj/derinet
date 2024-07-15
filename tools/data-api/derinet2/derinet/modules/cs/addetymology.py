from derinet import Block, Lexicon
import argparse
import logging
import json

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def read_etym_data(filename: str) -> dict[str, (list[str], bool)]:
    '''
    Parses a tsv file containing words and their etymological information.
    
    Parameters:
    - filename (str): The path to the tsv file containing data.
    
    Returns:
    - dict[str, (list[str], bool)]: A dictionary where each key is a word and each value 
    is a tuple, containig a list of abbreviations of countries from which the word came 
    to czech and a bool value describing whether a word is loan or not.
    '''
    etym_data = {}
    with open(filename, 'r') as etym_file:
        for line in etym_file.readlines():
            line = line.split('\t')
            word = line[0]
            etymology = line[1].split(',')
            loan = line[2]
            etym_data[word] = (etymology, loan)
    return etym_data


class AddEtymology(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def process(self, lexicon: Lexicon):
        '''
        Writes etymological information to root lexeme
        to new feature Etymology in misc in json format.
        Rewrites Loanword feature in feats accordingly.
        '''
        data = read_etym_data(self.fname)
        for word, (etymology, loanmark) in data.items():
            if loanmark == 'True':
                lexemes = lexicon.get_lexemes(lemma=word)
                for lexeme in lexemes:
                    root_lexeme = lexeme.get_tree_root()
                    if 'Etymology' not in root_lexeme.misc:
                        # propagate to all lexemes in a tree
                        for derived_lexeme in root_lexeme.iter_subtree():
                            derived_lexeme.misc['Etymology'] = json.dumps(etymology[:3])
                            if 'Loanword' not in derived_lexeme.feats:
                                derived_lexeme.add_feature('Loanword', loanmark)
                            else:
                                derived_lexeme.feats['Loanword'] = loanmark
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
