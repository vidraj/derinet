package Treex::Tool::DerivMorpho::Block::EmptyModule;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use strict;
use warnings;

use feature 'unicode_strings';
use utf8;
binmode STDIN,  ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

use Treex::Core::Log;

has file => (
	is            => 'ro',
	isa           => 'Str',
	documentation => q(file name to load),
);

sub process_dictionary {
	my ($self, $dict) = @_;

	open my $R, '<:utf8', $self->file
		or log_fatal('You have to pass a valid filename '
			. "as an argument named 'file'.\nError: $!");
	
	while (<$R>) {
		print;
	}
}

1;
