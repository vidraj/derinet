#!/usr/bin/env perl

# a script for extracting manually confirmed derivations (and not compounds) from false_roots_one_candidate_retrosort.tsv
# in the format expect by AddDerivations ("parentlemma TAB > TAB childlemma")

use strict;
use warnings;

while(<>) {
	chomp;
	my @columns = split/\t/;
	
	if (/^\#/) { # the first comment line
	}
	
	elsif ( defined $columns[2] and $columns[2] eq "+" ) { # a correctly predicted derivational parent lemma
		print "$columns[1]\t>\t$columns[0]\n"
	}

	elsif ($columns[2] and $columns[2]=~/^\w{3,}$/){ # a manually filled correct lemma; not a compound of two
	    print "$columns[2]\t>\t$columns[0]\n"
	}
	
}
