DERINET=../../../../../tools/build/cs/2.00/derinet-2-0.tsv

compounds.tsv: $(DERINET)
	../../../../../tools/data-api/derinet2/process_scenario.py Load "$<" cs.GuessCompoundParents "$@"
