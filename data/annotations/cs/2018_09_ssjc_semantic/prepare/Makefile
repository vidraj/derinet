SHELL=/bin/bash

DERINET='../../../../releases/cs/derinet-1-7.tsv'

# provede jednotlivé kroky
data: SSJC MORFFLEXCZ PMC VALLEX Multiple
preprocess: MergeAnnotations AddFeatures
install: virtual


# EXTRAKCE A ANOTACE DAT

# extrahuje sémantické labely ze SSJČ a automaticky je anotuje
SSJC: ../for-annotation/semantic-labels-ssjc.tsv
	@echo 'Extraction and annotation from SSJC complete. See file: ../for-annotation/semantic-labels-ssjc.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-ssjc.tsv: ssjc-utf8.xml
	python3 'extract-ssjc.py' 'ssjc-utf8.xml' $(DERINET) > '../for-annotation/potentials-ssjc.tsv'
	python3 'annotate.py' '../for-annotation/potentials-ssjc.tsv' $(DERINET) > '../for-annotation/semantic-labels-ssjc.tsv'
	rm '../for-annotation/potentials-ssjc.tsv'

ssjc-utf8.xml:
	@echo -e 'You need SSJČ .xml data.'


# extrahuje sémantické labely z MorfFlexu a automaticky je anotuje
MORFFLEXCZ: ../for-annotation/semantic-labels-morfflex.tsv
	@echo 'Extraction and annotation from MorfFlexCZ completed. See file: ../for-annotation/semantic-labels-morfflex.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-morfflex.tsv:
	python3 'extract-morfflex.py' $(DERINET) > '../for-annotation/potentials-morfflex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-morfflex.tsv' $(DERINET) > '../for-annotation/semantic-labels-morfflex.tsv'
	rm '../for-annotation/potentials-morfflex.tsv'


# extrahuje potenciální vztahy z DeriNetu na základě Příruční mluvnice češtiny (nutná manuální anotace)
PMC: ../for-annotation/semantic-labels-pmc.tsv
	@echo 'Extraction and annotation from PMC completed. See file: ../for-annotation/semantic-labels-pcm.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-pmc.tsv:
	python3 'extract-pmc.py' $(DERINET) > '../for-annotation/semantic-labels-pmc.tsv'


# extrahuje potenciální vztahy z VALLEXu a automaticky je anotuje
VALLEX: ../for-annotation/semantic-labels-vallex.tsv
	@echo 'Extraction and annotation from VALLEX3 completed. See file: ../for-annotation/semantic-labels-vallex.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels-vallex.tsv: vallex_3.0.xml
	python3 'extract-vallex.py' 'vallex_3.0.xml' > '../for-annotation/potentials-vallex.tsv'
	python3 'annotate.py' '../for-annotation/potentials-vallex.tsv' $(DERINET) > '../for-annotation/semantic-labels-vallex.tsv'
	rm '../for-annotation/potentials-vallex.tsv'

vallex_3.0.xml:
	@echo 'You need vallex_3.0.xml dictionary from LINDAT/CLARIN (http://hdl.handle.net/11234/1-2307).'


# vypíše vztahy s více sémantickými labely
Multiple: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-ssjc.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-morfflex.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-pmc.tsv'
	cat '../for-annotation/semantic-labels-vallex.tsv' | sed '1d' | grep -e '^%' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-vallex.tsv'


# PREPROCESING DAT

# sloučí anotace všech souborů
MergeAnnotations: ../for-annotation/semantic-labels.tsv
	@echo 'Merging of annotated files completed. See file: ../for-annotation/semantic-labels.tsv'
	@echo 'WARNING: BE CAREFUL, DATA CAN CONTAIN MANUAL ANNOTATIONS!'

../for-annotation/semantic-labels.tsv: ../for-annotation/semantic-labels-ssjc.tsv ../for-annotation/semantic-labels-morfflex.tsv ../for-annotation/semantic-labels-pmc.tsv
	cat '../for-annotation/semantic-labels-ssjc.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-morfflex.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-pmc.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-vallex.tsv' | grep $$'^\%' >> '../for-annotation/semantic-labels-1.tsv'
	cat '../for-annotation/semantic-labels-1.tsv' | sed -e 's/\r//g' | sort | uniq > '../for-annotation/semantic-labels.tsv'
	cat '../for-annotation/semantic-labels.tsv' | cut -d $$'\t' -f 2,3,4 | python3 'multiple-labels.py' > '../for-annotation/multiple-labeled-all.tsv'
	rm '../for-annotation/semantic-labels-1.tsv'


# restrukturalizuje dosavadní a přidá nové příznaky do dat
AddFeatures: ../for-annotation/MLdata-semantic-labels.tsv
	@echo 'Adding of features completed. See file: ../for-annotation/MLdata-semantic-labels.tsv'

../for-annotation/MLdata-semantic-labels.tsv: ../for-annotation/semantic-labels.tsv word-list-syn2015.tsv word-list-morphodita.json word-list-vallex.tsv
	cat '../for-annotation/semantic-labels.tsv' | grep -v $$'\tpodst\.' | grep -v $$'\tzpodst\.' > '../for-annotation/semantic-labels-1.tsv'
	python3 'add-features.py' '../for-annotation/semantic-labels-1.tsv' 'word-list-syn2015.tsv' 'word-list-morphodita.json' 'word-list-vallex.tsv' > '../for-annotation/MLdata-semantic-labels.tsv'
	rm '../for-annotation/semantic-labels-1.tsv'
	# rm 'word-list-morphodita.json' 'word-list-syn2015.tsv'

word-list-syn2015.tsv: syn2015.gz
	zgrep -v '^<' 'syn2015.gz' | cut -d $$'\t' -f 1,2,3 | sort | uniq -c | sort -nr > 'word-list-syn2015.tsv'

word-list-morphodita.json: ../for-annotation/semantic-labels.tsv
	cat '../for-annotation/semantic-labels.tsv' | cut -d $$'\t' -f 2,3 | sed -e 's/–[A-Z]*//g' | sed -e 's/\t/\n/g' | sort | uniq > 'for-analyze.txt'
	curl -F 'data=@for-analyze.txt' -F 'output=json' -F 'input=vertical' http://lindat.mff.cuni.cz/services/morphodita/api/tag > 'word-list-morphodita.json'
	rm 'for-analyze.txt'

word-list-vallex.tsv: vallex_3.0.xml
	cat 'vallex_3.0.xml' | grep -o $$'\<mlemma.*' | sed -e 's/>/ /g' -e 's/<\/mlemma//g' | grep -e $$'aspect' | awk '{print $$NF " " $$2}' | grep -v $$'"iter"' | sed -e 's/aspect="impf"/I/g' -e 's/aspect="pf"/P/g' -e 's/aspect="biasp"/B/g' | sort | uniq > word-list-vallex.tsv

syn2015.gz:
	@echo 'You need syn2015.gz corpus from Czech National Corpus Institution.'


# PŘÍPRAVA VIRTUÁLNÍHO PROSTŘEDÍ PRO ML METODY

# nainstaluje virtuální prostředí s potřebnými knihovnami
virtual:
	virtualenv -p /usr/bin/python3 py3env
	@( \
	source py3env/bin/activate; \
	pip3 install pandas; \
	pip3 install numpy; \
	)


# MACHINE LEARNING