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

class AddDerivationsEtymologyFromAnnotated(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname

        
    def process(self, lexicon: Lexicon) -> Lexicon:
        """
        Adds derivations to the lexicon based on hand annotations.

        Args:
            lexicon: The lexicon object of DeriNet
        """
        with open(self.fname, 'rt') as annotated_data:
            for line in annotated_data:
                if line.startswith("#") or line.strip() == "":
                    continue  # Skip comments and empty lines

                columns = line.split('\t')
                if len(columns) < 3: 
                    continue # skip lines where there isnt all three columns

                # there can be 3 or 4 columns, three for direct, four for intermediate
                # in intermediate the third column is just to see whre the edge came from
                # the edge to add is from the first to the second
                # the last column is always the annotation
                
                derivation_str = columns[0]
                parent_str = columns[1]
                annotation = columns[-1].strip() 

                derivation_lemma, derivation_pos = derivation_str.split("#")
                parent_lemma, parent_pos = parent_str.split("#")

                derivation_lexemes = lexicon.get_lexemes(derivation_lemma, derivation_pos)
                parent_lexemes = lexicon.get_lexemes(parent_lemma, parent_pos)

                # Check if derivation lexeme list has just one element
                if len(derivation_lexemes) != 1:
                    print(f"Error: Derivation lexeme list issue for {derivation_str} -> {derivation_lexemes}")
                    continue  # Skip this line if there's an issue

                # Check if parent lexeme list has just one element
                if len(parent_lexemes) != 1:
                    print(f"Error: Parent lexeme list issue for {parent_str} -> {parent_lexemes}")
                    continue  # Skip this line if there's an issue

                derivation = derivation_lexemes[0]
                parent = parent_lexemes[0]

                # Handle different annotations
                if annotation == "OK":
                    print(f"OK\tDerivation: {derivation_str} -> Parent: {parent_str}")
                    lexicon.add_derivation(derivation, parent)  # Add the original generated derivation

                elif annotation == "REVERSE":
                    new_parent = derivation
                    new_derivation = parent
                    print(f"REVERSE\tOriginal - Derivation: {derivation_str} -> Parent: {parent_str}")
                    # Check if the original parent (new_derivation) is a root
                    if new_derivation.parent is None:
                        print("Just reversing the direction of edge, the new derivation is a root")
                        print(f"New - New Derivation: {new_derivation} -> New Parent: {new_parent}")
                        lexicon.add_derivation(new_derivation, new_parent)  # Add the flipped edge
                    else:
                        root_of_new_derivation = new_derivation.parent
                        print("The new derivation is NOT a root, connecting the root of new_derivation instead")
                        print(f"New - New Derivation: {root_of_new_derivation} -> New Parent: {new_parent}")
                        lexicon.add_derivation(root_of_new_derivation, new_parent)  # Connect the root of new_derivation to new_parent

                elif annotation == "COMPOUND":
                    print(f"Compound\tOriginal - Derivation: {derivation_str} -> Parent: {parent_str}")
                    # Handle compound derivation if necessary (additional logic can be added here)

                elif annotation.isalpha():  # The annotation is a word (not empty or '???')
                    new_parent_lexemes = lexicon.get_lexemes(annotation)
                    if len(new_parent_lexemes) == 1:
                        new_parent = new_parent_lexemes[0]
                        lexicon.add_derivation(derivation, new_parent)  # Add edge from the original derivation to new parent
                    elif len(new_parent_lexemes) == 0:
                        print(f"Lexeme for word {annotation} not found!")
                    else:
                        print(f"There are homonyms for word {annotation}: {new_parent_lexemes}")

                else:  # Skip empty lines and other lines ('???')
                    print(f"Skipped annotation: {annotation}")

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
