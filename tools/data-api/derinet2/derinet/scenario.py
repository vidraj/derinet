import logging
from typing import Dict, List, Optional, Tuple, Type

from .block import Block
from .lexicon import Lexicon
from .utils import DerinetError


logger = logging.getLogger(__name__)


class Scenario:
    __slots__ = [
        "_modules"
    ]

    modules: List[Tuple[Type[Block], List, Dict]]

    def __init__(self, modules: List[Tuple[Type[Block], List, Dict]]) -> None:
        """
        Initialize a scenario using a list of Blocks.

        :param modules: A list of tuples of (Block class, args, kwargs).
        """
        self._modules = modules

    def process(self, lexicon: Optional[Lexicon] = None, *, keep_going: bool = False, version: Optional[str] = None) -> Lexicon:
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
            lexicon = Lexicon(record_changes=True)

        if version is not None:
            lexicon.set_execution_context(version=version)

        # Run all instances.
        for i, (module_class, module_args, module_kwargs) in enumerate(scenario, start=1):
            signature = "{}/{}".format(module_class.__module__, module_class.__name__)

            # Set the module name and its args as a property of the lexicon,
            #  so that any relation changes the module makes get attributed
            #  to it automatically.
            lexicon.set_execution_context(creator=signature, args=repr(module_args), kwargs=repr(module_kwargs))

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
