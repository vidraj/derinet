from derinet.utils import DeriNetError
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class Block:
    def __init__(self, args):
        self.args = args

    def process(self, derinet):
        for lexeme in derinet.iter_lexemes():
            try:
                self.process_lexeme(lexeme)
            except DeriNetError as e:
                logger.error(e)

        return derinet

    def process_lexeme(self, lexeme):
        raise NotImplementedError("process_lexeme method has to be implemented")

    @property
    def signature(self):
        # TODO use self.__class__.__name__ or similar, together with a printout of args.
        # TODO how to print args when subclasses can redefine __init__ and not save them?
        return self.__str__()
