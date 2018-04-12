DATA_DIR=../../../data/releases/cs

install:
	pip3 install --user -r requirements.txt

test: tests/test_derinet.py
	python3 -m nose tests/test_derinet.py

sample_scenario: scenarios/sample_scenario.txt scenarios/process_scenario.py
	python3 -m scenarios.process_scenario "${DATA_DIR}/derinet-1-4.tsv" scenarios/sample_scenario.txt
