from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class AddDerivationsEtymologyIntermediate(Block):

    def __init__(self, fname):
        # The arguments to __init__ are None (returned from below).
        self.fname = fname # source file with annotations
    
    @staticmethod
    def add_derivation(lexicon: Lexicon, parent, child) -> bool:
        """Cals add_derivation method on the lexicon with child and parent.
        
            Checks if the child and parent arent in the same tree, catches all exceptions.

            Args: lexicon: Lexicon object of DeriNet
                    parent: Lexeme object
                    child: Lexeme object
            Returns: True if the derivation was added, False otherwise
        """
        if child.lemma == parent.lemma and child.pos == parent.pos:
            logger.debug(f"Derivation {child} -> {parent} is the same lexeme")
            return False

        if (child.get_tree_root() != child):
            logger.debug(f"Derivation {child} is not a root")
            return False
        if child != parent.get_tree_root(): # the child has to be root and the parent cant be in a subtree of child
            try:
                lexicon.add_derivation(parent,child)
                return True
            except Exception as e:
                logger.debug(f"Exception {e} when adding derivation {child} -> {parent}")
                return False
        else:
            logger.debug(f"Derivation {child} -> {parent} was not added. Parent is in a subtree of child")
            return False
    
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

        with (open(self.fname, 'rt') as annotated_data):  
            for line in annotated_data:
                if line.startswith("#") or line.strip() == "":
                    continue  # Skip comments and empty lines

                columns = line.split('\t')
                if len(columns) < 4: 
                    continue # skip lines where there arent all four columns

                # there are four columns for intermediate
                # in intermediate the third column is just to see whre the edge came from
                # the edge to add is from the first to the second
                # the first column is the annotation
                
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
                        logger.warning(f"Lexeme not found! For word: {parent_str.strip()}")
                    else:
                        logger.warning(f"Multiple hononyms found! For word: {parent_str.strip()} -> {parent_lexemes}")
                    continue  # Skip this line if there's an issue
                
                
                parent = parent_lexemes[0]
                grandparent = None
                derivation = None

                # Handle different cases (annotations)
                if annotation == yes:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            logger.warning(f"Lexeme not found! For word: {grandparent_str.strip()}")
                        else:
                            logger.warning(f"Multiple hononyms found! For word: lemma: {grandparent_str.strip()} -> {parent_lexemes}")
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    if (self.add_derivation(lexicon,grandparent,parent)):  # Add the original generated derivation
                        logger.info(f"Derivation: {parent_str}\t Parent:{grandparent_str}")

                elif annotation == yes_reconnect:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            logger.warning(f"Lexeme not found! For word: {grandparent_str.strip()}")
                        else:
                            logger.warning(f"Multiple hononyms found! For word: {grandparent_str.strip()} -> {parent_lexemes}")
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    # Check if derivation lexeme list has just one element
                    if len(derivation_lexemes) != 1:
                        if len(derivation_lexemes) == 0:
                            logger.warning(f"Lexeme not found! For word: lemma: {derivation_lemma}, POS: {derivation_pos}")
                        else:
                            logger.warning(f"Multiple hononyms found! For word: lemma: {derivation_lemma}, POS: {derivation_pos} -> {derivation_lexemes}")
                        continue  # Skip this line if there's an issue
                    derivation = derivation_lexemes[0]

                    if (self.add_derivation(lexicon,grandparent,parent)):  # Add the original generated derivation
                        logger.info(f"Derivation: {parent_str.strip()}\t Parent: {grandparent_str.strip()}")
                    
                    derivation.parent_relation.remove_from_lexemes() # remove the original parent relation
                    if (self.add_derivation(lexicon,grandparent,derivation)):  # Add the new parent relation
                        logger.info(f"RECONNECT\tLexeme: {derivation_str.strip()}\tOld parent: {parent_str.strip()}\tNew parent: {grandparent_str.strip()}")

                elif annotation == no_reconnect:
                    # Check if grandparent lexeme list has just one element
                    if len(grandparent_lexemes) != 1:
                        if len (grandparent_lexemes) == 0:
                            logger.warning(f"Lexeme not found! For word: lemma: {grandparent_str.strip()}")
                        else:
                            logger.warning(f"Multiple hononyms found! For word: {grandparent_str.strip()} -> {parent_lexemes}")
                        continue  # Skip this line if there's an issue
                    grandparent = grandparent_lexemes[0]

                    # Check if derivation lexeme list has just one element
                    if len(derivation_lexemes) != 1:
                        if len(derivation_lexemes) == 0:
                            logger.warning(f"Lexeme not found! For word: {derivation_str.strip()}")
                        else:
                            logger.warning(f"Multiple hononyms found! For word: {derivation_str.strip()} -> {derivation_lexemes}")
                        continue  # Skip this line if there's an issue
                    derivation = derivation_lexemes[0]
        
                    derivation.parent_relation.remove_from_lexemes() # remove the original parent relation
                    if (self.add_derivation(lexicon,grandparent,derivation)): # Add the new parent relation
                        logger.info(f"RECONNECT\tLexeme: {derivation_str.strip()}\tOld parent: {parent_str.strip()}\tNew parent: {grandparent_str.strip()}")

                elif annotation == no:
                    continue # skip this line

                elif annotation.isalpha():  # The annotation is a word (not empty or '???')
                    new_parent_lexemes = lexicon.get_lexemes(annotation)
                    if len(new_parent_lexemes) == 1:
                        new_parent = new_parent_lexemes[0]
                        if(self.add_derivation(lexicon,new_parent, parent)):  # Add edge from the original derivation to new parent
                            logger.info(f"Derivation: {parent}\tParent: {new_parent}")
                            logger.debug(f"Manualy writen parent {annotation}, derivation: {parent}, parent {new_parent}")

                    elif len(new_parent_lexemes) == 0:
                        logger.warning(f"Lexeme for word \"{annotation}\" not found!")
                    else:
                        logger.warning(f"There are homonyms for word \'{annotation}\': {new_parent_lexemes}")

                else:  # Skip empty lines and other lines ('???')
                    pass
                    # logger.debug(f"Skipped line {derivation_str.strip()}, {parent_str.strip()}, annotation: {annotation}")

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
