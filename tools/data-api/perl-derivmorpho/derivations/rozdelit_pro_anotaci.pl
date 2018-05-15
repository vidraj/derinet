#!/usr/bin/env perl

use strict;
use warnings;

binmode STDIN,':utf8';
binmode STDOUT,':utf8';

my $current_rule;

my %multisource; # possibly generated from two sources (or by different rules)

my $line_number = 0;

my @lines;

while (<>) {
    s/\(/ \(/;
    push @lines, $_;

    chomp;

    my $present = s/(LINK ALREADY PRESENT)// ? $1 : '';

    my $change = ''; # hlaskova zmena
    if ( s/\((CHANGE: \S+ -> \S+)\)// ) {
        $change = $1;
    }

    if (/TRYING TO APPLY RULE (\S+ --> \S+)/) {
        $current_rule = $1;
    }

    elsif ( /(\S+) --> (\S+)/) {
        my ($source,$derived) = ($1,$2);
        $multisource{$derived}{"$source#$current_rule#$change#$present"} = $line_number;
    }

    $line_number++;
}


my %rulecomb2output;
my %rulecomb_count;

my @line_number_to_skip;

foreach my $derived ( keys %multisource ) {

    if ( keys %{$multisource{$derived}} > 1 ) { # multisource

        my %rule_combination;

        my $output = '';
        foreach my $source_item (sort keys %{$multisource{$derived}} ) {
            $line_number_to_skip[$multisource{$derived}{$source_item}] = 1;
            my ($source,$rule,$change,$present) = split /#/, $source_item;
            $rule_combination{$rule}++;
            $output .= "$source\t$derived\t$rule\t$change\t$present\n";
        }

        my $rule_combination_stringified = join ', ',sort keys %rule_combination;
        $rulecomb2output{$rule_combination_stringified}{$output} = 1;
        $rulecomb_count{$rule_combination_stringified}++;
    }
}



open my $MONO, ">:utf8","monosource.tsv";

foreach my $line_number (0..$#lines) {
    if (not $line_number_to_skip[$line_number] ) {
        print $MONO $lines[$line_number];
    }
}

close $MONO;



open my $MULTI, ">:utf8","multisource.tsv";

foreach my $rule_combination_stringified
    (sort { $rulecomb_count{$b} <=> $rulecomb_count{$a} } keys %rulecomb_count) {

    print $MULTI "\n---------------------------------\n";
    print $MULTI "$rulecomb_count{$rule_combination_stringified} GROUPS FOR RULE COMBINATION: $rule_combination_stringified\n";

    print $MULTI "\n";

    foreach my $output (sort keys %{$rulecomb2output{$rule_combination_stringified}}) {
        print $MULTI $output;
        print $MULTI "\n";
    }
}


close $MULTI;
