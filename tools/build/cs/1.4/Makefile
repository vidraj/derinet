.PHONY: all clean

all: derinet-1-4.tsv

derinet-1-4.tsv: derinet-1-3.tsv
	./create-1.4.py > log

derinet-1-3.tsv: ../1.3/derinet-1-3.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-3.tsv derinet-1-4.tsv
