all:
	cat ../hand_annotated/new_compounds.tsv | perl -ne 'print if /(\S+\t){3}\S+ / ' | cut -f4 | sed 's/ /\n/g' | sort | uniq -c | sort -nr > morphs_by_freq.tsv
	cat morphs_by_freq.tsv | perl -ne 'print "$$2\t$$1\n" if /(\d+)\s+(\S+)/' | sort > morphs_by_alphabet.tsv

	cat morphs_by_alphabet.tsv | cut -f1 | perl -ne 'print length($$_)-1; print "\t$$_"' | sort -nr > morphs_by_length.tsv


	cat ../hand_annotated/*tsv | ./merge.py > all_for_revision1.tsv

	cat all_for_revision1.tsv | LC_ALL=cs_CZ.UTF-8 sort -k1 |./find_inconsist_beginning.py > beginning_inconsist.tsv
	cat all_for_revision1.tsv | LC_ALL=cs_CZ.UTF-8 sort -k2 | ./find_inconsist_end.py > end_inconsist.tsv
