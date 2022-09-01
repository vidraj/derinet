merge:
	mkdir -p tmp
	cut -f1-3 first_annotations/cristina-eng.tsv | perl -ne 's/\s+$$//;print("$$_\n")' > tmp/cristina.tmp
	cut -f3-4 first_annotations/sarka-eng.tsv | perl -ne 'chomp;print("$$_\n")' > tmp/sarka.tmp
	paste tmp/cristina.tmp tmp/sarka.tmp | ./compare.py | grep CMP > rozdily.tsv
