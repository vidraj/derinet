SHELL=/bin/bash

all: merge lexinfos

merge:
	cat maillist.txt > all_comps.txt
	cat comps1.txt >> all_comps.txt
	cat comps2.txt >> all_comps.txt
	cat all_comps.txt | sort | uniq | sort > uniq_comps.txt
	rm all_comps.txt

lexinfos:
	python3 lexinfos.py '../../../../releases/cs/derinet-1-5.tsv' 'uniq_comps.txt' '../hand-annotated/compounds.tsv'
	rm uniq_comps.txt
