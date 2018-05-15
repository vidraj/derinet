# t1: find lexemes that disappeared between 0.5 and 0.9

t1:
	cat ../../derinet/derinet2.tsv | cut -f2,4 | sort | uniq > t1_unique_05_lexemes.tsv
	cat ../derinet09.tsv | cut -f2,4 | sort | uniq > t1_unique_09_lexemes.tsv
	cat t1_unique_05_lexemes.tsv t1_unique_09_lexemes.tsv | sort | uniq > t1_union0509.tsv
	cat t1_unique_09_lexemes.tsv t1_union0509.tsv | sort | uniq -u > t1_output_only05.tsv

cleant1:
	rm t1*

# t2: zjistit, ktere hrany ubyly

t2:
	../../derimor Load file=../derinet09.tsv PrintDerivationPairs > t2_09_derivations.tsv
	../../derimor Load file=../../derinet/derinet2.tsv PrintDerivationPairs > t2_05_derivations.tsv

t2cont:
	./check_derivation_overlap.pl > t2_output.tsv

# t3: extract a random sample for manual evaluation

t3:
	cat ../derinet09.tsv | ./extract_random_sample_for_eval.pl > t3_random_sample.tsv
