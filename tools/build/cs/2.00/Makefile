.PHONY: rootmorphemes clean

rootmorphemes:
	../../../data-api/derinet2/process_scenario.py Load -f DERINET_V1 ../../../../data/releases/cs/derinet-1-7.tsv cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv Save annotated-morphs.tsv

derinet-2-0.tsv: derinet-1-7-tag-masks.tsv prepare-root-segmentations/induced-segmentations.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddSemanticRelationLabels ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv \
		Save "$@" > log 2>&1

derinet-1-7-tag-masks.tsv: derinet-1-7.tsv tag-masks.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load -f DERINET_V1 "$<" \
		cs.AddTagMasks tag-masks.tsv \
		cs.GenerateFakeTagMasks \
		Save "$@" > log-tag-masks 2>&1

tag-masks.tsv: ../../../data-api/perl-derivmorpho/derinet-1-3b.tsv
	cut -f3,4 "$<" > "$@"

prepare-root-segmentations/induced-segmentations.tsv:
	$(MAKE) -C prepare-root-segmentations induced-segmentations.tsv

../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv: ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels/final-correction-add.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-correction-fix.tsv
	 $(MAKE) -C ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/ final-semantic-labels-fixed.tsv

derinet-1-7.tsv: ../1.7/derinet-1-7.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-7.tsv derinet-2-0.tsv
	rm -f annotated-morphs.tsv
	$(MAKE) -C prepare-root-segmentations clean
