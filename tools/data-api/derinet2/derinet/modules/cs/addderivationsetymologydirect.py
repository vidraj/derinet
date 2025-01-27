from derinet import Block, Lexicon
import argparse
import logging


logger = logging.getLogger(__name__)


class AddDerivationsEtymologyDirect(Block):

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
        with (open(self.fname, 'rt') as annotated_data):  
            for line in annotated_data:
                if line.startswith("#") or line.strip() == "":
                    logger.debug(f"Line skiped: {line.strip()}")
                    continue  # Skip comments and empty lines

                columns = line.split('\t')
                if len(columns) < 3: 
                    logger.debug(f"Line skiped: {line.strip()}")
                    continue # skip lines where there isnt all three columns

                # there are 3 columns for direct, annotation, parent and derivation
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
                        logger.warning(f"Lexeme not found! For word: {derivation_str.strip()}")
                    else:
                        logger.warning(f"Multiple hononyms found! For word: {derivation_str.strip()} -> {derivation_lexemes}")
                    continue  # Skip this line if there's an issue

                # Check if parent lexeme list has just one element
                if len(parent_lexemes) != 1:
                    if len (parent_lexemes) == 0:
                        logger.warning(f"Lexeme not found! For word: lemma: {parent_str.strip()}")
                    else:
                        logger.warning(f"Multiple hononyms found! For word: {parent_str.strip()} -> {parent_lexemes}")
                    continue  # Skip this line if there's an issue

                derivation = derivation_lexemes[0]
                parent = parent_lexemes[0]

                # Handle different annotations
                if annotation == "OK":
                    if (self.add_derivation(lexicon,parent,derivation)):  # Add the original generated derivation
                        logger.info(f"Derivation: {derivation_str.strip()} -> Parent: {parent_str.strip()}")

                elif annotation == "REVERSE":
                    new_parent = derivation
                    new_derivation = parent
                    logger.debug(f"REVERSE\tOriginal - Derivation: {derivation_str.strip()} -> Parent: {parent_str.strip()}")
                    # Check if the original parent (new_derivation) is a root
                    if new_derivation.parent is None:
                        logger.debug("\tReversing the direction of edge, new derivation is a root")
                        logger.debug(f"\tNew Derivation: {new_derivation} -> New Parent: {new_parent}")
                        if (self.add_derivation(lexicon,new_parent, new_derivation)):  # Add the flipped edge
                            logger.info(f"Derivation: {derivation_str}\tParent: {parent_str}")

                    else:
                        root_of_new_derivation = new_derivation.parent
                        logger.debug(f"\tNew derivation ({new_derivation}) is NOT a root, connecting the root of new_derivation ({root_of_new_derivation}) instead")
                        if (self.add_derivation(lexicon,new_parent,root_of_new_derivation)):  # Connect the root of new_derivation to new_parent
                            logger.info(f"Derivation:{root_of_new_derivation}\tParent: {new_parent}")

                elif annotation == "COMPOUND":
                    logger.info(f"Compound: Derivation: {derivation_str} -> Parent: {parent_str}")

                elif annotation.isalpha():  # The annotation is a word (not empty or '???')
                    new_parent_lexemes = lexicon.get_lexemes(annotation)
                    if len(new_parent_lexemes) == 1:
                        new_parent = new_parent_lexemes[0]
                        if (self.add_derivation(lexicon,new_parent, derivation)):  # Add edge from the original derivation to new parent
                            logger.info(f"Derivation: {derivation}\tParent: {new_parent}")
                        logger.info(f"Manualy writen parent, derivation: {derivation}, new parent {new_parent}, original parent {parent}")

                    elif len(new_parent_lexemes) == 0:
                        logger.warning(f"Lexeme for word \"{annotation}\" not found!")
                    else:
                        logger.warning(f"There are homonyms for word \'{annotation}\': {new_parent_lexemes}")

                else:  # Skip empty lines and other lines ('???')
                    pass
                    # logger.debug(f"Skipped line {derivation_str}, {parent_str}, annotation: {annotation}")

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
