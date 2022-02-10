#5k je toho dohromady
#1000 uniformně + 1100 frekvenčně samplovaných lemmat
#https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2020_04_complete_morphseg/prepare/union-2100-segmented.tsv
#1000 lemmat samplovaných po pásmech
#https://raw.githubusercontent.com/vidraj/derinet/master/data/annotations/cs/2021_05_complete_morphseg_bandsampling/zatim_vyreseno.tsv

#formy jsem bral z něj, ale ne všechny tam jsou pořešený. Tady je to vybraný:
#2000 forem po pásmech
#https://github.com/vidraj/derinet/blob/master/data/annotations/cs/2021_11_complete_morphseg-forms_bandsampling/zatim_vyreseno.tsv



collectinputs:
	mkdir -p inputs
	cp ../collect_existing/slavickova/normalized_slav_verbs.txt inputs//normalized_slav_verbs.tsv
	cp ../collect_existing/ostrava/normalized-MorfoCzech_dictionary.csv inputs/normalized-MorfoCzech_dictionary.tsv
#	cat ../ud/generated/ud_wordlist_for_annot.tsv

	cat ../../../2021_11_complete_morphseg-forms_bandsampling/zatim_vyreseno.tsv | cut -f4 | perl -ne 's/[- ]+/-/g;s/[+]//g;s/-0//g;print '> inputs/our-2k-bandsample-lemmas.tsv
	cat ../../../2021_11_complete_morphseg-forms_bandsampling/zatim_vyreseno.tsv | cut -f2 | perl -ne 's/[- ]+/-/g;s/[+]//g;s/-0//g;print '> inputs/our-2k-bandsample-forms.tsv
	cat ../../../2020_04_complete_morphseg/prepare/union-2100-segmented.tsv | grep -v '???' | cut -f4 | sed 's/ /-/g' > inputs/our-2.1k-uniffreqsample-lemmas.tsv
	cat ../../../2021_05_complete_morphseg_bandsampling/zatim_vyreseno.tsv | cut -f2 | sed 's/ /-/g' > inputs/our-1k-bandsample-lemmas.tsv


forannot:
	cat inputs/*tsv | sed 's/-//g' | sort | uniq > tmp-union-of-segmented.tsv

	cat ud/generated/ud_wordlist_for_annot.tsv tmp-union-of-segmented.tsv | sort | uniq -d > tmp-intersection.tsv

	cat ud/generated/ud_wordlist_for_annot.tsv  tmp-intersection.tsv  | sort | uniq -u | ../ud/retrosort.py > ud-forms-for-annot.tsv


homo:
	#cat ud/conllu/cs_pdt-ud-dev.conllu | ud/first_n_sentences.py  500 > tmp_form_homo.conllu
	#cat ud/conllu/cs_pdt-ud-test.conllu | ud/first_n_sentences.py  500 >> tmp_form_homo.conllu
	#cat ud/conllu/cs_pdt-ud-train.conllu | ud/first_n_sentences.py  1000 >> tmp_form_homo.conllu

	#cat tmp_form_homo.conllu | ./find_crosspos_homonyms.py  > cross_pos_homonyms.tsv

	cat ud/conllu/*.conllu | ./find_crosspos_homonyms.py  > cross_pos_homonyms.tsv
