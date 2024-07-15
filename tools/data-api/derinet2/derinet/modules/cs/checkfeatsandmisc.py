from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class CheckFeatsAndMisc(Block):
    def checkFE(self, lexeme, k):
        """
        Check that the given key `k` exists in Feats of `lexeme`.
        """
        if k in lexeme.feats:
            return True
        else:
            logger.error("Lexeme %s does not have %s in Feats.", lexeme, k)
            return False

    def checkFN(self, lexeme, k):
        """
        Check that the given key `k` does not exist in Feats of `lexeme`.
        """
        if k in lexeme.feats:
            logger.error("Lexeme %s has %s '%s' in Feats, it should not be present.", lexeme, k, lexeme.feats[k])
            return False
        else:
            return True

    def checkFV(self, lexeme, k, vs):
        """
        Check that if the given key `k` is present in Feats of `lexeme`,
        it has one of the values from `vs`.

        If the key is not present, that's OK, you should check that
        separately.
        """
        if k in lexeme.feats and lexeme.feats[k] not in vs:
            logger.error("Feat %s of %s has wrong value %s, expected one of %s.", k, lexeme, lexeme.feats[k], vs)
            return False
        else:
            # Either not present, or present with the correct value.
            return True

    def checkMV(self, lexeme, ks, vs):
        """
        Check that if the given sequence of keys `ks` is present as a
        nested sequence of keys in Misc of `lexeme`, the final retrieved
        value has one of the values from `vs`.

        If the sequence of keys is not present, that's OK, you should
        check that separately.
        """
        d = lexeme.misc
        for k in ks:
            if k in d:
                d = d[k]
            else:
                # Not present.
                return True
        else:
            # We ran out of keys to get, so `d` should now contain the
            #  final value.
            if d in vs:
                # Present with the correct value.
                return True
            else:
                # Present with a wrong value.
                logger.error("Feat %s of %s has wrong value %s, expected one of %s.", k, lexeme, d, vs)
                return False

    def process(self, lexicon: Lexicon):
        """
        Check that the contents of feats and misc conform to our expectations when releasing a new version.
        """
        for lexeme in lexicon.iter_lexemes(sort=False):
            if lexeme.pos not in {"ADJ", "ADP", "ADV", "NOUN", "NUM", "PRON", "VERB", "Affixoid"}:
                logger.error("Lexeme %s has unexpected POS %s.", lexeme, lexeme.pos)

            if lexeme.pos == "NOUN":
                # self.checkFE(lexeme, "Gender") # Commented out, too many words trigger it.
                self.checkFV(lexeme, "Gender", {"Fem", "Masc", "Neut"})

                if "Gender" in lexeme.feats and lexeme.feats["Gender"] == "Masc":
                    self.checkFE(lexeme, "Animacy")
                    self.checkFV(lexeme, "Animacy", {"Anim", "Inan"})
                else:
                    self.checkFN(lexeme, "Animacy")
            else:
                if lexeme.pos != "NUM":
                    # Not NOUN or NUM.
                    self.checkFN(lexeme, "Gender")
                    self.checkFN(lexeme, "Animacy")

            if lexeme.pos == "ADJ":
                self.checkFV(lexeme, "Poss", {"Yes"})
                if "Poss" in lexeme.feats and lexeme.feats["Poss"] == "Yes":
                    self.checkFE(lexeme, "PossGender")
                    self.checkFV(lexeme, "PossGender", {"Fem", "Masc"})

                    if lexeme.parent is None:
                        logger.error("Lexeme %s is a possessive, but has no parent relation.", lexeme)
                    elif "PossGender" in lexeme.feats:
                        assert lexeme.parent_relation is not None # We already tested parent for non-null.
                        # If this lexeme is possessive (Poss=Yes), check that its PossGender is identical to the gender of its parent.
                        # But it might also be a variant of another possessive and that's OK too.
                        if lexeme.parent_relation.type not in {"Derivation", "Variant"}:
                            logger.error("Lexeme %s is possessive, but created by %s instead of by derivation.", lexeme, lexeme.parent_relation)

                        if lexeme.parent_relation.type != "Variant":
                            if "Gender" not in lexeme.parent.feats or lexeme.parent.feats["Gender"] != lexeme.feats["PossGender"]:
                                # The PossGender must be identical to the gender of the parent.
                                logger.error("Lexeme %s is %s possessive, but its parent %s has a different gender %s.", lexeme, lexeme.feats["PossGender"], lexeme.parent, lexeme.parent.feats.get("Gender", "(none)"))
                            elif lexeme.feats["PossGender"] == "Masc" and ("Animacy" not in lexeme.parent.feats or lexeme.parent.feats["Animacy"] != "Anim"):
                                # Masc PossGender always implies Animate on the parent.
                                logger.error("Lexeme %s is Masc possessive, but its parent %s is not Animate.", lexeme, lexeme.parent)
                else:
                    self.checkFN(lexeme, "PossGender")
            else:
                self.checkFN(lexeme, "Poss")
                self.checkFN(lexeme, "PossGender")

            if lexeme.pos == "VERB":
                # TODO must (may?) have Aspect, values Imp or Perf
                # TODO must (may?) have ConjugClass, numerical value or multiple hashmark delimited values
                pass
            else:
                self.checkFN(lexeme, "Aspect")
                self.checkFN(lexeme, "ConjugClass")

            if lexeme.pos == "Affixoid":
                self.checkFE(lexeme, "Fictitious")

            self.checkFV(lexeme, "Fictitious", "Yes")

            # Loanword: False or True as strings. (TODO maybe we want to change this to Yes for loanwords and empty otherwise?)
            self.checkFV(lexeme, "Loanword", {"False", "True"})

            if lexeme.pos != "NOUN" and lexeme.pos != "ADJ":
                self.checkFN(lexeme, "NameType")
            self.checkFV(lexeme, "NameType", {"Com", "Geo", "Giv", "Nat", "Oth", "Pro", "Prs", "Sur"})

            # Style: check the values.
            self.checkFV(lexeme, "Style", {"Arch", "Coll", "Expr", "Rare", "Slng", "Vrnc", "Vulg"})

            # TODO misc/is_compound: If present, the lexeme must have a Compounding parent relation or be unattached.
            # TODO misc/techlemma: Must be present? Or not? If present, must start with the lemma, followed by [-`_]
            # TODO misc/unmotivated: If present, must be true and the lexeme must be unattached.

            # TODO Also check that there are no other keys in either feats or misc.
            # TODO Especially, the history and segmentation must not be present in Misc for the release.


            ## Check relations: Each lexeme has at most one parent relation.
            if lexeme.otherrels:
                logger.error("Lexeme %s has multiple relations: %s.", lexeme, ", ".join(str(rel) for rel in lexeme.parent_relations))

            if lexeme.parent_relation is not None:
                assert lexeme.parent is not None
                # Type has a permitted value
                # SemanticLabel has a permitted value

                if lexeme.parent_relation.type == "Variant":
                    # Variants have no further children
                    # Variants have properties identical to the base word – at least POS, gender, animacy, aspect, ... well, all of them.
                    # SemanticLabel not for variants
                    if lexeme.pos != lexeme.parent.pos:
                        logger.error("Variant relation %s does not preserve POS.", lexeme.parent_relation)
                    # TODO Check the other properties.

        return lexicon
