.PHONY: clean

derinet-1-3.tsv: derinet-1-2.tsv
	python3 import_data.py > release.log

derinet-1-2.tsv: ../../../data-api/perl-derivmorpho/derinet-1-3.tsv
	cp -a "$<" "$@"

clean:
	rm -f derinet-1-2.tsv
	rm -f derinet-1-3.tsv
	rm -f release.log
