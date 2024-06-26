.PHONY: clean

derinet-2-2.tsv: derinet-2-1.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=2.2 \
		Load "$<" \
		cs.AddEtymology ../../../../data/annotations/cs/2024_06_etymology_information/etymology_information.tsv\
		cs.AddSegmentationClassification ../../../../data/annotations/cs/2024_06_segmentation_classification/classification.tsv\
		Save "$@" > log 2>&1

derinet-2-1.tsv: ../2.1/derinet-2-1.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-2-2.tsv derinet-2-1.tsv
