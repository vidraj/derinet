stats:
	less lemmas_from_morfflex.tsv.xz | cut -f1 | perl -ne 's/_.+//;print' > /dev/null

	@echo "Pocet (kratkych) lemmat, u kterych je pouzite rozliseni cislickem"
	@less lemmas_from_morfflex.tsv.xz | grep -v Vm | cut -f1 | perl -ne 'print("$$1\n") if /^(\w+)\-/' | sort | uniq | wc -l

	@echo "Distribuce poctu cislicek na lemma"
	@less lemmas_from_morfflex.tsv.xz | grep -v Vm | cut -f1 | perl -ne 'print("$$1\n") if /^(\w+\-)/' | sort | uniq -c | sort -nr > prac 



test:
	@echo "Each full long lemma should be present only once"
	less lemmas_from_morfflex.tsv.xz | grep '1$$' | cut -f1 | sort | uniq -d | wc -l

	@echo "Each numbered lemma should be present only once"
	less lemmas_from_morfflex.tsv.xz | grep '1$$' | cut -f1 | perl -ne 's/_.+//;print'| sort | uniq -d | wc -l

masks:
	less lemmas_from_morfflex.tsv.xz | grep '1$$' | grep -v 'Vm\?' | grep '^[a-z]' | perl -ne 's/^(\S+?)[\-_]\S+/$$1/;print'| cut -f1,2 > malopismenne

x:
	cat malopismenne | ./najdi_ntice_masek.pl > homonymie_malopismennych

freq:
	cat homonymie_malopismennych | cut -f2 | sort | uniq -c | sort -nr > freq_masek_malopismennych.txt


