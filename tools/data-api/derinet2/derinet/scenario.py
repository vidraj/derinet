import importlib
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class Scenario:

    def __init__(self, fname):
        self.fname = fname
        self.modules = []
        self._parse(fname)

    def _parse(self, fname):
        with open(fname, "r") as f:
            for line in f.readlines():
                line = line.split()
                self.modules.append((line[0], line[1]))

    def process(self, derinet):
        for module_name, module_cls in self.modules:
            logger.info('processing: {}.{}'.format(module_name, module_cls))
            mdl = 'derinet.modules.{}'.format(module_name)
            module = importlib.import_module(mdl)
            class_ = getattr(module, module_cls)
            instance = class_(derinet)
            logger.info(instance.signature)
            instance.process()
            logger.info('Module processed.')
