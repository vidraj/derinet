#!/usr/bin/env perl

use strict;
use warnings;

use Treex::Tool::Lexicon::DerivDict::Dictionary;
use File::Slurp;
binmode STDOUT, ":utf8";

my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new;
$dict->load(shift @ARGV);

my $tmp_file = "tmp.tsv";
$dict->save($tmp_file);

open my $F, "<:utf8", $tmp_file or die $!;
while (<$F>) {
    print $_;
}


