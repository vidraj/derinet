.PHONY: all clean

SYN=/net/data/CNK/syn_v9/syn_v9.xz

all: syn-v9-lemma-freq.tsv.xz

syn-v9-form-freq.tsv.xz: $(SYN)
	xz -dvvvc '$<' | cut -sf2 | python3 count.py | xz -zvvv4T8 > '$@'

syn-v9-lemma-freq.tsv.xz: syn-v9-lemma-tag-counts.tsv.xz
	xz -dvvvc '$<' | python3 sum-by-lemid.py | xz -z4T8 > '$@'

syn-v9-lemma-tag-counts.tsv.xz: $(SYN)
	xz -dvvvc '$<' | cut -sf3-5 | python3 count.py | xz -zvvv4T8 > '$@'

clean:
	rm -f syn-v9-form-freq.tsv.xz syn-v9-lemma-freq.tsv.xz syn-v9-lemma-tag-counts.tsv.xz
