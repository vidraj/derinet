merge:
	./merge.py  > all-for-revision3.tsv


sourcestats:

	cat all-for-revision3.tsv | cut -f4 | sort | uniq -c | sort -nr > source-freq.txt
	cat all-for-revision3.tsv | cut -f3 | sed 's/-/\n/g' | sort | uniq -c | sort -nr > morpheme-freq.txt


inconsist:
	cat all-for-revision3.tsv | ./find_inconsist_beginning.py > beginning_inconsist.tsv
	cat all-for-revision3.tsv | LC_ALL=cs_CZ.UTF-8 sort -k2 | ./find_inconsist_end.py > end_inconsist.tsv


test:
	cat all-for-revision3.tsv | ./check_equality.py
