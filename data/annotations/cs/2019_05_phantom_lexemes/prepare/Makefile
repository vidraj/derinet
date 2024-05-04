extract: 
	PYTHONPATH=../../../../../tools/data-api/derinet2 python3 -m derinet.process_scenario \
	Load -f DERINET_V1 ../../../../releases/cs/derinet-1-7.tsv  \
	cs.ExtractPhantomsChildren phantom_lemmas_from_ssjc.txt > potential-phantoms-children.tsv

finalize:
	cat potential-phantoms-children.tsv | cut -f2,3 > potential-new-pairs.tsv
