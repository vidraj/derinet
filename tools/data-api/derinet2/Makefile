.PHONY: all profile time-load time-load-pickle time-unpickle clean

PROJECT_ROOT::=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PYTHON=python3
DERINET="../../../data/releases/cs/derinet-1-7.tsv"
PICKLE_FILE=output.pickle
PYTHONPATH=$(PROJECT_ROOT)

export PYTHONPATH

all: profile

profile: profile-load.pyprof
	# pyprof2calltree -i "$<" -k
	snakeviz "$<"

time-load: test/profile_load.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" "$(DERINET)"

time-load-pickle: test/profile_load.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" "$(DERINET)" "$(PICKLE_FILE)"

time-unpickle: test/python_load_pickle.py $(wildcard derinet/*.py)
	/usr/bin/time -v "$(PYTHON)" -O "$<" "$(PICKLE_FILE)"

profile-load.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" "$(DERINET)"

profile-load-pickle.pyprof: test/profile_load.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" "$(DERINET)" "$(PICKLE_FILE)"

profile-unpickle.pyprof: test/python_load_pickle.py $(wildcard derinet/*.py)
	"$(PYTHON)" -O -m cProfile -o "$@" "$<" "$(PICKLE_FILE)"

clean:
	rm -f profile-load.pyprof profile-load-pickle.pyprof profile-unpickle.pyprof
