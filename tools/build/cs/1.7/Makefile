.PHONY: stats clean

derinet-1-7.tsv: derinet-1-6.tsv
	PYTHONPATH=../../../data-api/derinet2 python3 -m derinet.process_scenario \
		--data-version=1.7 \
		Load -f DERINET_V1 "$<" \
		cs.DeleteDerivations delete_rel.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der5001-6000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der6001-7000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/der7001-8036.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-0001-0500.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-0501-1000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-1001-1500.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-1501-2000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-2001-2500.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-2501-3000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-3001-3500.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_04_wiktionary/hand-annotated/more-der-3501-3728.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der-0001-1000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der-1001-2000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der-2001-3000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der-3001-4000.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-one-der-4001-4616.tsv \
		cs.AddWiktionarySsjcAnnot ../../../../data/annotations/cs/2018_06_ssjc/hand-annotated/ssjc-more-der-0001-0500.tsv \
		cs.CheckCompoundMarks \
		Save "$@" 2>log

derinet-1-6.tsv: ../1.6/derinet-1-6.tsv
	cp -a "$<" "$@"

clean:
	rm -f log derinet-1-6.tsv derinet-1-7.tsv
