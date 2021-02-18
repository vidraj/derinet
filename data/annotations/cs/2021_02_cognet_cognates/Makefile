SHELL=/bin/bash

# need actual derinet-2-0-5.tsv release,
# but not from data/releases/cs/, rather from tools/build/cs/2.0.5
# name it derinet-2-0-5-corrected.tsv

derinet-2-0-5-corrected.tsv:
	echo 'READ FIRST COMMENT IN THE MAKEFILE, IT IS IMPORTANT'


loanwords-trees-annotated.tsv: derinet-2-0-5-corrected.tsv
	python3 create_annotation_sample.py \
		--DeriNet derinet-2-0-5-corrected.tsv \
		--Cognates1 czech_words_with_cognates_both_in_slavic_and_nonslavic_languages.txt \
		--Cognates2 czech_words_with_cognates_only_in_nonslavic_languages.txt \
		> loanwords-trees-annotated.tsv
