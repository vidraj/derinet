SHELL=/bin/bash


derinet-lemmaset.tsv:
	zcat ../../../../releases/cs/derinet-2-0.tsv.gz | cut -f 3 | sort | uniq | tail -n +2 > derinet-lemmaset.tsv

derinet-roots.tsv:
	zcat ../../../../releases/cs/derinet-2-0.tsv.gz | grep '^[0-9]*\.0' | cut -f3 | sort | uniq | tail -n +1 > derinet-roots.tsv

prefixation.tsv: derinet-lemmaset.tsv derinet-roots.tsv
	python3 find_prefixation.py prefixes.tsv derinet-lemmaset.tsv derinet-roots.tsv > prefixation.tsv

postprocessing:
	cat ../hand-annotated/prefixation.tsv | grep ^\+ | cut -c2- | sed 's/^\t//g' > ../into-derinet/prefixed-relations.tsv

clean:
	rm derinet-lemmaset.tsv derinet-roots.tsv prefixation.tsv
