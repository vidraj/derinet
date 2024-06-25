from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)



class AddDerivationsEtymologyIntermediate(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname
        #TODO
        # dostane to adresar s vice soubory, nebo vice souboru? Nebo jeden soubor kde bude vsechno dohromady?
        # ted je to ze jeden soubor anotovanych hran
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
                pass #; print(f"WARNING Exception when trying to add derivation from {child} to {parent}")

    def process(self, lexicon: Lexicon) -> Lexicon:
        """
        Adds derivations to the lexicon based on hand annotations.

        Args:
            lexicon: The lexicon object of DeriNet
        """
        yes_reconnect = "YES & RECONNECT DERIVATION FROM PARENT TO GRANDPARENT"
        no_reconnect  = "NO & RECONNECT DERIVATION FROM PARENT TO GRANDPARENT"
        yes           = "YES"
        no            = "NO"    
        # delete lines to open files and print information to them
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
                if len(columns) < 4: 
                    print(f"Line skiped: {line}",file=detailed)
                    continue # skip lines where there arent all four columns

                # there are four columns for intermediate
                # in intermediate the third column is just to see whre the edge came from
                # the edge to add is from the first to the second
                # the last column is always the annotation
                
                derivation_str = columns[3]
                parent_str = columns[2]
                grandparent_str = columns[1]
                annotation = columns[0].strip() 

                derivation_lemma, derivation_pos = derivation_str.split("#")
                parent_lemma, parent_pos = parent_str.split("#")
                grandparent_lemma, grandparent_pos = grandparent_str.split("#")

                
                derivation_lexemes = lexicon.get_lexemes(derivation_lemma,lemid=derivation_str)
                if derivation_lexemes == []:
                    derivation_lexemes = lexicon.get_lexemes(derivation_lemma)

                parent_lexemes = lexicon.get_lexemes(parent_lemma, lemid=parent_str)
                if parent_lexemes == []:
                    parent_lexemes = lexicon.get_lexemes(parent_lemma)
                
                grandparent_lexemes = lexicon.get_lexemes(grandparent_lemma,lemid =grandparent_pos)
                if grandparent_lexemes == []:
                    grandparent_lexemes = lexicon.get_lexemes(grandparent_lemma)
                
                # Check if parent lexeme list has just one element
                if len(parent_lexemes) != 1:
                    if len (parent_lexemes) == 0:
                        print(f"Lexeme not found! For word: lemma: {parent_lemma}, POS: {parent_pos}", file=detailed)
                    else:
                        print(f"Multiple hononyms found! For word: lemma: {parent_lemma}, POS: {parent_pos} -> {parent_lexemes}", file=detailed)
                    continue  # Skip this line if there's an issue
                
                
                

                # CHANGE TO SKIP JUST when just the needed lexemes are not found

                parent = parent_lexemes[0]
                grandparent = None
                derivation = None

                # Handle different annotations
                #WRONG!!!
                # JUST copied from similar block, needs to be finished

                if annotation == yes:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            print(f"Lexeme not found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos}", file=detailed)
                        else:
                            print(f"Multiple hononyms found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos} -> {parent_lexemes}", file=detailed)
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    print(f"OK\tDerivation: {parent_lemma} -> Parent: {grandparent_lemma}", file=detailed)
                    self.add_derivation(lexicon,grandparent,parent)  # Add the original generated derivation
                    print(f"{parent_str}\t{grandparent_str}", file=added_actual)

                elif annotation == yes_reconnect:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            print(f"Lexeme not found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos}", file=detailed)
                        else:
                            print(f"Multiple hononyms found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos} -> {parent_lexemes}", file=detailed)
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    # Check if derivation lexeme list has just one element
                    if len(derivation_lexemes) != 1:
                        if len(derivation_lexemes) == 0:
                            print(f"Lexeme not found! For word: lemma: {derivation_lemma}, POS: {derivation_pos}",file=detailed)
                        else:
                            print(f"Multiple hononyms found! For word: lemma: {derivation_lemma}, POS: {derivation_pos} -> {derivation_lexemes}",file=detailed)
                        continue  # Skip this line if there's an issue
                    derivation = derivation_lexemes[0]

                    print(f"OK\tDerivation: {parent_lemma} -> Parent: {grandparent_lemma}", file=detailed)
                    self.add_derivation(lexicon,grandparent,parent)  # Add the original generated derivation
                    print(f"{parent_str}\t{grandparent_str}", file=added_actual)
                    
                    derivation.parent_relation.remove_from_lexemes() # remove the original parent relation
                    self.add_derivation(lexicon,grandparent,derivation)  # Add the new parent relation
                    print(f"RECONNECT\tLexeme: {derivation_str}\tOld parent: {parent_str}\tNew parent: {grandparent_str}", file=detailed)
                    print(f"{derivation_str}\t{grandparent_str}", file=added_actual)

                elif annotation == no_reconnect:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            print(f"Lexeme not found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos}", file=detailed)
                        else:
                            print(f"Multiple hononyms found! For word: lemma: {grandparent_lemma}, POS: {grandparent_pos} -> {parent_lexemes}", file=detailed)
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    # Check if derivation lexeme list has just one element
                    if len(derivation_lexemes) != 1:
                        if len(derivation_lexemes) == 0:
                            print(f"Lexeme not found! For word: lemma: {derivation_lemma}, POS: {derivation_pos}",file=detailed)
                        else:
                            print(f"Multiple hononyms found! For word: lemma: {derivation_lemma}, POS: {derivation_pos} -> {derivation_lexemes}",file=detailed)
                        continue  # Skip this line if there's an issue
                    derivation = derivation_lexemes[0]
        
                    derivation.parent_relation.remove_from_lexemes() # remove the original parent relation
                    self.add_derivation(lexicon,grandparent,derivation)  # Add the new parent relation
                    print(f"RECONNECT\tLexeme: {derivation_str}\tOld parent: {parent_str}\tNew parent: {grandparent_str}", file=detailed)
                    print(f"{derivation_str}\t{grandparent_str}", file=added_actual)

                elif annotation == no:
                    continue # skip this line

                elif annotation.isalpha():  # The annotation is a word (not empty or '???')
                    new_parent_lexemes = lexicon.get_lexemes(annotation)
                    if len(new_parent_lexemes) == 1:
                        new_parent = new_parent_lexemes[0]
                        self.add_derivation(lexicon,new_parent, parent)  # Add edge from the original derivation to new parent
                        print(f"{parent}\t{new_parent}", file=added_actual)
                        print(f"Manualy writen parent, derivation: {parent}, parent {new_parent}", file=detailed)

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
