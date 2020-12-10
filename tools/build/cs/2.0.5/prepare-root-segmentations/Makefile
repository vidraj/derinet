# do 2.1 se oproti 2.0 pridavalo jeste jedno kolo rucnich anotaci hranic korenovych morfemu

INPUT=../../../../../data/annotations/cs/2020_01_root_allomorphs_cleanup/hand-annotated/batch3.xlsx

# tohle mi na olufsenovi nefunguje (ale na osirisovi jo), nevim proc, zatim to z libreoffice exportuju rucne, POZOR, pri rucnim exportu do csv je potreba zvolit quote all cells
batch3.csv: ${INPUT}
	cp ${INPUT} . # nechci znicit original
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ./batch3.xlsx

induced-segmentations.tsv: batch3.csv
	cat batch3.csv | egrep -v '^\".+"%' | ./find-root-morphemes.pl > induced-segmentations.tsv 2> errlog.txt

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
