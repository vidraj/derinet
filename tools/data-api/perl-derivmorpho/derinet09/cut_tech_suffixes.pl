#!/usr/bin/env perl

use strict;
use warnings;

while (<>) {
	my ($lemma, $pos) = $_ =~ /^(.*)\t(.*)$/;
	$lemma =~ s/[_`].*//;
	$lemma =~ s/-[0-9]+$//;
	print "$lemma\t$pos\n";
}
