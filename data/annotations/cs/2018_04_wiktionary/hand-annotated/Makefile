.PHONY: all check clean

TSVS::=der0001-1000-check.tsv der1001-2000-check.tsv der2001-3000-check.tsv der3001-4000-check.tsv der4001-5000-check.tsv

# The following is unnecessary, as the two consistency-checking scripts
#  have to be launched from their directory anyway, so they will find the
#  DeriNet API on their own.
#ifdef PYTHONPATH
#PYTHONPATH::=$(PYTHONPATH):$(abspath ../../../../../tools/data-api/derinet-python/)
#else
#PYTHONPATH::=$(abspath ../../../../../tools/data-api/derinet-python/)
#endif
#export PYTHONPATH

all: $(TSVS) check

%-check.tsv: %.csv
	sed -e 's/_/–/g; s/;/\t/g' "$<" > "$@"

check: $(TSVS)
	cd tools && ./consistency.py $(patsubst %,../%,$^)
	cd tools && ./handproposal.py $(patsubst %,../%,$^)

clean:
	rm -f $(TSVS)
