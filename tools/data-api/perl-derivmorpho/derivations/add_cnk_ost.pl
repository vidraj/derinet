#!/usr/bin/env perl

use strict;
use warnings;

use Treex::Tool::Lexicon::DerivDict::Dictionary;
use Treex::Tool::Lexicon::CS;

my ( $input_file, $output_file ) = @ARGV;
if ( not $input_file or not $output_file ) {
    die "Wrong usage";
}

use CzechMorpho;
my $analyzer = CzechMorpho::Analyzer->new();

my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new();
$dict->load($input_file);

open my $OST, '<:utf8', 'ost-z-CNK.csv' or die $!;
while (<$OST>) {
    chomp;
    next if /\*/ or not $_;
    my $short_new_lemma = $_;

    my ($source_lexeme) = $dict->get_lexemes_by_lemma($short_new_lemma);
    if (not $source_lexeme) {
        my @long_lemmas = map { $_->{lemma} } grep {  $_->{tag} =~ /^NN.S1/ } $analyzer->analyze($short_new_lemma);
        if (@long_lemmas == 0) {
            print STDERR "warning: unknown noun $short_new_lemma\n";
        }
        elsif (@long_lemmas > 1) {
            print STDERR "warning: more possible lemmas for $short_new_lemma\n";
        }
        else {
            $dict->create_lexeme({
                lemma  => $short_new_lemma,
                mlemma => $long_lemmas[0],
                pos => 'N',
                lexeme_origin => 'ost-from-cnk',
            });
        }

    }
}

$dict->save($output_file);
