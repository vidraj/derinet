VERSION::=1-5-6
DERINET::=derinet-$(VERSION).tsv

.PHONY: all release stats clean

# The annotation file to use when measuring precision and recall in target `stats-$(VERSION).txt`
ANNOT::=$(CURDIR)/../../../data/annotations/cs/2015-07-gold-standard/annot-devel.tsv

# Perl `derimor` setup.
# Make sure that $(CURDIR) is evaluated and not referenced here!
export DERIMOR_MAIN_DIR::=$(CURDIR)/../../data-api/perl-derivmorpho/
export PERL5LIB::=$(DERIMOR_MAIN_DIR)/lib:$(PERL5LIB)

all: $(DERINET)
release: $(DERINET)

# Copy the final database from the last version to the current directory.
$(DERINET): 1.5/derinet-1-5.tsv
	cp -a "$<" "$(DERINET)"

# The main target. Successively build all versions from oldest to newest.
# Be aware that this doesn't propagate dependency information and that it
#  inherently serializes the build. Recursive make is considered harmful for
#  a good reason. Therefore, `make clean` if you make changes in subdirs but
#  insist on running `make` from this main directory.
1.5/derinet-1-5.tsv:
	$(MAKE) -C ../../data-api/perl-derivmorpho derinet-1-3.tsv
	$(MAKE) -C 1.3 derinet-1-3.tsv
	$(MAKE) -C 1.4 derinet-1-4.tsv
	$(MAKE) -C 1.5 derinet-1-5.tsv


# Gather some statistics on precision, recall and database structure.
# Requires the old `derimor` Perl API.
stats: stats-$(VERSION).txt
stats-%.txt: derinet-%.tsv
	../../data-api/perl-derivmorpho/derimor \
	CreateEmpty \
	Load file="$<" \
	MeasurePrecisionRecall file="${ANNOT}" \
	PrintStats singletons_file="singletons-$*.tsv" > "$@" 2>&1


# Find all lemmas that are in the database multiple times.
homonymous-lemmas-pos.tsv:$(DERINET)
	cut -f2,4 "$<" |sort |uniq -c |sort -rn |grep -v '^[[:space:]]*1[[:space:]]' |sed -e 's/^.*[0-9] //' > "$@"

# Find all lexemes whose lemmas are in the database multiple times.
homonymous-lexemes-pos.tsv: homonymous-lemmas-pos.tsv
	sed -e 's/^\([^	]*\)	/	\1	[^	]*	/' "$<" | grep -f - "$(DERINET)" > "$@"

# Find all lemma+POS combinations that are in the database multiple times.
homonymous-lemmas.tsv:
	cut -f2 "$(DERINET)" |sort |uniq -c |sort -rn |grep -v '^[[:space:]]*1[[:space:]]' |sed -e 's/^.*[0-9] //' > "$@"

# Find all lexemes whose lemma+POS combinations are in the database multiple times.
homonymous-lexemes.tsv: homonymous-lemmas.tsv
	sed -e 's/^/	/; s/$$/	/' "$<" | grep -f - "$(DERINET)" > "$@"



# Find all nouns that end in -ý.
# Many of these are actually adjectives, just marked wrong.
nouns-ý.tsv:
	grep 'ý [^	]*	N' "$(DERINET)" > "$@"

# Find all nouns starting with a lowercase letter that end in -ý.
nouns-ý-lowercase.tsv: nouns-ý.tsv
	cat "$<" |grep '^[0-9]*	[^[:upper:]]' > "$@"


clean:
	$(MAKE) -C ../../data-api/perl-derivmorpho clean
	$(MAKE) -C 1.3 clean
	$(MAKE) -C 1.4 clean
	$(MAKE) -C 1.5 clean
	rm -f homonymous-lemmas-pos.tsv homonymous-lemmas.tsv homonymous-lexemes-pos.tsv homonymous-lexemes.tsv
	rm -f nouns-ý.tsv nouns-ý-lowercase.tsv



