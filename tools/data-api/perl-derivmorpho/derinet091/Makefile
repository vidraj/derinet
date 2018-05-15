BASE::=derinet091
.PHONY: all slex stats clean

all: $(BASE).tsv

slex: $(BASE).slex

$(BASE).tsv $(BASE).slex: $(BASE).%: ../derinet09/derinet09.% spravena_anotace_z_19_lenda_2015
	../derimor \
	Load file=$< \
	CS::AddConfirmedMluvCandidatesMonosource file=spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv \
	CS::AddConfirmedMluvCandidatesMonosource file=anotace_od_magdy_19_leden_2015/monosource_adj+spell1+spell2.csv \
	CS::AddConfirmedMluvCandidatesMonosource file=anotace_od_magdy_19_leden_2015/monosource_subst1+spell2_newchangeonly.csv \
	CS::AddConfirmedMluvCandidatesMonosource file=anotace_od_magdy_19_leden_2015/monosource_subst2+spell1+spell.csv \
	CS::RestructureClusters file=spravena_anotace_z_19_lenda_2015/multisource_adj+spell1+spell2.csv \
	CS::RestructureClusters file=anotace_od_magdy_19_leden_2015/multisource_subst1+spell2.csv \
	CS::RestructureClusters	file=anotace_od_magdy_19_leden_2015/multisource_subst1+spell2_newchangeonly.csv \
	CS::RestructureClusters	file=anotace_od_magdy_19_leden_2015/multisource_subst2+spell1+spell.csv \
	CS::RevertDerivationDirectionSpecial file=spravena_anotace_z_19_lenda_2015/obratit.txt \
	CS::AddConfirmedMluvCandidatesMonosource file=spravena_anotace_z_19_lenda_2015/RESTRUCTURE.csv \
	Save file=$@ >log.txt 2>&1

spravena_anotace_z_19_lenda_2015:
	mkdir -p spravena_anotace_z_19_lenda_2015

	./turn_deleted_line_to_asterisk.pl anotace_od_magdy_19_leden_2015/k_RESTRUCTURE-ALE-PROMAZANO.csv anotace_od_magdy_19_leden_2015/RESTRUCTURE-ALE-PROMAZANO.txt > spravena_anotace_z_19_lenda_2015/RESTRUCTURE.csv

	./turn_deleted_line_to_asterisk.pl anotace_od_magdy_19_leden_2015/k_OBRATIT-ALE-PROMAZANO.csv anotace_od_magdy_19_leden_2015/OBRATIT-ALE-PROMAZANO.txt > tmp.txt
	cat anotace_od_magdy_19_leden_2015/OBRATIT-SMER* tmp.txt > spravena_anotace_z_19_lenda_2015/obratit.txt

	@echo
	@echo Fixing monosource_subst1+spell2

	./turn_deleted_line_to_asterisk.pl anotace_od_magdy_19_leden_2015/ke_SMAZANO-MISTO-HVEZDICEK_monosource_subst1+spell2.csv anotace_od_magdy_19_leden_2015/SMAZANO-MISTO-HVEZDICEK_monosource_subst1+spell2.txt > spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv
	cat anotace_od_magdy_19_leden_2015/monosource_subst1+spell2.csv >> spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv
	cp spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv tmp.txt
	cat tmp.txt |  ./jednoudobryvzyckydobry.pl > spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv
	rm tmp.txt

	@echo
	@echo Fixing adj+spell1+spell2.csv

	./turn_deleted_line_to_asterisk.pl anotace_od_magdy_19_leden_2015/ke_SMAZANO-MISTO-HVEZDICEK_multisource_adj+spell1+spell2.csv anotace_od_magdy_19_leden_2015/SMAZANO-MISTO-HVEZDICEK_multisource_adj+spell1+spell2.txt > spravena_anotace_z_19_lenda_2015/multisource_adj+spell1+spell2.csv
	cat anotace_od_magdy_19_leden_2015/multisource_adj+spell1+spell2.txt >> spravena_anotace_z_19_lenda_2015/multisource_adj+spell1+spell2.csv

phonological-changes.txt: spravena_anotace_z_19_lenda_2015
	cat spravena_anotace_z_19_lenda_2015/monosource_subst1+spell2.csv anotace_od_magdy_19_leden_2015/monosource_adj+spell1+spell2.csv anotace_od_magdy_19_leden_2015/monosource_subst1+spell2_newchangeonly.csv anotace_od_magdy_19_leden_2015/monosource_subst2+spell1+spell.csv spravena_anotace_z_19_lenda_2015/RESTRUCTURE.csv |grep CHANGE |grep -v '^\*' |sed -e 's/.*(CHANGE: \([^)]* -> [^)]*\)).*/\1/' |sort |uniq -c |sort -rn > "$@"

stats:
	../derimor \
	Load file=$(BASE).tsv \
	PrintStats > stats.txt

	cat $(BASE).tsv | cut -f8 | sed -e 's/.*\(CS::[^:[]\+\).*/\1/' | sort | uniq -c | sort -nr > stats-derivation-creator.txt

clean:
	rm -rf spravena_anotace_z_19_lenda_2015 $(BASE).tsv $(BASE).slex log.txt stats.txt stats-derivation-creator.txt
