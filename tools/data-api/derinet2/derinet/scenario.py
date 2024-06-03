from .lexicon import Lexicon
from .utils import DerinetError
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


class Scenario:
    __slots__ = [
        "_modules"
    ]

    def __init__(self, modules):
        """
        Initialize a scenario using a list of Blocks.

        :param modules: A list of tuples of (Block class, args, kwargs).
        """
        self._modules = modules

    def process(self, lexicon=None, *, keep_going=False):
        """
        Process the scenario by threading `lexicon` through the specified list
        of Blocks. Each Block is specified as a class to init and its arguments.

        :param lexicon: The lexicon to pass to the first Block.
        :param keep_going: If set, continue execution when a DerinetError is
                raised in a Block.
        :return: The lexicon, as returned by the last Block.
        """
        scenario = self._modules

        logger.info("Processing a scenario of {} modules.".format(len(scenario)))

        if lexicon is None:
            lexicon = Lexicon()

        # Run all instances.
        for i, (module_class, module_args, module_kwargs) in enumerate(scenario, start=1):
            signature = "{}/{}".format(module_class.__module__, module_class.__name__)

            # Set the arg_string and class_name (or even module_name) as a property of the lexicon.
            #  That way, we don't have to pass the signature to every derinet method manually,
            #  no-one forgets about it and it is all clean, without stack inspection and other nasty
            #  hacks.
            # lexicon.set_execution_context(instance.signature)

            # Create an instance of the main class.
            logger.info("Initializing {}".format(signature))
            instance = module_class(*module_args, **module_kwargs)

            logger.info("Running module {} ({}/{}).".format(instance.signature, i, len(scenario)))

            try:
                lexicon = instance.process(lexicon)
            except DerinetError as e:
                logger.error(e)
                if not keep_going:
                    raise

            logger.info('Module {} finished.'.format(instance.signature))

            if not lexicon:
                logger.warning("Module {} didn't return the lexicon".format(instance.signature))

        logger.info("Scenario processed.")

        return lexicon
