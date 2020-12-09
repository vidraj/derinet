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



# POSTROCESSING: 'make extract-information'

# převést .ods na .tsv    TODO: s postupující anotací v souboru 6-20k posunovat hranici "head -n X" !!! (safe n=10003; new n=13741)
ods2csv:
	soffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 ../hand-annotated/revised-by-ZZ/merged-sorted-0001-6000.ods
	soffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 ../hand-annotated/revised-by-ZZ/sorted-roots-6001-20000.ods
	cat merged-sorted-0001-6000.csv | tail -n +3 > data-0001-6000.csv
	cat sorted-roots-6001-20000.csv > data-6001-20000.csv
	rm merged-sorted-0001-6000.csv sorted-roots-6001-20000.csv

# extrahuje:
# (1) derivační vztahy k doplnění
# (2) značku nemotivovanosti
# (3) značku kompozitnosti
# (4) kompozitní vztahy k doplnění
extract-information: ods2csv
	python3 postprocessing.py <(cat data-*.csv) ../hand-annotated/into-derinet/derivations.tsv \
												../hand-annotated/into-derinet/compounding.tsv \
												../hand-annotated/into-derinet/compound-labels.tsv \
												../hand-annotated/into-derinet/unmotivatedness-labels.tsv \
												../hand-annotated/into-derinet/variants.tsv > for-postprocessing.tsv
