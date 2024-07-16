import importlib
import inspect
import logging
import pkgutil
import sys
from typing import List, Tuple

from derinet.block import Block
from derinet.process_scenario import classload_module


logger = logging.getLogger(__name__)


def list_modules(package_name: str) -> Tuple[List[str], int]:
    """
    List all classes inheriting from Block found in package package_name.

    :param package_name: A string specifying the package to inspect.
    :return: A list of strings specifying the modules found in package_name, in the format expected by the classloader.
    """

    package = importlib.import_module(package_name)

    modules = []
    errors = 0

    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + '.'):
        #logger.info("Found submodule {} (is a {})".format(modname, "package" if ispkg else "module"))

        if not ispkg:
            # We've found a module. List its member classes that subclass Block.
            try:
                module = importlib.import_module(modname)
            except:
                logger.error("Couldn't load module {}:".format(modname), exc_info=True)
                errors += 1
                continue

            class_members = inspect.getmembers(
                module,
                lambda obj: inspect.isclass(obj) and issubclass(obj, Block) and obj is not Block
            )

            has_appropriate_class = False
            for name, cls in class_members:
                # The fact that we've found a suitable class in a suitable file doesn't mean that the class is loadable.
                # If the file name doesn't match the class name, our module loader won't find it.
                # Check whether that's the case and if so, print a warning.
                class_name = cls.__name__
                expected_module_last_name = class_name.lower()
                class_path = cls.__module__
                if class_path.startswith(package_name):
                    # Remove the known package prefix, as currently (early 2020) the user can't use
                    #  the full name to load modules; only modules from `derinet.modules` are usable.
                    class_path = class_path[len(package_name) + 1:]
                else:
                    logger.error("Module {} is not within the expected package {}".format(class_path, package_name))
                    continue
                class_path_list = class_path.split(".")

                if class_path_list[-1] == expected_module_last_name:
                    # All is well, the class should be loadable. Print the specification used to load it.
                    # This means we have to strip the last component of the module name, as it must be merely
                    #  the lowercased variant of the class name.
                    module_specifier = ".".join(class_path_list[:-1] + [class_name])

                    modules.append(module_specifier)
                    has_appropriate_class = True
                else:
                    logger.warning("Class {} found in module {} is not loadable, as its class name "
                                   "doesn't match its module name.".format(class_name, cls.__module__))

            if not has_appropriate_class:
                errors += 1

    return modules, errors


def main() -> int:
    modules, errors = list_modules("derinet.modules")
    for module in modules:
        classload_module(module)

    return 1 if errors else 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')
    sys.exit(main())
