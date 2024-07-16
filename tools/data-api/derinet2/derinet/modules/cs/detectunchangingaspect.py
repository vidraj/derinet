from derinet import Block, Format, Lexicon
import logging
import re


logger = logging.getLogger(__name__)


class DetectUnchangingAspect(Block):
    def process(self, lexicon: Lexicon):
        """
        List all x->y relations, where both nodes end with "ovat" and the aspect doesn't change between them.
        """
        ovat_re = re.compile("ovat$")
        for parent in lexicon.iter_lexemes(sort=False):
            if ovat_re.search(parent.lemma):
                for child_rel in parent.child_relations:
                    for child in child_rel.targets:
                        if ovat_re.search(child.lemma) and (("Aspect" not in parent.feats and "Aspect" not in child.feats) or (parent.feats.get("Aspect", None) == child.feats.get("Aspect", None))):
                            logger.info("Match: %s and %s", parent, child)

        return lexicon
