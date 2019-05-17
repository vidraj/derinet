SHELL=/bin/bash
.PHONY: clean

PYTHONPATH::="$(abspath ../../../../tools/data-api/derinet2)":${PYTHONPATH}
export PYTHONPATH

PROCESS::=../../../../tools/data-api/derinet2/scenarios/process_scenario.py
DERINET::=../../../releases/cs/derinet-1-6.tsv
CORPUS_COUNTS::=pro-zdenka-syn-lemata-od-ondreje

sorted-trees.tsv: derinet-largest-trees.tsv derinet-segmented-EMmh-roots.txt
	./sort-blocks.py derinet-segmented-EMmh-roots.txt < "$<" > "$@"

derinet-largest-trees.tsv: ${DERINET} ${CORPUS_COUNTS}
	@echo ${PYTHONPATH}
	PYTHONPATH=${PYTHONPATH} ${PROCESS} Load file="$<" \
	FilterTreesBySize min_size=300 \
	cs.AddCorpusCounts file=${CORPUS_COUNTS} name=syn2015 \
	cs.FilterByCorpusCounts name=syn2015 min-count=1 \
	Save file="$@" version=2 > "$@".log 2>&1

pro-zdenka-syn-lemata-od-ondreje: /home/jonas/škola/svn/undergrads/derinet/build/data/pro-zdenka-syn-lemata-od-ondreje.gz
	zcat "$<" | sed -e 's/^ *//; s/ *$$//' | egrep '[^[:space:]][[:space:]]+[^[:space:]]+[[:space:]]+[^[:space:]]' > "$@"

clean:
	rm -f derinet-largest-trees.tsv
	rm -f sorted-trees.tsv
