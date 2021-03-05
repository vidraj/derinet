from derinet import Block, Lexicon
import argparse
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class PrintStatsOfUnattested(Block):
    """
    Find all unattested lexemes and print their statistics.

    This module is best accompanied by a LibreOffice spreadsheet which
    calculates derived values -- see /tools/misc/stats-of-unattested.ods

    Import the computed data to that spreadsheet, amend the ranges of
    the pivot tables and you have the stats.
    """

    def get_by_count(self, root, f):
        """
        Return a list of all lexemes in subtree of `root` if function
        `f` applied to the absolute count of the lexeme returns true.
        """
        result = [lex for lex in root.iter_subtree() if f(lex.misc["corpus_stats"]["absolute_count"])]
        return result

    def find_deepest_leaf_depth(self, lexeme):
        """
        Return the depth of the deepest leaf in the subtree of `lexeme`.
        """
        return 1 + max([self.find_deepest_leaf_depth(child) for child in lexeme.children], default=0)

    def calculate_depth(self, lexeme):
        """
        Find how many lexemes we have to visit in order to reach the
        main root of this lexeme. Roots have depth 1.
        """
        depth = 1
        while lexeme.parent:
            depth += 1
            lexeme = lexeme.parent
        return depth

    def process(self, lexicon: Lexicon):
        """
        Print statistics for individual lexemes.
        """
        # Print the header.
        print("Lemma",
              "POS",
              "Corpus count",
              # Immediate children.
              "Attested children count",
              "Unattested children count",
              # Everything in the subtree of main relations, including
              #  this lexeme.
              "Attested sublexeme count",
              "Unattested sublexeme count",
              # Root is at depth 1.
              "Depth",
              "Max subtree depth",
              sep="\t",
              end="\n")

        # Go over the lexicon and print stats for lexemes.
        for lexeme in lexicon.iter_lexemes(sort=False):
            print(lexeme.lemma,
                  lexeme.pos,
                  lexeme.misc["corpus_stats"]["absolute_count"],
                  len([child for child in lexeme.children if child.misc["corpus_stats"]["absolute_count"] > 0]),
                  len([child for child in lexeme.children if child.misc["corpus_stats"]["absolute_count"] == 0]),
                  len(self.get_by_count(lexeme, lambda c: c > 0)),
                  len(self.get_by_count(lexeme, lambda c: c == 0)),
                  self.calculate_depth(lexeme),
                  self.find_deepest_leaf_depth(lexeme),
                  sep="\t",
                  end="\n")

        return lexicon
