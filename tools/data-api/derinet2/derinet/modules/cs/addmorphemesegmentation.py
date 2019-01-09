from derinet.modules.block import Block

import derinet as derinet_api
import logging
import random
from functools import reduce

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddMorphemeSegmentation(Block):
    def __init__(self, args):
        if "file" not in args or "name" not in args:
            raise ValueError("Arguments 'file' and 'name' must be supplied.")
        else:
            self.fname = args["file"]
            self.annotation_name = args["name"]

            if "manual" in args and args["manual"] == "true":
                self.manual = True
            else:
                self.manual = False

            if "roots" in args and args["roots"] == "true":
                self.root_annotation = True
                raise NotImplementedError("Sorry, root annotation is not supported yet.")
            else:
                self.root_annotation = False


    def process(self, derinet):
        """Add morpheme segmentation into the 'misc' section under the name from arg 'name'"""
        logger.info('Adding {}'.format(self.fname))
        with open(self.fname, 'rt', encoding='utf-8') as import_file:
            for line in import_file:
                raw_morphs = line.rstrip().split()

                if self.root_annotation:
                    # The input contains roots annotated by enclosing them in parentheses.
                    # Find the root morph (in parens), strip the parens and remember its position.
                    morphs = []
                    root_positions = []
                    for i, morph in enumerate(raw_morphs):
                        extracted_root = re.match(r"^\((.*)\)$", morph)
                        if extracted_root is not None:
                            # The morph is a root. Remember its position and save
                            #  only what's inside the parentheses.
                            root_positions.append(i)
                            morphs.append(extracted_root.group(1))
                        else:
                            # The morph is not tagged as a root. Just save it.
                            morphs.append(morph)
                    root_positions = set(root_positions)
                else:
                    # No root annotation is present, nothing to strip.
                    morphs = raw_morphs


                boundary_positions = list(reduce(lambda posits, morph: posits + [posits[-1] + len(morph)], morphs, [0]))[1:-1]

                lemma = "".join(morphs)
                candidate_lexemes = derinet.search_lexemes(lemma)
                if not candidate_lexemes:
                    logger.warning("lemma %s not found", lemma)
                    continue

                for lexeme in candidate_lexemes:
                    if "segmentation" not in lexeme.misc:
                        lexeme.misc["segmentation"] = {}
                    lexeme.misc["segmentation"][self.annotation_name] = {"manual": self.manual, "segments": morphs, "description": {position: {} for position in boundary_positions}}

                    if self.root_annotation:
                        for boundary_position in boundary_positions:
                            #lexeme.misc["segmentation"][self.annotation_name]["description"][boundary_position]["type"] = "root" if boundary_position in
                            pass

                    # If the segmentation was created manually, randomly assign it to
                    # train (60 %)
                    # dtest (20 %)
                    # etest (20 %)
                    if self.manual and "set" not in lexeme.misc["segmentation"]:
                        chosen_set = random.choices(["train", "dtest", "etest"], weights=[60, 20, 20], k=1)[0]
                        lexeme.misc["segmentation"]["set"] = chosen_set
        return derinet
