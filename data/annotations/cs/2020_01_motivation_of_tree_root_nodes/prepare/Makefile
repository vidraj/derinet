SHELL=/bin/bash

all: prepare

syn2015.gz:
	echo 'You need syn2015.gz corpus from Czech National Corpus Institution.'

# vytvoří seznam slov a jejich frekvencí
# freq \tab word \tab lemma \tab tag
freq-word-list.tsv: syn2015.gz
	zgrep -v '^<' 'syn2015.gz' | cut -d $$'\t' -f 1,2,3 | sort | uniq -c | sort -nr > 'freq-word-list.tsv'

# vytvoří seznamy DeriNetích kořenů zarovnaných
# dle frekvence lemmat z 'freq-word-list.tsv'
prepare: freq-word-list.tsv
	python3 'list-roots-by-freq.py' 'freq-word-list.tsv' '../../../../releases/cs/derinet-1-7.tsv' '-ex' > '../for-annotation/freq-roots-exclude-compounds.tsv'
	python3 'list-roots-by-freq.py' 'freq-word-list.tsv' '../../../../releases/cs/derinet-1-7.tsv' '-in' > '../for-annotation/freq-roots-include-compounds.tsv'

# vytvoří první sadu k anotaci (3k nejfrekventovanějších), ostatní sady vytvořeny ručně na základě seznamu 'freq-roots-include-compounds.tsv'
first_sample:
	cat '../for-annotation/freq-roots-exclude-compounds.tsv' | cut -f 2,3 | head -n 3000 > '../for-annotation/roots-exclude-3k.tsv'
	