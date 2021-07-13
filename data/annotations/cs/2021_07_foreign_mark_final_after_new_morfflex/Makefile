SHELL=/bin/bash

# INFO: needs the newest build 2.1 (created manually and copied in this folder)
loanwords-trees-annotated.tsv:
	python3 -B create_annotation_sample.py \
		--derinet_lexicon 'derinet-2-1.tsv' \
		--older_annotations '../2021_02_cognet_cognates/hand-annotated/loanwords-trees-annotated.tsv' '../2021_02_foreign_mark_to_loanword/hand-annotated/loanwords-trees-annotated.tsv' '../2020_03_loanwords/hand-annotated/loanwords-trees-annotated.tsv' \
		--output_annot_sample 'loanwords-trees-annotated.tsv' \
		--output_autom_sample 'loanwords-trees-automatical-annotated.tsv'
