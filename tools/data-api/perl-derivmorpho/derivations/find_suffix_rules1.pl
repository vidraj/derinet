#!/usr/bin/env perl

use strict;
use warnings;

binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';

my (@prev_lemmas,@prev_poss);
my $window = 5;

while (<>) {
    my ($id,$lemma,$long_lemma,$pos) = split;
    next if /2/;

    foreach my $index (0..$#prev_lemmas) {

        my $prev_lemma = $prev_lemmas[$index];
        my $prev_pos = $prev_poss[$index];

        my @letters_of_lemma = split//,$lemma;
        my @letters_of_prev_lemma = split//,$prev_lemma;
        my $common_prefix = '';

        while (@letters_of_lemma and @letters_of_prev_lemma) {
            if ($letters_of_lemma[0] eq $letters_of_prev_lemma[0]) {
                $common_prefix .= shift @letters_of_lemma;
                shift @letters_of_prev_lemma;
            }
            else {
                last;
            }
        }

        if ($common_prefix =~ /../) {
            my $suffix = join '',@letters_of_lemma;
            my $prev_suffix = join '',@letters_of_prev_lemma;
            if (length($suffix) < length($prev_suffix)) {
                ($suffix,$prev_suffix) = ($prev_suffix, $suffix);
                ($pos,$prev_pos) = ($prev_pos, $pos);
            }
            print "$prev_pos-$prev_suffix $pos-$suffix\t$prev_lemma $lemma\n";

        }

#        print "$lemma $prev_lemma PREFIX: $common_prefix\n";

    }

    if ( @prev_lemmas > $window ) {
        shift @prev_lemmas;
        shift @prev_poss;
    }
    push @prev_lemmas, $lemma;
    push @prev_poss,  $pos;
}
