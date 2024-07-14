.PHONY: all test coverage profile pylint typecheck typecheck-core typecheck-all time-load-v1 time-load-v2 time-load-v1-pickle time-load-v2-pickle compare-load-v2-cpython-pypy time-unpickle test-scenario clean

PROJECT_ROOT::=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PYTHON=python3
DERINET_V1=../../../data/releases/cs/derinet-1-7.tsv
DERINET_V2=../../../data/releases/cs/derinet-2-1.tsv.gz
PICKLE_FILE=output.pkl
PYTHONPATH=$(PROJECT_ROOT)

export PYTHONPATH

all: profile

test:
	"$(PYTHON)" -m unittest discover -s test/ -p 'test_*.py'

coverage:
	coverage run --branch --omit 'test/test_*.py' -m unittest discover -s test/ -p 'test_*.py' ; coverage report

profile: profile-load-v2.pyprof
	# pyprof2calltree -i "$<" -k
	snakeviz "$<"

pylint:
	pylint derinet

typecheck: typecheck-core typecheck-all

typecheck-core:
	mypy --disallow-untyped-calls derinet/*.py derinet/modules/load.py derinet/modules/save.py test/*.py

typecheck-all:
	mypy -p derinet

time-load-v1: test/profile_load.py $(wildcard derinet/*.py)
	command time -v "$(PYTHON)" -O "$<" derinet-v1 < "$(DERINET_V1)"

time-load-v2: test/profile_load.py $(wildcard derinet/*.py)
	gzip -dc "$(DERINET_V2)" | command time -v "$(PYTHON)" -O "$<" derinet-v2

time-load-v1-pickle: test/profile_load.py $(wildcard derinet/*.py)
	command time -v "$(PYTHON)" -O "$<" --save pickle-v4 derinet-v1 < "$(DERINET_V1)" > "$(PICKLE_FILE)"

time-load-v2-pickle: test/profile_load.py $(wildcard derinet/*.py)
	gzip -dc "$(DERINET_V2)" | command time -v "$(PYTHON)" -O "$<" --save pickle-v4 derinet-v2 > "$(PICKLE_FILE)"

compare-load-v2-cpython-pypy: test/profile_load.py $(wildcard derinet/*.py)
	hyperfine -m3 'make PYTHON=python3 time-load-v2' 'make PYTHON=pypy3 time-load-v2'

time-unpickle: test/profile_load.py $(wildcard derinet/*.py)
	command time -v "$(PYTHON)" -O "$<" pickle-v4 < "$(PICKLE_FILE)"

profile-load-v1.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" derinet-v1 < "$(DERINET_V1)"

profile-load-v2.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	gzip -dc "$(DERINET_V2)" | "$(PYTHON)" -O -m cProfile -o "$@" "$<" derinet-v2

profile-load-v1-pickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" --save pickle-v4 derinet-v1 < "$(DERINET_V1)" > "$(PICKLE_FILE)"

profile-load-v2-pickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	gzip -dc "$(DERINET_V2)" | "$(PYTHON)" -O -m cProfile -o "$@" "$<" --save pickle-v4 derinet-v2 > "$(PICKLE_FILE)"

profile-unpickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" pickle-v4 < "$(PICKLE_FILE)"

test-scenario: derinet/process_scenario.py
	python3 -m derinet.process_scenario Load derinet-2-0.tsv Save derinet-2-0.tsv.tmp
	diff -q derinet-2-0.tsv derinet-2-0.tsv.tmp

clean:
	rm -f profile-load-v1.pyprof profile-load-v1-pickle.pyprof profile-unpickle.pyprof
	rm -f profile-load-v2.pyprof profile-load-v2-pickle.pyprof
	rm -f "$(PICKLE_FILE)"
	rm -rf build/ derinet.egg-info/
	find . -name '__pycache__' -type d -exec rm -rf '{}' '+'
	coverage erase
