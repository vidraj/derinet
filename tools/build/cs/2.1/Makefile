.PHONY: clean

derinet-2-1.tsv: derinet-2-0.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddLoanwordMarks \
		Save "$@" > log 2>&1

derinet-2-0.tsv:
	@echo Unpacking derinet 2.0
	zless ../../../../data/releases/cs/derinet-2-0.tsv.gz > derinet-2-0.tsv

#derinet-1-7.tsv: ../1.7/derinet-1-7.tsv
#	cp -a "$<" "$@"

# clean:
# 	rm -f log log-tag-masks derinet-1-7.tsv derinet-1-7-tag-masks.tsv derinet-2-0.tsv
# 	rm -f allomorph-overlap.csv tag-masks.tsv
# 	$(MAKE) -C prepare-root-segmentations clean
