package Treex::Tool::DerivMorpho::Block::CS::AddDerivationsFromLemmaSuffices;

use utf8;

use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use Treex::Core::Log;
use Treex::Tool::Lexicon::CS;

sub process_dictionary {

    my ($self, $dict) = @_;

    LEXEME:
    foreach my $lexeme ( grep {not $_->source_lexeme} $dict->get_lexemes ) { # TODO: add an option for overriding?

        my ($lenght_of_old_suffix, $new_suffix);
        my $deriv_comment_type = 'standard';
        if ($lexeme->mlemma =~ /_\^?\(\*(\d+)([^)]*)\)/) {
            # There is a standard derivational comment, prefer it to the
            #  nonstandard ones parsed below.
            ($lenght_of_old_suffix, $new_suffix) = ($1, $2);
        } else {
            # The standard derivational comment isn't there, but there may be a ^GC, ^FM, ^OR, ^FA, ^H3, ^FC, ^KY, ^D2, ^DI, ^UV, ^FN, ^HN, ^H2…
            # With one * or two **s.
            ($deriv_comment_type, $lenght_of_old_suffix, $new_suffix) = $lexeme->mlemma =~ /_\^.*\(\^([^*]*)\*(\*|\d+)([^)]*)\)/;
        }

        next LEXEME unless (defined $lenght_of_old_suffix);

        my $old_mlemma = Treex::Tool::Lexicon::CS::truncate_lemma($lexeme->mlemma, 0);

        # If there are two **s in a non-standard derivational comment,
        #  it means the old lemma is completely replaced.
        if ($lenght_of_old_suffix eq '*') {
            $lenght_of_old_suffix = length($old_mlemma);
        }

        my $new_mlemma = $old_mlemma =~ s/.{$lenght_of_old_suffix}$/$new_suffix/r;
        if ($new_mlemma eq $old_mlemma or Treex::Tool::Lexicon::CS::truncate_lemma($new_mlemma, 1) eq Treex::Tool::Lexicon::CS::truncate_lemma($old_mlemma, 1)) { # Sometimes the derivational comments try to derive a lexeme from itself. Prevent this.
            log_warn("These two should not be equal: $new_mlemma and " . $lexeme->mlemma);
            next LEXEME;
        }

        my $short_new_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($new_mlemma, 1);

        my @source_lexeme_candidates = $dict->get_lexemes_by_lemma($short_new_lemma);

        # select the correct one – $new_mlemma contains numbers, which can help desambiguate the target lexemes.
        my $homonym_number = $lexeme->get_homonym_number();
        my @source_lexemes = grep { $_->get_homonym_number() eq $homonym_number } @source_lexeme_candidates;
        my $source_lexeme;

        if (@source_lexemes == 1) {
            $source_lexeme = $source_lexemes[0];
        } elsif (@source_lexemes) { # More than one candidate
            $source_lexeme = $source_lexemes[0];
            log_info('Multiple candidates with correct homonym-number for ' . $lexeme->mlemma . '. Selecting ' . $source_lexeme->mlemma);
        } elsif (@source_lexeme_candidates) {
            # If the parent with the correct homonym number isn't there, but there
            #  are some others, just pick the first one. It's better than nothing.
            $source_lexeme = $source_lexeme_candidates[0];
            if (@source_lexeme_candidates > 1) { # We are choosing essentially randomly from several alternatives. This isn't good; better warn the user.
                log_warn('No candidate with correct homonym-number for ' . $lexeme->mlemma . '. Selecting nonmatching ' . $source_lexeme->mlemma);
            }
        }

        if ($source_lexeme) {
            $dict->add_derivation({
                source_lexeme => $source_lexeme,
                derived_lexeme => $lexeme,
                deriv_type => $source_lexeme->pos."2".$lexeme->pos,
                derivation_creator => $self->signature . ($deriv_comment_type eq 'standard' ? '' : ": $deriv_comment_type"),
            });
        } else {
            # TODO: doresit generovani (na POS ale potreba analyza)
            log_warn('Error when processing ' . $lexeme->mlemma . ": $new_mlemma is not in the database!");
        }
    }

    return $dict;
}
