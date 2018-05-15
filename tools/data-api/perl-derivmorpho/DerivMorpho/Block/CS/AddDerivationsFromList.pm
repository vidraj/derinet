package Treex::Tool::DerivMorpho::Block::CS::AddDerivationsFromList;
use utf8;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

has file => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(file name to load),
);

has maxlimit => (
    is => 'ro',
    isa => 'Int',
    documentation => q(maximum number of lexemes to create),
);

use Treex::Tool::Lexicon::CS;

sub process_dictionary {
    my ($self,$dict) = @_;

    open my $LIST, '<:utf8', $self->file
        or log_fatal($!);

    my $line;
    while (<$LIST>) {
        $line++;
        last if defined $self->maxlimit and $line > $self->maxlimit;
        next if /&amp;/;

        chomp;
        my ($source_short_lemma,$source_pos,$target_short_lemma,$target_pos) = split;

        my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_short_lemma, $source_pos, $target_short_lemma, $target_pos);

        if (not $source_lexeme) {
            print  "ERR: No lexeme found for $source_short_lemma $source_pos\n";
        }
        elsif (not $target_lexeme) {
            print "ERR: No lexeme found for $target_short_lemma $target_pos\n";
        }
        elsif ($target_lexeme->source_lexeme and $source_lexeme eq $target_lexeme->source_lexeme) {
            print "OK: Already connected $source_short_lemma -> $target_short_lemma\n";
        }
        else {
            print "OK: adding $source_short_lemma -> $target_short_lemma  \n";
            $dict->add_derivation({
                                 source_lexeme => $source_lexeme,
                                 derived_lexeme => $target_lexeme,
                                 deriv_type => $source_lexeme->pos."2".$target_lexeme->pos,
                                 derivation_creator => $self->signature . ': ' . $self->file,
                                }
            );
        };
    }

    return $dict;
}

1;
