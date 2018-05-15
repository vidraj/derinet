import importlib
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

class Scenario:

    def __init__(self, modules):
        """Initialize a scenario using either a list of tuples – module specifiers, each containing a module name and a dictionary of its arguments.

        >>> modules = [("Load", {"file": "in.tsv"}), ("Save", {"format": "2", "file": "out.tsv"})]
        >>> Scenario(modules)    # doctest: +ELLIPSIS
        <scenario.Scenario object at 0x...>"""
        self.modules = modules

    def process(self, derinet=None):

        # Initialize all modules.
        modules = []
        for module_name, module_args in self.modules:
            # The file name is simply lowercased module name.
            module_file_name = module_name.lower()
            # The class name is the last component of the module name.
            class_name = module_name.split(".")[-1]

            arg_string = " ".join(["{}={}".format(k, v) for k, v in sorted(module_args.items())])
            logger.info('Initializing {}/{} {}.'.format(module_file_name, class_name, arg_string))

            # Import the module.
            mdl = 'derinet.modules.{}'.format(module_file_name)
            module = importlib.import_module(mdl)

            # Create an instance of its main class.
            module_class = getattr(module, class_name)
            module_instance = module_class(module_args)

            # Store the initialized module.
            modules.append(module_instance)

        logger.info('Initialization done.')

        # Run all instances.
        for instance in modules:
            derinet = instance.process(derinet)
            logger.info('Module {} processed.'.format(instance.signature))

        return derinet
