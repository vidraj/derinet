all: download normalize

download:
	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-4626{/MorfoCzech_dictionary.csv}

normalize:

	cat MorfoCzech_dictionary.csv | ./phono-to-text.py | sort | uniq > normalized-MorfoCzech_dictionary.csv
