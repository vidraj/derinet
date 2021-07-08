export RELVER::=1-3
export PERL5LIB::=$(CURDIR)/lib:$(PERL5LIB)
export ANNOT::=../../../data/annotations/cs/2015-07-gold-standard/annot-devel.tsv
export DERIMOR_MAIN_DIR::=$(CURDIR)

#MORFFLEX::=$(abspath data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz)
#MORFFLEX::=$(abspath data/czech-morfflex-180626-devel.raw.xz)
#MORFFLEX::=$(abspath data/czech-morfflex-20200720-devel.raw.xz)
MORFFLEX::=$(abspath data/czech-morfflex-2.0.tsv.xz)
# MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex-161115.dict
MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex-180626-devel.dict

export MORFFLEX

.PHONY: release build precision clean mrproper

release: derinet-$(RELVER).tsv
derinet-%.tsv: derinet-%b.tsv
	cut -f1-3,5-6 "$<" > "$@"


build: derinet-1-3b.tsv
derinet-1-3b.tsv: derinet-1-3/derinet-1-3.slex
	./derimor Load file="$<" Save file="$@"

derinet-1-3/derinet-1-3.slex: $(MORFFLEX) $(MORPHODITA_MODEL)
	$(MAKE) -C derinet09 slex
	$(MAKE) -C derinet091 slex
	$(MAKE) -C derinet092 slex
	$(MAKE) -C derinet-1-1 slex
	$(MAKE) -C derinet-1-3 slex

precision: derinet-1-3/derinet-1-3.slex
	./derimor Load file="$<" \
	MeasurePrecisionRecall file="${ANNOT}" 2>prec-recall.txt

data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1834/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz?sequence=1&isAllowed=y'

$(abspath data/czech-morfflex-2.0.tsv.xz):
	curl --remote-time --location --output '$@' 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3186/czech-morfflex-2.0.tsv.xz?sequence=1&isAllowed=y'

data/models/morphodita/cs/czech-morfflex-161115.dict: data/czech-morfflex-pdt-161115.zip
	unzip -DD -j -d data/models/morphodita/cs/ "$<" czech-morfflex-pdt-161115/czech-morfflex-161115.dict

data/czech-morfflex-pdt-161115.zip:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1836/czech-morfflex-pdt-161115.zip?sequence=1&isAllowed=y'


deleted.txt: build
	grep 'Deleting relation ' ./*/log.txt | sed -e 's/^.*	Deleting relation //; s/ made by .*$$//' |sort > "$@"

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
