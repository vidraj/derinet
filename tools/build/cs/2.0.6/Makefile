.PHONY: clean

derinet-2-0-6.tsv: derinet-2-0-5.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2021_01_conversion/into-derinet/lexemes-to-delete.tsv \
		cs.AddConversions ../../../../data/annotations/cs/2021_01_conversion/into-derinet/relations-of-conversion.tsv \
		cs.AddVariants ../../../../data/annotations/cs/2021_01_spelling_variants/v1/nsets-spelling-variants.tsv \
		Save "$@" > log 2>&1

derinet-2-0-5.tsv: ../2.0.5/derinet-2-0-5.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-0-6.tsv derinet-2-0-5.tsv
