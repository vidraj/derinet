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

class AddDerivationsEtymology(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

    
    def process(self, lexicon:Lexicon):
        """
        Processes the lexicon by iterating through its trees and comparing derivations with the normalized dictionary.
        Adds the derivations described in the Etymological dict which are not present in DeriNet.

        Args:
            lexicon: The lexicon object of DeriNet
        """

        dictionary_normalized = load_normalized_dictionary(self.fname)
        for tree_root in lexicon.iter_trees():  # iterate through trees
            # Initialize an empty dict to store derivations as keys and their parent as values
            dict_derivations_from_etym_dictionary = dict()

            # Iterate through each lexeme in the subtree of the tree_root
            # Adding all derivations from etym dict
            for lexeme in tree_root.iter_subtree():
                lemma = lexeme.lemma
                # Get derivations from the normalized dictionary for the current lemma
                lemma_derivations = dictionary_normalized.get(lemma)      
                if lemma_derivations: # if there are derivations for the current word
                    for derivation in lemma_derivations:
                        if derivation.strip(): # if the derivation isnt empty string
                            dict_derivations_from_etym_dictionary[derivation] = lexeme # add the derivation - parent pair to the dictionary

            # removing the already present derivations
            if len(dict_derivations_from_etym_dictionary.keys()) != 0:
                for lexeme in tree_root.iter_subtree():
                    lemma = lexeme.lemma
                    if lemma in dict_derivations_from_etym_dictionary.keys(): 
                        dict_derivations_from_etym_dictionary.pop(lemma) # remove the derivation because it is already in the DeriNet tree
            
            # adding the missing derivations
            if len(dict_derivations_from_etym_dictionary.keys()) != 0:
                for derivation_not_present in dict_derivations_from_etym_dictionary.keys():
                    lexeme = lexicon.get_lexemes(lemma=derivation_not_present)
                    if len(lexeme) == 1:  # if there are not homonymous lexemes, return first (only) one
                        lexeme = lexeme[0]
                        if lexeme.parent_relation is None: # the lexeme is root, connect it directly
                            try:
                                lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],lexeme)
                            except:
                                # there can be some errors with cyclic relations. Two errors that occured:
                                # Lexeme:játra#NNN??-----A---?, Tree root: celý#AA???----??---?, parent: jitrocel#NNI??-----A---?
                                # Lexeme:don#NNM??-----A---?, Tree root: Quijote#NNMXX-----A----, parent: donkichot#NNM??-----A---?
                                pass
                        else:
                            # the found derivation is not root of a tree, we will connect the whole tree (the root) instead
                            root_of_derivation_lexeme = lexeme.get_tree_root()
                            if root_of_derivation_lexeme != tree_root:
                                lexicon.add_derivation(dict_derivations_from_etym_dictionary[derivation_not_present],root_of_derivation_lexeme)                            
                            else:
                                pass
                                # for example for agent we have derivations found in Etym dict ['agentura', 'agenturni'] which are missing in Derinte
                                # However 'agentura' is root of tree containing 'agenturni' so when 'agentura' is added to 'agent' as derivation
                                # the root of 'agenturni' now becomes 'agent' so its already in the tree, we dont add it
            
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
