from derinet import Block, Lexicon
import argparse
import sys
from typing import Any, Dict, Optional

class RemoveMiscKeys(Block):
    """
    Modify information available in the `misc` part of each lexeme,
    removing values of keys given as arguments. The intended use is to
    sanitize information that is meant for internal debugging purposes
    only.
    """

    def __init__(self, keys):
        self.keys = keys

    def process(self, lexicon: Lexicon):
        for lexeme in lexicon.iter_lexemes(sort=False):
            for keylist in self.keys:
                d: Optional[Dict[str, Any]] = lexeme.misc
                for key in keylist[:-1]:
                    if d is None:
                        break
                    d = d.get(key)
                if d is None:
                    # The keylist is not present in the lexeme.
                    break
                if keylist[-1] in d:
                    del d[keylist[-1]]

        return lexicon

    @classmethod
    def parse_args(cls, args):
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("-k", "--key", required=True, action="append", help="The key to remove from misc. If the key is to be removed from a nested dict, provide a slash-separated path. Can be specified multiple times.")
        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        args = parser.parse_args(args)

        keys = [key.split("/") for key in args.key]

        return [keys], {}, args.rest
