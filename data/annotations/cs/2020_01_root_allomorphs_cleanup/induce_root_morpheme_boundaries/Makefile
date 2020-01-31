SHELL := bash

INPUTDIR=../hand-annotated/

all: xlsx2csv induce overlap3 crossoverlap


xlsx2csv:
	libreoffice --convert-to csv --infilter=CSV:44,34,76,1 --headless  --outdir . ${INPUTDIR}/batch*.xlsx


#ind:
#	for i in {1..3}; do echo $$i; done



induce:
	for NUMBER in {1..3}; do cat batch$$NUMBER.csv | ./find-root-morphemes.pl > induced$$NUMBER.tsv 2> err-induced$$NUMBER.log; done



overlap3:
	cat induced3.tsv | ./check_allomorph_overlaps.py | sort -nr > overlaps-inside-batch3.tsv



crossoverlap: # overlap between 1+2 vs 3
	cat induced1.tsv | perl -ne 'print "1\t$$_"' > induced_union123.tsv
	cat induced2.tsv | perl -ne 'print "2\t$$_"' >> induced_union123.tsv
	cat induced3.tsv | perl -ne 'print "3\t$$_"' >> induced_union123.tsv

	cat  induced_union123.tsv | ./check_allomorph_overlaps_across_batches_only.py | sort -nr > crossoverlap_1+2_vs_3.tsv

clean:
	rm -f *tsv *txt *csv

endvowel:
	cat induced?.tsv | grep SEGMENTED | cut -f3 | egrep '[aeiyouáéíýóů]\)' > lemmas_with_end_vowel_root_morpheme.tsv
	cat lemmas_with_end_vowel_root_morpheme.tsv | perl -ne '/\((.+)\)/;print "$$1\n"' | sort | uniq -c | sort -nr > end_vowel_root_morphemes.tsv

