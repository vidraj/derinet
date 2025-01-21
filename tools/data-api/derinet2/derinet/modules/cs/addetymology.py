from derinet import Block, Lexicon
import argparse
import logging
import json

logger = logging.getLogger(__name__)


def read_etym_data(filename: str) -> dict[str, (list[str], str)]:
    '''
    Parses a tsv file containing words and their etymological information.
    
    Parameters:
    - filename (str): The path to the tsv file containing data.
    
    Returns:
    - dict[str, (list[str], str)]: A dictionary where each key is a word and each value 
    is a tuple, containig a list of abbreviations of countries from which the word came 
    to czech and a string value loan or native.
    '''
    etym_data = {}
    with open(filename, 'r', encoding="utf8") as etym_file:
        for line in etym_file.readlines():
            line = line.split('\t')
            word = line[0]
            etymology = line[1].split(',')
            loan = line[2].strip()
            etym_data[word] = (etymology, loan)
    return etym_data


class AddEtymology(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    def write_etym_data(self, lexeme, etymology, loanmark):
        '''
        Writes etymological information to root lexeme
        to new feature Etymology in misc in json format.
        Rewrites Loanword feature in feats accordingly.
        Then recursively propagates the information to all lexemes in a subtree,
        but not to compounds.
        '''
        # loanword
        if loanmark == 'loan':
            lexeme.misc['Etymology'] = json.dumps(etymology)
            if 'Loanword' not in lexeme.feats:
                lexeme.add_feature('Loanword', True)
            else:
                lexeme.feats['Loanword'] = True
        # native word
        else:
            if 'Loanword' not in lexeme.feats:
                lexeme.add_feature('Loanword', False)
            else:
                lexeme.feats['Loanword'] = False
        # propagate to all lexemes in a subtree that are not compound
        for child in lexeme.children:
            if 'is_compound' in child.misc and child.misc['is_compound'] == False:
                self.write_etym_data(child, etymology, loanmark)

    def process(self, lexicon: Lexicon):
        '''
        Writes etymological information to root lexeme
        to new feature Etymology in misc in json format.
        Rewrites Loanword feature in feats accordingly.
        '''
        data = read_etym_data(self.fname)
        # collect etymological information for each root lexeme
        roots_with_etym_info = {}
        for word, (etymology, loanmark) in data.items():
            lexemes = lexicon.get_lexemes(lemma=word)
            for lexeme in lexemes:
                root_lexeme = lexeme.get_tree_root()
                # depth of the lexeme in the tree
                depth = 0
                while lexeme.parent is not None:
                    lexeme = lexeme.parent
                    depth += 1
                if root_lexeme.lemma in roots_with_etym_info:
                    roots_with_etym_info[root_lexeme.lemma].append((depth, etymology, loanmark))
                else:
                    roots_with_etym_info[root_lexeme.lemma] = [(depth, etymology, loanmark)]

        # write etymological information to root lexemes and propagate it
        for root_lexeme, etym_info in roots_with_etym_info.items():
            root_lexemes = lexicon.get_lexemes(lemma=root_lexeme)
            for root in root_lexemes:
                # only one etymological information for the tree
                if len(etym_info) == 1:
                    (depth, etymology, loanmark) = etym_info[0]
                    self.write_etym_data(root, etymology, loanmark)
                # multiple etymological information for the tree
                # choose the one with the smallest depth (closest to the root)
                else:
                    etym_info.sort()
                    (depth, etymology, loanmark) = etym_info[0]
                    self.write_etym_data(root, etymology, loanmark)
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
