package Treex::Tool::DerivMorpho::Block::CS::AddLexemesFromList;
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

has dictionary_name => (
    is => 'ro',
    isa => 'Str',
    documentation => q(name of the source of lemmas),
);

has verify_lemma_uniqueness => (
    is => 'ro',
    isa => 'Bool',
    documentation => q(ensure that the (short-)lemmas being added aren't present already)
);

use Treex::Tool::Lexicon::CS;

sub process_dictionary {
    my ($self,$dict) = @_;

    open my $LIST, '<:utf8', $self->file or log_fatal $!;

    my $line;
    
    LEMMA:
    while (<$LIST>) {
        $line++;
        last if defined $self->maxlimit and $line > $self->maxlimit;
        next if /&amp;/;

        my ($long_lemma, $tag) = split;
        my $pos = substr($tag, 0, 1);
        my $short_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($long_lemma, 1); # homonym number deleted too
        
        if ($short_lemma =~ /../ and $short_lemma =~ /[[:lower:]]/) {
            my @lexeme_candidates = $dict->get_lexemes_by_lemma($short_lemma);
            for my $candidate (@lexeme_candidates) {
                if ($candidate->pos eq $pos and ($candidate->mlemma eq $long_lemma or ($self->verify_lemma_uniqueness and $candidate->lemma eq $short_lemma))) {
                    print STDERR 'Lemma ' . ($self->verify_lemma_uniqueness ? $short_lemma : $long_lemma) . " is already present. Skipping.\n";
                    next LEMMA;
                }
            }

            $dict->create_lexeme({
                lemma  => $short_lemma,
                mlemma => $long_lemma,
                pos => $pos,
                tag => $tag,
                lexeme_creator => $self->signature . '-' . ($self->dictionary_name ? $self->dictionary_name : $self->file),
            });
        }
    }

    return $dict;
}

1;
