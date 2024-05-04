.PHONY: all clean

PROCESS::=PYTHONPATH=../../../../../tools/data-api/derinet2 python3 -m derinet.process_scenario
DERINET_W_FOREIGN::=derinet-2-0-with-foreign.tsv

all: to-annotate.tsv

to-annotate.tsv: $(DERINET_W_FOREIGN)
	$(PROCESS) Load "$<" cs.CheckEnumeratedWords > "$@" 2>out.log

derinet-2-0-with-foreign.tsv: derinet-2-0-with-foreign.tsv.xz
	xz -dkvv "$<"

clean:
	rm -f out.log to-annotate.tsv
