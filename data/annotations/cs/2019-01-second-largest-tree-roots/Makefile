.PHONY: clean

PYTHONPATH::="$(abspath ../../../../tools/data-api/derinet2)":${PYTHONPATH}
export PYTHONPATH

PROCESS::=../../../../tools/data-api/derinet2/scenarios/process_scenario.py
DERINET::=../../../releases/cs/derinet-1-7.tsv
CORPUS_COUNTS::=../2018-12-largest-tree-roots/pro-zdenka-syn-lemata-od-ondreje
SEGMENTATION::=../2018-12-largest-tree-roots/derinet-segmented-EMmh-roots.txt
SORT_BLOCKS::=../2018-12-largest-tree-roots/sort-blocks.py

COUNT::=500

druha-davka.tsv: second-batch-sorted.tsv
	 ./block-head.py ${COUNT} < "$<" | sed -e 's/^#/			#/' > "$@"
	grep --context=1 '^	*# Automatic roots for ' < "$@" | sed -e 's/^	*# //' > druha-davka-koreny.tsv

second-batch-sorted.tsv: second-batch.tsv ${SEGMENTATION} ${SORT_BLOCKS}
	${SORT_BLOCKS} ${SEGMENTATION} < "$<" > "$@"

second-batch.tsv: already-annotated-roots.tsv ${DERINET} ${CORPUS_COUNTS}
	# Load DeriNet 1.7 or whatever the newest version is. TODO: merge fixes produced by the previous annotation first.
	# Delete all trees rooted in words from already-annotated-roots.tsv.
	PYTHONPATH=${PYTHONPATH} ${PROCESS} Load file=${DERINET} \
	cs.DeleteSubtrees file="$<" \
	cs.AddCorpusCounts file=${CORPUS_COUNTS} name=syn2015 \
	cs.FilterByCorpusCounts name=syn2015 min-count=1 \
	Save file="$@" version=2 > "$@".log 2>&1


already-annotated-roots.tsv: ../2018-12-largest-tree-roots/sorted-trees-merged.tsv
	#grep '^Automatic roots for [^#]*#.:	' "$<" | sed -e 's/^Automatic roots for \([^#]*\)#\(.\):	.*$$/\1	\2/' > "$@"
	sed -ne '/^Manual roots for [^#]*#.:	/ b extract-root; d; : extract-root n; n; n; p' < "$<" | cut -f2-3 > "$@"

clean:
	rm -f already-annotated-roots.tsv
	rm -f second-batch.tsv
