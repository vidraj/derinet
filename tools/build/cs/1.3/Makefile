.PHONY: clean

PYTHONPATH=../../../data-api/derinet2:"$$PYTHONPATH"
export PYTHONPATH

derinet-1-3.tsv: derinet-1-2.tsv
	python3 import_data.py > release.log

derinet-1-3-scenario.tsv: derinet-1-2.tsv
	../../../data-api/derinet2/scenarios/process_scenario.py \
	    Load file="$<" \
	    cs.AddChangedEdgeProbabilities file=data_to_add/changed-edge-probabilities.csv \
	    cs.CorrectChangedEdgeProbabilities file=data_to_add/dvojiti_rodice_refined.txt \
	    cs.AddJK file=data_to_add/derivace-JK-NO_PARENT_IN_DERINET.csv \
	    cs.AddJK file=data_to_add/derivace-JK-DIFFERENT_PARENT_IN_DERINET.csv \
	    Save file="$@" > log-scenario 2>&1

derinet-1-2.tsv: ../../../data-api/perl-derivmorpho/derinet-1-3.tsv
	cp -a "$<" "$@"

clean:
	rm -f derinet-1-2.tsv
	rm -f derinet-1-3.tsv
	rm -f release.log
