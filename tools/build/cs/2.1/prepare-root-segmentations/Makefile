INPUTDIR=../../../../../data/annotations/cs/2019_12_morphrootsegm_3rd_round/hand-annotated/

# tohle mi na olufsenovi nefunguje, nevim proc, zatim to z libreoffice exportuju rucne, POZOR, pri exportu do csv je potreba zvolit quote all cells
treti-davka.csv: ${INPUTDIR}/treti-davka.xlsx
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . > treti-davka.csv

induced-segmentations.tsv: treti-davka.csv
	cat treti-davka.csv | egrep -v '^\".+"%' | ./find-root-morphemes.pl > induced-segmentations.tsv 2> errlog.txt

reportprosarku:
	less errlog.txt  | egrep -v "out of '%?'" | grep -v quantifier | grep -v initialized | grep -v Ambig | grep -v '%' > problemy.txt

all: batch1 batch2 merge



#batch1: batch1-induced-segmentations.tsv

#batch1-induced-segmentations.tsv: fixed-after-tests-by-ZZ.csv
#	cat fixed-after-tests-by-ZZ.csv | ./find-root-morphemes.pl > batch1-induced-segmentations.tsv 2>errlog1.txt

#pripravdruhoudavku:  # druha davka
#	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/druha-davka-koreny-def-anotace-od-Sarky.xls
#	./spoj-druhou-davku.pl > druha-davka-spojena.tsv


#batch2: batch2-induced-segmentations.tsv

#batch2-induced-segmentations.tsv: druha-davka-fixed-by-ZZ.csv
#	cat druha-davka-fixed-by-ZZ.csv | ./find-root-morphemes.pl > batch2-induced-segmentations.tsv 2> errlog2.txt

#%-by-ZZ.csv: ${INPUTDIR}/%-by-ZZ.xlsx
#	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . "$<"

#merge: induced-segmentations.tsv

#induced-segmentations.tsv: batch1-induced-segmentations.tsv batch2-induced-segmentations.tsv
#	cat batch1-induced-segmentations.tsv batch2-induced-segmentations.tsv > induced-segmentations.tsv

overlap:
	cat induced-segmentations.tsv | ./check_allomorph_overlaps.py | sort -nr


clean:
	rm -f *tsv *txt *csv
