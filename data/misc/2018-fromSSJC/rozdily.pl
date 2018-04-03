#!/usr/bin/env perl

use strict;
use warnings;

#binmode STDOUT,">:encoding(utf8)";

my %ssjc_parent;

print STDERR "Loading pairs extracted from SSJC\n";
open my $S,"ssjc-wf-all.tsv";
while (<$S>) {
  chomp;
  my ($child, $parent) = map {s/_.+//;$_} split;
  $ssjc_parent{$child} = $parent;
#  print "child=$child parent=$parent\n";
}

print STDERR "Loading pairs from DeriNet 1.5.1\n";
my @derinet_lemmas;
my %derinet_parent;
open my $D,"../../releases/cs/derinet-1-5-1.tsv";
while (<$D>) {
  chomp;
  my ($ord, $lemma, $longlemma, $pos, $parent) = split;
  if ($pos eq "V" and $lemma=~/t$/) {
    $lemma .= "i";
  }
  push @derinet_lemmas, $lemma;
  $derinet_parent{$lemma} = $parent;
}

print STDERR "Finding the differences\n";
foreach my $child_lemma (keys %derinet_parent) {
  if ($derinet_parent{$child_lemma}) {
    my $derinet_parent_lemma = $derinet_lemmas[$derinet_parent{$child_lemma}];

#    print "child=$child_lemma derinet=$derinet_parent_lemma\n";

    if (defined $ssjc_parent{$child_lemma} and $ssjc_parent{$child_lemma} ne $derinet_parent_lemma) {
      print "$child_lemma\t$derinet_parent_lemma\t$ssjc_parent{$child_lemma}\n";
    }
  }
}







