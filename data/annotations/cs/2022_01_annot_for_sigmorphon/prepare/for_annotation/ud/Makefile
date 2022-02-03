download:
	mkdir -p conllu
	scp zabokrtsky@osiris.ms.mff.cuni.cz:/net/data/universal-dependencies-2.9/UD_Czech-PDT/*conllu conllu/


select:
	mkdir -p generated
	cat conllu/cs_pdt-ud-train.conllu | ./first_n_sentences.py 1000 > generated/train.conllu
	cat conllu/cs_pdt-ud-test.conllu | ./first_n_sentences.py 500 > generated/test.conllu
	cat conllu/cs_pdt-ud-dev.conllu | ./first_n_sentences.py 500 > generated/dev.conllu

wordlist:
	cat generated/*conllu | egrep -v '^#' | grep .| cut -f2 | sort | uniq > generated/ud_wordlist_raw.tsv
	cat generated/ud_wordlist_raw.tsv | ./retrosort.py >   generated/ud_wordlist_for_annot.tsv


# dvouznakove
#less generated/*.conllu | cut -f2 | grep . | egrep '^..$' | egrep -v '[0-9]' | perl -ne 'print(lc())' | sort | uniq -c | sort -nr | perl -ne 's/^\s+//;chomp;s/ /\t/;print($_."\n")' > dvouznakove.tsv
