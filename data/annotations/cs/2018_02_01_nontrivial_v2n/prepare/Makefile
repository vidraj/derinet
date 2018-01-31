

extract:
	xzcat glm-1-5-1-filtered.tsv.xz | perl -ne 'print if s/\s+OLD:  $$//' | grep -v ';S' | grep -v -e ';[GSY]'  | perl -ne 'print if / N\t.+V$$/' > odjonase.tsv

merge:
	./merge.pl > nontrivial-v2n-merged-magda-jonas.tsv
