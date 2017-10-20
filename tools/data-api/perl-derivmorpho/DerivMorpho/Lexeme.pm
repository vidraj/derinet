package Treex::Tool::DerivMorpho::Lexeme;

use utf8;

use Moose;
use MooseX::SemiAffordanceAccessor;

use Scalar::Util qw(weaken);
use Treex::Tool::Lexicon::CS;
use Treex::Core::Log;

has 'lemma' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'basic word form',
);

has 'mlemma' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'lemma in the PDT m-layer style, including technical suffices',
);

has 'pos' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'part of speech, single-letter PDT m-layer convention',
);

has 'tag' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'positional tag in the PDT m-layer style',
);

has 'source_lexeme' => (
    is      => 'rw',
#    isa     => 'Ref',
    trigger => \&_set_source_lexeme_trigger,
    documentation => 'part of speech, single-letter PDT m-layer convention',
);

has 'deriv_type' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'type of word-formative derivation',
);

has 'lexeme_creator' => (
    is      => 'rw',
    isa     => 'Str',
    documentation => 'who generated this lexeme',
);


has '_id' => (
    is => 'rw',
    isa => 'Num',
    documentation => 'a unique value identifying each lexeme in hashes of derived lexemes'
);

has '_derivation_history' => (
    is      => 'rw',
    isa     => 'ArrayRef[HashRef]',
    documentation => 'a list of those who generated the link between this lexeme and its source lexeme plus the source lexemes themselves',
);

has '_dictionary' => (
    is      => 'rw',
    isa     => 'Ref',
    documentation => 'the dictionary in which this lexeme is contained',
);

has '_derived_lexemes' => (
    is      => 'rw',
    isa     => 'HashRef',
    default => sub {{}},
    documentation => 'array of lexemes that point to his one by their source_lexeme references',
);

sub get_derivation_creator {
    my ($self) = @_;
    if ($self->_derivation_history and @{$self->_derivation_history}) {
        return $self->_derivation_history->[-1]->{'creator'};
    } else {
        return '';
    }
}

sub set_derivation_creator {
    my ($self, $new_creator) = @_;
    my $history_ref = $self->_derivation_history;

    my %history_record = (
        'creator' => $new_creator,
        'type'    => $self->deriv_type,
        'source'  => $self->source_lexeme # TODO weaken perhaps? Rather not.
    );

    if ($history_ref) {
        push @$history_ref, \%history_record;
    } else {
        $self->{_derivation_history} = [\%history_record];
    }
}

sub get_derivation_history {
    my ($self) = @_;
    my $history_ref = $self->_derivation_history;
    return '' if not $history_ref;
    return join(',', map { $_->{'creator'} . '[' . ($_->{'source'} ? $_->{'source'}->mlemma : '') . ']' } @$history_ref);
}

sub _set_source_lexeme_trigger {
    my ( $self, $new_source, $old_source ) = @_;

    if (defined $old_source) {
        if (not delete $old_source->_derived_lexemes->{$self->_id}) {
            log_fatal("Failed to delete " . $self->mlemma . " from derived-lexeme set of " . $old_source->mlemma . ".\n"
                    . "The set is: '" . join("', '", map { $_->mlemma } values %{$old_source->_derived_lexemes}) . "'"
            );
        }
    }

    if (defined $new_source) {
        $new_source->_derived_lexemes->{$self->_id} = $self;
        weaken( $new_source->_derived_lexemes->{$self->_id} );
    } else {
        $self->set_deriv_type('');
        $self->set_derivation_creator('deleted');
    }
}

sub get_derived_lexemes {
    my ( $self ) = shift;
    return values %{$self->_derived_lexemes};
}

sub get_root_lexeme {
    my ( $self ) = shift;
    my $root_lexeme = $self;
    my %passed;
    while ( $root_lexeme->source_lexeme ) {
        if ($passed{$root_lexeme}) {
            log_warn('Warning: cycle in derivational relations!');
            last;
        }
        $passed{$root_lexeme} = 1;
        $root_lexeme = $root_lexeme->source_lexeme;
    }
    return $root_lexeme;
}

sub get_homonym_number {
    my ( $self ) = shift;
    if (Treex::Tool::Lexicon::CS::truncate_lemma($self->mlemma, 0) =~ /-([0-9]+)$/) {
        return $1;
    } else {
        return '';
    }
}

1;
