.PHONY: all test coverage profile pylint time-load time-load-pickle time-unpickle test-scenario clean

PROJECT_ROOT::=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PYTHON=python3
DERINET=../../../data/releases/cs/derinet-1-7.tsv
PICKLE_FILE=output.pkl
PYTHONPATH=$(PROJECT_ROOT)

export PYTHONPATH

all: profile

test:
	"$(PYTHON)" -m unittest discover -s test/ -p 'test_*.py'

coverage:
	coverage run --branch --omit 'test/test_*.py' -m unittest discover -s test/ -p 'test_*.py' ; coverage report

profile: profile-load.pyprof
	# pyprof2calltree -i "$<" -k
	snakeviz "$<"

pylint:
	pylint derinet

time-load: test/profile_load.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" derinet-v1 < "$(DERINET)"

time-load-pickle: test/profile_load.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" --save pickle-v4 derinet-v1 < "$(DERINET)" > "$(PICKLE_FILE)"

time-unpickle: test/profile_load.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" pickle-v4 < "$(PICKLE_FILE)"

profile-load.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" derinet-v1 < "$(DERINET)"

profile-load-pickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" --save pickle-v4 derinet-v1 < "$(DERINET)" > "$(PICKLE_FILE)"

profile-unpickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" pickle-v4 < "$(PICKLE_FILE)"

test-scenario: process_scenario.py
	./process_scenario.py Load derinet-2-0.tsv Save derinet-2-0.tsv.tmp
	diff -q derinet-2-0.tsv derinet-2-0.tsv.tmp

clean:
	rm -f profile-load.pyprof profile-load-pickle.pyprof profile-unpickle.pyprof
	rm -f "$(PICKLE_FILE)"
	find . -name '__pycache__' -type d -exec rm -rf '{}' '+'
	coverage erase
