#!/usr/bin/env python3

import sys

from derinet import DeriNet
from derinet.scenario import Scenario

if __name__ == '__main__':
    derinet = DeriNet(sys.argv[1])
    scenario = Scenario(sys.argv[2])
    scenario.process(derinet)
