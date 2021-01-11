.PHONY: clean

derinet-2-0-5.tsv: derinet-2-0.tsv ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2020_12_incorrect_lexemes/incorrect-lexemes-e.tsv \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2020_12_incorrect_lexemes/incorrect-lexemes-sko.tsv \
		cs.DelIncorrectLexemes ../../../../data/annotations/cs/2020_12_incorrect_lexemes/incorrect-lexemes-cko.tsv \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddLoanwordMarks ../../../../data/annotations/cs/2020_03_loanwords/hand-annotated/loanwords-trees-annotated.tsv \
		cs.AddConjugationClasses ../../../../data/annotations/cs/2020_07_conjugation_class/verbs-with-conjug-classes.tsv \
		cs.AddUnmotivatedMarks ../../../../data/annotations/cs/2020_01_motivation_of_tree_root_nodes/hand-annotated/into-derinet/unmotivatedness-labels.tsv \
		cs.AddCompoundMarks ../../../../data/annotations/cs/2020_01_motivation_of_tree_root_nodes/hand-annotated/into-derinet/compound-labels.tsv \
		cs.AddDerivations ../../../../data/annotations/cs/2020_01_motivation_of_tree_root_nodes/hand-annotated/into-derinet/derivations-classic.tsv \
		cs.AddCompounds2 ../../../../data/annotations/cs/2020_01_motivation_of_tree_root_nodes/hand-annotated/into-derinet/compounding-classic.tsv \
		cs.AddDerivations ../../../../data/annotations/cs/2020_12_prefixed_words/into-derinet/prefixed-relations.tsv \
		cs.AddSegmentation2 ../../../../data/annotations/cs/2021_01_generated_mophseg/segmentations.txt \
		cs.AddDerivationsFromEnumeratedWords ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv \
		cs.ImportCorpusCounts corpus-counts.tsv \
		cs.FindConversion \
		cs.ChangePosTags \
		Save "$@" > log 2>&1

../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv: ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.ods
	$(MAKE) -C ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/ vyjmenovana-slova-sd-jv.tsv

derinet-2-0.tsv: ../2.0/derinet-2-0.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-0-5.tsv derinet-2-0.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
	$(MAKE) -C ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/ clean
