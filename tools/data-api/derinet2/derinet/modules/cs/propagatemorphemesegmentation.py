from derinet.modules.block import Block

import derinet as derinet_api
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class PropagateMorphemeSegmentation(Block):
    def __init__(self, args):
        if "name" not in args:
            raise ValueError("Argument 'name' must be supplied.")
        else:
            self.name = args["name"]

    def propagate_bounds_in_tree(self, derinet, subtree, string_to_propagate, bounds_to_propagate):
        node = subtree[0]
        children = subtree[1]

        # Propagate changes to children for as long as there is a matching prefix of both lemmas.
        for i in range(min(len(string_to_propagate), len(node.lemma))):
            if string_to_propagate[i] == node.lemma[i]:
                if i in bounds_to_propagate:
                    derinet.add_boundary(node, i, self.name, "propagated through suffixation", True)
            else:
                matching_prefix_ended_at = i
                break
        else:
            matching_prefix_ended_at = min(len(string_to_propagate), len(node.lemma))

        # Propagate in the same way, starting at the end and go backwards, through matching suffixes.
        # If there happens to be a whole-word match, stop as soon as we reach the alerady-scanned area.
        for i in range(matching_prefix_ended_at):
            idx_stp = len(string_to_propagate) - i - 1
            idx_nl = len(node.lemma) - i - 1
            if string_to_propagate[idx_stp] == node.lemma[idx_nl]:
                if idx_stp in bounds_to_propagate:
                    derinet.add_boundary(node, idx_nl, self.name, "propagated through prefixation", True)
            else:
                break

        for child in children:
            self.propagate_bounds_in_tree(derinet, child, string_to_propagate, bounds_to_propagate)

    def process_tree(self, derinet, tree):
        root = tree[0]
        children = tree[1]

        if "segmentation" in root.misc and self.name in root.misc["segmentation"]:
            string_to_propagate = root.lemma
            bounds_to_propagate = [position for position, params in root.misc["segmentation"][self.name]["description"].items() if params["allowed"] and not params["propagated"]]

            if bounds_to_propagate:
                for child in children:
                    self.propagate_bounds_in_tree(derinet, child, string_to_propagate, bounds_to_propagate)

        for child in children:
            self.process_tree(derinet, child)

    def process(self, derinet):
        """Propagate lexeme boundaries across trees from parents to children."""

        for root_id in derinet.iter_roots():
            tree = derinet.get_subtree(root_id)
            self.process_tree(derinet, tree)

        return derinet
