.PHONY: clean

derinet-2-1.tsv: derinet-2-0.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddLoanwordMarks \
		cs.ImportCorpusCounts corpus-counts.tsv \
		Save "$@" > log 2>&1

derinet-2-0.tsv: ../2.0/derinet-2-0.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-1.tsv
# 	rm -f log log-tag-masks derinet-1-7.tsv derinet-1-7-tag-masks.tsv derinet-2-0.tsv
# 	rm -f allomorph-overlap.csv tag-masks.tsv
# 	$(MAKE) -C prepare-root-segmentations clean
