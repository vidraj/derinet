from derinet import Block, Format, Lexicon
import argparse
import re
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class GuessCompoundParents(Block):
    def __init__(self, fname):
        # The arguments to __init__ are those that the parse_args method (below) returns.
        self.fname = fname
        self.min_length_first = 3
        self.min_length_second = 3

    def process(self, lexicon: Lexicon):
        """
        Example processing method. Assumes that the opened file contains a list of morphs separated by spaces on each line.
        """

        cutting_regex = re.compile(r"^([^o]+)o([^o]+)$") # FIXME this doesn't iterate over the possibilities!
        with open(self.fname, "wt", encoding="utf-8", newline="\n") as out_file:
            for lexeme in lexicon.iter_lexemes():
                if "is_compound" in lexeme.misc and lexeme.misc["is_compound"] and not lexeme.parent:
                    candidates = []

                    # Najít všechny výskyty "o".
                    for match in cutting_regex.finditer(lexeme.lemma):
                        # Na tom místě to rozseknout.
                        first_part, second_part = match.groups()

                        # logger.debug("Looking at lexeme {} as {}/{}".format(lexeme, first_part, second_part))

                        if len(first_part) < self.min_length_first or len(second_part) < self.min_length_second:
                            continue

                        # Najít obě věci.
                        second_lexemes = lexicon.get_lexemes(second_part, pos=lexeme.pos)
                        if not second_lexemes:
                            # Ta druhá musí existovat.
                            # logger.debug("Second part {} {} not found".format(second_part, lexeme.pos))
                            continue

                        # Ta první může být trochu jiná. Zkusit přidat nic, "y", "i" nebo "o".
                        first_parts = [first_part, first_part + "ý", first_part + "í", first_part + "i", first_part + "o", first_part + "y", first_part + "a"]
                        first_parts += [part[0].upper() + part[1:] for part in first_parts]

                        for first_part in first_parts:
                            first_lexemes = lexicon.get_lexemes(first_part)
                            for first_lexeme in first_lexemes:
                                for second_lexeme in second_lexemes:
                                    # logger.info("For {} found {} and {}".format(lexeme, first_lexemes, second_lexemes))
                                    candidates.append((lexeme, first_lexeme, second_lexeme))

                    if len(candidates) == 1:
                        for lexeme, first, second in candidates:
                            if first.lemma[0].isupper():
                                # Ignore all the named entities. They are mostly wrong.
                                continue
                            print(lexeme, first, second, sep="\t", file=out_file)

        return lexicon

    def parse_args(args):
        """Parse a list of strings containing the arguments, pick the relevant
        ones from the beginning and leave the rest be. Return the parsed args
        to this module and the unprocessed rest."""
        parser = argparse.ArgumentParser(
            prog=__class__.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("file", help="The file to save the found parents to.")
        # argparse.REMAINDER tells argparse not to be eager and to process only the start of the args.
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        fname = args.file

        # Return *args to __init__, **kwargs to init and the unprocessed tail of arguments to other modules.
        return [fname], {}, args.rest
