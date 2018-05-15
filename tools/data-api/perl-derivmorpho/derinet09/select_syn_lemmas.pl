#!/usr/bin/env perl

use strict;
use warnings;

binmode STDIN,':utf8';
binmode STDOUT, ':utf8';

while (<>) {

    s/\s+/ /g;
    s/^ //;
    my ($number,$lemma,$tag) = split / /;
    my $shortlemma = $lemma;
    $shortlemma =~ s/[_`].+//;
    $shortlemma =~ s/-\d+$//;

    print "$lemma\t$tag\n" unless $shortlemma=~/\d/
	or $shortlemma=~/[[:punct:]]/
	or $shortlemma=~/.+[[:upper:]]$/
	or $number<2
	or length($shortlemma) < 3
	;
        

}
