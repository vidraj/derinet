.PHONY: clean

derinet-2-0.tsv: derinet-1-7-tag-masks.tsv prepare-root-segmentations/induced-segmentations.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv ../../../../data/annotations/cs/2019_05_compounds/annotated/compounds-annotated.tsv ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/hand-checked-phantoms-to-be-added-to-2.0 allomorph-overlap.csv
	../../../data-api/derinet2/process_scenario.py \
		Load "$<" \
		cs.AddCompounds ../../../../data/annotations/cs/2019_05_compounds/annotated/compounds-annotated.tsv \
		cs.AddPhantomLexemes ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/hand-checked-phantoms-to-be-added-to-2.0 \
		cs.AddDerivationsFromAllomorphOverlap allomorph-overlap.csv \
		cs.AddSemanticRelationLabels ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv \
		cs.AddRootMorphemesFromFile ./prepare-root-segmentations/induced-segmentations.tsv \
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

allomorph-overlap.csv: ../../../../data/annotations/cs/2019_05_allomorph_intersetion/allomorph-overlap.xlsx
	libreoffice --headless --convert-to csv:"Text - txt - csv (StarCalc)":9,34,UTF8 --outdir . "$<"

../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels-fixed.tsv: ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-semantic-labels.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-correction-add.tsv ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/final-correction-fix.tsv
	$(MAKE) -C ../../../../data/annotations/cs/2018_09_ssjc_semantic/hand-annotated/ final-semantic-labels-fixed.tsv

../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/hand-checked-phantoms-to-be-added-to-2.0: ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/potential-new-pairs.tsv
	$(MAKE) -C ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/ handchecked

derinet-1-7.tsv: ../1.7/derinet-1-7.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-7.tsv derinet-2-0.tsv
	rm -f allomorph-overlap.tsv
	$(MAKE) -C prepare-root-segmentations clean
