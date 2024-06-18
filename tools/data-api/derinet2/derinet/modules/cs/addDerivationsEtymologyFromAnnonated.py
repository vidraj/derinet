from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def load_normalized_dictionary(filename:str) -> dict[str,list[str]]:
    dictionary = dict()
    with open(filename, 'rt') as file_dict:
        for line in file_dict:
            line_split = line.split('\t')
            if len(line_split) == 2:
                entry,derivations = line_split
                dictionary[entry] = derivations.rstrip().split(', ')
            else:
                dictionary[line] = []
    return dictionary

class AddDerivationsEtymologyFromAnotated(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    
    def process(self, lexicon:Lexicon) -> Lexicon:
        """
        Adds derivations to the lexicon based on hand annotations.

        Args:
            lexicon: The lexicon object of DeriNet
        """
        with open(self.fname, 'rt') as annotated_data:
            for line in annotated_data:
                if line.startswith("#") or line.strip() == "": 
                    continue # skip comments and empty lines
                
                columns = line.split('\t')
                derivation_str = columns[0]
                parent_str = columns [1]
                annotation = columns[len(columns)-1]
                derivation_lemma,derivation_pos = derivation_str.split("#")
                parent_lemma,parent_pos = derivation_str.split("#")

                if annotation == "OK":
                    print(f"Derivation: {derivation_str} -> Parent: {parent_str}")     
                    derivation_lexeme_list = lexicon.get_lexemes(derivation_lemma,derivation_pos) 
                    parent_lexeme_list = lexicon.get_lexemes(parent_lemma,parent_pos) 
                    if len(derivation_lexeme_list) == 1 and len(parent_lexeme_list): 
                        derivation = derivation_lexeme_list[0]
                        parent = parent_lexeme_list[0]
                        lexicon.add_derivation(derivation,parent)
                    else:
                        print(f"derivation_lexeme_list: {derivation_lexeme_list}")
                        print(f"parent_lexeme_list: {parent_lexeme_list}")
                elif annotation == "REVERSE":
                    pass
                elif annotation == "COMPOUND":
                    pass
                else:
                    pass
        return Lexicon
    
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
