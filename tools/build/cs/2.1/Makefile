.PHONY: clean

derinet-2-1.tsv: derinet-2-0.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddLoanwordMarks \
		cs.AddConjugationClasses ../../../../data/annotations/cs/2020_07_conjugation_class/verbs-with-conjug-classes.tsv \
		cs.ImportCorpusCounts corpus-counts.tsv \
		Save "$@" > log 2>&1

derinet-2-0.tsv: ../2.0/derinet-2-0.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-1.tsv derinet-2-0.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
