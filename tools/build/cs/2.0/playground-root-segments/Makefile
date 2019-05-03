INPUTDIR=../../../../../data/annotations/cs/2019_01_freq_roots/hand-annotated/

test:
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/fixed-after-tests-by-ZZ.xlsx
	cat fixed-after-tests-by-ZZ.csv | ./try-root-morphemes.pl > log.txt 2>errlog.txt
