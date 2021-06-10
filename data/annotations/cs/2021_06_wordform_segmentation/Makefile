merge:
	cat frequency_sampling_of_words2-bez_opakovani-* | perl -ne 'chomp;/(.+);(.+)\s+/;print"$$2\t$$1\n"' | rev | sort | rev | cut -f2,1 | perl -ne 'chomp;/(.+)\s(.+)/;print"$$2\t$$1\n"' > wordformseg.txt
