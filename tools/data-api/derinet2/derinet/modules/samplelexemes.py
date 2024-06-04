from derinet import Block, Lexicon
import argparse
import bisect
import itertools
from random import Random
import sys

class SampleLexemes(Block):
    """
    Print a randomly selected sample (without replacement) of lexemes to
    a file, together with information about the main parent if available.

    The sample can be uniform or weighted by corpus frequency. Be aware
    that freq-weighted sampling never returns lexemes with weight 0.0,
    i.e. unattested lexemes are ignored when no lambda smoothing
    parameter is set.
    """

    def __init__(self, output, count, distribution, l=0.0, seed=None):
        self.output = output
        # Can be None, in which case the lexicon size should be used.
        #  That will be calculated at process() time.
        self.count = count
        self.distribution = distribution
        self.l = l
        self.seed = seed

    @staticmethod
    def corpus_count(lexeme):
        if "corpus_stats" in lexeme.misc:
            cs = lexeme.misc["corpus_stats"]
            if "absolute_count" in cs:
                return cs["absolute_count"]

        return 0

    @staticmethod
    def sample_lexemes_uniform(rng, lexicon, count):
        lexemes = list(lexicon.iter_lexemes(sort=True))
        if count is None:
            # Default count is len(lexemes), i.e. shuffle the whole
            #  dataset.
            rng.shuffle(lexemes)
            yield from lexemes
        else:
            yield from rng.sample(lexemes, k=count)

    @staticmethod
    def sample_lexemes_freq(rng, lexicon, count, l):
        # For efficiency, this methods works in batches:
        # 1. Generate a list of samples to return (with replacement).
        # 2. Sample using the list, making sure to return a lexeme at
        #    most once (without replacement).
        # 3. Because of the with-without replacement mismatch, if we
        #    happened to generate fewer than the requested amount of
        #    lexemes, remove the seen ones and try again.
        # Each iteration produces at least one element, so the loop
        #  surely terminates, but it avoids pathological behaviors with
        #  either removing elements after each sample or generating
        #  many redundant samples before finally hitting an unsampled
        #  lexeme.

        # Lexemes with zero weight are problematic and should be removed
        #  before sampling. Due to the bisect_left usage, the algorithm
        #  will never sample them until only zero-weighted lexemes
        #  remain in the lexicon, and then it will sample them one item
        #  at a time, alphabetically sorted. This is not what we want.
        # Two options: Forbid sampling them and report an error instead,
        #  or shuffle the list to output after all other lexemes have
        #  been processed first. Let's go with the former one.
        lexemes = []
        weights = []
        for lexeme in lexicon.iter_lexemes(sort=True):
            weight = SampleLexemes.corpus_count(lexeme) + l
            if weight <= 0.0:
                continue
            lexemes.append(lexeme)
            weights.append(weight)

        if count is None:
            count = len(lexemes)
        assert count <= len(lexemes), "Requested {} samples, but the lexicon only contains {} lexemes with nonzero weight".format(count, len(lexemes))

        seen_ids = set()
        sampled_lexeme_count = 0

        while sampled_lexeme_count < count:
            if seen_ids:
                # Not the first run – delete all previously seen items to
                #  prevent sampling the same items over and over again.
                lexemes = [lex for i, lex in enumerate(lexemes) if i not in seen_ids]
                weights = [w for i, w in enumerate(weights) if i not in seen_ids]

                # Reset the IDs, as they change meaning between runs.
                seen_ids = set()

            partial_sums = list(itertools.accumulate(weights))

            # Generate n+100 remaining points to sample. The 100 is
            #  there to prevent (costly) deletion of seen points if only
            #  a few extra points need to be generated.
            for i in range(count - sampled_lexeme_count + 100):
                point = rng.uniform(0.0, partial_sums[-1])
                sampled_id = bisect.bisect_left(partial_sums, point)

                # If there are multiple IDs at the 

                if sampled_id not in seen_ids:
                    seen_ids.add(sampled_id)
                    sampled_lexeme_count += 1

                    yield lexemes[sampled_id]

                    if sampled_lexeme_count == count:
                        break

    def process(self, lexicon: Lexicon):
        # TODO Allow drawing samples with replacement?
        # TODO Allow sampling whole trees / connected components in
        #  addition to lexemes?
        #  How would that work in combination w/ frequency? Sum up freqs across the tree, sample roots based on that? Or sample lexemes, and mark the whole tree as seen after a single lexeme from it is encountered?
        #    These are equivalent.

        rng = Random(self.seed)

        if self.distribution == "uniform":
            sample = self.sample_lexemes_uniform(rng, lexicon, self.count)
        elif self.distribution == "freq-weighted":
            sample = self.sample_lexemes_freq(rng, lexicon, self.count, self.l)
        else:
            raise ValueError("Unknown distribution type '{}'".format(self.distribution))

        for lexeme in sample:
            print(
                lexeme.lemma,
                lexeme.pos,
                lexeme.parent.lemma if lexeme.parent else "",
                lexeme.parent.pos if lexeme.parent else "",
                sep="\t",
                end="\n",
                file=self.output
            )

        return lexicon

    @staticmethod
    def parse_args(args):
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("--count", type=int, help="The number of lexemes to sample. Default: the lexicon size.")
        parser.add_argument("--distribution", choices={"uniform", "freq-weighted"}, default="uniform", help="The type of statistical distribution to use for sampling.")
        parser.add_argument("--lambda", type=float, default=0.0, dest="l", help="The add-lambda factor for smoothing the freq-weighted sampling distribution.")
        parser.add_argument("--seed", type=int, help="The seed for the random number generator.")
        parser.add_argument("output", type=argparse.FileType("wt", encoding="utf-8"), help="The file to write the output to.")
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        return [args.output, args.count, args.distribution], {"l": args.l, "seed": args.seed}, args.rest
