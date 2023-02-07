SHELL=/bin/bash

derinet:='../../../../releases/cs/derinet-2-1.tsv.gz'
ssjc:='ssjc.tgz'
enwikti:='enwiktionary-20230201-pages-meta-current.xml.bz2'

# only at UFAL network
# derinet:='../../../../releases/cs/derinet-2-1.tsv.gz'
# ssjc:='/net/data/ssjc/ssjc.tgz'
# enwikti:='/net/data/wiktionary/enwiktionary-20230201-pages-meta-current.xml.bz2'

# 1. extract compounds from SSJČ
resulting-data/extracted-compounds-from-ssjc.tsv:
	zcat ${ssjc} > ssjc.xml
	python3 extract_from_ssjc.py --input 'ssjc.xml' --output 'extracted.tsv'
	sort 'extracted.tsv' | uniq > 'resulting-data/extracted-compounds-from-ssjc.tsv'
	rm -f 'extracted.tsv' 'ssjc.xml'

# 2. extract compounds from EN-Wiktionary
resulting-data/extracted-compounds-from-enwiktionary.tsv:
	python3 extract_from_enwiktionary.py --input ${enwikti} --output 'extracted.tsv'
	sort 'extracted.tsv' | uniq > 'resulting-data/extracted-compounds-from-enwiktionary.tsv'
	rm -f 'extracted.tsv'

# 3. compare to DeriNet
