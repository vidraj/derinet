package Treex::Tool::DerivMorpho::Block::CS::AddOstLexemesFromCNC;

use utf8;

use strict;
use warnings;

use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use Treex::Tool::Lexicon::CS;
use Treex::Tool::Lexicon::Generation::CS;

sub process_dictionary {
    my ($self,$dict) = @_;

    my $analyzer = Treex::Tool::Lexicon::Generation::CS->new();

    open my $OST, '<:utf8', $self->my_directory.'/manual.AddOstLexemesFromCNC.txt' or log_fatal($!);
    while (<$OST>) {
        chomp;
        next if /\*/ or not $_;
        my $short_new_lemma = $_;

        my ($source_lexeme) = $dict->get_lexemes_by_lemma($short_new_lemma);
        if (not $source_lexeme) {
            my @long_lemmas = map { $_->{lemma} } grep {  $_->{tag} =~ /^NN.S1/ } $analyzer->analyze_form($short_new_lemma, 0); # 0 == don't use guesser.

            my $long_lemma;
            if (@long_lemmas == 0) {
                # We could theoretically continue by using the short lemma as a techlemma,
                #  but in practice this means we've tried to analyze a bogus word, so we stop.
                print STDERR "warning: unknown noun $short_new_lemma\n";
                next;
            }
            else {
                # if (@long_lemmas > 1) {
                #     print STDERR "warning: more possible lemmas for $short_new_lemma\n";
                # }
                ($long_lemma) = grep { Treex::Tool::Lexicon::CS::truncate_lemma($_, 1) eq $short_new_lemma } @long_lemmas;

                if ($long_lemma) {
                    # print STDERR "\tchoosing $long_lemma\n";
                } else {
                    $long_lemma = $short_new_lemma;
                    print STDERR "warning: no good candidates found for $short_new_lemma.\n";
                }
            }

            $dict->create_lexeme({
                lemma  => $short_new_lemma,
                mlemma => $long_lemma,
                pos => 'N',
                lexeme_creator => $self->signature,
            });
        }
    }

    return $dict;
}

1;
