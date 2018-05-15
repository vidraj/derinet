package Treex::Tool::DerivMorpho::Block::CS::AddAdj2AdvByRules;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use utf8;

use Treex::Core::Log;

use Treex::Tool::Lexicon::CS qw(truncate_lemma);

use Treex::Tool::Lexicon::Generation::CS; #use CzechMorpho;
my $analyzer = Treex::Tool::Lexicon::Generation::CS->new(); #CzechMorpho::Analyzer->new();

sub process_lexeme {

    my ($self, $adv_lexeme, $dict) = @_;
    return if $adv_lexeme->pos ne 'D' or $adv_lexeme->lemma !~ /ě$/;

    my $adv_lemma = $adv_lexeme->lemma;
    my @candidates = map {my $lemma = $adv_lemma; $lemma =~ s/ě$/$_/;$lemma} qw(í ý);

    my @long_lemmas;
    foreach my $candidate (@candidates) {
        push @long_lemmas,  map { $_->{lemma} } grep { $_->{tag} =~ /^AAMS1/ } $analyzer->analyze_form($candidate);
    }

#    print scalar(@long_lemmas)."\t".$adv_lemma."\t".(join ' ',@long_lemmas)."\n";

    if (@long_lemmas) {

        my $adj_long_lemma = $long_lemmas[0]; # TODO: vyjimecne neni spravny ten prvni, chtelo by to seznam vyjimek
        my $adj_short_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($adj_long_lemma, 1); # The "1" makes truncate_lemma() strip the homonym number as well.

        my @adj_lexemes = $dict->get_lexemes_by_lemma($adj_short_lemma);

	if (($adj_short_lemma =~ s/.$/ě/r) ne $adv_lemma) { # There is a spelling change in the new lemma. We will now check whether it is really necessary by searching for an unchanged lexeme in the DB.
            my @backup_lexemes;
            foreach my $candidate (@candidates) {
                push @backup_lexemes, grep { $_->{pos} eq 'A' } $dict->get_lexemes_by_lemma($candidate);
            }

            if (@backup_lexemes == 1) {
                log_info("Selecting backup candidate for $adv_lemma: " . $backup_lexemes[0]->{mlemma});
                @adj_lexemes = @backup_lexemes;
            } elsif (@backup_lexemes > 1) {
                log_info("More possibilities for $adv_lemma: " . join(' ', map { $_->{mlemma} } @backup_lexemes));
                @adj_lexemes = @backup_lexemes;
            } else {
                log_info("LINGUISTS BEWARE! Trying to attach $adv_lemma to $adj_short_lemma");
            }
        }

        if (not @adj_lexemes) {
            push @adj_lexemes,
                $dict->create_lexeme({
                    lemma  => $adj_short_lemma,
                    mlemma => $adj_long_lemma,
                    pos => 'A',
                    lexeme_creator => $self->signature,
                });
        }

        $dict->add_derivation({
            source_lexeme => $adj_lexemes[0],
            derived_lexeme => $adv_lexeme,
            deriv_type => 'A2D',
            derivation_creator => $self->signature,
        });
    }
}


1;
