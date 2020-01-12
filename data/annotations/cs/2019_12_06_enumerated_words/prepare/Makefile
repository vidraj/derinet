.PHONY: all clean

PROCESS::=../../../../../tools/data-api/derinet2/process_scenario.py
DERINET_W_FOREIGN::=derinet-2-0-with-foreign.tsv

all: out.log

out.log: $(DERINET_W_FOREIGN) $(PROCESS)
	$(PROCESS) Load "$<" cs.CheckEnumeratedWords > "$@" 2>&1

derinet-2-0-with-foreign.tsv: derinet-2-0-with-foreign.tsv.xz
	xz -dkvv "$<"

clean:
	rm -f out.log
