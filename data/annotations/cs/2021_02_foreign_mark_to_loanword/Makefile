SHELL=/bin/bash

loanwords-trees-annotated.tsv:
	python3 create_annotation_sample.py \
		--DeriNet <(zcat ../../../releases/cs/derinet-2-0.tsv.gz) \
		> loanwords-trees-annotated.tsv
