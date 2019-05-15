from derinet import Block, Format, Lexicon
from derinet.utils import techlemma_to_lemma
import re
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class AddTagMasks(Block):
    """
    Add tag masks from the specified file and parse the information contained
    therein into useful features.
    """
    positional_tag_feature_map = [
        # POS tag.
        {},
        # Extended POS tag.
        {},
        # Gender.
        {
            "-": {"Gender": None},  # N/A
            "F": {"Gender": "Fem"},
            "H": {"Gender": None},  # Fem or Neut.
            "I": {"Gender": "Masc", "Animacy": "Inan"},
            "M": {"Gender": "Masc", "Animacy": "Anim"},
            "N": {"Gender": "Neut"},
            "Q": {"Gender": None},  # Feminine (with singular only) or Neuter (with plural only).
            "T": {"Gender": None},  # Masculine inanimate or Feminine (plural only).
            "X": {"Gender": None},  # Any.
            "Y": {"Gender": "Masc", "Animacy": None},  # Without animacy.
            "Z": {"Gender": None},  # Not fenimine (i.e., Masculine animate/inanimate or Neuter).
            "?": {"Gender": None},  # Varies with form (i.e. agreement).
        },
        # Number.
        {},
        # Case.
        {},
        # Possgender.
        {},
        # Possnumber.
        {},
        # Person.
        {},
        # Tense.
        {},
        # Grade.
        {},
        # Negation.
        {},
        # Voice.
        {},
        # 13, 14: reserved
        {}, {},
        # 15: variant
        {}
    ]

    term_extractor = re.compile("_;(.)")
    term_feature_map = {
        # Y	given name (formerly used as default): Petr, John
        "Y": {"NameType": "Giv"},
        # S	surname, family name: Dvořák, Zelený, Agassi, Bush
        "S": {"NameType": "Sur"},
        # E	member of a particular nation, inhabitant of a particular territory: Čech, Kolumbijec, Newyorčan
        "E": {"NameType": "Nat"},
        # G	geographical name: Praha, Tatry (the mountains)
        "G": {"NameType": "Geo"},
        # K	company, organization, institution: Tatra (the company)
        "K": {"NameType": "Com"},
        # R	product: Tatra (the car)
        "R": {"NameType": "Pro"},
        # m	other proper name: names of mines, stadiums, guerilla bases, etc.
        "m": {"NameType": "Oth"},
        # H	chemistry
        # U	medicine
        # L	natural sciences
        # j	justice
        # g	technology in general
        # c	computers and electronics
        # y	hobby, leisure, travelling
        # b	economy, finances
        # u	culture, education, arts, other sciences
        # w	sports
        # p	politics, governement, military
        # z	ecology, environment
        # o	color indication
    }

    style_extractor = re.compile("_,(.)")
    style_feature_map = {
        # t	foreign word - see Chapter 6, Foreign words and phrases
        "t": {"Foreign": "Yes"},
        # n	dialect
        "n": {"Style": "Vrnc"},
        # a	archaic
        "a": {"Style": "Arch"},
        # s	bookish
        #"s": {"Style": "Form"},  # Form is only in UD1.
        "s": {"Style": "Rare"},  # Rare seems to be the closest equivalent in UD2.
        # h	colloquial
        "h": {"Style": "Coll"},
        # e	expressive
        "e": {"Style": "Expr"},
        # l	slang, argot
        "l": {"Style": "Slng"},
        # v	vulgar
        "v": {"Style": "Vulg"},
        # x	outdated spelling or misspelling
        "x": {"Typo": "Yes"}
    }


    def __init__(self, fname):
        self.fname = fname

    def mask_to_features(self, mask):
        all_features = {}

        for pos_part, feat_map in zip(mask, self.positional_tag_feature_map):
            if pos_part in feat_map:
                feats = feat_map[pos_part]
                for k, v in feats.items():
                    if k in all_features:
                        raise Exception("Key {} defined multiple times".format(k))
                    all_features[k] = v

        return all_features

    def techlemma_to_features(self, techlemma: str):
        all_features = {}

        # Lemma category is indicated by "_:" followed by a letter.
        # Interesting ones:
        # T	imperfect verb
        # W	perfect verb
        # B	abbreviation
        is_imperfect = "_:T" in techlemma
        is_perfect = "_:W" in techlemma
        if is_perfect:
            if is_imperfect:
                # Biaspectual verb.
                logger.warning("Techlemma {} has both aspects".format(techlemma))
            else:
                all_features["Aspect"] = "Perf"
        else:
            if is_imperfect:
                all_features["Aspect"] = "Imp"
            else:
                # No aspect given.
                pass

        if "_:B" in techlemma:
            # Abbreviation.
            all_features["Abbr"] = "Yes"


        # Terms: _; followed by a letter.
        for match in self.term_extractor.finditer(techlemma):
            term = match.group(1)
            if term not in self.term_feature_map:
                continue

            features = self.term_feature_map[term]
            for k, v in features.items():
                if k in all_features and all_features[k] != v:
                    logger.warning("Key {} defined multiple times in techlemma {}".format(k, techlemma))
                    all_features[k] = None
                all_features[k] = v

        # Style: _, followed by a letter.
        for match in self.style_extractor.finditer(techlemma):
            style = match.group(1)
            if style not in self.style_feature_map:
                continue

            features = self.style_feature_map[style]
            for k, v in features.items():
                if k in all_features and all_features[k] != v:
                    logger.warning("Key {} defined multiple times in techlemma {}".format(k, techlemma))
                    all_features[k] = None
                all_features[k] = v

        return all_features

    def process(self, lexicon: Lexicon):
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 2
                techlemma, tag_mask = fields
                lemma = techlemma_to_lemma(techlemma)
                pos = tag_mask[0]
                tag_mask_features = self.mask_to_features(tag_mask)
                techlemma_features = self.techlemma_to_features(techlemma)

                lexemes = lexicon.get_lexemes(lemma, pos, techlemma)

                if not lexemes:
                    logger.error("Lexeme for '{} {}' not found".format(techlemma, tag_mask))
                elif len(lexemes) > 1:
                    logger.error("Lexeme for '{} {}' ambiguous".format(techlemma, tag_mask))
                else:
                    lexeme = lexemes[0]

                    for k, v in tag_mask_features.items():
                        if k in lexeme.feats and lexeme.feats[k] != v:
                            logger.error("Lexeme {} visited multiple times with different masks".format(lexeme))
                        else:
                            lexeme.add_feature(k, v)

                    for k, v in techlemma_features.items():
                        if k in lexeme.feats and lexeme.feats[k] != v:
                            logger.error("Lexeme {} visited multiple times with different masks".format(lexeme))
                        else:
                            lexeme.add_feature(k, v)

                    if lexeme.lemid != "{}#{}".format(lemma, pos):
                        logger.error("Lemid of lexeme {} already set".format(lexeme))
                    else:
                        lexeme._lemid = "{}#{}".format(lemma, tag_mask)

        return lexicon

    @staticmethod
    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to load tag masks from, in a `techlemma TAB tag-mask` format.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
