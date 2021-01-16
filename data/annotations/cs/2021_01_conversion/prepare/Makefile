SHELL=/bin/bash


potential-conversion.tsv:
	python3 find_conversion.py --DeriNet <(zcat ../../../../releases/cs/derinet-2-0.tsv.gz) \
							   --Output potential-conversion.tsv

postprocessing:
	mkdir -p ../into-derinet/
	python3 postprocessing.py --AnnotInput <(cat ../hand-annotated/potential-conversion-AN.tsv ../hand-annotated/potential-conversion-AD.tsv) \
							  --OutputConversion ../into-derinet/relations-of-conversion.tsv \
							  --OutputDeleteLexemes ../into-derinet/lexemes-to-delete.tsv \
							  --OutputCreateLexemes ../into-derinet/lexemes-to-create.tsv
	# be carefull, POS tags were change manually to NOUN, ADJ, ADV
