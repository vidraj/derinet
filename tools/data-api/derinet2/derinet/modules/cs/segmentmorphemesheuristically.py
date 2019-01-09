from derinet.modules.block import Block

import derinet as derinet_api
import logging
import re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class SegmentMorphemesHeuristically(Block):
    def __init__(self, args):
        if "name" not in args:
            raise ValueError("Argument 'name' must be supplied.")
        else:
            self.name = args["name"]

    def process(self, derinet):
        """Segment well-known morphemes."""
        for lexeme in derinet.iter_lexemes():
            #if lexeme.pos == "V":
                #if re.search("t$", lexeme.lemma) is not None:
                    #self.add_boundary(lexeme, len(lexeme.lemma) - 1, "verbal -t")

            if lexeme.pos == "D" and re.search("ě$", lexeme.lemma) is not None:
                derinet.add_morpheme(lexeme, len(lexeme.lemma) - 1, len(lexeme.lemma), self.name, "adverbial -ě", False)
                if re.search("telně$", lexeme.lemma) is not None:
                    derinet.add_morpheme(lexeme, len(lexeme.lemma) - 5, len(lexeme.lemma) - 1, self.name,
                                         "adjectival -teln-", False)

            if lexeme.pos == "N" and re.search("ost$", lexeme.lemma) is not None:
                derinet.add_morpheme(lexeme, len(lexeme.lemma) - 3, len(lexeme.lemma), self.name, "nominal -ost", False)
                if re.search("telnost$", lexeme.lemma) is not None:
                    derinet.add_morpheme(lexeme, len(lexeme.lemma) - 7, len(lexeme.lemma) - 3, self.name,
                                         "adjectival -teln-", False)

            if lexeme.pos == "A" and re.search("ův$", lexeme.lemma) is not None:
                derinet.add_morpheme(lexeme, len(lexeme.lemma) - 2, len(lexeme.lemma), self.name, "adjectival -ův",
                                     False)

            if lexeme.pos == "A" and re.search("[ýí]$", lexeme.lemma) is not None:
                derinet.add_morpheme(lexeme, len(lexeme.lemma) - 1, len(lexeme.lemma), self.name, "adjectival -ý or -í",
                                     False)
                if re.search("telný$", lexeme.lemma) is not None:
                    derinet.add_morpheme(lexeme, len(lexeme.lemma) - 5, len(lexeme.lemma) - 1, self.name,
                                         "adjectival -teln-", False)
                #if re.search("[cs]ký$", lexeme.lemma) is not None:
                    #self.add_morpheme(lexeme, len(lexeme.lemma) - 3, len(lexeme.lemma) - 1, "adjectival -ck- or -sk-")

            parent = derinet.get_parent(lexeme)
            if parent is not None:
                parent_lemma = parent.lemma
                lexlemma = lexeme.lemma

                # Lowercasing
                parent_lemma = parent_lemma.lower()
                lexlemma = lexlemma.lower()

                # Dediacritization
                dediacritize_vowel = str.maketrans("áéíýóúů", "aeiyouu")
                vowel_change = str.maketrans("eu", "io")
                dediacritize_consonant = str.maketrans("čďňřšťž", "cdnrstz")
                consonant_change = str.maketrans("hgk", "zzc")

                parent_lemma = parent_lemma.translate(dediacritize_vowel)
                parent_lemma = parent_lemma.translate(vowel_change)
                parent_lemma = parent_lemma.translate(dediacritize_consonant)
                lexlemma = lexlemma.translate(dediacritize_vowel)
                lexlemma = lexlemma.translate(vowel_change)
                lexlemma = lexlemma.translate(dediacritize_consonant)

                if len(parent_lemma) < len(lexlemma):
                    if parent_lemma == lexlemma[0:len(parent_lemma)]:
                        derinet.add_boundary(lexeme, len(parent_lemma), self.name, "shared parental prefix", False)
                    if parent_lemma == lexlemma[len(lexlemma) - len(parent_lemma):]:
                        derinet.add_boundary(lexeme, len(lexlemma) - len(parent_lemma), self.name,
                                             "shared parental suffix", False)

        return derinet
