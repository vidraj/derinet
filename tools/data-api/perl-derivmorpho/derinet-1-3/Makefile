BASE::=derinet-1-3
export ANNOT::=../../annot-devel.tsv

# When run recursively by the main Makefile one level higher, don't set the version, but inherit it instead.
ifndef RELVER
RELVER::=1-3
endif

.PHONY: all stats clean release

all: $(BASE).tsv

slex: $(BASE).slex

$(BASE).tsv $(BASE).slex: ../derinet-1-1/derinet-1-1.slex vallex_bracketed_all-fixed
	derimor \
	Load file="$<" \
	CS::AddDerivationsFromTrees file=vallex_bracketed_all-fixed pos=V ignore_missing=1 \
	Save file="$@" >log.txt 2>&1

missing-words.txt: $(BASE).slex
	grep "Lexeme '.*' not found." < log.txt |sed -e "s/.*Lexeme '\([^']*\)' not found.*/\1/" > "$@"

stats: # $(BASE).slex
	derimor \
	Load file=$(BASE).slex \
	MeasurePrecisionRecall file=${ANNOT} ignore_composition=1 verbose=1 \
	PrintStats singletons_file=singletons.tsv > stats-${RELVER}.txt 2>&1

deadj:
	derimor \
	Load file=$(BASE).tsv \
	PrintDeadjectivalDerivs > deadj-${RELVER}.tsv

clean:
	rm -f $(BASE).tsv $(BASE).slex log.txt reconnected.tsv reconnections.tsv stats.txt stats-derivation-creator.txt prec-recall.txt

release: $(BASE).tsv
	cut -f1-5 $(BASE).tsv > derinet-final-${RELVER}.tsv
	mv derinet-final-${RELVER}.tsv derinet-${RELVER}.tsv
	gzip -f9 derinet-${RELVER}.tsv

reconnected.tsv: $(BASE).tsv
	# grep for all lines with >2 derivation-author records | grep all whose contents of the square brackets match
	grep '],CS::' $< |grep -v '\[\([^]]*\)\].*\[\1\]' > reconnected.tsv

reconnections.tsv: reconnected.tsv
	# Get the reconnections only
	#cut -f 3,8 reconnected.tsv |sed -e 's/^\([^\t]*\)\t[^\t]*\[\([^]]*\)\],[^\t]*\[\([^]]*\)\].*$/\1\t\2\t\3/' > reconnections.tsv
	cat reconnected.tsv |./reconnections.sh > reconnections.tsv
