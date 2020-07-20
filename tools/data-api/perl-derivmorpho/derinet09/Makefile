BASE::=derinet09

# Alternatives: morfflex syn
LEMMAS_SOURCE::=morfflex

# Alternatives: lemmas_from_morfflex.tsv lemmas_from_syn.tsv
LEMMAS::=lemmas_from_${LEMMAS_SOURCE}.tsv

# ../data/morfflex-cz.2013-11-12.utf8.lemmaID_suff-tag-form.tab.csv.xz
#MORFFLEX::=../data/morfflex-cz.2016-03-10.utf8.lemmaID_suff-tag-form.tab.csv.xz
#MORFFLEX::=../data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz
MORFFLEX?=../data/morfflex-cz.2016-11-15.utf8.lemmaID_suff-tag-form.tab.csv.xz

DERIMOR_MAIN_DIR?=$(CURDIR)/..
export DERIMOR_MAIN_DIR

.PHONY: all slex diff stats clean

all: $(BASE).tsv

slex: $(BASE).slex

lemmas_from_syn.tsv: ../data/pro-zdenka-syn-lemata-od-ondreje.gz ./select_syn_lemmas.pl
	zcat $< | grep '[ANDV]$$' | ./select_syn_lemmas.pl > $@

lemmas_from_morfflex.tsv: ${MORFFLEX} ./select_morfflex_lemmas.pl lemmas-to-ignore.tsv
	xz -dkvvc $< | ./select_morfflex_lemmas.pl --ignore-list lemmas-to-ignore.tsv > $@

sorted_lemmas.tsv: ${LEMMAS} ./remove_false_homonyms.pl ../data/straka_same_lemma_sense_classes.txt
	./remove_false_homonyms.pl < "$<" | sort > $@

# This target reads the extra words that should be inserted into the database
#  and guesses their techlemmas and POS-tags. These guesses then have to be
#  manually desambiguated and saved to extra_lemmas.tsv
extra_lemmas.tsv: extra_words.txt ./words_to_lemmas.pl ./select_morfflex_lemmas.pl ./remove_false_homonyms.pl ../data/straka_same_lemma_sense_classes.txt
	./words_to_lemmas.pl < "$<" | ./select_morfflex_lemmas.pl | ./remove_false_homonyms.pl | sort > $@

otaznickovi.tsv: ../data/annotated_cleaned_otaznickovi_kandidati.tsv ./priprav_otaznickove.pl # zz otaznikovi potvrzeni
	grep -v POSSIBLE $< | ./priprav_otaznickove.pl | sort | uniq > $@

phantom_lexemes.tsv: ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/hand-checked-phantoms-to-be-added-to-2.0
	cut -f2 "$<" | sort -u | sed -e 's/$$/	V/' | ./words_to_lemmas.pl | ./select_morfflex_lemmas.pl | ./remove_false_homonyms.pl | sort > "$@"

../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/hand-checked-phantoms-to-be-added-to-2.0: ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/potential-new-pairs.tsv
	$(MAKE) -C ../../../../data/annotations/cs/2019_05_phantom_lexemes/annotated/ handchecked

$(BASE).tsv $(BASE).slex: sorted_lemmas.tsv extra_lemmas.tsv otaznickovi.tsv one_off_derivations.tsv phantom_lexemes.tsv
	../derimor \
	CreateEmpty \
	CS::AddLexemesFromList file=sorted_lemmas.tsv dictionary_name=$(LEMMAS_SOURCE) \
	CS::AddLexemesFromList file=extra_lemmas.tsv dictionary_name=manual verify_lemma_uniqueness=1 \
	CS::AddLexemesFromList file=phantom_lexemes.tsv dictionary_name=phantoms verify_lemma_uniqueness=1 \
	CS::AddOstLexemesFromCNC \
	CS::AddOstLexemesByRules \
	CS::AddAdj2AdvByRules \
	CS::AddManuallyConfirmedAutorules \
	CS::Prefixes \
	CS::AddDerivationsFromLemmaSuffices \
	CS::ReconnectVerbalDerivatives aggressive=1 \
	CS::AddManuallyConfirmedAutorules2 \
	CS::AddManuallyConfirmedAutorules rules=morfflex-new-autorules-rules.txt instances=morfflex-new-autorules-instances.txt \
	CS::AddConfirmedMluvCandidatesMonosource \
	CS::RevertDerivationDirection \
	CS::RestructureClusters \
	CS::AddOrDeleteLinksInClusters \
	CS::AddDerivationsFromList file=otaznickovi.tsv \
	CS::AddDerivationsFromList file=one_off_derivations.tsv \
	Save file=$@ >log.txt 2>&1

diff: lemmas_from_morfflex.tsv lemmas_from_syn.tsv
	./diff_syn_morfflex.sh > lemmas_diff.txt

stats:
	../derimor \
	Load file=$(BASE).tsv \
	PrintStats > stats.txt

	cat $(BASE).tsv | cut -f8 | sed -e 's/.*\(CS::[^:[]\+\).*/\1/' | sort | uniq -c | sort -nr > stats-derivation-creator.txt

ost-added-lexemes.txt: log.txt
	# Print all adjectival lexemes added (and then derived into -ost nouns) by AddOstLexemes…
	sed -ne '/NEW LEXEME CREATED:/ b nprint; d; :nprint; n; s/^.*Adding derivation //; p' "$<" > "$@"
	#sed -ne '/NEW LEXEME CREATED/ b print ; d ; : print ; N ; p' "$<" > "$@"

clean:
	rm -f lemmas_from_syn.tsv sorted_lemmas.tsv extra_lemmas.tsv otaznickovi.tsv $(BASE).tsv $(BASE).slex log.txt stats.txt stats-derivation-creator.txt lemmas_diff.txt
	rm -f phantom_lexemes.tsv
	rm -f lemmas_from_morfflex.tsv
