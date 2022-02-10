merge:
	./merge.py  > all-for-revision2.tsv


sourcestats:

	cat all-for-revision2.tsv | cut -f4 | sort | uniq -c | sort -nr


inconsist:
	cat all-for-revision2.tsv | ./find_inconsist_beginning.py > beginning_inconsist.tsv
	cat all-for-revision2.tsv | LC_ALL=cs_CZ.UTF-8 sort -k2 | ./find_inconsist_end.py > end_inconsist.tsv


test:
	cat all-for-revision2.tsv | ./check_equality.py
