INPUTDIR=../../../../../data/annotations/cs/2019_01_freq_roots/hand-annotated/

all: batch1 batch2 merge



batch1: batch1-induced-segmentations.tsv

batch1-induced-segmentations.tsv: fixed-after-tests-by-ZZ.csv
	cat fixed-after-tests-by-ZZ.csv | ./find-root-morphemes.pl > batch1-induced-segmentations.tsv 2>errlog1.txt

#pripravdruhoudavku:  # druha davka
#	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/druha-davka-koreny-def-anotace-od-Sarky.xls
#	./spoj-druhou-davku.pl > druha-davka-spojena.tsv


batch2: batch2-induced-segmentations.tsv

batch2-induced-segmentations.tsv: druha-davka-fixed-by-ZZ.csv
	cat druha-davka-fixed-by-ZZ.csv | ./find-root-morphemes.pl > batch2-induced-segmentations.tsv 2> errlog2.txt

%-by-ZZ.csv: ${INPUTDIR}/%-by-ZZ.xlsx
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . "$<"

merge: induced-segmentations.tsv

induced-segmentations.tsv: batch1-induced-segmentations.tsv batch2-induced-segmentations.tsv
	cat batch1-induced-segmentations.tsv batch2-induced-segmentations.tsv > induced-segmentations.tsv

overlap:
	cat induced-segmentations.tsv | ./check_allomorph_overlaps.py | sort -nr


clean:
	rm *tsv *txt *csv
