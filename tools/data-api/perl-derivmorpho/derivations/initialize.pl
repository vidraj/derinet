#!/usr/bin/env perl

use strict;
use warnings;
use Treex::Tool::Lexicon::DerivDict::Dictionary;
use Treex::Tool::Lexicon::CS;

my ( $input_file, $output_file ) = @ARGV;

if ( not $input_file or not $output_file ) {
    die "Usage: initialize.pl <lemmalist.tsv> <dictname.tsv>";
}

open my $INPUT, '<:utf8', $input_file or die $!;

my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new();

print STDERR "Loading...\n";
while (<$INPUT>) {
#    last if $. > 10000;
    next if /\&/;
    chomp;
    my ($long_lemma, $pos) = split;
    my $short_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($long_lemma, 1); # homonym number deleted too
    if ($short_lemma =~ /../ and $short_lemma =~ /[[:lower:]]/) {
        $dict->create_lexeme({
            lemma  => $short_lemma,
            mlemma => $long_lemma,
            pos => $pos,
            lexeme_origin => 'czeng',
        });
    }
}

print STDERR "Storing...";
$dict->save($output_file);
print STDERR "Done.";
