#!/usr/bin/env perl

use utf8;
binmode STDOUT, ":utf8";
binmode STDIN, ":utf8";


use strict;
use warnings;

my $current_cluster = "";

while (<>) {
    if (/^STARTOFCLUSTER/) {
	my @columns = split /\t/;
	$current_cluster = $columns[1];
    }
    elsif (/^SEGMENTEDNODE/) {
	my @columns = split /\t/;
	my $segmented = $columns[2];
	if ($segmented =~ /\(([^(]*[aeiyouáéíýóů])\)/) {
	    print "$1\tout of\t$current_cluster\n";
	}
    }
}
