SHELL=/bin/bash

# KOMPLETNÍ RYCHLÉ SPUŠTĚNÍ

# provede vše: 	extrakci (extrahuje sémantické derivační vztahy)
# 				anotaci (zjistí, které vztahy jsou v DeriNetu a z nich
# 						 vytvoří anotační dávku)
all: ssjc-utf8.xml
	python3 'extract-semantic.py' 'ssjc-utf8.xml' > '../hand-annotated/potentials.tsv'
	# python3 'annotate-semantic.py' '../hand-annotated/potentials.tsv' '../../../../releases/cs/derinet-1-7.tsv' > '../hand-annotated/semantic-labels.tsv'
	# rm '../hand-annotated/potentials.tsv'

# vypíše vztahy s více sémantickými labely
multiple:
	python3 'multiple-labels.py' '../hand-annotated/potentials.tsv' > 'multiple-labeled.tsv'

# upozornění na vstupní data
ssjc-utf8.xml:
	@echo -e 'You need SSJČ .xml data.'
