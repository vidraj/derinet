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

