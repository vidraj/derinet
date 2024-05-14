.PHONY: clean

derinet-2-2.tsv: derinet-2-1.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		Load "$<" \
		Save "$@" > log 2>&1

derinet-2-1.tsv: ../2.1/derinet-2-1.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-2.tsv derinet-2-1.tsv
