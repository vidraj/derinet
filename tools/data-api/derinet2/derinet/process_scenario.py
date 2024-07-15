#!/usr/bin/env python3

"""Process a derivational network using a scenario specified as individual args."""
import argparse
import importlib
import logging
import sys
from typing import Dict, List, Tuple, Type

from derinet.block import Block
from derinet.scenario import Scenario

import derinet.modules


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


def parse_args() -> Tuple[argparse.Namespace, List[str]]:
    """
    Parse the known arguments of the top-level program and get a list of other argument strings, to be used as
    the specification of a scenario.

    :return: A tuple of (main_args, rest_args).
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Get help for an individual module by passing `MODULE --help` as arguments.",
        allow_abbrev=False
        # TODO Enable fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "--data-version",
        help="Record the specified string into any changes made by the scenario's modules."
    )
    parser.add_argument(
        "--seed",
        type=int,
        help=("An integer random seed to set for repeatable experimenting. If omitted, is set randomly "
              "as per Python's default.")
    )
    parser.add_argument(
        "-k",
        "--keep-going",
        dest="keep_going",
        action="store_true",
        help="Continue the scenario after a module raises DerinetError."
    )
    parser.add_argument(
        "-l",
        "--list-modules",
        dest="list_modules",
        action="store_true",
        help="List all known invokable modules from `derinet.modules` and exit."
    )
    parser.add_argument(
        "--version",
        action="store_true"
    )
    parser.add_argument(
        "modules",
        nargs=argparse.REMAINDER,
        help=("A list of modules and their arguments. New modules must be placed into "
              "`derinet.modules` and its name specified without the `derinet.modules`, "
              "so e.g. `derinet.modules.Load` is specified as `Load`.")
    )

    main_args = parser.parse_args()
    rest_args = main_args.modules

    if main_args.version:
        import importlib.metadata
        try:
            v = importlib.metadata.version("derinet")
        except importlib.metadata.PackageNotFoundError:
            v = "development version"
        print("derinet", v)
        print("\nCopyright (C) 2024 Jonáš Vidra\n\n"
              "This program is free software: you can redistribute it and/or modify\n"
              "it under the terms of the GNU General Public License version 3 only,\n"
              "as published by the Free Software Foundation.\n\n"
              "This program is distributed in the hope that it will be useful,\n"
              "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
              "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
              "GNU General Public License for more details.\n\n"
              "You should have received a copy of the GNU General Public License\n"
              "along with this program.  If not, see <https://www.gnu.org/licenses/>.")
        sys.exit(0)

    return main_args, rest_args


def parse_first_module(args: List[str]) -> Tuple[Type[Block], List, Dict, List[str]]:
    """
    From the list of strings `args`, parse out the first module and its arguments and initialize it.

    :param args: A list of strings, the first being a module name, followed by its arguments, followed by other module specifications.
    :return: A tuple of (the loaded class of the module, args of the module, kwargs of the module, the unprocessed tail of the arguments).
    """
    module_name = args[0]
    args = args[1:]

    # The file name is simply lowercased module name.
    module_file_name = module_name.lower()
    # The class name is the last component of the module name.
    class_name = module_name.split(".")[-1]

    logger.info('Classloading {}/{}'.format(module_file_name, class_name))

    # Import the module.
    mdl = '.{}'.format(module_file_name)
    module = importlib.import_module(mdl, "derinet.modules")

    # Get the module's main class.
    module_class = getattr(module, class_name)
    assert issubclass(module_class, Block)

    # Let the module parse its arguments.
    module_args, module_kwargs, rest_args = module_class.parse_args(args)

    # Store the parsed module info.
    return module_class, module_args, module_kwargs, rest_args


def parse_modules(args: List[str]) -> List[Tuple[Type[Block], List, Dict]]:
    """
    Parse the whole list of args as a list of modules and their arguments, and initialize the modules.

    :param args: A list of modules and their arguments.
    :return: A list of tuples of (module classes, args, kwargs).
    """
    modules = []
    rest_args = args

    while rest_args:
        module, a, kwa, rest_args = parse_first_module(rest_args)
        modules.append((module, a, kwa))

    return modules


def list_modules(package_name: str) -> List[str]:
    """
    List all classes inheriting from Block found in package package_name.

    :param package_name: A string specifying the package to inspect.
    :return: A list of strings specifying the modules found in package_name, in the format expected by the classloader.
    """
    import inspect
    import pkgutil

    package = importlib.import_module(package_name)

    modules = []

    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + '.'):
        logger.info("Found submodule {} (is a {})".format(modname, "package" if ispkg else "module"))

        if not ispkg:
            # We've found a module. List its member classes that subclass Block.
            try:
                module = importlib.import_module(modname)
            except:
                logger.error("Couldn't load module {}:".format(modname), exc_info=True)
                continue

            class_members = inspect.getmembers(
                module,
                lambda obj: inspect.isclass(obj) and issubclass(obj, Block) and obj is not Block
            )

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
                else:
                    logger.warning("Class {} found in module {} is not loadable, as its class name "
                                   "doesn't match its module name.".format(class_name, cls.__module__))

    return modules


def main() -> int:
    """
    Run the scenario specified on the command line, or do whatever else depending on `sys.argv`.

    :return: A shell-compatible error code.
    """
    main_args, rest_args = parse_args()

    if main_args.list_modules:
        module_list = list_modules("derinet.modules")
        print("\n".join(module_list))
        return 0

    if main_args.seed is not None:
        import random
        random.seed(main_args.seed, version=2)

    modules = parse_modules(rest_args)

    scenario = Scenario(modules)
    scenario.process(keep_going=main_args.keep_going, version=main_args.data_version)

    return 0


if __name__ == '__main__':
    sys.exit(main())
