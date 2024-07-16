from derinet import Block, Lexicon
import argparse
import logging
from contextlib import ExitStack


logger = logging.getLogger(__name__)


class MeasurePrecisionRecall(Block):
    """
    Measure statistics of the lexicon on a gold-standard dataset.
    """

    def __init__(self, gold_standard_file, ignore_pos, edge_details_file=None):
        self.gold_standard_file = gold_standard_file
        self.ignore_pos = ignore_pos
        self.ignore_compounding = False
        self.edge_details_file = edge_details_file
        self.stats = {"lex": {"tp": 0,
                              "fp": 0,
                              "tn": 0,
                              "fn": 0},
                      "irel": {"tp": 0,
                               "fp": 0,
                               "tn": 0,
                               "fn": 0},
                      "grel": {"tp": 0,
                               "fp": 0,
                               "tn": 0,
                               "fn": 0},
                      "crel": {"tp": 0,
                               "fp": 0,
                               "tn": 0,
                               "fn": 0}}

    def parse_possibilities(self, annot):
        """
        Parse the possible parents out of annot, returning a set of
        tuples of (reltype, [parent-lemmas]).
        """
        possibilities = [item.strip() for item in annot.split(",")]
        parsed = []
        for possibility in possibilities:
            parents = possibility.split()
            if len(parents) == 1:
                if parents[0] == "-":
                    parsed.append((None, ()))
                else:
                    parsed.append(("Derivation", tuple(parents)))
            elif len(parents) > 1:
                parsed.append(("Compounding", tuple(parents)))
            else:
                logger.error("Malformed annotation '{}' in '{}'".format(possibility, annot))

        assert len(parsed) >= 1, "Annotation parsing error!"

        return set(parsed)

    def record_correct(self, kind):
        self.stats[kind]["tp"] += 1

    def record_nonexistent(self, kind):
        self.stats[kind]["tn"] += 1

    def record_incorrect(self, kind):
        self.stats[kind]["fp"] += 1

    def record_missing(self, kind):
        self.stats[kind]["fn"] += 1

    def total(self, kind):
        return self.stats[kind]["tp"] + self.stats[kind]["tn"] + self.stats[kind]["fp"] + self.stats[kind]["fn"]

    def relevant(self, kind):
        return self.stats[kind]["tp"] + self.stats[kind]["fn"]

    def correct(self, kind):
        return self.stats[kind]["tp"] + self.stats[kind]["tn"]

    def predicted(self, kind):
        return self.stats[kind]["tp"] + self.stats[kind]["fp"]

    def precision(self, kind):
        predicted = self.predicted(kind)
        if predicted == 0:
            logger.warning("No predicted elements found when calculating precision of {}".format(kind))
            return 0.0
        else:
            return self.stats[kind]["tp"] / predicted

    def recall(self, kind):
        relevant = self.relevant(kind)
        if relevant == 0:
            logger.warning("No relevant elements found when calculating recall of {}".format(kind))
            return 1.0
        else:
            return self.stats[kind]["tp"] / relevant

    def specificity(self, kind):
        negative = self.stats[kind]["tn"] + self.stats[kind]["fp"]
        if negative == 0:
            logger.warning("No negative elements found when calculating specificity of {}".format(kind))
            return 1.0
        else:
            return self.stats[kind]["tn"] / negative

    def accuracy(self, kind):
        if self.total(kind) == 0:
            return 0.0
        else:
            return self.correct(kind) / self.total(kind)

    def f1(self, kind):
        twotp = 2 * self.stats[kind]["tp"]
        denom = twotp + self.stats[kind]["fp"] + self.stats[kind]["fn"]
        if denom == 0:
            return 0.0
        else:
            return twotp / denom


    def judge_correctness(self, lexicon, lexeme, possible_rels):
        if not lexeme.parent_relations:
            # The lexeme is not derived.
            if (None, ()) in possible_rels:
                # True negative case.
                self.record_nonexistent("irel")
                self.record_nonexistent("grel")
                if self.edge_details is not None:
                    print("N", lexeme.lemma, lexeme.pos, "-", str(possible_rels), sep="\t", file=self.edge_details)
            else:
                # False negative case.
                logger.info("Missing relation for {}, should be {}".format(lexeme, ", ".join([" + ".join(pr[1]) for pr in possible_rels])))
                self.record_missing("irel")
                self.record_missing("grel")
                if self.edge_details is not None:
                    print("M", lexeme.lemma, lexeme.pos, "-", str(possible_rels), sep="\t", file=self.edge_details)

        for rel in lexeme.parent_relations:
            # Map all relation types to Derivation and just compounding
            #  to compounding. This ensures that e.g. variants are
            #  processed semi-correctly.
            reltype = "Derivation"
            if rel.type == "Compounding":
                reltype = "Compounding"

            parent_lemmas = tuple([lex.lemma for lex in rel.sources])

            if (reltype, parent_lemmas) in possible_rels:
                # True positive case.
                self.record_correct("irel")
                self.record_correct("grel")
                if self.edge_details is not None:
                    print("C", lexeme.lemma, lexeme.pos, str(parent_lemmas), str(possible_rels), sep="\t", file=self.edge_details)
            else:
                # False positive case.
                logger.info("Incorrectly derived {} from {}, should be {}".format(lexeme, ", ".join([str(src) for src in rel.sources]), ", ".join([" + ".join(pr[1]) for pr in possible_rels])))
                self.record_incorrect("irel")
                self.record_incorrect("grel")
                if self.edge_details is not None:
                    print("I", lexeme.lemma, lexeme.pos, str(parent_lemmas), str(possible_rels), sep="\t", file=self.edge_details)

        # Lastly, solve the `crel` – gold relation found anywhere in
        #  the cluster.
        # If the lexeme can be only nonderived, find out whether it is.
        if len(possible_rels) == 1 and (None, ()) in possible_rels:
            if not lexeme.parent_relations:
                self.record_nonexistent("crel")
            else:
                self.record_incorrect("crel")
        else:
            # Try to find any of the gold parents anywhere in the cluster.
            found = False
            for reltype, parent_lemmas in possible_rels:
                for parent_lemma in parent_lemmas:
                    parent_lexemes = lexicon.get_lexemes(parent_lemma)
                    roots = set([pl.get_tree_root() for pl in parent_lexemes])
                    if lexeme.get_tree_root() in roots:
                        # Both are in the same family.
                        self.record_correct("crel")
                        found = True
                        break
            if not found:
                if not lexeme.parent_relations:
                    self.record_missing("crel")
                else:
                    self.record_incorrect("crel")

    def process(self, lexicon: Lexicon):
        with open(self.gold_standard_file, "rt", encoding="utf-8", errors="strict", newline="\n") as f, \
             ExitStack() as extra_f:
            # Store the edge-details open file for use in the judges.
            if self.edge_details_file is not None:
                self.edge_details = extra_f.enter_context(open(self.edge_details_file, "wt", encoding="utf-8"))
            else:
                self.edge_details = None

            for line in f:
                line = line.rstrip()
                if not line or line.startswith("#"):
                    # An empty line or a comment.
                    continue

                lemma, pos, manual_deriv = line.split("\t", maxsplit=2)

                if not manual_deriv:
                    logger.error("Manual annotation not filled on line '{}'".format(line))
                    continue
                elif manual_deriv == "?":
                    logger.warning("Untagged lexeme '{} {}'".format(lemma, pos))
                    continue
                elif self.ignore_compounding:
                    # TODO
                    pass

                if self.ignore_pos:
                    lexemes = lexicon.get_lexemes(lemma)
                else:
                    lexemes = lexicon.get_lexemes(lemma, pos)

                if not lexemes:
                    # The lexeme is not in the DB. Is that right?
                    if manual_deriv == "!":
                        self.record_nonexistent("lex")
                        # TODO do we consider this a correct derivation as well?
                    else:
                        self.record_missing("lex")

                        if manual_deriv != "-":
                            # Not only is the lexeme incorrectly missing,
                            #  but it should have been derived as well.
                            self.record_missing("grel")
                            #self.record_missing("crel")
                            if self.edge_details is not None:
                                print("MD", lemma, pos, "-", manual_deriv, sep="\t", file=self.edge_details)
                        logger.info("Incorrectly deleted '{} {}'".format(lemma, pos))

                    continue

                possible_parent_rels = self.parse_possibilities(manual_deriv)

                for lexeme in lexemes:
                    if manual_deriv == "!":
                        # The lexeme is in the DB, but shouldn't be.
                        self.record_incorrect("lex")
                        # Do we judge the derivations? Probably not.
                        continue
                    else:
                        self.record_correct("lex")

                    self.judge_correctness(lexicon, lexeme, possible_parent_rels)

        print("lexeme total\t{}".format(self.total("lex")),
              "lexeme not in gold\t{}".format(lexicon.lexeme_count() - self.stats["lex"]["tp"]),
              "lexeme relevant\t{}".format(self.relevant("lex")),
              "lexeme predicted\t{}".format(self.predicted("lex")),
              "lexeme correct\t{}".format(self.correct("lex")),
              "lexeme precision\t{:.2%}".format(self.precision("lex")),
              "lexeme recall\t{:.2%}".format(self.recall("lex")),
              "lexeme specificity\t{:.2%}".format(self.specificity("lex")),
              "lexeme accuracy\t{:.2%}".format(self.accuracy("lex")),
              "lexeme F1\t{:.2%}".format(self.f1("lex")),
              "internal relation total\t{}".format(self.total("irel")),
              "internal relation relevant\t{}".format(self.relevant("irel")),
              "internal relation predicted\t{}".format(self.predicted("irel")),
              "internal relation correct\t{}".format(self.correct("irel")),
              "internal relation precision\t{:.2%}".format(self.precision("irel")),
              "internal relation recall\t{:.2%}".format(self.recall("irel")),
              "internal relation specificity\t{:.2%}".format(self.specificity("irel")),
              "internal relation accuracy\t{:.2%}".format(self.accuracy("irel")),
              "internal relation F1\t{:.2%}".format(self.f1("irel")),
              "gold relation total\t{}".format(self.total("grel")),
              "gold relation relevant\t{}".format(self.relevant("grel")),
              "gold relation predicted\t{}".format(self.predicted("grel")),
              "gold relation correct\t{}".format(self.correct("grel")),
              "gold relation precision\t{:.2%}".format(self.precision("grel")),
              "gold relation recall\t{:.2%}".format(self.recall("grel")),
              "gold relation specificity\t{:.2%}".format(self.specificity("grel")),
              "gold relation accuracy\t{:.2%}".format(self.accuracy("grel")),
              "gold relation F1\t{:.2%}".format(self.f1("grel")),
              "cluster relation total\t{}".format(self.total("crel")),
              "cluster relation relevant\t{}".format(self.relevant("crel")),
              "cluster relation predicted\t{}".format(self.predicted("crel")),
              "cluster relation correct\t{}".format(self.correct("crel")),
              "cluster relation precision\t{:.2%}".format(self.precision("crel")),
              "cluster relation recall\t{:.2%}".format(self.recall("crel")),
              "cluster relation specificity\t{:.2%}".format(self.specificity("crel")),
              "cluster relation accuracy\t{:.2%}".format(self.accuracy("crel")),
              "cluster relation F1\t{:.2%}".format(self.f1("crel")),
              "cluster rel C\t{}".format(self.stats["crel"]["tp"]),
              "cluster rel I\t{}".format(self.stats["crel"]["fp"]),
              "cluster rel N\t{}".format(self.stats["crel"]["tn"]),
              "cluster rel M\t{}".format(self.stats["crel"]["fn"]),

              "relation C\t{}".format(self.stats["irel"]["tp"]),
              # TODO break this down into those which should have a derivation,
              #  but a different one, and those which should stay unconnected.
              "relation I\t{}".format(self.stats["irel"]["fp"]),
              "relation N\t{}".format(self.stats["irel"]["tn"]),
              "relation M\t{}".format(self.stats["irel"]["fn"]),
              "relation MD-M\t{}".format(self.stats["grel"]["fn"] - self.stats["irel"]["fn"]),
              sep="\n", end="\n")

        return lexicon

    @classmethod
    def parse_args(cls, args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        # TODO add ignore-compounding, ignore-pos etc.
        parser.add_argument("gold_standard", metavar="gold-standard", help="File with the gold-standard annotation")
        parser.add_argument("--ignore-pos", dest="ignore_pos", action="store_true", help="Do not take POS information into account when matching lexemes")
        parser.add_argument("--details", help="A file to which to store details of the correct and incorrect edges")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [args.gold_standard, args.ignore_pos], {"edge_details_file": args.details}, args.rest
