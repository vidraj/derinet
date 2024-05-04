.PHONY: all clean

DERINET=../../../data/releases/cs/derinet-2-0.tsv.gz

all: derinet-with-segmentation.tsv

derinet-with-segmentation.tsv: derinet.tsv segmentation.txt
	PYTHONPATH=../../data-api/derinet2 python3 -m derinet.process_scenario \
		Load "$<" \
		cs.AddSegmentation segmentation.txt \
		Save "$@" > log.txt 2>&1

derinet.tsv: $(DERINET)
	gzip -dc "$<" > "$@"

clean:
	rm -f derinet.tsv
	rm -f derinet-with-segmentation.tsv
	rm -f log.txt
