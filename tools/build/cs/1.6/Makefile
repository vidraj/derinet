.PHONY: stats clean

derinet-1-6.tsv: derinet-1-5.tsv
	./create-1.6.py > log

derinet-1-5.tsv: ../1.5/derinet-1-5.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-5.tsv derinet-1-6.tsv
