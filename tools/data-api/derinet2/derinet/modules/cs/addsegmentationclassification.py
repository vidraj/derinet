#python3
from derinet import Block, Lexicon
from collections import defaultdict


class AddSegmentationClassification(Block):
    def __init__(self, fname):
        self.fname = fname

    def _load_segmentations(self, filename):
        types = {"R":"Root", "D":"Derivational", "I":"Inflective"}
        segmentations = defaultdict(list)
        with open(filename, "r") as r:
            for line in r:
                ls = line.strip().split("\t")
                word = "".join(ls[0].split())
                sms = ls[1].split()
                useg_annotation = []
                span = []
                tp = ""
                for i in range(len(sms)):
                    if sms[i][:1] in {"B", "S"} and i > 0:
                        useg_annotation.append({"type":tp, "span":span})
                        tp = ""
                        span = []
                    span.append(i)
                    tp = types[sms[i][1:]]
                morph = [str(word[s]) for s in span]
                useg_annotation.append({"type":tp, "span":span, "morph":morph})
                # useg_annotation.append({"type":tp, "morph":morph})
                segmentations[word] = useg_annotation
        return segmentations

    def process(self, lexicon: Lexicon):
        segmentations = self.load_segmentations(self.fname)
        for lexeme in lexicon.iter_lexemes:
            segmentation = segmentations[lexeme.lemma.lower()]
            #lexeme.misc["useg"] = segmentation
            for morph in segmentation:
                lexeme.add_morph(start=segmentation["span"][0], end=segmentation["span"][-1], annot=segmentation["type"])

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

