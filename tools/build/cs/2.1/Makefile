.PHONY: clean

derinet-2-1.tsv: derinet-2-0-6.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		Save "$@" > log 2>&1

derinet-2-0-6.tsv: ../2.0.6/derinet-2-0-6.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-1.tsv derinet-2-0-6.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
