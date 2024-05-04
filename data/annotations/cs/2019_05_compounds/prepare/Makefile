DERINET=../../../../../tools/build/cs/2.0/derinet-2-0.tsv

compounds.tsv: $(DERINET)
	PYTHONPATH=../../../../../tools/data-api/derinet2 python3 -m derinet.process_scenario Load "$<" cs.GuessCompoundParents "$@"
