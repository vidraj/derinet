#!/usr/bin/env perl

use strict;
use warnings;

binmode STDIN,":utf8";
binmode STDOUT,":utf8";


my @lexemes;
while (<>) {
  chomp;
  my ($ord,$short,$long,$pos,$source) = split;

  push @lexemes,{short=>$short,long=>$long,pos=>$pos,source=>$source};
}


foreach my $n (1..10000) {
    my $index = int(rand($#lexemes));

    print $lexemes[$index]{short}."-".$lexemes[$index]{pos}."\t ---> \t";
    if ( $lexemes[$index]{source} =~ /^\d+$/ ) {
	my $source_index = $lexemes[$index]{source};
	print $lexemes[$source_index]{short}."-".$lexemes[$source_index]{pos};
    }
    print "   # \n";

}
