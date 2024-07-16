from derinet import Block, Lexicon
import sys
import argparse
import logging


logger = logging.getLogger(__name__)


class PrintParents(Block):
    """
    For each lemma and POS in file, find its lexeme and print a comma-delimited
    list of its parent lemmas, comma-delimited list of their POSes and
    a comma-delimited list of the cluster roots reachable from it.
    Both files are tab-separated.
    """

    def __init__(self, fname, output=None):
        self.fname = fname

        if output is None:
            self.output = sys.stdout
            self.close_out_at_end = False
        else:
            self.output = open(output, mode="wt", encoding="utf-8", newline="\n")
            self.close_out_at_end = True

    def process(self, lexicon: Lexicon):
        corpus_total = 0

        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for lineno, line in enumerate(f):
                line = line.rstrip("\n")
                fields = line.split("\t")
                assert len(fields) == 2, "Lemma or POS is missing on line {}: '{}'".format(lineno, line)
                lemma, pos = fields

                lexemes = lexicon.get_lexemes(lemma, pos)

                if not lexemes:
                    logger.warning("Lexeme for '{} {}' not found".format(lemma, pos))
                    # FIXME maybe also output something? "ROOT"?
                    #  Currently it prints nothing in columns 3-6.

                if len(lexemes) > 1:
                    logger.info("Lexeme for '{} {}' ambiguous, printing parents of all of them".format(lemma, pos))

                parents = []
                roots = []
                # Get all parents and the main tree root for all lexemes in the list.
                # Also, convert the parents and roots from a list of lexemes to
                #  a list of lemma-pos tuples. We need this for the uniquing.
                for lexeme in lexemes:
                    lpar = lexeme.all_parents
                    if not lpar:
                        lpar = [("ROOT", None)]
                        lroot = ("ROOT", None)
                    else:
                        lpar = [(p.lemma, p.pos) for p in lpar]
                        tree_root = lexeme.get_tree_root()
                        lroot = (tree_root.lemma, tree_root.pos)

                    parents.extend(lpar)
                    roots.append(lroot)

                # Remove duplicates from the lists.
                parent_set = set(parents)
                root_set = set(roots)
                parents = sorted(parent_set)
                roots = sorted(root_set)

                # Create separate lists of lemmas and poses from the tuples.
                parent_lemmas = [record[0] for record in parents]
                parent_poses = [record[1] if record[1] is not None else "" for record in parents]
                root_lemmas = [record[0] for record in roots]
                root_poses = [record[1] if record[1] is not None else "" for record in roots]

                print(
                    lemma,
                    pos,
                    ",".join(parent_lemmas),
                    ",".join(parent_poses),
                    ",".join(root_lemmas),
                    ",".join(root_poses),
                    sep="\t",
                    end="\n",
                    file=self.output
                )

        if self.close_out_at_end:
            self.output.close()

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

        parser.add_argument("-o", "--output", help="Where to store the results."
                                                  "If unspecified, prints to STDOUT.")
        parser.add_argument("file", help="The file to load the lemmas from."
                                         "In case of homonyms, all options are listed.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file
        output = args.output

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {"output": output}, args.rest
