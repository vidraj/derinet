from derinet.modules.block import Block

import derinet as derinet_api
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class CopyMorphBounds(Block):
    def __init__(self, args):
        if "from" not in args and "to" not in args:
            raise ValueError("Arguments 'from' and 'to' must be supplied.")
        else:
            self.from_db = args["from"]
            self.to_db = args["to"]

    def process(self, derinet):
        """Copy morph bound from 'from' to the longest contiguous sequence of allowed positions in 'to'."""

        for lexeme in derinet.iter_lexemes():
            if "segmentation" in lexeme.misc and self.from_db in lexeme.misc["segmentation"] and self.to_db in lexeme.misc["segmentation"]:
            #if "segmentation" in lexeme.misc and self.from_db in lexeme.misc["segmentation"]:
                #if self.to_db not in lexeme.misc["segmentation"]:
                    #lexeme.misc["segmentation"][self.to_db] = {"manual": False, "segments": [lexeme.lemma], "description": {}}

                current_run_start = 0
                current_run_len = 0
                longest_run_start = 0
                longest_run_len = 0

                for i in range(1, len(lexeme.lemma) + 1):
                    if i not in lexeme.misc["segmentation"][self.to_db]["description"] or lexeme.misc["segmentation"][self.to_db]["description"][i]["allowed"]:
                        current_run_len += 1
                    else:
                        if current_run_len > longest_run_len:
                            longest_run_start = current_run_start
                            longest_run_len = current_run_len
                        current_run_start = i + 1
                        current_run_len = 0

                if current_run_len > longest_run_len:
                    longest_run_start = current_run_start
                    longest_run_len = current_run_len

                #logger.info("Longest allowed run in lemma %s has len %d", lexeme.lemma, longest_run_len)

                for boundary_position, description in lexeme.misc["segmentation"][self.from_db]["description"].items():
                    #logger.info("Considering copying position %d in lemma %s. Longest run is %d + %d", boundary_position, lexeme.lemma, longest_run_start, longest_run_len)
                    if boundary_position in range(longest_run_start, longest_run_start + longest_run_len + 1):
                        #logger.info("Copying boundary %d in lemma %s", boundary_position, lexeme.lemma)
                        derinet.add_boundary(lexeme, boundary_position, self.to_db, description, True)

        return derinet
