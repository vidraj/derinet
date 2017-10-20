#!/usr/bin/env perl

use strict;
use warnings;
use utf8;

my ($filename_orig,$filename_pruned) = @ARGV;
print STDERR "Unannotated file: $filename_orig\n";
print STDERR "File with annotation by deletion: $filename_pruned\n";

#binmode STDOUT,'>:utf8';

open my $D,#'<:utf8',
  $filename_pruned or die $!;
my %not_deleted;
while (<$D>) {
  $not_deleted{remove_spaces($_)}++;
}

open my $O,#'<:utf8',
  $filename_orig or die $!;
while (<$O>) {
  if ($not_deleted{remove_spaces($_)}) {
    print;
  }
  else {
    print "* $_";
  }
}


sub remove_spaces {
  my $string = shift;
  $string =~ s/\s//g;
  return $string;
}
