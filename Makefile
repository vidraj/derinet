
SHELL=/bin/bash

release:
	wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1807/derinet-1-2.tsv
	python3 import_data.py > release.log
