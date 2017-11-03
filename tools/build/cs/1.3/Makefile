.PHONY: clean

derinet-1-3.tsv: derinet-1-2.tsv
	python3 import_data.py > release.log

clean:
	rm -f derinet-1-3.tsv
	rm -f release.log
