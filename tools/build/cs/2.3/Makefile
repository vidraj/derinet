.PHONY: clean

derinet-2-3.tsv: derinet-2-2.tsv
	cat ../../../../data/annotations/cs/2025_01_revised_suggestions_by_PaReNT/false_roots_one_candidate_retrosort.tsv | ../../../../data/annotations/cs/2025_01_revised_suggestions_by_PaReNT/extract_confirmed_derivations.pl > new_derivations.tsv


	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.3 \
		Load "$<" \
		cs.AddDerivations new_derivations.tsv \
		cs.AddDerivationsEtymologyDirect ../../../../data/annotations/cs/2024_06_etymology_new_derivations/hand_annotated/added_derivations_direct-2-1-1.tsv \
		cs.AddDerivationsEtymologyIntermediate ../../../../data/annotations/cs/2024_06_etymology_new_derivations/hand_annotated/added_derivations_intermediates-2-1-1.tsv \
		cs.AddCompoundRelations ../../../../data/annotations/cs/2025-01-compounds/compounds.tsv ../../../../data/annotations/cs/2024-06-ambiguous-compounds/ambiguities.tsv \
		cs.AddEtymology ../../../../data/annotations/cs/2024_06_etymology_information/etymology_information.tsv\
		cs.AddSegmentationClassification ../../../../data/annotations/cs/2024_06_segmentation_classification/classification.tsv\
		Save --format=DERINET_V2_JSONSEG "$@" > log 2>&1


derinet-2-2.tsv: ../2.2/derinet-2-2.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-3.tsv derinet-2-2.tsv
	
