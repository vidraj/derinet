#!/usr/bin/env perl

use strict;
use warnings;

binmode STDIN,':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

# This function helps with choosing a variant with the richest technical information.
#  bigger score == richer information
sub calculate_score {
  my ($word_description) = @_;
  my $word = $word_description->{lemma};

  # Lemmas with more forms should be better.
  my $score = log $word_description->{count};
  $score += 1001 if $word_description->{lemma_matches_tag};

  $score += length($word); # Longer is better. Longer lemmas may contain explanations etc.
  $score += 1000 if $word =~ /[_^]\(\*/; # The word has a derivation in the techlemma

  # A small penalty for each occurence of a style information tag in the techlemma
  #  (We want to include only the 'most neutral form' of a lemma.)
  my $style_info_count = () = $word =~ /_,/g;
  $score -= 4 * $style_info_count;
  return $score;
}



# reading equivalence classes
open my $EQ , '<:utf8', '../data/straka_same_lemma_sense_classes.txt' or die $!;


my %substitute;


while (<$EQ>) {
  chomp;
  my @alternatives = split / /;
  foreach my $alternative (@alternatives[1..$#alternatives]) {
    if (exists $substitute{$alternative}) {
      # Check that no lemma is in more than one substitution rule, because that would lead to rules being overwritten.
      die "The alternative $alternative already has a substitution " . $substitute{$alternative} . ', substitution ' . $alternatives[0] . ' not added.'
    }
    $substitute{$alternative} = $alternatives[0];
  }
}

my %seen;

while (<>) {
  chomp;
  my ($lemma, $tag, $count, $lemma_matches_tag) = split;
  #print STDERR "Loaded $lemma $tag\n";
  my $pos = substr($tag, 0, 1);

  my $shortened = $lemma;
  $shortened =~ s/[_`].+//;

  if ($seen{"$shortened#$pos"}) {
    #print STDERR "Adding second variant for " . $seen{"$shortened#$pos"}->[0] . ": $lemma $tag.\n";
    push @{$seen{"$shortened#$pos"}}, {
      lemma => $lemma,
      tag => $tag,
      count => $count,
      lemma_matches_tag => $lemma_matches_tag
    };
  }
  else {
    $seen{"$shortened#$pos"} = [{
      lemma => $lemma,
      tag => $tag,
      count => $count,
      lemma_matches_tag => $lemma_matches_tag
    }];
  }
}

for my $shortened_w_pos (keys %seen) {
  my ($shortened, $pos) = $shortened_w_pos =~ /^(.*)#(.)$/;
  
  if ($substitute{$shortened}) {
    if ($seen{$substitute{$shortened} . '#' . $pos}) {
      # I've either already printed the substituted form, or I'll print it in the future.
      next;
    } else {
      print STDERR "ERROR: Seen $shortened but haven't seen " . $substitute{$shortened} . " -- not substituting.\n";
    }
  }

  # Select the best long version for this short one.
  my @long_variants = @{$seen{$shortened_w_pos}};
  my $best = $long_variants[0];
  my $best_score = calculate_score($best);

  for my $long_variant (@long_variants) {
    my $score = calculate_score($long_variant);
    if ($score > $best_score) {
      $best = $long_variant;
      $best_score = $score;
    } elsif ($score == $best_score and ($best->{lemma} cmp $long_variant->{lemma}) > 0) {
      # This is added to ensure stability of output.
      $best = $long_variant;
      $best_score = $score;
    }
     #print STDERR "Selected variant '$best'.\n";
  }

  my $best_lemma = $best->{lemma};
  my $best_tag = $best->{tag};
  
  die "THE TAGS DON'T MATCH: '$shortened' '$pos' and '$best_lemma' '$best_tag'\n" if substr($best_tag, 0, 1) ne $pos;
  print "$best_lemma\t$best_tag\n";
}
