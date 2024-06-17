.PHONY: clean

derinet-2-2.tsv: derinet-2-1.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.2 \
		Load "$<" \
		cs.AddNumerals ../../../../data/annotations/cs/2024-05-numerals/MorfFlex_numeral_parents.tsv \
		cs.AddNumeralParents ../../../../data/annotations/cs/2024-05-numerals/MorfFlex_numeral_parents.tsv \
		cs.AddPronouns ../../../../data/annotations/cs/2024-05-pronouns/MorfFlex_pronouns.tsv \
		cs.AddAdpositions ../../../../data/annotations/cs/2024-05-adpositions/MorfFlex_adpositions.tsv \
		cs.AddCompoundRelations ../../../../data/annotations/cs/2024-05-compounds/compounds.tsv \
		cs.AddEtymology all_etym_columns.tsv \
		cs.AddSegmentationClassification ../../../../data/annotations/cs/2024_06_segmentation_classification/classification.tsv\
		Save "$@" > log 2>&1

derinet-2-1.tsv: ../2.1/derinet-2-1.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-2.tsv derinet-2-1.tsv
