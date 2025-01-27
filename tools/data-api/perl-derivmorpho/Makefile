export RELVER::=1-3
export PERL5LIB::=$(CURDIR)/lib:$(PERL5LIB)
export ANNOT::=../../../data/annotations/cs/2015-07-gold-standard/annot-devel.tsv
export DERIMOR_MAIN_DIR::=$(CURDIR)

#MORFFLEX::=$(abspath data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz)
#MORFFLEX::=$(abspath data/czech-morfflex-180626-devel.raw.xz)
#MORFFLEX::=$(abspath data/czech-morfflex-20200720-devel.raw.xz)
#MORFFLEX::=$(abspath data/czech-morfflex-2.0.tsv.xz)
# new model from 12 2024
MORFFLEX::=$(abspath data/czech-morfflex-2.1.tsv.xz)
# MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex-161115.dict
# MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex-180626-devel.dict
# model from 10.7.2022
MORPHODITA_MODEL::=data/models/morphodita/cs/czech-morfflex2.0-220710.dict

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

$(abspath data/czech-morfflex-2.1.tsv.xz):
	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5833{/czech-morfflex-2.1.tsv.xz}

data/models/morphodita/cs/czech-morfflex-161115.dict: data/czech-morfflex-pdt-161115.zip
	unzip -DD -j -d data/models/morphodita/cs/ "$<" czech-morfflex-pdt-161115/czech-morfflex-161115.dict

data/models/morphodita/cs/czech-morfflex2.0-220710.dict: data/czech-morfflex2.0-pdtc1.0-220710.zip
	unzip -DD -j -d data/models/morphodita/cs/ "$<" czech-morfflex2.0-pdtc1.0-220710/czech-morfflex2.0-220710.dict

data/czech-morfflex-pdt-161115.zip:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1836/czech-morfflex-pdt-161115.zip?sequence=1&isAllowed=y'

data/czech-morfflex2.0-pdtc1.0-220710.zip:
	wget -O "$@" 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4794/czech-morfflex2.0-pdtc1.0-220710.zip'

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
