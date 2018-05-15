extract_only_compounds:
	cat derinet-1-4_compounds_marked.tsv | grep [ANDV]C | cut -f2,3,4 > only_compounds.tsv

test_length:
	cat only_compounds.tsv | perl -ne 'print length($$_)."\t$$_"' | sort -n | less

test_cky:
	cat only_compounds.tsv | grep DC |  grep cky

test_re: # svetlemodre, veledobre
	cat only_compounds.tsv | grep DC |  perl -ne 'print if /ře\t/' 
