SHELL=/bin/bash

all: potential-conversion.tsv

potential-conversion.tsv:
	python3 find_conversion.py --DeriNet <(zcat ../../../../releases/cs/derinet-2-0.tsv.gz) \
							   --Output potential-conversion.tsv
