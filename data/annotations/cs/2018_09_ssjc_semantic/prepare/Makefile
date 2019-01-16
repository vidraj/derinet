SHELL=/bin/bash

DERINET='../../../../releases/cs/derinet-1-7.tsv'

# provede jednotlivé kroky (příprava dat, manuální! anotace, preprocessing)
data: SSJC MORFFLEXCZ PMC Multiple
preprocess: MergeAnnotations AddFeatures


# EXTRAKCE A ANOTACE DAT

# extrahuje sémantické labely ze SSJČ a automaticky je anotuje
SSJC: ../for-annotation/semantic-labels-ssjc.tsv
	@echo 'Extraction and annotation from SSJC complete. See file: ../for-annotation/semantic-labels-ssjc.tsv'

../for-annotation/semantic-labels-ssjc.tsv: ssjc-utf8.xml
	python3 'extract-ssjc.py' 'ssjc-utf8.xml' $(DERINET) > '../for-annotation/potentials-ssjc.tsv'
	python3 'annotate.py' '../for-annotation/potentials-ssjc.tsv' $(DERINET) > '../for-annotation/semantic-labels-ssjc.tsv'
	rm '../for-annotation/potentials-ssjc.tsv'

ssjc-utf8.xml:
	@echo -e 'You need SSJČ .xml data.'


# extrahuje sémantické labely z MorfFlexu a automaticky je anotuje
MORFFLEXCZ: ../for-annotation/semantic-labels-morfflex.tsv
	@echo 'Extraction and annotation from MorfFlexCZ completed. See file: ../for-annotation/semantic-labels-morfflex.tsv'

../for-annotation/semantic-labels-morfflex.tsv:
	python3 'extract-morfflex.py' $(DERINET) > '../for-annotation/potentials-morfflex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-morfflex.tsv' $(DERINET) > '../for-annotation/semantic-labels-morfflex.tsv'
	rm '../for-annotation/potentials-morfflex.tsv'


# extrahuje potenciální vztahy z DeriNetu na základě Příruční mluvnice češtiny (nutná manuální anotace)
PMC: ../for-annotation/semantic-labels-pmc.tsv
	@echo 'Extraction and annotation from PMC completed. See file: ../for-annotation/semantic-labels-pcm.tsv'

../for-annotation/semantic-labels-pmc.tsv:
	python3 'extract-pmc.py' $(DERINET) > '../for-annotation/semantic-labels-pmc.tsv'


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
	# přidat kontrolu více sémantických labelů
	# poznámky v jednotlivých souborech (někde mizí samy?)


# restrukturalizuje dosavadní a přidá nové příznaky do dat
AddFeatures: ../hand-annotated/MLdata-semnatic-labels.tsv
	@echo 'Adding of features completed. See file: ../hand-annotated/MLdata-semnatic-labels.tsv'

../hand-annotated/MLdata-semnatic-labels.tsv: ../hand-annotated/semnatic-labels.tsv word-list.tsv
	python3 'add-features.py' '../hand-annotated/semnatic-labels.tsv' 'word-list.tsv' > '../hand-annotated/MLdata-semnatic-labels.tsv'
	# rm 'word-list.tsv'
	# přidat rod, poč. písmeno (velké/malé), vid, request na MorphoDitu

word-list.tsv: syn2015.gz
	zgrep -v '^<' 'syn2015.gz' | cut -d $$'\t' -f 1,2,3 | sort | uniq -c | sort -nr > 'word-list.tsv'

syn2015.gz:
	echo 'You need syn2015.gz corpus from Czech National Corpus Institution.'
