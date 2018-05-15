package Treex::Tool::DerivMorpho::Block::Dummy;
use utf8;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

sub process_dictionary {
	my ($self, $dict) = @_;
	$dict->create_lexeme({
		lemma          => 'testlemma',
		lexeme_creator => $self->signature
	});
	return $dict;
}

1;
