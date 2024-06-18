from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)



class AddDerivationsEtymologyFromAnnotated(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname
        #TODO
        # dostane to adresar s vice soubory, nebo vice souboru? Nebo jeden soubor kde bude vsechno dohromady?
    
    @staticmethod
    def add_derivation(lexicon: Lexicon, parent, child):
        """Cals add_derivation method on the lexicon with child and parent.
        
            Checks if the child and parent arent in the same tree, catches all exceptions.
        """
        is_root = child.get_tree_root() == child
        if is_root and child != parent.get_tree_root(): # the child has to be root and the parent cant be in a subtree of child
            try:
                lexicon.add_derivation(parent,child)
            except:
                pass

    def process(self, lexicon: Lexicon) -> Lexicon:
        """
        Adds derivations to the lexicon based on hand annotations.

        Args:
            lexicon: The lexicon object of DeriNet
        """
        with (
            open(self.fname, 'rt') as annotated_data,
            open("compunds.txt", 'wt') as compunds,
            open("actualy_added.txt", 'wt') as added_actual,
            open("detailed_output.txt", 'wt') as detailed
        ):  
            for line in annotated_data:
                if line.startswith("#") or line.strip() == "":
                    print(f"Line skiped: {line}",file=detailed)
                    continue  # Skip comments and empty lines

                columns = line.split('\t')
                if len(columns) < 3: 
                    print(f"Line skiped: {line}",file=detailed)
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

                derivation_lexemes = lexicon.get_lexemes(derivation_lemma,lemid=derivation_str)
                if derivation_lexemes == []:
                    derivation_lexemes = lexicon.get_lexemes(derivation_lemma)
                parent_lexemes = lexicon.get_lexemes(parent_lemma, lemid=parent_str)
                if parent_lexemes == []:
                    parent_lexemes = lexicon.get_lexemes(parent_lemma)

                # Check if derivation lexeme list has just one element
                if len(derivation_lexemes) != 1:
                    if len(derivation_lexemes) == 0:
                        print(f"Lexeme not found! For word: lemma: {derivation_lemma}, POS: {derivation_pos}",file=detailed)
                    else:
                        print(f"Multiple hononyms found! For word: lemma: {derivation_lemma}, POS: {derivation_pos} -> {derivation_lexemes}",file=detailed)
                    continue  # Skip this line if there's an issue

                # Check if parent lexeme list has just one element
                if len(parent_lexemes) != 1:
                    if len (parent_lexemes) == 0:
                        print(f"Lexeme not found! For word: lemma: {parent_lemma}, POS: {parent_pos}", file=detailed)
                    else:
                        print(f"Multiple hononyms found! For word: lemma: {parent_lemma}, POS: {parent_pos} -> {parent_lexemes}", file=detailed)
                    continue  # Skip this line if there's an issue

                derivation = derivation_lexemes[0]
                parent = parent_lexemes[0]

                # Handle different annotations
                if annotation == "OK":
                    print(f"OK\tDerivation: {derivation_str} -> Parent: {parent_str}", file=detailed)
                    self.add_derivation(lexicon,parent,derivation)  # Add the original generated derivation
                    print(f"{derivation_str}\t{parent_str}", file=added_actual)

                elif annotation == "REVERSE":
                    new_parent = derivation
                    new_derivation = parent
                    print(f"REVERSE\tOriginal - Derivation: {derivation_str} -> Parent: {parent_str}", file=detailed)
                    # Check if the original parent (new_derivation) is a root
                    if new_derivation.parent is None:
                        print("\tReversing the direction of edge, new derivation is a root",file=detailed)
                        print(f"\tNew Derivation: {new_derivation} -> New Parent: {new_parent}",file=detailed)
                        self.add_derivation(lexicon,new_parent, new_derivation)  # Add the flipped edge
                        print(f"{derivation_str}\t{parent_str}", file=added_actual)

                    else:
                        root_of_new_derivation = new_derivation.parent
                        print("\tNew derivation is NOT a root, connecting the root of new_derivation instead", file=detailed)
                        print(f"\tNew Derivation: {root_of_new_derivation} -> New Parent: {new_parent}", file=detailed)
                        self.add_derivation(lexicon,new_parent,root_of_new_derivation)  # Connect the root of new_derivation to new_parent
                        print(f"{root_of_new_derivation}\t{new_parent}", file=added_actual)

                elif annotation == "COMPOUND":
                    print(f"Compound: Derivation: {derivation_str} -> Parent: {parent_str}", file=detailed)
                    print(f"Compound: Derivation: {derivation_str} -> Parent: {parent_str}", file=compunds)

                elif annotation.isalpha():  # The annotation is a word (not empty or '???')
                    new_parent_lexemes = lexicon.get_lexemes(annotation)
                    if len(new_parent_lexemes) == 1:
                        new_parent = new_parent_lexemes[0]
                        self.add_derivation(lexicon,new_parent, derivation)  # Add edge from the original derivation to new parent
                        print(f"{derivation}\t{new_parent}", file=added_actual)
                        print(f"Manualy writen parent, derivation: {derivation}, new parent {new_parent}, original parent {parent}", file=detailed)

                    elif len(new_parent_lexemes) == 0:
                        print(f"Lexeme for word \"{annotation}\" not found!", file=detailed)
                    else:
                        print(f"There are homonyms for word \'{annotation}\': {new_parent_lexemes}", file=detailed)

                else:  # Skip empty lines and other lines ('???')
                    print(f"Skipped line {derivation_str}, {parent_str}, annotation: {annotation}", file=detailed)

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
