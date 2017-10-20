BASE::=derinet-1-1
export ANNOT::=../../annot-devel.tsv

# When run recursively by the main Makefile one level higher, don't set the version, but inherit it instead.
ifndef RELVER
RELVER::=1-1
endif

.PHONY: all stats clean release

all: $(BASE).tsv

slex: $(BASE).slex

$(BASE).tsv $(BASE).slex: $(wildcard ../derinet092/derinet092.*)
	../derimor \
	Load file=$< \
	CS::AddAlterationsFromManualAnnot file=anotace-alternace.txt \
	Save file=$@ >log.txt 2>&1

stats: # $(BASE).slex
	../derimor \
	Load file=$(BASE).slex \
	MeasurePrecisionRecall file=${ANNOT} ignore_composition=1 verbose=1 \
	PrintStats singletons_file=singletons.tsv > stats-${RELVER}.txt 2>&1

	cat $(BASE).tsv | cut -f8 | sed -e 's/.*\(CS::[^:[]\+\).*/\1/' | sort | uniq -c | sort -nr > stats-derivation-creator.txt
	#cat $(BASE).tsv | cut -f8 | sed -e 's/.*\(CS::[^[]\+\).*/\1/' | sort | uniq -c | sort -nr > stats-derivation-creator.txt

deadj:
	../derimor \
	Load file=$(BASE).tsv \
	PrintDeadjectivalDerivs > deadj-${RELVER}.tsv

clean:
	rm -f $(BASE).tsv $(BASE).slex log.txt reconnected.tsv reconnections.tsv stats.txt stats-derivation-creator.txt prec-recall.txt

release: $(BASE).tsv
	cut -f1-5 $(BASE).tsv > derinet-final-${RELVER}.tsv
	mv derinet-final-${RELVER}.tsv derinet-${RELVER}.tsv
	gzip -9 derinet-${RELVER}.tsv

reconnected.tsv: $(BASE).tsv
	# grep for all lines with >2 derivation-author records | grep all whose contents of the square brackets match
	grep '],CS::' $< |grep -v '\[\([^]]*\)\].*\[\1\]' > reconnected.tsv

reconnections.tsv: reconnected.tsv
	# Get the reconnections only
	#cut -f 3,8 reconnected.tsv |sed -e 's/^\([^\t]*\)\t[^\t]*\[\([^]]*\)\],[^\t]*\[\([^]]*\)\].*$/\1\t\2\t\3/' > reconnections.tsv
	cat reconnected.tsv |./reconnections.sh > reconnections.tsv
