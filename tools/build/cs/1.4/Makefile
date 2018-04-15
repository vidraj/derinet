.PHONY: all clean

all: derinet-1-4.tsv

derinet-1-4.tsv: derinet-1-3.tsv
	./create-1.4.py > log

derinet-1-4-scenario.tsv: derinet-1-3.tsv final_sorted
	PYTHONPATH=../../../data-api/derinet2:"$$PYTHONPATH" ../../../data-api/derinet2/scenarios/process_scenario.py Load file="$<" AddFromTsvLemmaList file=final_sorted Save file="$@" > log-scenario 2>&1

derinet-1-3.tsv: ../1.3/derinet-1-3.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-3.tsv derinet-1-4.tsv
