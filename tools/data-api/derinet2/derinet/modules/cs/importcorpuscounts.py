from derinet import Block, Lexicon
import argparse
import logging
import math


logger = logging.getLogger(__name__)


class ImportCorpusCounts(Block):
    """
    Add corpus counts into the misc section of lexemes.
    """

    def __init__(self, fname, corpus_size, counts_type="v4"):
        self.fname = fname
        self.corpus_size = corpus_size
        self.counts_type = counts_type

    def record_count(self, lexemes, count):
        if len(lexemes) > 1:
            logger.warning("Lexeme for '{} {}' ambiguous, filling the count to all of them".format(lexemes[0].lemma, lexemes[0].pos))

        for lexeme in lexemes:
            stats = lexeme.misc.setdefault("corpus_stats", {})

            if "absolute_count" in stats:
                logger.warning("Lexeme {} already has corpus count filled"
                                " with value {}, will add {}".format(
                    lexeme,
                    stats["absolute_count"],
                    count
                ))
                stats["absolute_count"] += count
            else:
                stats["absolute_count"] = count

    def gen_counts(self):
        """
        Generate parsed items from self.fname, returning the lemma, pos and
        integer count for each item.
        """
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 3
                lemma, pos, count = fields
                yield lemma, pos, int(count)

    def fill_counts_from_file(self, lexicon: Lexicon):
        """
        Read self.fname and record all counts found therein to the appropriate
        lexemes from lexicon as misc.corpus_stats.absolute_count. Return the sum
        of all processed counts.

        If a lemma-pos pair from the count file is ambiguous (the lemma has
        several homonymous lexemes), the same count is assigned to all of them,
        but only counted once towards the returned total.

        If a lemma-pos pair is not found in the lexicon, the count is added to
        the total anyway.

        Lexemes from lexicon not found in the file are untouched.
        """
        corpus_size = 0

        for lemma, pos, count in self.gen_counts():
            corpus_size += count

            lexemes = lexicon.get_lexemes(lemma, pos)

            if not lexemes:
                logger.info("Lexeme for '{} {}' not found".format(lemma, pos))
                continue

            self.record_count(lexemes, count)

        return corpus_size

    def gen_counts_v9(self):
        """
        Generate parsed items from self.fname, returning the lemma,
        sublemmma, tag and integer count for each item.
        """
        with open(self.fname, "rt", encoding="utf-8", newline="\n") as f:
            for line in f:
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 4
                lemma, sublemma, tag, count = fields
                yield lemma, sublemma, tag, int(count)

    def fill_counts_from_file_v9(self, lexicon: Lexicon):
        """
        Read self.fname and record all counts found therein to the appropriate
        lexemes from lexicon as misc.corpus_stats.absolute_count. Return the sum
        of all processed counts.

        This method assumes the input file is generated from SYN v9, with its
        lemma-sublemma distinction, and with the tag being expressed as a tag mask:

        být	bejt	Vf--------?-I-?	19228
        být	být	V???---??-??I-?	177834134

        The method uses two passes to write the counts: First, it adds all counts
        where the sublemma is different from the lemma, and then it sums the
        counts from unused sublemmas to the respective lemmas and stores that to
        the lemmas. This is done to avoid double-counting.

        If a lemma-pos pair from the count file is ambiguous (the lemma has
        several homonymous lexemes), the same count is assigned to all of them,
        but only counted once towards the returned total.

        If a lemma-pos pair is not found in the lexicon, the count is added to
        the total anyway.

        Lexemes from lexicon not found in the file are untouched.
        """
        corpus_size = 0

        lemma_proper_counts = {}

        for lemma, sublemma, tag_mask, count in self.gen_counts_v9():
            corpus_size += count

            pos = tag_mask[0]

            if sublemma != lemma:
                lexemes = lexicon.get_lexemes(sublemma, pos)
                if lexemes:
                    self.record_count(lexemes, count)
                else:
                    # The sublemma was not found. If the lemma proper is
                    #  present, record the sublemma's count there.
                    if lexicon.get_lexemes(lemma, pos):
                        key = (lemma, pos)
                        lemma_proper_counts[key] = lemma_proper_counts.get(key, 0) + count
            else:
                # The sublemma and lemma are identical. Just remember the
                #  count for now; we'll process it later, after counts
                #  from all unused sublemmas are added.
                if lexicon.get_lexemes(lemma, pos):
                    key = (lemma, pos)
                    lemma_proper_counts[key] = lemma_proper_counts.get(key, 0) + count

        for (lemma, pos), count in lemma_proper_counts.items():
            lexemes = lexicon.get_lexemes(lemma, pos)
            # We know that lexemes are nonempty, otherwise we wouldn't
            #  have remembered this count.
            self.record_count(lexemes, count)

        return corpus_size

    def init_default_counts(self, lexicon: Lexicon):
        """
        Initialize the misc.corpus_stats.absolute_count of lexemes which don't have
        the key yet to 0.
        """
        for lexeme in lexicon.iter_lexemes():
            lexeme.misc.setdefault("corpus_stats", {}).setdefault("absolute_count", 0)

    def add_relative_frequency(self, lexicon, corpus_size):
        """
        Initialize the misc.corpus_stats.relative_frequency using the
        absolute_count of the lexeme and provided corpus_size.
        """
        for lexeme in lexicon.iter_lexemes():
            stats = lexeme.misc["corpus_stats"]
            stats["relative_frequency"] = stats["absolute_count"] / corpus_size

    def add_sparsity(self, lexicon, corpus_size):
        """
        Add the "sparsity", defined as the negative log_10 of relative frequency,
        to each lexeme.
        """
        for lexeme in lexicon.iter_lexemes():
            stats = lexeme.misc["corpus_stats"]
            rf = stats["relative_frequency"]
            if rf > 0:
                stats["sparsity"] = - math.log10(rf)
            else:
                # For OOV words, we perform fake `add-1 smoothing`. Fake,
                #  because the 1 is not added to any other lexeme nor to the
                #  corpus size.
                stats["sparsity"] = - math.log10(1/corpus_size)

    def add_percentile(self, lexicon):
        """
        Add the percentile to each lexeme. Lexemes with identical absolute
        frequency get assigned identical percentile value.
        """
        lexemes = list(lexicon.iter_lexemes(sort=False))
        lexemes.sort(key=lambda l: l.misc["corpus_stats"]["absolute_count"])

        denom = len(lexemes)
        current_count = 0
        current_percentile = 0.0
        for i, lexeme in enumerate(lexemes):
            count = lexeme.misc["corpus_stats"]["absolute_count"]
            if count > current_count:
                current_count = count
                current_percentile = 100.0 * i / denom
            lexeme.misc["corpus_stats"]["percentile"] = current_percentile


    def process(self, lexicon: Lexicon):
        # Fill in the absolute counts.
        if self.counts_type == "v4":
            corpus_size = self.fill_counts_from_file(lexicon)
        elif self.counts_type == "v9":
            corpus_size = self.fill_counts_from_file_v9(lexicon)
        else:
            raise ValueError("Unknown counts corpus file format '{}'".format(self.counts_type))

        self.init_default_counts(lexicon)

        # If the user provided the total corpus size (because they want to
        #  include words that are not in the lexicon), use that.
        if self.corpus_size is not None:
            corpus_size = self.corpus_size

        # Add the derived scores.
        # FIXME do we want to use the total corpus size or the processed count
        #  as the denominator there?
        self.add_relative_frequency(lexicon, corpus_size)
        self.add_sparsity(lexicon, corpus_size)
        self.add_percentile(lexicon)
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

        parser.add_argument("--corpus-size", type=int, metavar="COUNT",
                            help="The total token count of the corpus, to be"
                            " used as the denominator in the relative sizes."
                            " If not provided, use the sum of seen counts from"
                            " the corpus file.")
        parser.add_argument("--counts-type", choices={"v4", "v9"}, default="v4",
                            help="The type of the counts input file: v4 is a TSV file"
                                 " with lemma, pos and count; v9 is a TSV file with"
                                 " lemma, sublemma, 15-position morphological tag and"
                                 " count.")
        parser.add_argument("file", help="The file to load the corpus counts from,"
                                         " in a `lemma TAB pos TAB count` format."
                                         " In case of homonyms, the same count is"
                                         " added to all of them.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file
        corpus_size = args.corpus_size

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname, corpus_size], {"counts_type": args.counts_type}, args.rest
