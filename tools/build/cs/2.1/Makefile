.PHONY: clean

derinet-2-1.tsv: derinet-2-0-6.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.1 \
		Load "$<" \
		cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_07_foreign_mark_final_after_new_morfflex/hand-annotated/loanwords-trees-automatical-annotated.tsv \
		cs.AddLoanwordMarks ../../../../data/annotations/cs/2021_07_foreign_mark_final_after_new_morfflex/hand-annotated/loanwords-trees-annotated.tsv \
		cs.AddUniverbisation ../../../../data/annotations/cs/2021_06_univerbisation/dataset_cely.txt \
		cs.CheckLoanwordPropriums \
		cs.AddChunks ../../../../data/annotations/cs/2021_07_phantom_lexemes/phantom_chunks.tsv \
		cs.AddPhantomLexemes ../../../../data/annotations/cs/2021_07_phantom_lexemes/phantom_chunks.tsv \
		cs.AddCompounds3 ../../../../data/annotations/cs/2021_07_add_compounds3/compounds.tsv \
		cs.AddSegmentation2 ../../../../data/annotations/cs/2021_07_generated_morphseg/segmentations.txt \
		Save "$@" > log 2>&1

derinet-2-0-6.tsv: ../2.0.6/derinet-2-0-6.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-1.tsv derinet-2-0-6.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
