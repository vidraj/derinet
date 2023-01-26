.PHONY: all clean

PYTHONPATH::=$(abspath ../../../../../tools/data-api/derinet2):${PYTHONPATH}
export PYTHONPATH

PROCESS::=../../../../../tools/data-api/derinet2/process_scenario.py
DERINET::=../../../../releases/cs/derinet-2-1.tsv.gz
CORPUS_COUNTS::=../../2018-12-largest-tree-roots/pro-zdenka-syn-lemata-od-ondreje
SORT_BLOCKS::=./sort-blocks.py
BLOCK_HEAD::=../../2019-01-second-largest-tree-roots/block-head.py

COUNT::=1000

.SUFFIXES:
.SUFFIXES: .tsv .xlsx

all: fourth-batch-sorted.xlsx fourth-batch-roots.tsv

.tsv.xlsx:
	soffice --headless --infilter=CSV:'9,,76,1,1/1/2/2/3/1/4/2/5/2/6/2,false,false' --convert-to xlsx:'Calc MS Excel 2007 XML' '$<'

fourth-batch-roots.tsv: fourth-batch-sorted.tsv
	grep --text --context=1 '^	*# Automatic roots for ' < '$<' | sed -e 's/^	*# //' > '$@'

fourth-batch-sorted.tsv: fourth-batch.tsv ${SORT_BLOCKS}
	PYTHONPATH='${PYTHONPATH}' '${SORT_BLOCKS}' -n '$(COUNT)' '$<' > '$@'

fourth-batch.tsv: already-annotated-roots.tsv ${DERINET} ${CORPUS_COUNTS}
	# Load DeriNet 1.7 or whatever the newest version is. TODO: merge fixes produced by the previous annotation first.
	# Delete all trees rooted in words from already-annotated-roots.tsv.
	zcat '${DERINET}' | PYTHONPATH='${PYTHONPATH}' '${PROCESS}' Load /dev/stdin \
	DeleteSubtrees --lemma-type=fuzzy-techlemma '$<' \
	cs.DeleteUnattestedLeaves \
	Save '$@' > '$@'.log 2>&1


already-annotated-roots.tsv: ../../2018-12-largest-tree-roots/sorted-trees-merged.tsv ../../2019-01-second-largest-tree-roots/druha-davka.tsv  ../../2019-01-second-largest-tree-roots/treti-davka.tsv
	# Gather roots of already annotated trees to exclude.
	# Change the POS tags from single letters to UPOS.
	# Manually add -t verbal endings to -i verbal endings (i.e. if
	#  we already annotated péci, add also péct)
	( \
		sed -ne '/^Manual roots for [^#]*#.:	/ b extract-root; d; : extract-root n; n; n; p' < '$<' | cut -f2-3 && \
		for f in $(wordlist 2,$(words $^),$^); do \
			sed -ne '/^	*# Manual roots for [^#]*#.:	/ b extract-root; d; : extract-root n; p' < "$${f}" | cut -f2-3; \
		done \
	) | sed -e 's/	A$$/	ADJ/; s/	D$$/	ADV/; s/	N$$/	NOUN/; s/	V$$/	VERB/; /i	VERB$// b addending; b; :addending p; s/i	/t	/' > '$@'

clean:
	rm -f already-annotated-roots.tsv
	rm -f fourth-batch.tsv fourth-batch-sorted.tsv ctvrta-davka-koreny.tsv
