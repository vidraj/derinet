#!/usr/bin/env perl

use strict;
use warnings;

# remove asterisked lines that are left unastersked elsewhere in the file (regardless the ordering of positive and negative lines)

my @lines;
while (<>) {
    push @lines,$_;
}

my %positive;

foreach my $line (@lines) {
    if ($line !~ /\*/) {
	$positive{remove_spaces($line)} = 1;
    }
}

#print STDERR "XXX".($positive{"tvarovat-->tvarovka"})."\n";


foreach my $line (@lines) {
#    if ($line=~/tvarovka/) {print STDERR "TV: 1\n"};
    my $unasterisked = $line;
    if ($unasterisked =~ s/\*// #and do {print STDERR "TV1.5\n" if $line=~/tvarovka/;1}
	) {

	if ( $positive{remove_spaces($unasterisked)}) {
#	    print STDERR "Q1\n";
	}
	else {
	    print $line;
#	    print STDERR "Q2\n";
	}

#	    if ($line=~/tvarovka/) {print STDERR "TV: 2\n"};
	


#	print $line;
    }
    else {
#	if ($line=~/tvarovka/) {print STDERR "TV: 3\n"};
	print $line;
    }
}


sub remove_spaces {
    my $string = shift;
    $string =~ s/\s+//g;
    return $string;
}
