#!/usr/bin/perl

use strict;
use warnings;

my $current_rule;
my %pair_by_rule;

while (<>) {
    chomp;
    if (/TRYING TO APPLY RULE (.+)/) {
        $current_rule = $1;
    }

    s/\(.+//;
    if (/(\S+ --> \S+)/) {
        $pair_by_rule{$1}{$current_rule}++;
    }
}


foreach my $pair (keys %pair_by_rule) {
    if (keys %{$pair_by_rule{$pair}} >1) {
        print $pair."  BY RULES  ".(join " , ",keys %{$pair_by_rule{$pair}})."\n";
    }
}
