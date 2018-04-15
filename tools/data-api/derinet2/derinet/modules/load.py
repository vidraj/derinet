from derinet.modules.block import Block
from derinet import DeriNet

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class Load(Block):
    def __init__(self, args):
        if "file" not in args:
            raise ValueError("Argument 'file' must be supplied.")
        else:
            self.fname = args["file"]

            # We'll pass the other arguments to the DeriNet constructor.
            #  Therefore, delete 'file' as it is passed separately as 'fname'.
            del args["file"]

            self.args = args

    def process(self, derinet):
        if derinet is not None:
            logger.warning("You are throwing the previous database away by loading a new one from '{}'.".format(self.fname))

        derinet = DeriNet(fname=self.fname, **self.args)
        return derinet
