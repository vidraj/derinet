import argparse
import logging
from abc import ABC, abstractmethod

from .lexicon import Lexicon


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class Block(ABC):
    """
    The class all derinet block should inherit from. Due to the classloading mechanism we use, its lowercased name
    must be identical to the file name it resides in (without the .py extension).
    """
    @abstractmethod
    def process(self, lexicon: Lexicon) -> Lexicon:
        return lexicon

    @classmethod
    def parse_args(cls, args):
        """
        Parse the known args from the start of `args` and return them as a list and a dict together with the
        unprocessed tail of args. The list and dict returned from this method will be passed as args and kwargs
        to the block constructor later, while the unprocessed tail will be parsed for further blocks.

        Make sure to never eat more args than you need. In particular, never include an unbounded number
        of positional parameters in your parser. Also, be careful with optional parameters and make sure that
        a module name cannot be mistaken for an optional argument to your block.

        The easiest way of parsing is to use argparse and add a `rest` parameter to the list of positional parameters
        with `nargs=argparse.REMAINDER` and return that.

        :param args: The list of args from which to parse its start.
        :return: A tuple of (parsed args, parsed kwargs, unprocessed tail of args)
        """
        parser = argparse.ArgumentParser(
            prog=cls.__name__,
            description="This module takes no arguments."
        )

        parser.add_argument("rest", nargs=argparse.REMAINDER, help="A list of other modules and their arguments.")

        parsed_args = parser.parse_args(args)

        return [], {}, parsed_args.rest

    @property
    def signature(self):
        return "{}/{}".format(self.__module__, self.__class__.__name__)
