#!/usr/bin/env perl

use strict;
use warnings;

my @root_allomorphs;

sub root_len {
    my ($segmented) = @_;

    if ($segmented =~ /\|(.+)\|/) {
	return length($1);
    }
    else {
	return 0;
    }
}

while (<>) {
    chomp;
    if (/^\s*$/) {  }

    elsif (/^Automatic/) {}
    
    elsif (s/Manual roots for (\S+)://) {
	my $root_lemma = $1;
	s/[\$\%\*].*//;
	s/^\s+//;
	s/\s+$//;
	s/\s+/ /g;
	print "$_\n";
	@root_allomorphs = split / /;
    }

    elsif (/^(\S+)\t(\S+)\t([A-Z])/) {
	my $short_lemma = $1;
	my $long_lemma = $2;
	my $pos = $3;

	my @solutions;
	foreach my $root (@root_allomorphs) {
	    my $segmented_lemma = $short_lemma;
	    
	    if ( ($segmented_lemma =~ /$root/) > 1 ) {
		print STDERR "Error: Ambiguous segmentation 1: more occurrences of root allomorph\t'$root' in '$short_lemma'\n";
	    }
	    elsif ( $segmented_lemma =~ s/($root)/|$root|/ ) {
		push @solutions, $segmented_lemma;
		@solutions = sort { root_len($b) <=> root_len($a) } @solutions; 
	    }
	}

	if (@solutions == 0) {
	    print STDERR "Error: No root allomorph found\t out of '".(join " ",@root_allomorphs)."' in '$short_lemma'\n";
	}
	elsif (@solutions > 1 and root_len($solutions[0]) == root_len($solutions[1])) {
	    print STDERR "Error: Ambiguous segmentation 2: more matching allomorphs of the same length\t in '$short_lemma' out of ".(join " ",@solutions)."\n";
	}
	else {
	    chomp;
	    print $_."\t".$solutions[0]."\n";
	}

    }

    else {
	print STDERR "Error: unrecognized line: $_ \n";
    }
    
    
}
