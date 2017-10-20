INPUTDIR=/net/data/czeng10-public-release/data.export-format/
TMPDIR=/net/projects/tectomt_shared/tmp/
NUMBER=001
FORMAT=slex

x:

# preparing lemmas from CzEng

extract:
	zcat $(INPUTDIR)/*gz | cut -f3 | perl -ne 's/ /\n/g;print' | perl -ne 's/\|/\t/g;print' | cut -f2,3 \
	| perl -ne 'my ($$lemma,$$pos)=split;print "$$lemma\t".substr($$pos,0,1)."\n"'> lemmas_from_czeng.tsv

sort:
	cat lemmas_from_czeng.tsv | grep '[NDAV]$$' | sort > $(TMPDIR)/sorted_lemmas_from_czeng.tsv
	cat $(TMPDIR)/sorted_lemmas_from_czeng | uniq > $(TMPDIR)/unique_lemmas_from_czeng.tsv

# more general stuff

stats:
	./print_stats.pl $(TMPDIR)/$(NUMBER).tsv > $(NUMBER).stats


full:
	../derimor \
	CreateEmpty \
	CS::AddLexemesFromList file=$(TMPDIR)/unique_lemmas_from_czeng.tsv  \
	CS::AddOstLexemesFromCNC \
	CS::AddOstLexemesByRules \
	CS::AddAdj2AdvByRules \
	CS::AddManuallyConfirmedAutorules \
	CS::Prefixes \
	CS::AddDerivationsFromLemmaSuffices \
	Save file=fulltest.tsv

fullstats:
	../derimor \
	Load file=fulltest.tsv \
	PrintStats > stats.txt

	cat fulltest.tsv | cut -f8 | sort | uniq -c | sort -nr > stats-derivation-creator.txt


build2:
	../derimor \
	CreateEmpty \
	CS::AddLexemesFromList file=$(TMPDIR)/unique_lemmas_from_czeng.tsv maxlimit=5000  \
	CS::AddManuallyConfirmedAutorules \
	Save file=test.tsv

forannot:
	 time ../derimor Load file=fulltest.tsv  CS::ExtractCandidatesForUnexploitedRules | sort | uniq | sort -k7,9 > automaticti_degenerati_oprava.txt


ostita:
	../derimor Load file=fulltest.tsv CS::ExtractOst > ostita.tsv



# ------- all the stuff below is obsolete ----------

000:  # zalozeni slovniku mnozinou lemmat z CzEngu                                                                                                     
	@echo Initialize the dictionary by lemmas from CzEng, to be stored into $(TMPDIR)/000.$(FORMAT)
	./initialize.pl $(TMPDIR)/unique_lemmas_from_czeng.tsv $(TMPDIR)/$@.$(FORMAT)



001:  # pridani lemmat -ost z CNK
	@echo Adding -ost nouns from the Czech National Corpus
	./add_cnk_ost.pl $(TMPDIR)/000.$(FORMAT) $(TMPDIR)/$@.$(FORMAT)

002:  # pridani derivacnich vztahu podle suffixu JH's morfologie
	./add_relations_from_lemma_suffixes.pl $(TMPDIR)/001.$(FORMAT) $(TMPDIR)/$@.$(FORMAT)

003:  # pridani derivacnich vztahu podle pravidel pro -ost (v pripade potreby i zalozeni zdrojoveho lexemu)
	./add_relations_by_rules_for_ost.pl $(TMPDIR)/002.$(FORMAT) $(TMPDIR)/$@.$(FORMAT) > $@.log


004:  # pridani derivacnich vztahu podle pravidel pro a2d (v pripade potreby i zalozeni zdrojoveho lexemu)
	./add_relations_rules_a2d.pl $(TMPDIR)/003.$(FORMAT)  $(TMPDIR)/$@.$(FORMAT) > $@.log


rules:
	cat $(TMPDIR)/003.tsv | ././find_suffix_rules1.pl | cut -f1 | sort | uniq -c | sort -nr > rules.txt


test:
	./add_relations_from_automatic_rules.pl rules.txt pokus.$(FORMAT) pokus2.$(FORMAT)

004x:
	./add_relations_from_automatic_rules.pl rules.txt $(TMPDIR)/003.$(FORMAT)  $(TMPDIR)/$@.$(FORMAT) > $@.log



mluvnice:
	../derimor Load file=fulltest.tsv CS::ExtractCandidatesByMluvnice > mluvnice-kanidati.tsv

opak:
	cat mluvnice-kanidati.tsv | uniq > mluvnice-kandidati-bezopakovani.tsv
	cat mluvnice-kandidati-bezopakovani.tsv | perl -ne 's/\(.+//;print' | uniq | ./find_dupl.pl > duplicity.tsv

# pro anotaci z hesel vygenerovanych podle mluvnice
multisource:
	cat mluvnice-kandidati-bezopakovani.tsv | ./rozdelit_pro_anotaci.pl
	cat multisource.tsv | grep GROUP > multisource-groups.tsv

# --------------- vice kombinaci sad derivacnich pravidel a hlaskovych zmen najednou

mixed:
	../derimor Load file=fulltest.tsv CS::ExtractGeneralizedCandidatesByMluv > mluvnice-2nd-round-mixed.tsv

multisource_mixed:
	cat mluvnice-2nd-round-mixed.tsv | uniq > mluvnice-2nd-round-mixed-no-repet.tsv
	cat mluvnice-2nd-round-mixed-no-repet.tsv | grep 'subst2+spell1+spell2' | cut -f2 -s | ./rozdelit_pro_anotaci_podle_typu.pl 'subst2+spell1+spell'
	cat mluvnice-2nd-round-mixed-no-repet.tsv | grep 'subst1+spell2' | cut -f2 -s | ./rozdelit_pro_anotaci_podle_typu.pl 'subst1+spell2'
	cat mluvnice-2nd-round-mixed-no-repet.tsv | grep 'adj+spell1+spell2' | cut -f2 -s | ./rozdelit_pro_anotaci_podle_typu.pl 'adj+spell1+spell2'
	cat monosource_subst1+spell2.tsv | grep -E '(CHANGE|TRY)' >  monosource_subst1+spell2_newchangeonly.tsv
	cat multisource_subst1+spell2.tsv | ./filter_multisource_clusters_with_change.pl >  multisource_subst1+spell2_newchangeonly.tsv
