SHELL=/bin/bash


# list of lemmas with automatically assigned loanword marks
derinet-lemmaset-with-loanword-marks.tsv:
	zcat ../../../releases/cs/derinet-2-0.tsv.gz | cut -f 3,4 | sed 's/\t/_/g' | grep -v $$'^$$' | sort | uniq > derinet-lemmaset.tsv
	cat derinet-lemmaset.tsv | python3 recogFW.py > lemmaset-with-loanword-marks.tsv
	paste <(cat lemmaset-with-loanword-marks.tsv | cut -f 1) \
		  <(cat derinet-lemmaset.tsv | cut -d'_' -f2) \
		  <(cat lemmaset-with-loanword-marks.tsv | cut -f 2) > derinet-lemmaset-with-loanword-marks.tsv


derinet-2-0.tsv:
	zcat ../../../releases/cs/derinet-2-0.tsv.gz > derinet-2-0.tsv

# automatic editation of automatically assigned loanwordmarks to do the annotation more correct and consistent
loanwords-trees-for-annotation.tsv: derinet-lemmaset-with-loanword-marks.tsv derinet-2-0.tsv
	python3 filter_marks.py --DeriNet derinet-2-0.tsv \
							--Loanwords derinet-lemmaset-with-loanword-marks.tsv \
							--Output loanwords-trees-for-annotation.tsv
