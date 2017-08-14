all: clone 1.3 1.4

clone:
	git clone https://github.com/tiefling-cat/derinet-python

1.3:
	wget http://ufal.mff.cuni.cz/~straka/derinet/derinet-1-3.tsv

1.4:
	export PYTHONPATH=$$PYTHONPATH:derinet-python && ./create-1.4.py > log
