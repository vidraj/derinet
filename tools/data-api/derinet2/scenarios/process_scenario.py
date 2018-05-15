#!/usr/bin/env python3

import sys
import logging

from derinet.scenario import Scenario


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    modules = []

    # The first argument must always specify the first module to load.
    # TODO allow for loading the module list from a file.
    current_module = (sys.argv[1], {})
    for arg in sys.argv[2:]:
        if "=" in arg:
            # The arg is a parameter to a module.
            param_name, param_value = arg.split("=", 1)
            if param_name in current_module[1]:
                logger.error("Parameter '%s' to module '%s' specified twice, with values '%s' and '%s'.", param_name, current_module[0], current_module[1][param_name], param_value)
                #raise ValueError("Parameter '{}' to module '{}' specified twice, with values '{}' and '{}'.".format(param_name, current_module[0], current_module[1][param_name], param_value))
                sys.exit(1)
            else:
                current_module[1][param_name] = param_value
        else:
            # The arg is a module name.
            # Store the module and parameters of the previous one.
            modules.append(current_module)
            # Store the name of the new module and start parsing its parameters.
            current_module = (arg, {})
    # Store the module that was processed last.
    modules.append(current_module)

    scenario = Scenario(modules)
    scenario.process()
