.PHONY: clean

derinet-2-3.tsv: derinet-2-2.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.3 \
		Load "$<" \
		cs.AddEtymology ../../../../data/annotations/cs/2024_06_etymology_information/etymology_information.tsv\
		cs.AddSegmentationClassification ../../../../data/annotations/cs/2024_06_segmentation_classification/classification.tsv\
		cs.AddDerivationsEtymologyDirect ../../../../data/annotations/cs/2024_06_etymology_new_derivations/hand_annotated/added_derivations_direct-2-1-1.tsv \
		cs.AddDerivationsEtymologyIntermediate ../../../../data/annotations/cs/2024_06_etymology_new_derivations/hand_annotated/added_derivations_intermediates-2-1-1.tsv \
		Save "$@" > log 2>&1


derinet-2-2.tsv: ../2.2/derinet-2-2.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-3.tsv derinet-2-2.tsv
