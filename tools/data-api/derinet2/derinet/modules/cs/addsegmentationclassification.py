#python3
import argparse
from derinet import Block, Lexicon
from collections import defaultdict


class AddSegmentationClassification(Block):
    def __init__(self, fname):
        self.fname = fname

    def _load_segmentations(self, filename):
        # types = {"R":"Root", "D":"Derivational", "I":"Inflective"}
        segmentations = defaultdict(list)
        with open(filename, "r") as r:
            for line in r:
                ls = line.strip().split("\t")
                word = "".join(ls[0].split())
                sms = ls[1].split()
                annotation = []
                start = 0
                for mph, ann in zip(ls[0].split(), sms):
                    span = [i for i in range(start, start+len(mph))]
                    annotation.append({"type":ann, "span":span, "morph":mph})
                segmentations[word] = annotation
        return segmentations

    def process(self, lexicon: Lexicon):
        segmentations = self._load_segmentations(self.fname)
        for lexeme in lexicon.iter_lexemes():
            lexeme._segmentation = {
            "boundaries": {},
            "morphs": [{
                "Type": "Implicit",
                "Start": 0,
                "End": len(lexeme.lemma),
                "Morph": lexeme.lemma
                }]
            }
        for lexeme in lexicon.iter_lexemes():
            segmentation = segmentations[lexeme.lemma.lower()]
            for morph in segmentation:
                lexeme.add_morph(start=morph["span"][0], end=morph["span"][-1], annot={"Type":morph["type"]})

    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("fname", help="The file to load annotation from.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.fname

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest

