export RELVER::=1-3
export PERL5LIB::=$(CURDIR)/lib:$(PERL5LIB)
export ANNOT::=../../../data/annotations/cs/2015-07-gold-standard/annot-devel.tsv
export DERIMOR_MAIN_DIR::=$(CURDIR)

MORFFLEX::=data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz
MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex-161115.dict

.PHONY: release build precision clean mrproper

release: build
	$(MAKE) -C derinet-1-3 release
	cp derinet-1-3/derinet-${RELVER}.tsv.gz .

build: $(MORFFLEX) $(MORPHODITA_MODEL)
	$(MAKE) -C derinet09 slex
	$(MAKE) -C derinet091 slex
	$(MAKE) -C derinet092 slex
	$(MAKE) -C derinet-1-1 slex
	$(MAKE) -C derinet-1-3 slex

precision: build
	./derimor Load file=derinet-1-1/derinet-1-1.slex \
	MeasurePrecisionRecall file=annotation-cut.tsv 2>prec-recall.txt

data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1834/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz?sequence=1&isAllowed=y'

data/models/morphodita/cs/czech-morfflex-161115.dict: data/czech-morfflex-pdt-161115.zip
	unzip -DD -j -d data/models/morphodita/cs/ "$<" czech-morfflex-pdt-161115/czech-morfflex-161115.dict

data/czech-morfflex-pdt-161115.zip:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1836/czech-morfflex-pdt-161115.zip?sequence=1&isAllowed=y'




clean:
	$(MAKE) -C derinet09 clean
	$(MAKE) -C derinet091 clean
	$(MAKE) -C derinet092 clean
	$(MAKE) -C derinet-1-1 clean
	$(MAKE) -C derinet-1-3 clean
	rm -f derinet-${RELVER}.tsv.gz
	rm -f prec-recall.txt
	rm -f data/models/morphodita/cs/czech-morfflex-161115.dict

mrproper: clean
	rm -f "$(MORFFLEX)"
	rm -f data/czech-morfflex-pdt-161115.zip
