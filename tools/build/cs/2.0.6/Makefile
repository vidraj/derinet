.PHONY: clean

derinet-2-0-6.tsv: derinet-2-0-5.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		Load "$<" \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2021_01_spelling_variants/lexemes-to-delete.tsv \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2021_01_conversion/into-derinet/lexemes-to-delete.tsv \
		cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_02_cognet_cognates/hand-annotated/loanwords-trees-annotated.tsv \
		cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_02_foreign_mark_to_loanword/hand-annotated/loanwords-trees-annotated.tsv \
		cs.AddConversions ../../../../data/annotations/cs/2021_01_conversion/into-derinet/relations-of-conversion.tsv \
		cs.AddVariants ../../../../data/annotations/cs/2021_01_spelling_variants/v1/nsets-spelling-variants.tsv \
		cs.AddDerivations ../../../../data/annotations/cs/2021_01_spelling_variants/v2/into-derinet-derivations.tsv \
		cs.AddVariants ../../../../data/annotations/cs/2021_01_spelling_variants/v2/into-derinet-variants.tsv \
		cs.AddVariants ../../../../data/annotations/cs/2021_01_spelling_variants/v3/into-derinet-variants-gaps.tsv \
		cs.AddDerivations ../../../../data/annotations/cs/2021_03_various_derivatives/into-derinet-derivations.tsv \
		cs.CheckLoanwordPropriums \
		cs.RemoveForeignMark \
		Save "$@" > log 2>&1

derinet-2-0-5.tsv: ../2.0.5/derinet-2-0-5.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-0-6.tsv derinet-2-0-5.tsv
