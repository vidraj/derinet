from derinet import Block, Format, Lexicon
import argparse
import logging

from collections import defaultdict

import re


logger = logging.getLogger(__name__)


class ExtractPhantomsChildren(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Finding parentless nodes that could be considered children of phantom lexemes (according to the list from SSJC, extracted from it by Adela Kaluzova)
        """

        phantom_category = {}  # Adela's division of phantom lexemes
        current_category = ""
        
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()

                if re.match(r'\#', line):
                    current_category = line

                else:
                
                    columns = line.split(" ")
                    phantom_lemma = re.sub(r'i$', '', columns[0])  # archaic infinitives

                    lexemes = lexicon.get_lexemes(phantom_lemma)

                    if lexemes:
#                        print("LEMMA-ALREADY-EXISTS\t"+phantom_lemma)
                        pass


                    else:    
                        phantom_category[phantom_lemma] = current_category


        phantom_regex = r'{}'.format( ".+?(" + ( "|".join( phantom_category.keys()))+ ")$")
#        print(phantom_regex)

        
        for lexeme in lexicon.iter_trees(): # for all roots

            matchObj = re.match(phantom_regex,lexeme.lemma)
            if matchObj and lexeme.pos == "V":
                print("CANDIDATE-PHANTOM-CHILD\t"+lexeme.lemma+"\t"+matchObj.group(1)+"\t"+phantom_category[matchObj.group(1)])

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

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
