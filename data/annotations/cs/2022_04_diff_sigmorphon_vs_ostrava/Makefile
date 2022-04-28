OSTRAVA=../2022_01_annot_for_sigmorphon/prepare/collect_existing/ostrava/normalized-MorfoCzech_dictionary.csv

SIGMORPHON = ../../../../data/annotations/cs/2022_01_annot_for_sigmorphon/merge-all/all-for-revision4.tsv

run:
	./find-differences.py $(OSTRAVA) $(SIGMORPHON)  > differences-ostrava-sigmorphon.tsv
	cat differences-ostrava-sigmorphon.tsv | sort -k 2 > retrogr-differences-ostrava-sigmorphon.tsv

	cat differences-ostrava-sigmorphon.tsv | ./aggregate-differences.py > cetnosti-rozdilu-s-priklady.tsv
	cat cetnosti-rozdilu-s-priklady.tsv | grep . | cut -f1,2 > cetnosti-rozdilu-bez-prikladu.tsv
