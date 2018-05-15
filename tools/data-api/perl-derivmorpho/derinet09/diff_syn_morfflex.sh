#!/bin/sh

cat lemmas_from_syn.tsv |./cut_tech_suffixes.pl |sort |uniq > syn.tsv
cat lemmas_from_morfflex.tsv |./cut_tech_suffixes.pl |sort |uniq > morfflex.tsv

echo -ne 'Common lemmas:\t'
#diff --unchanged-line-format='%L' --old-line-format= --new-line-format= syn.tsv morfflex.tsv > common.tsv
#grep -Fxf syn.tsv morfflex.tsv > common.tsv
comm -12 syn.tsv morfflex.tsv > common.tsv
wc -l common.tsv

echo -ne 'DeriNet only:\t'
#diff --unchanged-line-format= --old-line-format='%L' --new-line-format= syn.tsv morfflex.tsv > onlysyn.tsv
#grep -Fxvf morfflex.tsv syn.tsv > onlysyn.tsv
comm -23 syn.tsv morfflex.tsv > onlysyn.tsv
wc -l onlysyn.tsv

echo -ne 'MorfFlex only:\t'
#diff --unchanged-line-format= --old-line-format= --new-line-format='%L' syn.tsv morfflex.tsv > onlymorfflex.tsv
#grep -Fxvf syn.tsv morfflex.tsv > onlymorfflex.tsv
comm -13 syn.tsv morfflex.tsv > onlymorfflex.tsv
wc -l onlymorfflex.tsv

# rm syn.tsv morfflex.tsv
