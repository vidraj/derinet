.PHONY: clean

derinet-2-1.tsv: derinet-2-0-5.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		Save "$@" > log 2>&1

derinet-2-0-5.tsv: ../2.0.5/derinet-2-0-5.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-1.tsv derinet-2-0-5.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
