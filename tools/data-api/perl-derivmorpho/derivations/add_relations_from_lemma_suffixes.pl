#!/usr/bin/env perl

use strict;
use warnings;

use Treex::Tool::Lexicon::DerivDict::Dictionary;
use Treex::Tool::Lexicon::CS;

my ( $input_file, $output_file ) = @ARGV;
if ( not $input_file or not $output_file ) {
    die "Wrong usage";
}

my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new();
$dict->load($input_file);

foreach my $lexeme ($dict->get_lexemes) {
    if ( $lexeme->mlemma =~ /\^\(\*(\d)(.*)\)/ ) {
        my ( $lenght_of_old_suffix, $new_suffix ) = ($1, $2);
        my $new_mlemma = $lexeme->mlemma;
        $new_mlemma =~ s/_.+//;
        $new_mlemma =~ s/.{$lenght_of_old_suffix}$/$new_suffix/;
        if ($new_mlemma eq $lexeme->mlemma) {
            print "These two should not be equal\n";
        }
        my $short_new_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($new_mlemma);

        my ($source_lexeme) = $dict->get_lexemes_by_lemma($short_new_lemma);
        if ($source_lexeme) {
            $dict->add_derivation({
                source_lexeme => $source_lexeme,
                derived_lexeme => $lexeme,
                deriv_type => $source_lexeme->pos."2".$lexeme->pos,
            });

#            print "  orig_mlemma ".$lexeme->mlemma."\n";
#            print "  new_mlemma ".$new_mlemma."\n";
#            print "  short_new_lemma ".$short_new_lemma."\n";
#            print "  found_lexeme_lemma ".$source_lexeme->lemma."\n";
#            print "relation created: ".$lexeme->lemma." --> ".$short_new_lemma."\n\n";
        }
        else {
#            print STDERR "Source lexeme not available: ".$lexeme->mlemma." --> $new_mlemma\n";
        }
    }
}


$dict->save($output_file);
