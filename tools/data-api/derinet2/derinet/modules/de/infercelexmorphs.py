from derinet import Block, Lexicon
from derinet.utils import DerinetMorphError
import argparse
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


hier_extract_regex = re.compile("\((.*)\)\[[^][]*\]")
def hier_to_morphemes(s):
    """
    Parse the hierarchical information `s` from a CELEX lexeme info to a list
    of morphemes contained therein.

    Example: (((arbeit)[V],(er)[N|V.])[N],((dicht)[V],(er)[N|V.])[N])[N]
    """
    match = hier_extract_regex.fullmatch(s)
    if not match:
        # The hierarchy is not further subdivisible, therefore the entire string
        #  is the morpheme we were looking for.
        return [s], s

    inside = match[1]

    flat_morphemes = []
    hier_morphemes = []

    paren_level = 0
    part = ""

    # Use a very naive recursive algorithm for parsing the content in parentheses.
    for char in inside:
        if paren_level < 0:
            raise ValueError("Paren level must not be negative in '{}'".format(s))

        if char == "," and paren_level == 0:
            flat_parsed_part, hier_parsed_part = hier_to_morphemes(part)
            flat_morphemes += flat_parsed_part
            hier_morphemes.append(hier_parsed_part)
            part = ""
        elif char == "(":
            paren_level += 1
            part += char
        elif char == ")":
            paren_level -= 1
            part += char
        else:
            part += char

    # Parse the last part, which has no ',' after it.
    flat_parsed_part, hier_parsed_part = hier_to_morphemes(part)
    flat_morphemes += flat_parsed_part
    hier_morphemes.append(hier_parsed_part)

    return flat_morphemes, hier_morphemes


def record_boundaries(lexeme, segments):
    """
    The list of strings `segments` is the lexeme's lemma broken down into
    contiguous segments (potentially multi-morph). That means that boundaries
    between the segments are morph boundaries in lexeme. Record them.
    """
    position = 0
    for segment in segments:
        position += len(segment)
        lexeme.add_boundary(position, True)

def record_morphemes(lexeme, morphs, morphemes):
    """
    The list of strings `morphs` is the lexeme's lemma broken down into
    morphs. The list of strings `morphemes` contains the corresponding
    morphemes. Record them.
    """
    assert len(morphs) == len(morphemes), "The morphs and morphemes must match"
    start_position = 0
    for morph, morpheme in zip(morphs, morphemes):
        end_position = start_position + len(morph)
        lexeme.add_morph(start_position, end_position)
        start_position = end_position

class InferCELEXMorphs(Block):
    """
    Use the morpheme information contained in the various CELEXes to infer
    their morphs.

    The CELEX annotation contains two major pieces of information: The stem
    list and the morpheme hierarchy. Neither can be used for morph segmentation
    as-is, because their spelling is normalized. For example, “Abdikation” has
    stem list “abdiz;ation”.

    But sometimes, the spelling does match. In that case, the stem list can be
    used to find boundaries in the lemma and the morpheme list can be used to
    delimit individual morphs and assign them the somewhat-disambiguated
    morpheme string.
    """

    allomorphs = {}

    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes():
            # Ignore lexemes which don't contain the necessary information.
            if "segmentation" not in lexeme.misc or "segmentation_hierarch" not in lexeme.misc:
                continue

            lemma = lexeme.lemma.lower()
            segments = lexeme.misc["segmentation"].lower().split(sep=";")
            flat_morphemes, hier_morphemes = hier_to_morphemes(lexeme.misc["segmentation_hierarch"].lower())

            # Fixup verbs, which lack the (inflectional) infinitive marker at
            #  the end.
            if lexeme.pos == "VERB":
                segments.append("en")
                flat_morphemes.append("en")
                hier_morphemes.append(["en"])

            #print(flat_morphemes, hier_morphemes)

            # Record the boundaries present in the stem list.
            if "".join(segments) == lemma:
                # The boundaries can be simply concatenated, there are no
                #  phonological or other changes. Easy!
                #print("Stem segmentation success:", lemma, segments)
                record_boundaries(lexeme, segments)
            else:
                #print("Stem segmentation fail:", lemma, segments)
                pass

            # Record the boundaries present in the morpheme list.
            if "".join(flat_morphemes) == lemma:
                # The boundaries can be simply concatenated, there are no
                #  phonological or other changes. Easy!
                #print("Full morpheme segmentation success:", lemma, flat_morphemes)
                record_morphemes(lexeme, flat_morphemes, flat_morphemes)
            else:
                #print("Full morpheme segmentation fail:", lemma, flat_morphemes)
                pass

        return lexicon
