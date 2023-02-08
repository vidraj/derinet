download:
	mkdir -p input_data
	mkdir -p input_data/sigmorphon2022
	git clone https://github.com/sigmorphon/2022SegmentationST.git input_data/sigmorphon2022
	mkdir -p input_data/ud/
	scp zabokrtsky@osiris.ms.mff.cuni.cz:/net/data/universal-dependencies-2.11/UD_Czech-PDT/cs_pdt-ud-train.conllu input_data/ud/
	mkdir -p input_data/derinet/
	wget -P input_data/derinet/  https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3765/derinet-2-1.tsv

extract:
	mkdir -p tmp

	# (A) compounds to be added, around 5k

	# priority 1: all compounds that have both (or more) parents already recognized in DeriNet 2.1, and that are corpus attested at the same time, 1747 cases
	cat input_data/derinet/derinet-2-1.tsv | grep Compounding | ./prepend_abs_count.pl | grep -v "^0" | cut -f4 > tmp/compounds__Type=Compounding__CNK-attested.tsv

	# priority 2: all (mostly inflected) forms of compounds from the PDT
	cat input_data/derinet/derinet-2-1.tsv | grep is_compound | grep -v Compounding | cut -f3 > tmp/all_compounds_from_derinet.tsv
	cat input_data/ud/cs_pdt-ud-train.conllu | ./from_connlu_select_lemmas.py tmp/all_compounds_from_derinet.tsv | cut -f2 | sort | uniq > tmp/compounds__is_compound_from_derinet_as_lemma_in_pdt

	# priority 3: fill the rest (up to total around 5k) by the most frequent compounds from DeriNet
	cat input_data/derinet/derinet-2-1.tsv | grep is_compound | grep -v Compounding | ./prepend_abs_count.pl | sort -nr | cut -f4 | perl -ne 'print(lc())' | head -n 1900 > tmp/compounds__from_derinet_by_frequency.tsv

	cat input_data/sigmorphon2022/data/ces.word.*tsv | cut -f1 | sort | uniq > tmp/all_forms_from_sigmorphon.tsv	

	cat tmp/compounds__* | sort | uniq | ./subtract.py tmp/all_forms_from_sigmorphon.tsv | sort | uniq > tmp/compounds__selection.tsv

	@echo Number of compounds:
	@wc -l tmp/compounds__selection.tsv

	# (B) roots lemmas to be added (lemmas of roots of deriv. trees), around 5k
	# most CNC-frequent root lemmas
	less input_data/derinet/derinet-2-1.tsv | perl -ne 'print if /^\d+\.0/' | grep -v Fictiti | grep -v is_compound |  ./prepend_abs_count.pl | sort -nr | cut -f4 |./subtract.py tmp/all_forms_from_sigmorphon.tsv |  ./subtract.py tmp/compounds__selection.tsv | head -n 5400 | sort | uniq > tmp/roots__selection.tsv

	# (C) and the last 5k added from PDT sentences
	# (running text from the beginning of train)
	cat input_data/ud/cs_pdt-ud-train.conllu | grep . | grep -v '\#' | grep -v PUNCT | grep -v NUM | cut -f2 | grep ... | perl -ne 'print(lc())' | head -n35000 | sort | uniq | ./subtract.py tmp/all_forms_from_sigmorphon.tsv | ./subtract.py tmp/compounds__selection.tsv | ./subtract.py tmp/roots__selection.tsv | sort | uniq > tmp/pdt_running_text__selection.tsv


finalize:
	mkdir -p for_annotation
	cat tmp/*selection.tsv | perl -ne  's/(.+)/$$1\t$$1/;print' | ./add_reverted_first_column.py > for_annotation/sigmorphon23-new-extension.tsv

	cat input_data/sigmorphon2022/data/ces.word.train.tsv input_data/sigmorphon2022/data/ces.word.dev.tsv input_data/sigmorphon2022/data/ces.word.test.gold.tsv| sed 's/ @@/ /g' | sort | uniq | ./add_reverted_first_column.py > for_annotation/sigmorphon22-all.tsv


clean:
	rm tmp/*

#	./forms_from_ud_without_sigmorphon22.py > sigmorphon23-extension.tsv
