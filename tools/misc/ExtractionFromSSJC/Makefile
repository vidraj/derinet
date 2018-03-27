SHELL=/bin/bash

all: extract compare clean

extract:
	python3 'extract.py' -s 'ssjc-utf8.xml'

derinet:
	git clone 'https://github.com/vidraj/derinet.git'
	@mv 'derinet' 'derinet-git'
	@cp -r 'derinet-git/tools/data-api/derinet2/derinet' .
	@cp 'derinet-git/data/releases/cs/derinet-1-5-1.tsv' .

compare: derinet
	@mkdir -p 'output'
	python3 'comparison.py' -s 'ssjc-wf.tsv' -d 'derinet-1-5-1.tsv' -i 'output/inside.dat' -o 'output/outside.dat' -c 'output/composites.dat' -n 'output/noncomposites.dat' -a 'output/all-relations.dat'

clean:
	@rm -rf 'derinet-git'
	@rm -rf 'derinet'
	@rm 'derinet-1-5-1.tsv'
