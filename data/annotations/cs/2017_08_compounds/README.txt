Contents:
=========

Files whose names start with "patterns" contain the patterns which have been
used to identify the candidates.

Files whose names start with "candidates" contain the (already selected) lemmas
of words which have been identified using the corresponding patterns or criteria
and could be considered as compounds. All the files except the one whose name
contains "cky_sky_ovy" contain only a list of lemmas. The "cky_sky_ovy" file
contains also some metainformation.

The file "all_solitary_compounds" contains compounds which have been encountered
among the candidates without also encountering any of their derived words.

The file "all_compound_clusters" contains the clusters of compound and their
derived words which have been identified using the given patterns and criteria.
The clusters are organised in such a way that the head of the cluster (i.e. 
the actual compound) is first, its direct derived words follow in a bracket, 
separated by space, their respective derived words follow the base word in
another bracket and so on. Thus, extracting the first column, we get a list 
containing only compounds without the words derived from them.

The file "all actual compounds" contains all words from "all_solitary_compounds"
plus all the words from "all_compound_clusters" which are considered actual
compounds (i.e. words from the first column). The words in this file are sorted
alphabetically as they are intended as the input for "quickselect.pl".

The script "quickselect.pl" serves to mark compounds from annotated files in the
DeriNet database. It requires two arguments, the first one is the DeriNet
database file, the second one is the file containing words to be marked. Both
files have to be sorted according to the same criteria (the script goes through
both files sequentially to increase its speed).
                                                              
The file "derinet-1-4_compounds_marked.tsv" contains the whole DeriNet 1.4 
database except compounds are marked by adding "C" to the letter denoting the
PoS of a given entry.

How to get the candidates based on patterns:
============================================

grep -f patternfile lemmalist

where patternfile is the file containing the desired set of patterns and
lemmalist is a file containing a list of lemmas we are interested in (I used
the list of parentless lemmas in DeriNet)

However, the candidate files in this folder have already been annotated, so they
do not contain all the lemmas which can be found using this method.

How to get the candidates based on hyphenation:
===============================================

grep "-" lemmalist

How to get candidates based on length:
======================================

grep ".{15}" lemmalist

How to mark compounds based on an annotated file
================================================

First, both files need to be sorted according to the same criterion. The file 
"all_actual_compounds" is in alphabetical order but the same is not true for the
DeriNet database files. The easiest way is to sort the database alphabetically
by lemmas. This can be done as follows:

sort -k2,2 derinet-1-4.tsv > derinet-1-4_sorted.tsv

The sorted file can then be used as an input for the "quickselect.pl" script;
the results will be in alphabetical order of lemmas, so to get the original
DeriNet sorting back, we need to sort the file by numerical value of the ID.

perl quickselect.pl derinet-1-4_sorted.tsv all_actual_compounds | sort -n > 
derinet-1-4_compounds_marked.tsv

In the resulting file, there are more words marked as compounds than in the
annotated compounds file. The reason is that multiple DeriNet entries have the 
same lemma, and therefore multiple entries can be marked for each annotated 
lemma. However, such cases are not very frequent, the difference should be about
100 entries.

In the current version of the "derinet-1-4_compounds_marked.tsv" file, entries
with the same lemma have been annotated and the wrongly marked compounds 
unmarked, so the difference between the number of annotated lemmas and of marked
entries in this file is only 19 (sometimes multiple marked entries with the same
lemma could be considered correct). 