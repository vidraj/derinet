.PHONY: stats clean

derinet-1-7.tsv: derinet-1-6.tsv
	./create-1.7.py > log

derinet-1-6.tsv: ../1.6/derinet-1-6.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-6.tsv derinet-1-7.tsv
