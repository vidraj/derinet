.PHONY: clean

derinet-2-0-5.tsv: derinet-2-0.tsv ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv ../../../../data/releases/cs/derinet-2-0.tsv syn-v9-lemma-freq.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.0.5 \
		Load "$<" \
		cs.CopyAspect ../../../../data/releases/cs/derinet-2-0.tsv \
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
		cs.ImportCorpusCounts --counts-type=v9 syn-v9-lemma-freq.tsv \
		cs.FindConversion \
		cs.ChangePosTags \
		Save "$@" > log 2>&1

../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv: ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.ods
	$(MAKE) -C ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/vyjmenovana-slova-sd-jv.tsv

derinet-2-0.tsv: ../2.0/derinet-2-0.tsv
	cp -a "$<" "$@"

../../../../data/releases/cs/derinet-2-0.tsv:
	zcat ../../../../data/releases/cs/derinet-2-0.tsv.gz > ../../../../data/releases/cs/derinet-2-0.tsv

syn-v9-lemma-freq.tsv: ../../../../data/annotations/cs/2024_06_corpus_counts_synv9/syn-v9-lemma-freq.tsv.xz
	xz -dvvvc '$<' > '$@'

../../../../data/annotations/cs/2024_06_corpus_counts_synv9/syn-v9-lemma-freq.tsv.xz:
	$(MAKE) -C ../../../../data/annotations/cs/2024_06_corpus_counts_synv9/ syn-v9-lemma-freq.tsv.xz

clean:
	rm -f log derinet-2-0-5.tsv derinet-2-0.tsv
	rm -rf ../../../../data/annotations/cs/2020_03_loanwords/__pycache__/
	rm -rf ../../../../data/annotations/cs/2020_07_conjugation_class/__pycache__/
	$(MAKE) -C ../../../../data/annotations/cs/2019_12_06_enumerated_words/annotated/ clean
	rm -f ../../../../data/releases/cs/derinet-2-0.tsv
	rm -f syn-v9-lemma-freq.tsv
	#$(MAKE) -C ../../../../data/annotations/cs/2024_06_corpus_counts_synv9/ clean
