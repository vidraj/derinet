SHELL=/bin/bash

DERINET='../../../../releases/cs/derinet-1-7.tsv'

# provede jednotlivé kroky
data: SSJC MORFFLEXCZ PMC Multiple  # následně manuální anotace (zejména PMC) a opravy v extrahovaných datech

preprocess: MergeAnnotations


# EXTRAKCE A ANOTACE DAT

# extrahuje sémantické labely ze SSJČ a automaticky je anotuje
SSJC: ../for-annotation/semantic-labels-ssjc.tsv
	@echo 'Extraction and annotation from SSJC complete. See file: ../for-annotation/semantic-labels-ssjc.tsv'

../for-annotation/semantic-labels-ssjc.tsv: ssjc-utf8.xml
	python3 'extract-ssjc.py' 'ssjc-utf8.xml' > '../for-annotation/potentials-ssjc.tsv'
	python3 'annotate.py' '../for-annotation/potentials-ssjc.tsv' $(DERINET) > '../for-annotation/semantic-labels-ssjc.tsv'
	rm '../for-annotation/potentials-ssjc.tsv'

ssjc-utf8.xml:
	@echo -e 'You need SSJČ .xml data.'


# extrahuje sémantické labely z MorfFlexu a automaticky je anotuje
MORFFLEXCZ: ../for-annotation/semantic-labels-morfflex.tsv
	@echo 'Extraction and annotation from MorfFlexCZ completed. See file: ../for-annotation/semantic-labels-morfflex.tsv'

../for-annotation/semantic-labels-morfflex.tsv:
	cat $(DERINET) | grep -e '\^DI' | cut -d $$'\t' -f 2,3,4 > '../for-annotation/deminutives.tsv'
	cat $(DERINET) | grep -e '\^FC' | cut -d $$'\t' -f 2,3,4 > '../for-annotation/feminines.tsv'
	cat $(DERINET) | grep -e '\^FM' | cut -d $$'\t' -f 2,3,4 > '../for-annotation/feminines-posesives.tsv'
	python3 'extract-morfflex.py' '../for-annotation/deminutives.tsv' '../for-annotation/feminines.tsv' '../for-annotation/feminines-posesives.tsv' > '../for-annotation/potentials-morfflex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-morfflex.tsv' $(DERINET) > '../for-annotation/semantic-labels-morfflex.tsv'
	rm '../for-annotation/deminutives.tsv' '../for-annotation/feminines.tsv' '../for-annotation/feminines-posesives.tsv' '../for-annotation/potentials-morfflex.tsv'


# extrahuje potenciální vztahy z DeriNetu na základě Příruční mluvnice češtiny
PMC: ../for-annotation/semantic-labels-pmc.tsv
	@echo 'Extraction and annotation from PCM completed. See file: ../for-annotation/semantic-labels-pcm.tsv'

AFFIXES1Adem = '[^(ič)]ičký\t' 'oučký\t' '[^(oul)]inký\t' 'ounký\t' 'ičičký\t' 'ilinký\t' 'oulinký\t' 'ouninký\t' 'inkatý\t'
AFFIXES1Vdem = '[^(in)]kat\t' 'inkat\t'
AFFIXES1Ddem = 'čko\t' 'nko\t'
AFFIXES1Apos = 'ův\t' 'in\t' 'čí\t' 'ovský\t'
../for-annotation/semantic-labels-pmc.tsv:
	for line in $(AFFIXES1Adem); do \
		grep -P $$line $(DERINET) | grep -e $$'\tA\t' | grep -e $$'\t[0-9]' | sort -R | head -n 500 >> '../for-annotation/deminutives-adj-1.tsv'; \
	done
	for line in $(AFFIXES1Vdem); do \
		grep -P $$line $(DERINET) | grep -e $$'\tV\t' | grep -e $$'\t[0-9]' | sort -R | head -n 500 >> '../for-annotation/deminutives-verb-1.tsv'; \
	done
	for line in $(AFFIXES1Ddem); do \
		grep -P $$line $(DERINET) | grep -e $$'\tD\t' | grep -e $$'\t[0-9]' | sort -R | head -n 500 >> '../for-annotation/deminutives-adv-1.tsv'; \
	done
	for line in $(AFFIXES1Apos); do \
		grep -P $$line $(DERINET) | grep -e $$'\tA\t' | grep -e $$'\t[0-9]' | sort -R | head -n 500 >> '../for-annotation/posesives-adj-1.tsv'; \
	done
	cat '../for-annotation/deminutives-adj-1.tsv' | sort | uniq > '../for-annotation/deminutives-adj.tsv'
	cat '../for-annotation/deminutives-verb-1.tsv' | sort | uniq > '../for-annotation/deminutives-verb.tsv'
	cat '../for-annotation/deminutives-adv-1.tsv' | sort | uniq > '../for-annotation/deminutives-adv.tsv'
	cat '../for-annotation/posesives-adj-1.tsv' | sort | uniq > '../for-annotation/posesives-adj.tsv'
	python3 'extract-pmc.py' $(DERINET) '../for-annotation/deminutives-adj.tsv' '../for-annotation/deminutives-verb.tsv' '../for-annotation/deminutives-adv.tsv' '../for-annotation/posesives-adj.tsv' > '../for-annotation/semantic-labels-pmc.tsv'
	rm '../for-annotation/deminutives-adj.tsv' '../for-annotation/deminutives-verb.tsv' '../for-annotation/deminutives-adv.tsv' '../for-annotation/posesives-adj.tsv'
	rm '../for-annotation/deminutives-adj-1.tsv' '../for-annotation/deminutives-verb-1.tsv' '../for-annotation/deminutives-adv-1.tsv' '../for-annotation/posesives-adj-1.tsv'


# vypíše vztahy s více sémantickými labely
Multiple: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-ssjc.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-morfflex.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-pmc.tsv'


# PREPROCESING DAT

# sloučí anotace všech souborů
MergeAnnotations: ../hand-annotated/semnatic-labels.tsv
	@echo 'Merging of annotated files completed. See file: ../hand-annotated/semnatic-labels.tsv'

../hand-annotated/semnatic-labels.tsv: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | grep $$'^\%' >> '../hand-annotated/semnatic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | grep $$'^\%' >> '../hand-annotated/semnatic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | grep $$'^\%' >> '../hand-annotated/semnatic-labels-1.tsv'
	cat '../hand-annotated/semnatic-labels-1.tsv' | sort | uniq > '../hand-annotated/semnatic-labels.tsv'
	rm '../hand-annotated/semnatic-labels-1.tsv'


# restrukturalizuje dosavadní a přidá nové příznaky do dat
AddFeatures: ../hand-annotated/MLdata-semnatic-labels.tsv
	@echo 'Adding of features completed. See file: ../hand-annotated/MLdata-semnatic-labels.tsv'

../hand-annotated/MLdata-semnatic-labels.tsv: ../hand-annotated/semnatic-labels.tsv word-list.tsv
	python3 'add-features.py' '../hand-annotated/semnatic-labels.tsv' 'word-list.tsv' > '../hand-annotated/MLdata-semnatic-labels.tsv'
	# rm 'word-list.tsv'

word-list.tsv: syn2015.gz
	zgrep -v '^<' 'syn2015.gz' | cut -d $$'\t' -f 1,2,3 | sort | uniq -c | sort -nr > 'word-list.tsv'

syn2015.gz:
	echo 'You need syn2015.gz corpus from Czech National Corpus Institution.'
