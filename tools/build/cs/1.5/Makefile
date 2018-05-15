.PHONY: stats clean

derinet-1-5.tsv: derinet-1-4.tsv
	./create-1.5.py > log

derinet-1-4.tsv: ../1.4/derinet-1-4.tsv
	cp -a "$<" "$@"

stats:
	grep success log | cut -f2 | sort | uniq -c | sort -nr

clean:
	rm -f log derinet-1-4.tsv derinet-1-5.tsv
