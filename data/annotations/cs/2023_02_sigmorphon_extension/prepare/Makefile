download:
	mkdir -p input_data
	mkdir -p input_data/sigmorphon2022
	git clone https://github.com/sigmorphon/2022SegmentationST.git input_data/sigmorphon2022
	mkdir -p input_data/ud/
	scp zabokrtsky@osiris.ms.mff.cuni.cz:/net/data/universal-dependencies-2.11/UD_Czech-PDT/cs_pdt-ud-train.conllu input_data/ud/

extract:
	./forms_from_ud_without_sigmorphon22.py > sigmorphon23-extension.tsv
