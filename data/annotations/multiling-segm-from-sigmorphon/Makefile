sigmoclone:
	mkdir -p tmp/
	git clone https://github.com/sigmorphon/2022SegmentationST.git tmp/


select:
	mkdir -p selection/

	 for LANG in eng rus spa ita fra lat; do ./select-random-n-lines.py tmp/data/$${LANG}.word.train.tsv 1000 | cut -f1 > selection/$${LANG}-random-1000-from-sigmorphon-train.tsv ; done
