#!/usr/bin/env perl

use strict;
use warnings;

my %lemmas_to_numbers;

while (<>) {
	chomp;
	my ($techlemma, $tag) = /^(.*)\t(.)$/;
	
	print STDERR "Lemma '$techlemma' has bad tag $tag\n" unless $tag =~ /[ADNV]/;

	$techlemma =~ s/[_`].+//;
	
	my $lemma;
	my $number;
	if ($techlemma =~ /^(.+)-(\d+)$/) {
		($lemma, $number) = ("$1-$tag", $2);
	} else {
		($lemma, $number) = ("$techlemma-$tag", 0);
	}
	
	my $numbers_array_ref = $lemmas_to_numbers{$lemma};
	if ($numbers_array_ref) {
		push @$numbers_array_ref, $number;
	} else {
		$lemmas_to_numbers{$lemma} = [$number];
	}
}

for my $lemma (keys %lemmas_to_numbers) {
	my @numbers_array = @{$lemmas_to_numbers{$lemma}};
	print $lemma . "\n" if (@numbers_array >= 2 and grep { $_ == 0 } @numbers_array);
}
