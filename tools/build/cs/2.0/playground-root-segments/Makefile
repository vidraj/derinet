INPUTDIR=../../../../../data/annotations/cs/2019_01_freq_roots/hand-annotated/

ladim: test2


test:
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/fixed-after-tests-by-ZZ.xlsx
	cat fixed-after-tests-by-ZZ.csv | ./try-root-morphemes.pl > log.txt 2>errlog.txt


pripravdruhoudavku:  # druha davka
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/druha-davka-koreny-def-anotace-od-Sarky.xls
	./spoj-druhou-davku.pl > druha-davka-spojena.tsv


test2:
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/druha-davka-fixed-by-ZZ.xlsx
	cat druha-davka-fixed-by-ZZ.csv | ./try-root-morphemes.pl > 2log.txt 2> 2errlog.txt
