.PHONY: rootmorphemes clean

rootmorphemes:
	../../../data-api/derinet2/process_scenario.py Load -f DERINET_V1 ../../../../data/releases/cs/derinet-1-7.tsv cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv Save annotated-morphs.tsv

derinet-2-0.tsv: derinet-1-7-tag-masks.tsv prepare-root-segmentations/induced-segmentations.tsv ../../../../data/annotations/cs/2019_03_semantic_labelling/final-semantic-labels.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
		cs.AddSemanticRelationLabels ../../../../data/annotations/cs/2019_03_semantic_labelling/final-semantic-labels.tsv \
		Save "$@" > log 2>&1

derinet-1-7-tag-masks.tsv: derinet-1-7.tsv tag-masks.tsv
	../../../data-api/derinet2/process_scenario.py \
		Load -f DERINET_V1 "$<" \
		cs.AddTagMasks tag-masks.tsv \
		cs.GenerateFakeTagMasks \
		Save "$@" > log-tag-masks 2>&1

tag-masks.tsv: ../../../data-api/perl-derivmorpho/derinet09/lemmas_from_morfflex.tsv ../../../data-api/perl-derivmorpho/derinet09/extra_lemmas.tsv
	cut -f1,2 $^ > "$@"

prepare-root-segmentations/induced-segmentations.tsv:
	$(MAKE) -C prepare-root-segmentations induced-segmentations.tsv

derinet-1-7.tsv: ../1.7/derinet-1-7.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-7.tsv derinet-2-0.tsv
	rm -f annotated-morphs.tsv
	$(MAKE) -C prepare-root-segmentations clean
