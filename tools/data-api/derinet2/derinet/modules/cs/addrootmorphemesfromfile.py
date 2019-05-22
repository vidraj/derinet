from derinet import Block, Format, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

from collections import defaultdict

import re

class AddRootMorphemesFromFile(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname

    def process(self, lexicon: Lexicon):
        """
        Reading root morpheme boundaries from an already prepared file with boundaries induced from hand-annotation of allomorphs
        """

        rootlemma = None
        roottechlemma = None
        stopnodes = None
        segmentednodes = None
        allomorph_regex = None
        
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                line = line.rstrip()

                columns = line.split("\t")

                if columns[0] == "STARTOFCLUSTER":
                    stopnodes = defaultdict()
                    segmentednodes = defaultdict()
                    allomorph_regex = r'{}'.format( "^(.*)("+( "|".join( columns[1].split(" ")))+ ")(.*)$")
                
                elif columns[0] == "ROOTNODE":
                    rootlemma = columns[1]
                    roottechlemma = columns[2]                    

                elif columns[0] == "SEGMENTEDNODE":
                    segmentednodes[columns[1]] = columns[2]  # keys: techlemmas, values: shortlemmas with indicated root morpheme boundaries

                elif columns[0] == "STOPNODE":
#                    print("adding STOPtechlemma "+columns[1])
                    stopnodes[columns[1]] = True

                elif columns[0] == "ENDOFCLUSTER":
                    rootlexemes = lexicon.get_lexemes(rootlemma, techlemma=roottechlemma)

                    if len(rootlexemes) == 0:
                        logger.warning("Lexeme for lemma {} not found".format(roottechlemma))

                    elif len(rootlexemes) > 1:    
                        logger.warning("Techlemma {} ambiguous".format(roottechlemma))

                    else:
                        self._process_subtree(rootlexemes[0],lexicon,segmentednodes,stopnodes,allomorph_regex)
                        pass

                else:
                    logger.warning("Unrecognized line:\t"+line+"\n")
                
                

        return lexicon


    def same_prefix_and_root(self,childlemma,parentsegmentation):
        (prefix,root,suffix) = re.split(r'[\(\)]',parentsegmentation)
        return ( childlemma[:len(prefix)+len(root)].upper() == prefix.upper()+root.upper() )

        
    def guess_from_parent(self,childlemma,parentsegmentation):
        (prefix,root,suffix) = re.split(r'[\(\)]',parentsegmentation)
        return ( prefix+"("+root+")"+childlemma[len(prefix)+len(root):] )

    def guess_using_allomorphs(self,childlemma,allomorph_regex):
        matchObj = re.match(  allomorph_regex , childlemma, re.IGNORECASE)
        if matchObj:
            return (matchObj.group(1)+"("+matchObj.group(2)+")"+matchObj.group(3))
        else:
            logger.warning("This should never happen RX="+allomorph_regex+"  L= " + childlemma)
            return "x(x)x"

    def _process_subtree(self, subtreeroot, lexicon, segmentednodes, stopnodes, allomorph_regex):  # recursive processing of derivational cluster
       
        if subtreeroot.techlemma in stopnodes:
            print("SKIPPED SUBTREE\t" +subtreeroot.techlemma)

        else:
            if subtreeroot.techlemma in segmentednodes:
                print("SEGMENTATION LOADED FROM PERL\t" +subtreeroot.techlemma+"\t"+segmentednodes[subtreeroot.techlemma])
                subtreeroot.misc['segmentation'] = segmentednodes[subtreeroot.techlemma]

            elif subtreeroot.parent and 'segmentation' in subtreeroot.parent.misc:

                if self.same_prefix_and_root(subtreeroot.lemma, subtreeroot.parent.misc['segmentation']):
                    subtreeroot.misc['segmentation'] = self.guess_from_parent(subtreeroot.lemma,subtreeroot.parent.misc['segmentation'])
                    print("SEGMENTATION PROJECTED FROM PARENT\t" + subtreeroot.lemma + " from " + subtreeroot.parent.misc['segmentation'] + " as " + subtreeroot.misc['segmentation'])

                elif len(re.findall(allomorph_regex,subtreeroot.lemma, re.IGNORECASE)) == 1:
                    subtreeroot.misc['segmentation'] = self.guess_using_allomorphs(subtreeroot.lemma,allomorph_regex)
                    print("SEGMENTATION USING ALLOMORPHS\t" + subtreeroot.lemma + " as " + subtreeroot.misc['segmentation'])
                    
                else:
                    print("UNSUCCESSFUL SEGMENTATION\t"+subtreeroot.lemma + " from " + subtreeroot.parent.misc['segmentation'])
                
                            
            for childnode in subtreeroot.children: # the recursion step
                self._process_subtree(childnode, lexicon, segmentednodes, stopnodes, allomorph_regex)
            
        pass

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest