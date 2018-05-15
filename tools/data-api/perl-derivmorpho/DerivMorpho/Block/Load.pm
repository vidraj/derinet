package Treex::Tool::DerivMorpho::Block::Load;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

has file => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(file name to load),
);

has limit => (
    is            => 'ro',
    isa           => 'Int',
    documentation => 'maximum number of lexemes to load (risky because of forward links)',
);

has filetype => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(type of the file to load. Supported types are ".slex" and ".tsv"),
);


use Treex::Tool::DerivMorpho::Dictionary;

sub process_dictionary {
    my ($self, $dict) = @_;
    $dict = Treex::Tool::DerivMorpho::Dictionary->new;
    $dict->load($self->file,{limit=>$self->limit, filetype=>$self->filetype});
    return $dict;
}

1;
