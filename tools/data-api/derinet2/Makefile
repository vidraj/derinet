.PHONY: install test sample_scenario

DATA_DIR=../../../data/releases/cs

install:
	pip3 install --user -r requirements.txt

test: tests/test_derinet.py
	python3 -m nose tests/test_derinet.py

sample_scenario: scenarios/process_scenario.py
	./scenarios/process_scenario.py Load file="${DATA_DIR}/derinet-1-4.tsv" PrintLexemes
