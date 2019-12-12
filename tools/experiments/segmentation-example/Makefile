.PHONY: all clean

DERINET=../../../data/releases/cs/derinet-2-0.tsv.gz
PROCESS=../../data-api/derinet2/process_scenario.py

all: derinet-with-segmentation.tsv

derinet-with-segmentation.tsv: derinet.tsv segmentation.txt
	$(PROCESS) \
		Load "$<" \
		cs.AddSegmentation segmentation.txt \
		Save "$@" > log.txt 2>&1

derinet.tsv: $(DERINET)
	gzip -dc "$<" > "$@"

clean:
	rm -f derinet.tsv
	rm -f derinet-with-segmentation.tsv
