#!/usr/bin/env python3

import sys

from derinet import DeriNet
from derinet.scenario import Scenario

if __name__ == '__main__':
    derinet = DeriNet('data/derinet-1-4.tsv')
    scenario = Scenario(sys.argv[1])
    scenario.process(derinet)