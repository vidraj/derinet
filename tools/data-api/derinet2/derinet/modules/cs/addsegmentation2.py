from derinet import Block, Format, Lexicon
from collections import defaultdict
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddSegmentation2(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Example processing method. Assumes that the opened file contains a list of morphs separated by spaces on each line.
        """
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            lemma_counter=defaultdict(lambda:0)
            translate_morph_type={"S":"Suffix","R":"Root","P":"Prefix"}
            for line in f:
                line = line.rstrip().rstrip("\r")
                if(line==""):
                    continue
                groups = line.split("|")
                lemma=""
                start=0
                morphemes_to_add=[]
                idx=0
                for group in groups:
                    morph,morph_lemma,morph_type=group.split(":")
                    morph_type2=translate_morph_type.get(morph_type)
                    if(morph_type2 is None):
                        logger.warning("Unknown morph type {} for lemma {} not found. Should be one of P,R,S.".format(morph_type,lemma))
                        continue
                    lemma+=morph
                    morphemes_to_add.append((idx, idx+len(morph),morph_type2, morph, morph_lemma))
                    idx+=len(morph)

                lexemes = lexicon.get_lexemes(lemma)
                if len(lexemes) == 0:
                    logger.warning("Lexeme for lemma {} not found".format(lemma))
                    continue
                elif(len(lexemes)==1):
                    lexeme=lexemes[0]
                else:
                    logger.warning("Lemma {} ambiguous, using heuristics".format(lemma))
                    #if the relative ordering of lexemes remamins consistent, assigns the words correctly.
                    if(lemma_counter[lemma]>=len(lexemes)):
                        logger.warning("Annotations contain more occurances of lemma {} than dataset".format(lemma))
                        continue
                    lexeme = lexemes[lemma_counter[lemma]]
                    lemma_counter[lemma]+=1
                lexeme._segmentation = {
                     "boundaries": {},
                     "morphs": [{
                           "Type": "Implicit",
                           "Start": 0,
                           "End": len(lemma),
                           "Morph": lemma
                         }]
                    }
                for start,end, morph_type, morph,morph_lemma in morphemes_to_add:
                    annot={"Type": morph_type, "Start":start, "End":end, "Morph":morph}
                    if(morph_lemma!=morph.lower()):
                        annot["Lemma"]=morph_lemma
                    lexeme.add_morph(start, end, annot)


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

        # Return *args and **kwargs to __init__ and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
