#!/usr/bin/env perl

use strict;
use warnings;

my %lemma2masks;

while (<>) {
    chomp;
    my ($lemma,$mask) = split('\t');
    $lemma2masks{$lemma}{$mask} = 1;
}

foreach my  $lemma (sort keys %lemma2masks) {
    my @masks =  sort keys %{$lemma2masks{$lemma}};
    if (@masks>1) {
	print "$lemma\t";
	print (join " ", @masks);
	print "\n";
    }
}

    
