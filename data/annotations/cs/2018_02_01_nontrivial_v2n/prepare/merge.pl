#!/usr/bin/env perl

use strict;
use warnings;

binmode STDOUT,":utf8";

open my $J,"<:utf8", "odjonase.tsv";

my %union_reversed;

while (<$J>) {
#    předtančení-2 N 0.999999999991338       NEW: předtančit_:W V
    s/^\s+//;
    s/_\S+//g;
    s/-\S+//g;
    s/NEW://g;
    s/\s+/\t/g;
    my ($derivedlemma,$derivedpos,$score,$sourcelemma,$source_pos) = split;
#    print "$derivedlemma\t$sourcelemma\n";
    $union_reversed{reverse($derivedlemma)}{$sourcelemma}{'J'} = 1;
}

binmode STDERR, ":utf8";

open my $D, "<:utf8", "../../../../releases/cs/derinet-1-5-1.tsv";
my %parentless_noun;
while (<$D>) {
    # 31      Aakash  Aakash-1_;Y     N
    my ($id, $shortlemma, $longlemma, $pos, $parentid) = split;
    if (not $parentid and $pos eq "N") {
	$parentless_noun{$shortlemma} = 1;
    }
}


open my $M,"<:utf8", "deverbalnouns.csv";
while (<$M>) {
    #přemalba                        přemalovat / přemalovávat
    s/\?//;
    s/\s+/ /g;
    s/^ //;
    s/ $//;
    s/ \/ /\//g;
    my ($derived,$source) = split / /;
    if ( $derived and $source ) {
#	print "XXXX nacteno\n";
	if ($parentless_noun{$derived}) {
	    $union_reversed{reverse($derived)}{$source}{'M'}=1;
#	    print "XXX ok\n";
	}
	else {
	    print STDERR "$derived uz ma predka\n";
#	    print "XXX uz ma predka\n";
	}
#	print "$derived $source\n";
    }
}

for my $reversed (sort keys %union_reversed) {
    my $derived = reverse $reversed;
    for my $source (sort keys %{$union_reversed{$reversed}}) {
	my $fromwhom = join "",(sort keys %{$union_reversed{$reversed}{$source}});
	print "$derived\t$source\t$fromwhom\n";
    }



}    



