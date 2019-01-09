from derinet.modules.block import Block

import derinet as derinet_api
import logging
from functools import reduce

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class CalcMorphemeStats(Block):
    def __init__(self, args):
        if "gold" not in args or "predicted" not in args:
            raise ValueError("Arguments 'gold' and 'predicted' must be supplied.")
        else:
            self.gold = args["gold"]
            self.predicted = args["predicted"]
            if "set" in args:
                self.chosen_set = args["set"]
            else:
                self.chosen_set = "train"

        self.true_positive = 0
        self.true_negative = 0
        self.false_positive = 0
        self.false_negative = 0

    def boundary_positions(self, morphs):
        all_positions = list(reduce(lambda posits, morph: posits + [posits[-1] + len(morph)], morphs, [0]))
        return set(all_positions[1:-1])

    def process(self, derinet):
        """Calculate precision and recall of morpheme segmentation from 'predicted' annotation against the 'set' fold of 'gold' annotation."""
        for lexeme in derinet.iter_lexemes():
            if "segmentation" in lexeme.misc and self.gold in lexeme.misc["segmentation"] and self.chosen_set in lexeme.misc["segmentation"]["set"]:
                gold_boundary_positions = self.boundary_positions(lexeme.misc["segmentation"][self.gold]["segments"])

                if self.predicted in lexeme.misc["segmentation"]:
                    predicted_boundary_positions = self.boundary_positions(lexeme.misc["segmentation"][self.predicted]["segments"])
                else:
                    # The predicted segmentation was not filled in.
                    # Act as if the word is unsegmented.
                    predicted_boundary_positions = []

                for i in range(len(lexeme.lemma) + 1):
                    if i in predicted_boundary_positions:
                        if i in gold_boundary_positions:
                            self.true_positive += 1
                        else:
                            self.false_positive += 1
                    else:
                        if i in gold_boundary_positions:
                            self.false_negative += 1
                        else:
                            self.true_negative += 1

        precision = self.true_positive / (self.true_positive + self.false_positive)
        recall = self.true_positive / (self.true_positive + self.false_negative)
        logger.info("precision\t%f\nrecall\t%f", precision * 100.0, recall * 100.0)

        return derinet
