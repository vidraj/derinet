#!/usr/bin/env perl

use strict;
use warnings;

binmode STDOUT,":utf8";

my %source_lexeme;
foreach my $version (qw(05 09)) {
    
    open my $F,"<:utf8","t2_${version}_derivations.tsv" or die $!;

    while (<$F>) {
	chomp;
	my ($source,$target) = split;
	$source_lexeme{$target}{$version} = $source;

    }
}

foreach my $lexeme (sort keys %source_lexeme) {
    
    print $lexeme."\t<---\t".($source_lexeme{$lexeme}{"05"}||"_NONE05_")."\t".($source_lexeme{$lexeme}{"09"}||"_NONE09_")."\n";



}
